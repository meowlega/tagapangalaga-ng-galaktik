from mitmproxy import http
import json
import os
import uuid # Import the uuid module

# Folder to save packets
OUTPUT_DIR = r"C:/Users/Administrator/Desktop/bot/packets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def simple_string_decrypt(obfuscated: str) -> str:
    output = ""
    for i, ch in enumerate(obfuscated):
        code = ord(ch)
        if 32 <= code < 128:
            low_bits = (code ^ (i + 3)) & 0x1F
            code = (code & 0xFFFFFFE0) | low_bits
        output += chr(code)
    return output

def response(flow: http.HTTPFlow):
    # No need for 'global packet_index' anymore

    if "/star/game" not in flow.request.path:
        return

    # Generate a unique ID for this flow attempt
    # We generate it here so that both successful saves and errors use a unique ID
    # related to this specific packet processing attempt.
    current_uuid = str(uuid.uuid4())

    try:
        text = flow.response.get_text()
        json_body = json.loads(text)

        if "data" not in json_body:
            return

        decrypted = simple_string_decrypt(json_body["data"])
        parsed = json.loads(decrypted)

        # Only save if it contains important commands
        if not any(cmd.get("cmdName") in ("queryGalaxyWindow", "queryStarInfo") for cmd in parsed.get("list", [])):
            return

        # Use the generated UUID for the filename
        filename = f"packet_{current_uuid}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(decrypted.strip() + "\n")

        print(f"[+] Saved: {filename}")
        # packet_index += 1 # No longer needed

    except Exception as e:
        err_file = os.path.join(OUTPUT_DIR, f"error_{current_uuid}.txt")
        with open(err_file, "w", encoding="utf-8") as f:
            f.write("[ERROR] " + str(e) + "\n") # Added newline for consistency
            f.write(f"Original request path: {flow.request.path}\n") # Added path for debugging
            f.write(f"Original response text (truncated): {flow.response.get_text()[:500]}\n") # Added response for debugging
        print(f"[!] Error saved: error_{current_uuid}.txt")