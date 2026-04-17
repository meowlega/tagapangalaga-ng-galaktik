import json
import os
import uuid
from mitmproxy import http # Essential import for HTTPFlow
import datetime # Good for logging timestamps if needed, though UUID is requested

# --- Configuration ---
LOG_DIR = r"C:\Users\Administrator\Desktop\logs" # Use a raw string for Windows paths

# --- Mitmproxy Addon Class ---
class GamePacketLogger:
    def __init__(self):
        # Create the log directory if it doesn't exist
        os.makedirs(LOG_DIR, exist_ok=True)
        print(f"[{self.__class__.__name__}] Log directory set to: {LOG_DIR}")

        # These were global in your original snippet. If you need to maintain state
        # across different requests/responses within this mitmproxy session,
        # they should be instance variables. For this script, we'll mainly focus on logging.
        self.last_packet = None
        self.center_coords = None
        self.overlap_found = False

    # Your provided decryption function, now a static method of the class
    @staticmethod
    def simple_string_decrypt(obfuscated: str) -> str:
        output = ""
        for i, ch in enumerate(obfuscated):
            code = ord(ch)
            if 32 <= code < 128:
                # This bitwise operation effectively "xor"s the low 5 bits with (i+3)
                # and then puts them back, while preserving the higher bits.
                low_bits = (code ^ (i + 3)) & 0x1F
                code = (code & 0xFFFFFFE0) | low_bits
            output += chr(code)
        return output

    # The mitmproxy response hook
    def response(self, flow: http.HTTPFlow):
        # Only process responses for the specific path
        if "/star/game" not in flow.request.path:
            return

        try:
            # Ensure the response content is available and can be treated as text
            if flow.response.text is None:
                print(f"[GamePacketLogger] Response text is None for {flow.request.path}")
                return

            # Attempt to parse the outer JSON structure
            raw = json.loads(flow.response.text)
            if "data" not in raw:
                # print(f"[GamePacketLogger] No 'data' field found in response from {flow.request.path}")
                return

            # Decrypt the 'data' part
            decrypted = self.simple_string_decrypt(raw["data"])

            # Parse the inner decrypted JSON
            parsed = json.loads(decrypted)

            print(f"[GamePacketLogger] Captured and decrypted data from {flow.request.path}")

            # --- Save the decoded packet ---
            log_filename = f"{uuid.uuid4()}.json" # Generate a unique UUID filename
            log_filepath = os.path.join(LOG_DIR, log_filename)

            with open(log_filepath, "w", encoding="utf-8") as f:
                # Use json.dump for pretty-printing the JSON
                json.dump(parsed, f, indent=4, ensure_ascii=False) # ensure_ascii=False keeps non-ASCII chars as is

            print(f"[GamePacketLogger] Saved decrypted data to: {log_filepath}")

            # --- Original "queryGalaxyWindow" logic (commented out) ---
            # This part of your original code involves external dependencies (like
            # image processing, YOLO, clicking actions). For this mitmproxy script
            # to run independently without errors, these external calls are commented.
            # You would integrate them in a separate script or modify this one
            # significantly if they are to be triggered by mitmproxy.

            # for item in parsed.get("list", []):
            #     cmd = item.get("cmdName")
            #     self.last_packet = cmd # Update instance variable
            #
            #     if cmd == "queryGalaxyWindow":
            #         print(f"[GamePacketLogger] [EVENT] queryGalaxyWindow received")
            #         # The following functions (capture_monitor1, run_yolo, check_overlaps,
            #         # center_of, click_all_galaxies) are NOT part of this mitmproxy script.
            #         # They would need to be defined elsewhere in your broader application.
            #         # Commenting them out to allow the mitmproxy script to run without errors.
            #         # filepath = capture_monitor1()
            #         # boxes = run_yolo(filepath)
            #         # self.overlap_found = check_overlaps(boxes)
            #         # self.center_coords = [center_of(b) for b in boxes]
            #         # click_all_galaxies(self.center_coords)

        except json.JSONDecodeError as e:
            print(f"[GamePacketLogger] JSONDecodeError: {e} in response from {flow.request.path}. Raw response might not be valid JSON.")
            # print(f"Raw response start: {flow.response.text[:200]}...") # Uncomment for debugging
        except Exception as e:
            print(f"[GamePacketLogger] An unexpected error occurred during processing {flow.request.path}: {e}")
            # import traceback # Uncomment and use traceback.print_exc() for more detailed errors
            # traceback.print_exc()


# mitmproxy looks for an 'addons' list at the top level of the script
addons = [
    GamePacketLogger()
]