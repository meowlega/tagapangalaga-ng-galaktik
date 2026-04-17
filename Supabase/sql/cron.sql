
DECLARE
    -- || --- Variable Declarations --- ||
    ally_data jsonb;
    opponent_data jsonb;
    current_state record;
    is_in_war boolean;
    opponent_name text;
    member_data jsonb;
    player_base_info jsonb;
    max_retries integer := 3;
    retry_count integer;
    request_id bigint;
    
    -- New variables for journaling logic
    new_points integer;
    old_points integer;
    points_gain integer;
    
    -- We define the headers we want to send in a variable for easy reuse.
    request_headers jsonb := jsonb_build_object('User-Agent', 'Supabase/pg_net Cron Job');

BEGIN
    -- || --- 1. GET CURRENT STATE FROM OUR DATABASE --- ||
    SELECT "isInWar", "isTrackPopulated" INTO current_state
    FROM public."allyAllianceState" WHERE id = 1;
    
    -- || --- 2. FETCH ALLIANCE DATA FROM API (with retry logic and headers) --- ||
    retry_count := 0;
    WHILE retry_count < max_retries LOOP
        BEGIN
            request_id := extension.net.http_get(
                url := 'https://api.galaxylifegame.net/Alliances/get?name=pinoy%20warriors',
                headers := request_headers -- ADDING THE HEADER HERE
            );
            SELECT content::jsonb INTO ally_data FROM extension.net.http_collect_response(request_id, '10s');
            EXIT; 
        EXCEPTION
            WHEN OTHERS THEN
                retry_count := retry_count + 1;
                IF retry_count >= max_retries THEN
                    RAISE EXCEPTION 'Failed to fetch ally data after % attempts.', max_retries;
                END IF;
                PERFORM pg_sleep(3);
        END;
    END LOOP;

    is_in_war := (ally_data ->> 'InWar')::boolean;

    -- || --- 3. CORE LOGIC: ARE WE IN A WAR? --- ||
    IF is_in_war THEN
        -- ---- WAR IS ACTIVE ----
        opponent_name := ally_data ->> 'OpponentAllianceId';

        -- Fetch opponent data
        retry_count := 0;
        WHILE retry_count < max_retries LOOP
            BEGIN
                request_id := extension.net.http_get(
                    url := 'https://api.galaxylifegame.net/Alliances/get?name=' || url_encode(opponent_name),
                    headers := request_headers -- ADDING THE HEADER HERE
                );
                SELECT content::jsonb INTO opponent_data FROM extension.net.http_collect_response(request_id, '10s');
                EXIT;
            EXCEPTION
                WHEN OTHERS THEN
                    retry_count := retry_count + 1;
                    IF retry_count >= max_retries THEN
                        RAISE EXCEPTION 'Failed to fetch opponent data for % after % attempts.', opponent_name, max_retries;
                    END IF;
                    PERFORM pg_sleep(3);
            END;
        END LOOP;

        IF NOT current_state."isTrackPopulated" THEN
            -- --- 3A. INITIALIZATION PHASE ---
            RAISE LOG 'War is active and not initialized. Populating all data...';

            DELETE FROM public."wpLogGains";
            DELETE FROM public."wpTrackPlayers";
            DELETE FROM public."wpTrackAlliance";

            -- Combine members for initialization
            FOR member_data IN SELECT * FROM jsonb_array_elements(ally_data -> 'Members' || opponent_data -> 'Members')
            LOOP
                -- Fetch baseInfo for this member
                retry_count := 0;
                WHILE retry_count < max_retries LOOP
                    BEGIN
                        request_id := extension.net.http_get(
                            url := 'https://api.galaxylifegame.net/Users/get?id=' || (member_data ->> 'Id'),
                            headers := request_headers -- ADDING THE HEADER HERE
                        );
                        SELECT content::jsonb INTO player_base_info FROM extension.net.http_collect_response(request_id, '10s');
                        EXIT;
                    EXCEPTION
                        WHEN OTHERS THEN
                            retry_count := retry_count + 1;
                            IF retry_count >= max_retries THEN
                                RAISE EXCEPTION 'Failed to fetch baseInfo for player ID %.', (member_data ->> 'Id');
                            END IF;
                            PERFORM pg_sleep(3);
                    END;
                END LOOP;
                
                -- Insert player data
                INSERT INTO public."wpTrackPlayers" ("accountId", name, "isAlly", "baseInfo", "initPoints", "curPoints")
                VALUES (
                    (member_data ->> 'Id')::integer,
                    member_data ->> 'Name',
                    (SELECT EXISTS (SELECT 1 FROM jsonb_array_elements(ally_data -> 'Members') AS m WHERE m ->> 'Id' = member_data ->> 'Id')),
                    player_base_info,
                    (member_data ->> 'TotalWarPoints')::integer,
                    (member_data ->> 'TotalWarPoints')::integer
                );
            END LOOP;

            INSERT INTO public."wpTrackAlliance" (name, "isAlly", "initPoints", "curPoints") VALUES
            (ally_data ->> 'Id', true, (ally_data ->> 'WarPoints')::integer, (ally_data ->> 'WarPoints')::integer),
            (opponent_data ->> 'Id', false, (opponent_data ->> 'WarPoints')::integer, (opponent_data ->> 'WarPoints')::integer);

            UPDATE public."allyAllianceState" SET "isInWar" = true, "isTrackPopulated" = true WHERE id = 1;

        ELSE
            -- --- 3B. UPDATE & JOURNALING PHASE (EVERY MINUTE) ---
            RAISE LOG 'War is ongoing. Checking for point changes...';
            
            -- Combine members for the update loop
            FOR member_data IN SELECT * FROM jsonb_array_elements(ally_data -> 'Members' || opponent_data -> 'Members')
            LOOP
                new_points := (member_data ->> 'TotalWarPoints')::integer;
                
                SELECT "curPoints" INTO old_points 
                FROM public."wpTrackPlayers" 
                WHERE "accountId" = (member_data ->> 'Id')::integer;

                old_points := COALESCE(old_points, 0);
                points_gain := new_points - old_points;

                IF points_gain > 0 THEN
                    INSERT INTO public."wpLogGains" ("accountId", name, gain)
                    VALUES (
                        (member_data ->> 'Id')::integer,
                        (member_data ->> 'Name'),
                        points_gain
                    );

                    UPDATE public."wpTrackPlayers" 
                    SET "curPoints" = new_points 
                    WHERE "accountId" = (member_data ->> 'Id')::integer;
                END IF;
            END LOOP;

            -- Update overall alliance scores
            UPDATE public."wpTrackAlliance" SET "curPoints" = (ally_data ->> 'WarPoints')::integer WHERE name = (ally_data ->> 'Id');
            UPDATE public."wpTrackAlliance" SET "curPoints" = (opponent_data ->> 'WarPoints')::integer WHERE name = (opponent_data ->> 'Id');
        END IF;

    ELSE
        -- ---- WAR IS OVER OR WE ARE NOT IN ONE ----
        IF current_state."isInWar" THEN
            RAISE LOG 'War has ended. Clearing data.';
            DELETE FROM public."wpLogGains";
            DELETE FROM public."wpTrackPlayers";
            DELETE FROM public."wpTrackAlliance";
            UPDATE public."allyAllianceState" SET "isInWar" = false, "isTrackPopulated" = false WHERE id = 1;
        ELSE
            RAISE LOG 'Not in a war. Nothing to do.';
        END IF;
    END IF;
END;
