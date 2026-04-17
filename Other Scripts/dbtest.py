import os
import json
import sqlite3
import time
import re # For regular expressions to parse SKU

# --- Configuration ---
LOGS_DIR = r"C:/Users/Administrator/Desktop/bot/block"
DATABASE_FILE = "game_data.db"

# --- Pre-check the logs directory ---
if not os.path.exists(LOGS_DIR):
    print(f"Error: The configured logs directory '{LOGS_DIR}' does not exist.")
    print("Please create this directory or update LOGS_DIR to the correct path.")
    exit()

# --- Data Extraction Function (now only focused on queryStarInfo) ---
def extract_planet_info(json_string: str) -> list:
    """
    Parses a game packet JSON string, specifically looking for the 'queryStarInfo' command
    and extracts relevant planet data.

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

                    # Extracting only "sku", "HQLevel", "accountId", "name", "planetId"
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

# --- SQLite Database Functions ---
def create_planets_table(conn: sqlite3.Connection):
    """
    Creates the 'planets' table if it doesn't exist.
    'sku' is TEXT UNIQUE for duplicate checking.
    'coord_sku' stores the transformed SKU (e.g., "100:10").
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,      -- Original SKU for unique identification (e.g., 100:10:20)
            coord_sku TEXT,       -- Transformed SKU (e.g., 100:10)
            HQLevel INTEGER,
            accountId TEXT,
            name TEXT,
            planetId INTEGER
        )
    """)
    conn.commit()

def extract_coord_sku(full_sku: str) -> str:
    """
    Extracts the coordinate part (e.g., "100:10") from a full SKU (e.g., "100:10:20").
    Returns None if the format doesn't match.
    """
    if full_sku is None:
        return None
    
    match = re.match(r"(\d+:\d+):\d+", str(full_sku)) # Ensure full_sku is string
    if match:
        return match.group(1) # Return "100:10"
    return full_sku # Return original if regex fails, or None if original was None

def insert_planet_data(conn: sqlite3.Connection, data: dict) -> bool:
    """
    Attempts to insert extracted planet data into the 'planets' table.
    Uses INSERT OR IGNORE to skip if a record with the same UNIQUE 'sku' already exists.
    Populates 'coord_sku' by transforming the 'sku'.

    Returns:
        bool: True if a new record was inserted, False if it was ignored (duplicate).
    """
    cursor = conn.cursor()
    
    original_sku = data.get("sku")
    transformed_coord_sku = extract_coord_sku(original_sku)

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO planets (sku, coord_sku, HQLevel, accountId, name, planetId)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            original_sku,
            transformed_coord_sku,
            data.get("HQLevel"),
            data.get("accountId"),
            data.get("name"),
            data.get("planetId")
        ))
        conn.commit()
        return cursor.rowcount > 0 # rowcount will be 1 if inserted, 0 if ignored
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False

# --- Main Script Logic ---
def main():
    conn = None
    start_time = time.time()
    print("--- Starting data extraction and database population ---")

    try:
        # Establish connection to the SQLite database
        conn = sqlite3.connect(DATABASE_FILE)
        
        # Create the necessary table
        create_planets_table(conn)

        processed_files_count = 0
        inserted_planet_records = 0
        ignored_planet_records = 0
        
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

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    json_content = f.read()

                # Extract only planet info
                extracted_planets = extract_planet_info(json_content)

                # Process planet data
                if extracted_planets:
                    for entity_data in extracted_planets:
                        if insert_planet_data(conn, entity_data):
                            inserted_planet_records += 1
                        else:
                            ignored_planet_records += 1

            except IOError as e:
                # Print error messages on a new line to not interfere with progress bar
                print(f"\n[!] Error reading file '{filename}': {e}")
            except Exception as e:
                print(f"\n[!] An unexpected error occurred while processing '{filename}': {e}")

    except sqlite3.Error as e:
        print(f"\nDatabase error encountered: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during script execution: {e}")
    finally:
        if conn:
            conn.close()
            # Ensure the last progress line is cleared or completed before final summary
            if total_files_to_process > 0:
                # Print a final 100% and then move to a new line for summary
                print(f"Progress: 100% ({total_files_to_process}/{total_files_to_process} files)", end='\n')
            print("Database connection closed.")
        
        end_time = time.time()
        duration = end_time - start_time

        print("\n--- Data Extraction and Database Population Complete ---")
        print(f"Total files scanned and processed: {processed_files_count}")
        print(f"Total planet records NEWLY INSERTED: {inserted_planet_records}")
        print(f"Total planet records IGNORED (duplicates): {ignored_planet_records}")
        print(f"Execution finished in {duration:.2f} seconds.")

# This ensures that main() is called only when the script is executed directly
if __name__ == "__main__":
    main()
