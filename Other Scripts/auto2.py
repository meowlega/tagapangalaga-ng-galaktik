import pyautogui
import time
import threading
from pynput import mouse, keyboard

# --- Configuration ---
PIXEL_COORD = (782, 473)
PIXEL_COLOR = (255, 255, 255) # Pure white
CLICK_COORD = (1170, 430)
CHECK_DURATION_SECONDS = 15
COLOR_TOLERANCE = 10

# --- State Variables (Global) ---
# 'is_paused' controls whether clicks trigger the action
is_paused = False
# 'is_checking' prevents multiple checks from running at once
is_checking = False
# A lock for thread-safe modification of the state variables
lock = threading.Lock()

def perform_check_and_click():
    """
    Checks for a pixel for a set duration. Clicks a target coordinate
    if the pixel is found or if the time runs out. This function is
    designed to run in its own thread to not block the listeners.
    """
    global is_checking
    
    # Safely check and set the 'is_checking' flag
    with lock:
        if is_checking:
            print("(Action already in progress, ignoring this click.)")
            return
        is_checking = True

    print("\nLeft-click detected. Starting 15-second check...")
    
    start_time = time.time()
    pixel_found = False

    try:
        # Loop for the specified duration
        while time.time() - start_time < CHECK_DURATION_SECONDS:
            if pyautogui.pixelMatchesColor(PIXEL_COORD[0], PIXEL_COORD[1], PIXEL_COLOR, tolerance=COLOR_TOLERANCE):
                print(f"Success! White pixel found at {PIXEL_COORD}.")
                pixel_found = True
                break # Exit the checking loop immediately
            time.sleep(0.1)

        if not pixel_found:
            print(f"Timeout. {CHECK_DURATION_SECONDS} seconds passed and pixel was not found.")

        print(f"Clicking at {CLICK_COORD} as per instructions.")
        pyautogui.click(CLICK_COORD[0], CLICK_COORD[1])

    finally:
        # IMPORTANT: Reset the flag in a 'finally' block to ensure it's always reset
        with lock:
            is_checking = False
        print("-" * 30)
        print(f"Ready for next click. Automation is {'PAUSED' if is_paused else 'ACTIVE'}.")

# --- Event Handlers for Listeners ---

def on_click(x, y, button, pressed):
    """
    This function is called whenever a mouse click occurs.
    """
    # We only care about the left-button press, not its release
    if button == mouse.Button.left and pressed:
        with lock: # Safely read the 'is_paused' state
            if not is_paused:
                # Run the main logic in a new thread to avoid blocking the listener
                action_thread = threading.Thread(target=perform_check_and_click)
                action_thread.start()

def on_press(key):
    """
    This function is called whenever a keyboard key is pressed.
    """
    global is_paused
    try:
        if key.char == 'e':
            with lock: # Safely toggle the 'is_paused' state
                is_paused = not is_paused
            
            status = "PAUSED" if is_paused else "ACTIVE"
            print(f"\n--- SCRIPT {status} ---")
    except AttributeError:
        # This handles special keys (like Shift, Ctrl) that don't have a 'char' attribute
        pass

# --- Main Program Execution ---

if __name__ == "__main__":
    print("--- Advanced Automated Clicker ---")
    print("CONTROLS:")
    print(" - Press 'e' to PAUSE or RESUME the script.")
    print(" - Left-click to start the 15-second pixel check.")
    print("\nScript is now ACTIVE and listening for clicks...")
    print("Press Ctrl+C in this terminal to stop the script.")

    # Create and start the listener threads
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    
    keyboard_listener.start()
    mouse_listener.start()

    # Keep the main script alive while the listeners run in the background
    keyboard_listener.join()
    mouse_listener.join()
