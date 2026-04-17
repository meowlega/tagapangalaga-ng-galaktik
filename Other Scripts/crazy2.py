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

# -> Configurations

# Paths
main_path = r"C:/Users/Administrator/Desktop/galaxy_bot"
yolo_path = r"C:/Users/Administrator/Desktop/galaxy_bot/yolo/best.pt"
ss_path = r"C:/Users/Administrator/Desktop/galaxy_bot/ss1"

# Timings
delay = 0.4
start_cd = 5

# Coords
x_coordInput = (680, 160)
y_coordInput = (740, 160)
go_coordButton = (755, 160)

rebootButton = (965, 660)
refreshButton = (90, 45)
x_galaxyViewButton = (1220, 405)

# Starting Coords (Where to search)
view_x = 1
view_y = 1

# YOLO
model = YOLO(yolo_path)
yolo_confidence = 0.5 # 0.0 to 1

# Internal Tracking
last_packet = ""
center_coords = []
overlap_found = False

# -> Functions
# write "wait" instead of "time.sleep()"
def wait(ms):
    time.sleep(ms)

# decrypt "data"
def data_packet_decrypt(obfuscated: str) -> str:
    output = ""
    for i, ch in enumerate(obfuscated):
        code = ord(ch)
        if 32 <= code < 128:
            low_bits = (code ^ (i + 3)) & 0x1F
            code = (code & 0xFFFFFFE0) | low_bits
        output += chr(code)
    return output

# Screenshot monitor and make the filename unique
def capture_monitor1():
    uid = uuid.uuid4().hex # make it unique
    filename = f"monitor1_{uid}.png"
    filepath = os.path.join(screenshot_dir, filename)
    with mss.mss() as sct:
        monitor1 = sct.monitors[1]
        img = sct.grab(monitor1)
        mss.tools.to_png(img.rgb, img.size, output=filepath)
    return filepath

# Find if overlap?
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

# Checks for overlaps
def check_overlaps(boxes, threshold=0.5):
    for i in range(len(boxes)):
        for j in range(i+1, len(boxes)):
            if calculate_iou(boxes[i], boxes[j]) >= threshold:
                return True
    return False

# Hover to something
def click(x, y):
    pyautogui.moveTo(x, y)
    wait(delay)
    pyautogui.click()
    wait(delay)

# Type the coordinate?
def type_slow(text):
    for char in str(text):
        keyboard.write(char)
        wait(delay)