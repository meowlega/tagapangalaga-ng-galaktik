# tagapangalaga-ng-galaktik

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

<img width="1235" height="2681" alt="schema" src="https://github.com/user-attachments/assets/6fb353f4-2097-47db-a6f5-26ab00dd2b40" />

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
    subgraph Automation_Bot ["1. Automation Loop (auto.py)"]
        A[mss screenshot] --> B[yolo ai predict]
        B --> C[pyautogui click predicted galaxies]
        C --> D{if UI shows, click 'exit'}
        D -- Loop --> C
        D --> E[save raw packets]
        E --> F[if all clicked: hover next]
        F --> G[if no galaxies in 8 hovers: increment y]
        G -- Loop back to start --> A
    end

    subgraph Data_Processing ["2. Data Pipeline"]
        H[decrypt all packets] --> I[save to db]
        I --> J[convert db to csv]
        J --> K[upload csv to Supabase]
        K --> L[setup supabase edge function]
    end

    subgraph Messenger_Integration ["3. Facebook Bot"]
        M[Chat to facebook business bot] --> N[webhook called]
        N --> O[supabase edge function run]
        O --> P[fetch and output results]
    end

    subgraph UI_Access ["4. Flashbrowser UI"]
        Q[open Flashbrowser] --> R[api key check]
        R --> S[access data from supabase in real time]
    end

    %% Connections between groups
    E -.-> H
    L --> O
    L --> S
```
