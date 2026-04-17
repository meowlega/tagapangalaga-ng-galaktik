import os
import time
import json
import glob

# --- CONFIGURATION ---
WATCH_DIR = r"C:\Users\Administrator\Desktop\Desktop2\logs2"

def clear_screen():
    # Execute 'cls' command for Windows
    os.system('cls')

def print_separator(char="=", length=50):
    print(char * length)

def parse_and_display(filepath):
    try:
        # 1. Read the decrypted JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Locate the obtainUniverse command
        command_list = data.get("list", [])
        uni_data = None
        
        for cmd in command_list:
            if cmd.get("cmdName") == "obtainUniverse":
                # Universe data is a list, take the first item
                uni_data = cmd.get("cmdData", {}).get("Universe", [])[0]
                break
        
        if not uni_data:
            return # Skip if not a valid universe packet

        # 3. Extract Player Data
        player_name = uni_data.get("playerName", "Unknown")
        alliance = uni_data.get("allianceId", "None")
        shield_time = uni_data.get("damageProtectionTimeLeft", "N/A")

        # 4. Extract Planets 
        # (Planets are inside one of the objects in the 'Profile' list)
        planets_found = []
        profile_list = uni_data.get("Profile", [])
        for item in profile_list:
            if "Planets" in item:
                raw_planets = item["Planets"]
                for p in raw_planets:
                    planets_found.append({
                        "sku": p.get("sku"),
                        "hq": p.get("HQLevel"),
                        "id": p.get("planetId")
                    })
                break 

        # 5. Extract Bunkers
        # (Bunkers are inside one of the objects in the 'World' list)
        bunkers_found = []
        world_list = uni_data.get("World", [])
        for item in world_list:
            if "Bunkers" in item:
                raw_bunkers = item["Bunkers"]
                for b in raw_bunkers:
                    # Count units inside the 'Bunker' list of this object
                    unit_list = b.get("Bunker", [])
                    count = len(unit_list)
                    
                    # Try to get the name of the first unit if it exists
                    u_type = "Empty"
                    if count > 0:
                        u_type = unit_list[0].get("sku", "Unknown")
                    
                    bunkers_found.append({
                        "sid": b.get("sid"),
                        "count": count,
                        "type": u_type
                    })
                break

        # --- OUTPUT TO SCREEN ---
        
        clear_screen() # <--- CLEARS SCREEN HERE
        
        print_separator("=")
        print(f" LIVE PACKET VIEW")
        print(f" File: {os.path.basename(filepath)}")
        print_separator("=")
        
        print(f" PLAYER   : {player_name}")
        print(f" ALLIANCE : {alliance}")
        print(f" SHIELD   : {shield_time}")
        
        print("\n [PLANETS]")
        if planets_found:
            for p in planets_found:
                print(f"   > ID: {p['id']:<3} | HQ: {p['hq']:<2} | SKU: {p['sku']}")
        else:
            print("   > No planets found.")

        print("\n [BUNKERS]")
        if bunkers_found:
            for b in bunkers_found:
                print(f"   > SID: {b['sid']:<4} | Units: {b['count']:<2} | Type: {b['type']}")
        else:
            print("   > No bunkers found.")
            
        print("\n")
        print_separator("=")
        print(" Waiting for next packet...")

    except Exception as e:
        print(f"[!] Error reading file: {e}")

def main():
    clear_screen()
    print(f"[*] Watching folder: {WATCH_DIR}")
    print("[*] Waiting for new 'obtainUniverse' files...")
    
    # Ignore existing files so we only see NEW ones
    seen_files = set(glob.glob(os.path.join(WATCH_DIR, "universe_*.json")))
    
    try:
        while True:
            # Get current list of json files
            current_files = glob.glob(os.path.join(WATCH_DIR, "universe_*.json"))
            
            # Sort by modification time to ensure we process in order
            current_files.sort(key=os.path.getmtime)

            for file in current_files:
                if file not in seen_files:
                    # Brief pause to ensure file write is finished by the other script
                    time.sleep(0.1) 
                    parse_and_display(file)
                    seen_files.add(file)
            
            time.sleep(1) # Refresh rate
    except KeyboardInterrupt:
        print("\n[!] Viewer stopped.")

if __name__ == "__main__":
    main()
