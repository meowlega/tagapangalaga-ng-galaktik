import json
import os
import glob

# --- CONFIGURATION ---
# Path to your logs folder
LOGS_DIR = r"C:\Users\Administrator\Desktop\logs2"
# The alliance to search for
TARGET_ALLIANCE = "serbia alliance"

def search_files():
    # Find all .json files in the directory
    files = glob.glob(os.path.join(LOGS_DIR, "*.json"))
    
    print(f"[*] Scanning {len(files)} files for Alliance: '{TARGET_ALLIANCE}'...")
    print("=" * 60)

    found_count = 0

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 1. Dig into the structure to find the Universe data
            command_list = data.get("list", [])
            for cmd in command_list:
                if cmd.get("cmdName") == "obtainUniverse":
                    # Get the Universe list (usually index 0 has the player data)
                    universe_arr = cmd.get("cmdData", {}).get("Universe", [])
                    
                    if not universe_arr:
                        continue

                    player_data = universe_arr[0]
                    
                    # 2. Check if Alliance Matches
                    if player_data.get("allianceId") == TARGET_ALLIANCE:
                        found_count += 1
                        print(f"\n[+] MATCH FOUND in file: {os.path.basename(filepath)}")
                        print(f"    Player Name: {player_data.get('playerName')}")
                        
                        # 3. Find and Print Planets
                        # Planets are nested inside one of the items in the 'Profile' list
                        profile_list = player_data.get("Profile", [])
                        planets_found = False

                        for profile_item in profile_list:
                            if "Planets" in profile_item:
                                planets = profile_item["Planets"]
                                
                                if planets:
                                    print("    Planets List:")
                                    for p in planets:
                                        # Extracting the specific fields you asked for
                                        p_sku = p.get("sku", "N/A")
                                        p_hq = p.get("HQLevel", "N/A")
                                        p_id = p.get("planetId", "N/A")

                                        print(f"      - Planet: []")
                                        print(f"        sku: \"{p_sku}\"")
                                        print(f"        HQLevel: {p_hq}")
                                        print(f"        planetId: {p_id}")
                                        print("") # Empty line for readability
                                    planets_found = True
                        
                        if not planets_found:
                            print("    (No Planets found in this profile)")
                        
                        print("-" * 60)

        except Exception as e:
            print(f"[!] Error reading {os.path.basename(filepath)}: {e}")

    print(f"\n[*] Scan Complete. Found {found_count} matching profiles.")

if __name__ == "__main__":
    search_files()
