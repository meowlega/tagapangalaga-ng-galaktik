import os
import json
import uuid
import time
import mss
import mss.tools
import pyautogui
import keyboard
from datetime import datetime
from ultralytics import YOLO
from mitmproxy import http

# ---------------------------- CONFIG ---------------------------- #
base_dir = r"C:/Users/Administrator/Desktop/galaxy_bot"
model_path = os.path.join(base_dir, "yolo", "best.pt")
screenshot_dir = os.path.join(base_dir, "screenshots1")
os.makedirs(screenshot_dir, exist_ok=True)

# Action timing
DELAY_MS = 400
STARINFO_TIMEOUT = 5  # seconds

# Galaxy coordinate input + control buttons
coord_x_input = (680, 160)
coord_go_button = (755, 160)
close_ui_button = (1220, 405)

# Starting coordinate (user will edit before running)
view_x = 1  # <- EDIT THIS BEFORE RUNNING
view_y = 1  # <- Unused for now

# Confidence threshold
YOLO_CONFIDENCE = 0.5

# Load YOLO model once
model = YOLO(model_path)
print("[INFO] YOLO model loaded.")

# Internal tracking
last_packet = ""
center_coords = []
overlap_found = False

# ------------------------- UTILITIES --------------------------- #
def wait(ms):
    time.sleep(ms / 1000)

def simple_string_decrypt(obfuscated: str) -> str:
    output = ""
    for i, ch in enumerate(obfuscated):
        code = ord(ch)
        if 32 <= code < 128:
            low_bits = (code ^ (i + 3)) & 0x1F
            code = (code & 0xFFFFFFE0) | low_bits
        output += chr(code)
    return output

def capture_monitor1():
    uid = uuid.uuid4().hex
    filename = f"monitor1_{uid}.png"
    filepath = os.path.join(screenshot_dir, filename)
    with mss.mss() as sct:
        monitor1 = sct.monitors[1]
        img = sct.grab(monitor1)
        mss.tools.to_png(img.rgb, img.size, output=filepath)
    print(f"[CAPTURE] Screenshot saved: {filename}")
    return filepath

def calculate_iou(box1, box2):
    xa = max(box1[0], box2[0])
    ya = max(box1[1], box2[1])
    xb = min(box1[2], box2[2])
    yb = min(box1[3], box2[3])
    inter_area = max(0, xb - xa) * max(0, yb - ya)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area else 0

def check_overlaps(boxes, threshold=0.5):
    for i in range(len(boxes)):
        for j in range(i+1, len(boxes)):
            if calculate_iou(boxes[i], boxes[j]) >= threshold:
                return True
    return False

def click(x, y):
    pyautogui.moveTo(x, y)
    wait(DELAY_MS)
    pyautogui.click()
    wait(DELAY_MS)

def type_slow(text):
    for char in str(text):
        keyboard.write(char)
        wait(DELAY_MS)

def clear_input():
    for _ in range(4):
        keyboard.press_and_release("backspace")
        wait(DELAY_MS)

def run_yolo(filepath):
    results = model(filepath, conf=YOLO_CONFIDENCE)
    coords = []
    for box in results[0].boxes.xyxy.cpu().numpy():
        x1, y1, x2, y2 = box[:4]
        coords.append((x1, y1, x2, y2))
    return coords

def center_of(box):
    x1, y1, x2, y2 = box
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

def click_all_galaxies(center_coords):
    global overlap_found
    for center in center_coords:
        clicked = False
        for attempt in range(2):  # max 2 attempts if fail
            click(*center)
            print(f"[CLICK] Galaxy at {center}, waiting for queryStarInfo...")
            start = time.time()
            while time.time() - start < STARINFO_TIMEOUT:
                if last_packet == "queryStarInfo":
                    clicked = True
                    break
                time.sleep(0.1)
            if clicked:
                click(*close_ui_button)
                break
            else:
                print("[WARN] No packet, retrying click")
        wait(DELAY_MS)
    # After clicking all
    if overlap_found:
        update_view_coords(5)
    else:
        update_view_coords(10)
    update_coordinate_input()

def update_view_coords(increment):
    global view_x
    view_x += increment
    print(f"[UPDATE] View X incremented to {view_x}")

def update_coordinate_input():
    click(*coord_x_input)
    clear_input()
    type_slow(view_x)
    click(*coord_go_button)
    print("[ACTION] Updated coordinate input.")

# -------------------- MITMPROXY MAIN LOGIC --------------------- #
def response(flow: http.HTTPFlow):
    global last_packet, center_coords, overlap_found

    if "/star/game" not in flow.request.path:
        return

    try:
        raw = json.loads(flow.response.get_text())
        if "data" not in raw:
            return

        decrypted = simple_string_decrypt(raw["data"])
        parsed = json.loads(decrypted)

        for item in parsed.get("list", []):
            cmd = item.get("cmdName")
            last_packet = cmd

            if cmd == "queryGalaxyWindow":
                print(f"[EVENT] queryGalaxyWindow received")
                filepath = capture_monitor1()
                boxes = run_yolo(filepath)
                overlap_found = check_overlaps(boxes)
                center_coords = [center_of(b) for b in boxes]
                click_all_galaxies(center_coords)

    except Exception as e:
        print("[ERROR]", e)
