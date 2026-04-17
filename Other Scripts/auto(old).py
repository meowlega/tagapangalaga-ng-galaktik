import os
import time
import pyautogui
import mss
from PIL import Image
from ultralytics import YOLO
import keyboard # Already installed, good!

# --- Configuration ---
YOLO_MODEL_PATH = "C:/Users/Administrator/Desktop/bot/best.pt"
PACKETS_DIR = "C:/Users/Administrator/Desktop/bot/packets"

# Adjust these values based on your game's UI and screen resolution
CLOSE_BUTTON_X = 1220
CLOSE_BUTTON_Y = 400

# Drag coordinates for map panning
# This will drag the map to the left, revealing new areas on the right.
DRAG_START_X = 1600
DRAG_START_Y = 670
DRAG_END_X = 550
DRAG_END_Y = 670
DRAG_DURATION_SECONDS = 1.5 # How long the drag action takes (for smoothness)

# Time to wait after clicking a galaxy before checking for packets
POST_CLICK_WAIT_TIME_SECONDS = 1

# YOLO Confidence Threshold (objects with lower confidence will be ignored)
YOLO_CONFIDENCE_THRESHOLD = 0.75 # Now set to 75%

# PyAutoGUI safety features (highly recommended)
pyautogui.FAILSAFE = True  # Moves mouse to (0,0) corner to abort script
pyautogui.PAUSE = 0.05     # Short pause after each pyautogui call for stability

# --- Global State for Pause ---
is_paused = False

# --- Helper Functions ---

def toggle_pause():
    """Toggles the global pause state of the bot."""
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print("\n--- Bot PAUSED. Press F6 to RESUME. ---")
    else:
        print("\n--- Bot RESUMED. ---")

def check_for_pause():
    """Checks the pause state and waits if the bot is paused."""
    while is_paused:
        print("Bot is paused. Waiting for F6 to resume...")
        time.sleep(0.5) # Wait briefly while paused to avoid busy-waiting

def load_yolo_model(path):
    """Loads the YOLOv8 model."""
    try:
        model = YOLO(path)
        print(f"YOLO model loaded from: {path}")
        return model
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        print("Please ensure the path is correct and ultralytics is installed.")
        exit()

def get_screenshot_as_pil_image():
    """Captures the entire screen and returns it as a Pillow Image object."""
    with mss.mss() as sct:
        # Get information of monitor 1 (usually your primary monitor)
        monitor = sct.monitors[1] 
        
        # Capture the screen
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image: mss.grab returns a dict with 'rgb' bytes
        # Pillow needs (width, height) and the pixel data.
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        return img

def predict_galaxies(model, screenshot_img):
    """Runs YOLO prediction on the screenshot and returns detected box midpoints."""
    print("Running YOLO prediction...")
    # Predict with verbose=False to keep console clean
    results = model.predict(source=screenshot_img, conf=YOLO_CONFIDENCE_THRESHOLD, iou=0.7, verbose=False) 
    
    galaxy_midpoints = []
    # results[0] contains the detections for the first (and only) image in our batch
    for r in results[0].boxes:
        # xywh returns [x_center, y_center, width, height]
        x_center, y_center, width, height = r.xywh[0].cpu().numpy()
        
        # Convert to integers for pyautogui, which expects pixel coordinates
        mid_x = int(x_center)
        mid_y = int(y_center)
        
        galaxy_midpoints.append((mid_x, mid_y))
        
    print(f"YOLO detected {len(galaxy_midpoints)} potential galaxies on the current screen (conf > {YOLO_CONFIDENCE_THRESHOLD*100}%).")
    return galaxy_midpoints

def get_current_packet_files():
    """Returns a set of current file names in the packets directory."""
    try:
        return set(os.listdir(PACKETS_DIR))
    except FileNotFoundError:
        # This will be printed if mitmproxy isn't active and the folder doesn't exist
        # or if the path is wrong. For this test, it's fine.
        # print(f"Error: Packets directory not found at {PACKETS_DIR}")
        return set() # Return empty set if directory doesn't exist

def wait_for_new_packet(initial_files, timeout=5):
    """
    Waits for a new file to appear in the packets directory within a timeout.
    Returns True if a new file is detected, False otherwise.
    """
    start_time = time.time()
    # print("Waiting for new packet file...") # Keep this commented for cleaner test output if no mitmproxy
    while time.time() - start_time < timeout:
        current_files = get_current_packet_files()
        new_files = current_files - initial_files
        if new_files:
            # print(f"New packet file detected: {list(new_files)[0]}") # Keep commented for cleaner test output
            return True
        time.sleep(0.1) # Check frequently
    # print("No new packet file detected within timeout.") # Keep commented for cleaner test output
    return False

def click_close_button():
    """Moves mouse to and clicks the close button."""
    print(f"Clicking close button at ({CLOSE_BUTTON_X}, {CLOSE_BUTTON_Y})...")
    pyautogui.moveTo(CLOSE_BUTTON_X, CLOSE_BUTTON_Y, duration=0.2)
    pyautogui.click()
    time.sleep(0.5) # Give it a moment to register

def perform_map_drag():
    """Performs the specified mouse drag action to pan the map."""
    print(f"Performing map drag from ({DRAG_START_X}, {DRAG_START_Y}) to ({DRAG_END_X}, {DRAG_END_Y})...")
    
    # Move to the starting point of the drag
    pyautogui.moveTo(DRAG_START_X, DRAG_START_Y, duration=0.2) 
    
    # Perform the drag action (click, hold, move, release)
    pyautogui.dragTo(DRAG_END_X, DRAG_END_Y, duration=DRAG_DURATION_SECONDS, button='left')
    
    time.sleep(1.0) # Give the map a moment to settle after the drag

# --- Main Application Loop ---
if __name__ == "__main__":
    # Load the YOLO model once when the script starts
    yolo_model = load_yolo_model(YOLO_MODEL_PATH)

    print("\n--- Galaxy Bot Initialized ---")
    print("Ensure your game is visible on the primary monitor.")
    print("Press F8 to start the automated scanning, clicking, and map panning process.")
    print("Press F6 at any time to PAUSE/RESUME the bot.")
    print("To stop the bot completely, move your mouse to the top-left corner (0,0) of the screen (PyAutoGUI FailSafe).")
    print("Alternatively, press Ctrl+C in the console to abort manually.")
    
    # Set up the F6 hotkey listener (active throughout script execution)
    keyboard.add_hotkey('f6', toggle_pause)

    # Initial wait for F8 to begin the continuous loop
    print("\nWaiting for F8 key press to begin automated scanning loop...")
    keyboard.wait('f8') # This will block until F8 is pressed
    
    print("F8 detected! Starting automated process in 5 seconds...")
    time.sleep(5) # 5-second delay before the very first scan

    # This is the main continuous loop for scanning and panning
    while True:
        try:
            check_for_pause() # Check pause state before starting a new scan cycle

            print("\n--- Starting New Scan & Click Cycle ---")
            screenshot = get_screenshot_as_pil_image()
            predicted_midpoints = predict_galaxies(yolo_model, screenshot)

            if not predicted_midpoints:
                print("No galaxies detected in this screenshot with current confidence. Performing map drag to find more.")
                # Even if no galaxies, we still want to pan the map
            else:
                print(f"Starting to click {len(predicted_midpoints)} galaxies on the current screen.")
                for i, (gx, gy) in enumerate(predicted_midpoints):
                    check_for_pause() # Check pause state before each click
                    print(f"Clicking galaxy {i+1}/{len(predicted_midpoints)} at ({gx}, {gy})...")
                    
                    initial_packet_files = get_current_packet_files()
                    pyautogui.moveTo(gx, gy, duration=0.2)
                    pyautogui.click()
                    time.sleep(POST_CLICK_WAIT_TIME_SECONDS)

                    # Packet detection is still in, but output is commented out for cleaner test runs
                    packet_detected = wait_for_new_packet(initial_packet_files, timeout=3)
                    if packet_detected:
                        click_close_button()
                    else:
                        click_close_button() # Always try to close, even if no packet

                    time.sleep(0.5) # Short pause between clicks

                print(f"Finished clicking all {len(predicted_midpoints)} galaxies found on this screen view.")
            
            # After clicking all galaxies (or if none were found), perform the map drag
            check_for_pause() # Check pause state before performing drag
            perform_map_drag()
            
            print("Map drag completed. Beginning next scan cycle automatically.")
            time.sleep(2) # Short pause before the next cycle starts

        except pyautogui.FailSafeException:
            print("\nPyAutoGUI FailSafe triggered! Script aborted by mouse movement to (0,0).")
            break # Exit the main loop
        except KeyboardInterrupt:
            print("\nBot stopped by user (Ctrl+C).")
            break # Exit the main loop
        except Exception as e:
            print(f"\nAn unexpected error occurred during the scan cycle: {e}")
            import traceback
            traceback.print_exc()
            print("Attempting to continue after 5 seconds...")
            time.sleep(5) # Wait before attempting next cycle

    # Clean up the hotkey when the script exits
    keyboard.remove_hotkey('f6')
    print("\n--- Galaxy Bot terminated. ---")