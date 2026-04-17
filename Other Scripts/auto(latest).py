import os
import time
import pyautogui
import mss
from PIL import Image
from ultralytics import YOLO
import keyboard # Already installed, good!

# --- Configuration ---
YOLO_MODEL_PATH = "C:/Users/Administrator/Desktop/bot/best.pt"

# Adjust these values based on your game's UI and screen resolution
CLOSE_BUTTON_X = 1220
CLOSE_BUTTON_Y = 400

# Drag coordinates for map panning
DRAG_START_X = 1600
DRAG_START_Y = 670
DRAG_END_X = 550
DRAG_END_Y = 670
DRAG_DURATION_SECONDS = 1.5

# Time to wait after clicking a galaxy before performing a check
POST_CLICK_WAIT_TIME_SECONDS = 1

# Pixel check configuration
TARGET_PIXEL_COLOR = (255, 255, 255)
PIXEL_CHECK_X = 738
PIXEL_CHECK_Y = 449
COLOR_CHECK_TIMEOUT_SECONDS = 10
COLOR_CHECK_INTERVAL_SECONDS = 0.5

# YOLO Confidence Threshold
YOLO_CONFIDENCE_THRESHOLD = 0.75

# --- Auto-Map Adjustment Configuration ---
MAP_X_INPUT_COORD = (680, 155)
MAP_Y_INPUT_COORD = (740, 155)
MAP_ENTER_BUTTON_COORD = (750, 155)

MAP_Y_START_VALUE = 20                # NEW: configurable starting Y
MAP_Y_INCREMENT_VALUE = 5             # Increment value
MAP_TYPEWRITE_INTERVAL_SECONDS = 0.2  # NEW: typing delay
MAP_RELOAD_WAIT_TIME_SECONDS = 15

# --- Control Configuration ---
MAX_CONSECUTIVE_EMPTY_PREDICTIONS = 8

# PyAutoGUI safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# --- Global State for Pause and Map Coordinates ---
is_paused = False
current_map_y = MAP_Y_START_VALUE  # start from config

# --- Helper Functions ---

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print("\n--- Bot PAUSED. Press F6 to RESUME. ---")
    else:
        print("\n--- Bot RESUMED. ---")

def check_for_pause():
    while is_paused:
        print("Bot is paused. Waiting for F6 to resume...")
        time.sleep(0.5)

def load_yolo_model(path):
    try:
        model = YOLO(path)
        print(f"YOLO model loaded from: {path}")
        return model
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        exit()

def get_screenshot_as_pil_image():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        return img

def predict_galaxies(model, screenshot_img):
    print("Running YOLO prediction...")
    results = model.predict(source=screenshot_img, conf=YOLO_CONFIDENCE_THRESHOLD, iou=0.7, verbose=False) 
    galaxy_midpoints = []
    for r in results[0].boxes:
        x_center, y_center, width, height = r.xywh[0].cpu().numpy()
        mid_x = int(x_center)
        mid_y = int(y_center)
        galaxy_midpoints.append((mid_x, mid_y))
    print(f"YOLO detected {len(galaxy_midpoints)} potential galaxies.")
    return galaxy_midpoints

def wait_for_specific_pixel_color(target_color, x, y, timeout=5, interval=0.1):
    start_time = time.time()
    print(f"Waiting for pixel at ({x}, {y}) to be {target_color}...")
    while time.time() - start_time < timeout:
        screenshot = get_screenshot_as_pil_image()
        try:
            pixel_color = screenshot.getpixel((x, y))
            if pixel_color == target_color:
                print(f"Target pixel color {target_color} detected at ({x}, {y}).")
                return True
        except IndexError:
            print(f"Warning: Pixel coordinates ({x}, {y}) out of bounds. Retrying...")
        time.sleep(interval)
    print(f"Target pixel color {target_color} not detected within {timeout} seconds.")
    return False

def click_close_button():
    print(f"Clicking close button at ({CLOSE_BUTTON_X}, {CLOSE_BUTTON_Y})...")
    pyautogui.moveTo(CLOSE_BUTTON_X, CLOSE_BUTTON_Y, duration=0.2)
    pyautogui.click()
    time.sleep(0.5)

def perform_map_drag():
    print(f"Performing map drag from ({DRAG_START_X}, {DRAG_START_Y}) to ({DRAG_END_X}, {DRAG_END_Y})...")
    pyautogui.moveTo(DRAG_START_X, DRAG_START_Y, duration=0.2) 
    pyautogui.dragTo(DRAG_END_X, DRAG_END_Y, duration=DRAG_DURATION_SECONDS, button='left')
    time.sleep(1.0)

def adjust_map_and_reset_scan():
    global current_map_y
    global consecutive_empty_predictions

    print(f"\n--- !!! WARNING: {MAX_CONSECUTIVE_EMPTY_PREDICTIONS} empty scans. Adjusting map coordinates. !!! ---")

    # --- Adjust X coordinate ---
    print(f"Setting map X coordinate to '2' at {MAP_X_INPUT_COORD}...")
    pyautogui.moveTo(MAP_X_INPUT_COORD[0], MAP_X_INPUT_COORD[1], duration=0.2)
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.press('backspace', presses=4)
    pyautogui.write('2', interval=MAP_TYPEWRITE_INTERVAL_SECONDS)  # NEW
    time.sleep(0.5)

    # --- Increment and Adjust Y coordinate ---
    current_map_y += MAP_Y_INCREMENT_VALUE
    print(f"Setting map Y coordinate to '{current_map_y}' at {MAP_Y_INPUT_COORD}...")
    pyautogui.moveTo(MAP_Y_INPUT_COORD[0], MAP_Y_INPUT_COORD[1], duration=0.2)
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.press('backspace', presses=4)
    pyautogui.write(str(current_map_y), interval=MAP_TYPEWRITE_INTERVAL_SECONDS)  # NEW
    time.sleep(0.5)

    # --- Click the Enter button ---
    print(f"Clicking map 'Enter' button at {MAP_ENTER_BUTTON_COORD}...")
    pyautogui.moveTo(MAP_ENTER_BUTTON_COORD[0], MAP_ENTER_BUTTON_COORD[1], duration=0.2)
    pyautogui.click()
    
    print(f"Waiting {MAP_RELOAD_WAIT_TIME_SECONDS} seconds for reload (X=2, Y={current_map_y})...")
    time.sleep(MAP_RELOAD_WAIT_TIME_SECONDS) 

    print("Map adjustment complete. Resetting scan counter.")
    consecutive_empty_predictions = 0

# --- Main Application Loop ---
if __name__ == "__main__":
    yolo_model = load_yolo_model(YOLO_MODEL_PATH)

    print("\n--- Galaxy Bot Initialized ---")
    print("Ensure your game is visible on the primary monitor.")
    print(f"IMPORTANT: Manually set your in-game map coordinates to X=2, Y={MAP_Y_START_VALUE} before starting the bot.")
    print("Press F8 to start. Press F6 to PAUSE/RESUME.")
    print(f"Bot will auto-adjust Y by {MAP_Y_INCREMENT_VALUE} after {MAX_CONSECUTIVE_EMPTY_PREDICTIONS} empty scans.")
    print("Failsafe: move mouse to (0,0) or Ctrl+C to stop.")

    keyboard.add_hotkey('f6', toggle_pause)

    print("\nWaiting for F8 key press to begin...")
    keyboard.wait('f8') 
    print("F8 detected! Starting in 5 seconds...")
    time.sleep(5)

    consecutive_empty_predictions = 0

    while True:
        try:
            check_for_pause()

            print("\n--- Starting New Scan & Click Cycle ---")
            screenshot = get_screenshot_as_pil_image()
            predicted_midpoints = predict_galaxies(yolo_model, screenshot)

            if not predicted_midpoints:
                print("No galaxies detected, performing map drag...")
                consecutive_empty_predictions += 1
                print(f"Consecutive empty predictions: {consecutive_empty_predictions}/{MAX_CONSECUTIVE_EMPTY_PREDICTIONS}")

                if consecutive_empty_predictions >= MAX_CONSECUTIVE_EMPTY_PREDICTIONS:
                    adjust_map_and_reset_scan()
                    continue
            else:
                consecutive_empty_predictions = 0
                print(f"Clicking {len(predicted_midpoints)} galaxies...")
                for i, (gx, gy) in enumerate(predicted_midpoints):
                    check_for_pause()
                    print(f"Clicking galaxy {i+1}/{len(predicted_midpoints)} at ({gx}, {gy})...")
                    
                    pyautogui.moveTo(gx, gy, duration=0.2)
                    pyautogui.click()
                    time.sleep(POST_CLICK_WAIT_TIME_SECONDS)

                    color_detected = wait_for_specific_pixel_color(
                        TARGET_PIXEL_COLOR, PIXEL_CHECK_X, PIXEL_CHECK_Y,
                        timeout=COLOR_CHECK_TIMEOUT_SECONDS, interval=COLOR_CHECK_INTERVAL_SECONDS
                    )
                    if not color_detected:
                        print("Pixel not detected, clicking close anyway.")
                    click_close_button()
                    time.sleep(0.5)

                print("Finished clicking galaxies.")

            check_for_pause()
            perform_map_drag()
            print("Map drag complete. Next cycle...")
            time.sleep(2)

        except pyautogui.FailSafeException:
            print("\nFailSafe triggered! Script aborted.")
            break
        except KeyboardInterrupt:
            print("\nBot stopped by user (Ctrl+C).")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            import traceback
            traceback.print_exc()
            print("Continuing after 5s...")
            time.sleep(5)

    keyboard.remove_hotkey('f6')
    print("\n--- Galaxy Bot terminated. ---")
