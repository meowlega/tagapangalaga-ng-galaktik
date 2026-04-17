import pyautogui
import keyboard
import time
import datetime

# --- Configuration ---
# Set the coordinates (pixels) where the script should click.
# You can use a tool or another script to find these.
X_COORDINATE = 730  # <--- Change this to your desired X pixel coordinate
Y_COORDINATE = 900  # <--- Change this to your desired Y pixel coordinate

# The delay (in seconds) between the two clicks/actions.
CLICK_DELAY_SECONDS = 6 

# --- State Variables ---
# The main switch to start or stop the entire process (F8)
is_running = False 
# The switch to temporarily suspend the clicks while running (F6)
is_paused = False  

print("--- Mouse Automation Script Initialized ---")
print(f"Target Coordinates: ({X_COORDINATE}, {Y_COORDINATE})")
print(f"Delay between clicks: {CLICK_DELAY_SECONDS} seconds")
print("\nPress **F8** to **START/STOP** the automation.")
print("Press **F6** to **PAUSE/RESUME** the automation.")
print("Press **ESC** to **EXIT** the script.")
print("------------------------------------------")


def toggle_running():
    """Toggles the main ON/OFF state of the script (F8)."""
    global is_running, is_paused
    is_running = not is_running
    
    if is_running:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] **STARTING** Automation.")
        # When starting, ensure it is not paused
        is_paused = False
    else:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] **STOPPING** Automation.")

def toggle_paused():
    """Toggles the PAUSED/RESUMED state of the script (F6)."""
    global is_paused
    
    # Only allow pausing/resuming if the script is currently running
    if is_running:
        is_paused = not is_paused
        if is_paused:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] **PAUSED**.")
        else:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] **RESUMED**.")
    else:
        print("Automation is not running. Press F8 to start first.")


# --- Hotkey Setup ---
# Register the hotkeys to the functions
keyboard.add_hotkey('f8', toggle_running)
keyboard.add_hotkey('f6', toggle_paused)
keyboard.add_hotkey('esc', lambda: keyboard.unhook_all() and exit()) # ESC to exit cleanly

# --- Main Loop ---
try:
    while True:
        if is_running and not is_paused:
            
            # --- ACTION 1 ---
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Moving to ({X_COORDINATE}, {Y_COORDINATE}) and clicking (Action 1)...")
            pyautogui.moveTo(X_COORDINATE, Y_COORDINATE)
            time.sleep(1)
            pyautogui.click()
            
            # Wait for the configured delay
            time.sleep(CLICK_DELAY_SECONDS)
            
            # Re-check flags in case F6 or F8 was pressed during the sleep
            if not is_running or is_paused:
                continue # Skip the second click if state changed
            
            # --- ACTION 2 ---
            # Action 2 is the same as Action 1, as requested in the logic
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Moving to ({X_COORDINATE}, {Y_COORDINATE}) and clicking (Action 2)...")
            pyautogui.moveTo(X_COORDINATE, Y_COORDINATE)
            time.sleep(1)
            pyautogui.click()
            
            # Wait for the configured delay before the loop repeats
            time.sleep(CLICK_DELAY_SECONDS)
            
        else:
            # Short sleep when not running to prevent 100% CPU usage
            time.sleep(0.1)

except KeyboardInterrupt:
    print("\nScript exited by user (Ctrl+C).")
except Exception as e:
    print(f"\nAn error occurred: {e}")
finally:
    # Always unhook hotkeys on exit
    keyboard.unhook_all()
    print("Hotkeys unhooked. Goodbye!")
