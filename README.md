# tagapangalaga-ng-galaktik

## Packet Collections Demo
Youtube: https://youtu.be/7cqsey8IzDU

## Technology Stack

### Programming Language
- **Python v3.13** for overall portability, and AI stuff
- **Typescript** for Supabase functions and Webhook from Facebook
- **HTML / CSS / JS** for the User Interface

### Libraries (Python)
- **Pillow** for image manipulation, mostly for debugging / testing
- **mss** for quick, silent screenshots. It is the *eye* of this script
- **PyAutoGUI** for automatic Inputs. It is the *hands* of this script
- **Keyboard** for listening hotkey inputs, lets say I wanna pause, or resume running script
- **Ultralytics** (YOLO AI) for running AI shenanigans
- **torch** (PyTorch) doing the heavy lifting on training the AI
- **mitmproxy** for packet sniffing

### Database
- **SQLITE** for initial testing and validation of my schema
- **PostgreSQL**, used by *Supabase*, which is my free backend. Also has *cron-jobs*

<img width="741" height="1609" alt="schema" src="https://github.com/user-attachments/assets/6fb353f4-2097-47db-a6f5-26ab00dd2b40" />

### Frontend
- **Flashbrowser** (https://github.com/radubirsan/FlashBrowser) free open source Flashbrowser that i forked, so that I can integrate my bot
- **Facebook Business Page** via webhook, for automatic messenger bot directly on *messenger*
- **bot.html** standalone UI file to check details even without Flashbrowser (since this file is just integrated on Flashbrowser anyways)

### Backend
- **Supabase**, a very generous free SQL backend with free Disk and CPU compute

## YOLO AI Files here:
GDRIVE Link: https://drive.google.com/drive/folders/1akZ7zv4Uz__sUlJ_11Prw9YaaMR09WU7?usp=sharing

Path for **best.pt** (AI predicting model):
- \YOLO AI\runs\detect\train\weights\best.pt

Path for training images:
- \YOLO AI\Label Studio\images\train

## Kind of core logic?

```mermaid
graph TD
    %% EXTERNAL APIS
    GL_API((Galaxy Life API))

    %% ================= LOCAL SYSTEM =================
    subgraph Local_System ["Local Desktop Environment"]
        
        subgraph Automation ["Game Automation (auto.py)"]
            A[Screenshot MSS] --> B[YOLO Predict]
            B -->|Found| C[PyAutoGUI Clicks]
            B -->|Empty x8| AdjustMap[Auto-adjust Map Y]
            C --> WaitPixel[Wait UI Pixel & Close]
            WaitPixel --> A
        end

        subgraph ETL_Pipeline ["Data Interception & Pipeline"]
            F[mitmproxy] 
            C -.->|Triggers API| F
            F --> G{Path /star/game?}
            G -- Yes --> H[Decrypt XOR & Save .txt]
            H --> K[eguls.py: Parse JSON & Filter HQ]
            K --> P[(SQLite: eguls.db)]
            P --> Q[csv & csvtime: Export & Format Dates]
        end
    end

    %% ================= CLOUD BACKEND =================
    subgraph Cloud_Backend ["Supabase Cloud Architecture"]
        DB_Planets[(DB: planetsv2)]
        DB_War[(DB: allianceState & Logs)]
        
        Q == "Uploads Formatted CSV" ===> DB_Planets
        
        Cron[[pg_cron: cron.sql]]
        Cron <-->|Polls for Points| GL_API
        Cron -.->|Updates War State & Logs| DB_War
        
        %% EXPLODED EDGE FUNCTION LOGIC
        subgraph Supabase_Edge_Function ["Deno Edge Function (index.ts)"]
            Parse[Parse Webhook Payload] --> SendWait[Send 'Searching...' Reply]
            SendWait --> FetchAlly[Fetch Primary Alliance]
            FetchAlly --> WarCheck{Is Alliance in War?}
            
            %% Not in War Path
            WarCheck -- No --> SimpleStatus[Format Simple Status]
            SimpleStatus --> SendChunks
            
            %% In War Path
            WarCheck -- Yes --> FetchEnemy[Fetch Opponent Alliance]
            FetchEnemy --> FetchUsers[Fetch Base Info for ALL Members]
            FetchUsers --> MapPlanets[Map Enemy Planets]
            
            MapPlanets --> QueryDB[Query DB for Coordinates]
            QueryDB --> CalcStats[Calculate WP & Regen Hours]
            CalcStats --> SortMembers[Sort Members by Role & WP]
            SortMembers --> FormatReport[Format War Report]
            
            FormatReport --> ChunkCheck{Message > 2000 chars?}
            ChunkCheck -- Yes --> SplitChunks[Split into Chunks]
            ChunkCheck -- No --> SendChunks[Send to FB Graph API]
            SplitChunks --> SendChunks
        end

        %% Internal Edge Connections
        QueryDB -.->|Reads X/Y Coords| DB_Planets
        FetchAlly -.->|API Call| GL_API
        FetchEnemy -.->|API Call| GL_API
        FetchUsers -.->|Concurrent API Calls| GL_API
    end

    %% ================= FRONTENDS =================
    subgraph Frontends ["User Interfaces"]
        
        subgraph Messenger_App ["Facebook Messenger"]
            User([User]) <-->|Types Alliance Name & Reads Reports| FB[Messenger Chat]
        end
        
        subgraph Web_UI ["Flashbrowser Web App"]
            Browser[Flashbrowser] --> API_Check[Validate API Key]
            API_Check --> Realtime[Access Live Supabase Data]
        end
    end

    %% ================= CONNECTIONS =================
    FB -->|POST Webhook| Parse
    SendChunks -->|Deliver Message| FB
    Realtime -.-> DB_Planets
    Realtime -.-> DB_War

    %% ================= STYLING =================
    classDef database fill:#22543d,stroke:#48bb78,stroke-width:2px,color:#fff;
    classDef cron fill:#742a2a,stroke:#fc8181,stroke-width:2px,color:#fff;
    classDef local fill:#4a5568,stroke:#a0aec0,stroke-width:2px,color:#fff;
    classDef edge fill:#2b6cb0,stroke:#90cdf4,stroke-width:1px,color:#fff;
    
    class DB_Planets,DB_War,P database;
    class Cron cron;
    class A,B,C,AdjustMap,WaitPixel,F,G,H,K,Q local;
    class Parse,SendWait,FetchAlly,WarCheck,SimpleStatus,FetchEnemy,FetchUsers,MapPlanets,QueryDB,CalcStats,SortMembers,FormatReport,ChunkCheck,SplitChunks,SendChunks edge;
```
