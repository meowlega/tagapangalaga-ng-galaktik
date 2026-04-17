import os
import json
import sqlite3
import time
import re # For regular expressions to parse SKU
from typing import Optional, Tuple

# --- Configuration ---
LOGS_DIR = r"C:/Users/Administrator/Desktop/bot/block_1to96"
DATABASE_FILE = "eguls.db" # Renamed to avoid conflicts with original dbtest.py

# --- Pre-check the logs directory ---
if not os.path.exists(LOGS_DIR):
    print(f"Error: The configured logs directory '{LOGS_DIR}' does not exist.")
    print("Please create this directory or update LOGS_DIR to the correct path.")
    exit()

# --- Data Extraction Function (focused on queryStarInfo) ---
def extract_planet_info(json_string: str) -> list:
    """
    Parses a game packet JSON string, specifically looking for the 'queryStarInfo' command
    and extracts relevant planet data.
    It extracts 'sku', 'HQLevel', 'accountId', 'name', and 'planetId' because these
    are needed for filtering or coordinate parsing, even if not all are stored.

    Args:
        json_string (str): The JSON string content read directly from a log file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a planet
              and contains its 'sku', 'HQLevel', 'accountId', 'name', and 'planetId'.
              Returns an empty list if no relevant data is found or if parsing fails.
    """
    extracted_planets = []
    try:
        parsed_data = json.loads(json_string)
        command_list = parsed_data.get("list")

        if not isinstance(command_list, list):
            return extracted_planets

        for command in command_list:
            if not isinstance(command, dict):
                continue

            if command.get("cmdName") == "queryStarInfo":
                cmd_data = command.get("cmdData")

                if not isinstance(cmd_data, dict):
                    continue

                space_star_info_list = cmd_data.get("spaceStarInfo")

                if not isinstance(space_star_info_list, list):
                    continue

                for entity_info in space_star_info_list:
                    if not isinstance(entity_info, dict):
                        continue

                    # Extract all fields needed for filtering and coordinate parsing
                    extracted_planets.append({
                        "sku": entity_info.get("sku"),
                        "HQLevel": entity_info.get("HQLevel"),
                        "accountId": entity_info.get("accountId"),
                        "name": entity_info.get("name"),
                        "planetId": entity_info.get("planetId")
                    })
                break # Stop after finding and processing the first 'queryStarInfo'

    except json.JSONDecodeError:
        pass # Silently skip malformed JSON files
    except Exception:
        pass # Silently skip other unexpected errors during extraction

    return extracted_planets

# --- Coordinate Parsing Function ---
def parse_coords_from_full_sku(full_sku: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extracts coordX and coordY from a full SKU string like "100:10:20".
    Returns (coordX, coordY) as integers, or (None, None) if parsing fails.
    """
    if full_sku is None:
        return None, None
    
    sku_str = str(full_sku) # Ensure full_sku is a string before regex
    
    # Regex to capture the first two numbers separated by a colon.
    # The (?:...) means a non-capturing group, and ? makes it optional,
    # so it correctly handles "X:Y" or "X:Y:Z" formats.
    match = re.match(r"(\d+):(\d+)(?::\d+)?", sku_str)
    if match:
        try:
            coordX = int(match.group(1))
            coordY = int(match.group(2))
            return coordX, coordY
        except ValueError:
            return None, None
    return None, None

# --- SQLite Database Functions ---
def create_planets_table(conn: sqlite3.Connection):
    """
    Creates the 'planets' table if it doesn't exist, with the specified schema:
    accountId, name, planetId, coordX, coordY, timeTaken.
    Uses (accountId, planetId) as the PRIMARY KEY.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planets (
            accountId TEXT NOT NULL,
            name TEXT,
            planetId INTEGER NOT NULL,
            coordX INTEGER NOT NULL,
            coordY INTEGER NOT NULL,
            HQLevel INTEGER NOT NULL,
            timeTaken INTEGER NOT NULL, -- Unix epoch timestamp
            PRIMARY KEY (accountId, planetId)
        )
    """)
    conn.commit()

def insert_or_update_planet_data(conn: sqlite3.Connection, data: dict, file_timestamp: int) -> str:
    """
    Attempts to insert or update extracted planet data into the 'planets' table.
    It checks for existing records by (accountId, planetId) and updates if the
    new file_timestamp is newer, otherwise ignores.

    Args:
        conn (sqlite3.Connection): The database connection.
        data (dict): Dictionary containing 'accountId', 'name', 'planetId', 'coordX', 'coordY', 'HQLevel'.
        file_timestamp (int): Unix epoch timestamp from the log file.

    Returns:
        str: "inserted", "updated", "ignored_older", or "error".
    """
    cursor = conn.cursor()
    
    account_id = data.get("accountId")
    planet_name = data.get("name")
    planet_id = data.get("planetId")
    coordX = data.get("coordX")
    coordY = data.get("coordY")
    HQLevel = data.get("HQLevel")

    # Critical check: Ensure all NOT NULL fields for the PRIMARY KEY are present
    if account_id is None or planet_id is None or coordX is None or coordY is None or HQLevel is None or file_timestamp is None:
        return "error"

    try:
        # Step 1: Check if a record with this (accountId, planetId) already exists
        cursor.execute("""
            SELECT timeTaken FROM planets WHERE accountId = ? AND planetId = ?
        """, (account_id, planet_id))
        existing_record = cursor.fetchone()

        if existing_record:
            existing_timeTaken = existing_record[0]
            if file_timestamp > existing_timeTaken:
                # Step 2a: Record exists and new data is newer, so UPDATE
                cursor.execute("""
                    UPDATE planets
                    SET name = ?, coordX = ?, coordY = ?, HQLevel = ?, timeTaken = ?
                    WHERE accountId = ? AND planetId = ?
                """, (planet_name, coordX, coordY, HQLevel, file_timestamp, account_id, planet_id))
                conn.commit()
                return "updated"
            else:
                # Step 2b: Record exists but new data is older or same, so IGNORE
                return "ignored_older"
        else:
            # Step 3: No existing record, so INSERT
            cursor.execute("""
                INSERT INTO planets (accountId, name, planetId, coordX, coordY, HQLevel, timeTaken)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (account_id, planet_name, planet_id, coordX, coordY, HQLevel, file_timestamp))
            conn.commit()
            return "inserted"
        
    except sqlite3.Error as e:
        # Catch any specific SQLite errors
        print(f"\n[!] Database error during insert/update for (accountId={account_id}, planetId={planet_id}): {e}")
        return "error"
    except Exception as e:
        # Catch any other unexpected errors
        print(f"\n[!] An unexpected error occurred in insert_or_update_planet_data for (accountId={account_id}, planetId={planet_id}): {e}")
        return "error"

# --- Main Script Logic ---
def main():
    conn = None
    start_time = time.time()
    print("--- Starting data extraction and database population ---")

    try:
        # Establish connection to the SQLite database
        conn = sqlite3.connect(DATABASE_FILE)
        
        # Create the necessary table with the new schema and primary key
        create_planets_table(conn)

        processed_files_count = 0
        inserted_planet_records = 0
        updated_planet_records = 0
        skipped_filtered_records = 0
        ignored_older_duplicates = 0
        errored_records = 0
        
        # Get a list of files to process and count them
        all_log_files = [f for f in os.listdir(LOGS_DIR) if f.startswith("packet_") and f.endswith(".txt")]
        total_files_to_process = len(all_log_files)

        # Initialize progress tracking
        last_printed_percentage = -1
        
        for filename in all_log_files:
            filepath = os.path.join(LOGS_DIR, filename)
            processed_files_count += 1
            
            # --- Progress Indicator ---
            if total_files_to_process > 0:
                current_percentage = int((processed_files_count / total_files_to_process) * 100)
                if current_percentage > last_printed_percentage:
                    # Clear line and print new progress. Ensure it's responsive.
                    print(f"Progress: {current_percentage}% ({processed_files_count}/{total_files_to_process} files)", end='\r')
                    last_printed_percentage = current_percentage
            # --- End Progress Indicator ---

            # Get the modification time of the log file as Unix epoch
            # This serves as the 'timeTaken' for the extracted data
            try:
                file_timestamp = int(os.path.getmtime(filepath))
            except OSError as e:
                print(f"\n[!] Could not get timestamp for file '{filename}': {e}. Skipping file.")
                errored_records += 1
                continue # Skip to the next file if timestamp can't be obtained

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    json_content = f.read()

                # Extract all raw planet info (includes HQLevel and sku for filtering/parsing)
                extracted_planets = extract_planet_info(json_content)

                # Process planet data
                if extracted_planets:
                    for entity_data in extracted_planets:
                        # NEW: 1. Skip condition: if planetId = 1, and HQLevel <=3, then skip
                        planet_id = entity_data.get("planetId")
                        hq_level = entity_data.get("HQLevel")

                        if planet_id == 1 and (hq_level is not None and hq_level <= 3):
                            skipped_filtered_records += 1
                            continue # Skip this record

                        # 2. Parse coord_sku (full sku) to coordX, coordY
                        full_sku = entity_data.get("sku")
                        coordX, coordY = parse_coords_from_full_sku(full_sku)

                        # Check for critical missing data (coordX, coordY, accountId, planetId)
                        # We also check for 'accountId' and 'planetId' being None, as they are part of the PK.
                        if (coordX is None or coordY is None or 
                            entity_data.get("accountId") is None or entity_data.get("planetId") is None):
                            skipped_filtered_records += 1
                            continue # Skip if essential coordinates or PK components are missing

                        # Add parsed coordinates to the entity_data dictionary for insertion
                        entity_data["coordX"] = coordX
                        entity_data["coordY"] = coordY

                        # Attempt to insert/update the filtered and processed data
                        status = insert_or_update_planet_data(conn, entity_data, file_timestamp)

                        if status == "inserted":
                            inserted_planet_records += 1
                        elif status == "updated":
                            updated_planet_records += 1
                        elif status == "ignored_older":
                            ignored_older_duplicates += 1
                        elif status == "error":
                            errored_records += 1

            except IOError as e:
                # Print error messages on a new line to not interfere with progress bar
                print(f"\n[!] Error reading file '{filename}': {e}")
                errored_records += 1
            except Exception as e:
                print(f"\n[!] An unexpected error occurred while processing '{filename}': {e}")
                errored_records += 1

    except sqlite3.Error as e:
        print(f"\nDatabase error encountered: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during script execution: {e}")
    finally:
        if conn:
            conn.close()
            # Ensure the last progress line is cleared or completed before final summary
            if total_files_to_process > 0:
                print(f"Progress: 100% ({total_files_to_process}/{total_files_to_process} files)", end='\n')
            print("Database connection closed.")
        
        end_time = time.time()
        duration = end_time - start_time

        print("\n--- Data Extraction and Database Population Complete ---")
        print(f"Total files scanned and processed: {processed_files_count}")
        print(f"Total planet records NEWLY INSERTED: {inserted_planet_records}")
        print(f"Total planet records UPDATED (with newer timestamp): {updated_planet_records}")
        print(f"Total planet records SKIPPED (filtered by HQLevel/planetId, invalid SKU, or missing data): {skipped_filtered_records}")
        print(f"Total planet records IGNORED (older duplicates): {ignored_older_duplicates}")
        print(f"Total records that caused an ERROR: {errored_records}")
        print(f"Execution finished in {duration:.2f} seconds.")

# This ensures that main() is called only when the script is executed directly
if __name__ == "__main__":
    main()
