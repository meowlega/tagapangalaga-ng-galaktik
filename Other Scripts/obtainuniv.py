from mitmproxy import http
import json
import os
import uuid

# --- CONFIGURATION ---
OUTPUT_DIR = r"C:\Users\Administrator\Desktop\logs2"
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
    # 1. Filter: Only look at game traffic
    if "/star/game" not in flow.request.path:
        return

    try:
        text = flow.response.get_text()
        json_body = json.loads(text)

        # 2. Safety check for data field
        if "data" not in json_body or not isinstance(json_body["data"], str):
            return

        # 3. Decrypt
        decrypted_data = simple_string_decrypt(json_body["data"])
        parsed_decrypted = json.loads(decrypted_data)

        # 4. Filter: Only save if it contains "obtainUniverse"
        # We check the command list inside the packet
        command_list = parsed_decrypted.get("list", [])
        is_universe_packet = any(cmd.get("cmdName") == "obtainUniverse" for cmd in command_list)

        if is_universe_packet:
            # Generate filename
            current_uuid = str(uuid.uuid4())
            filename = f"universe_{current_uuid}.json" # Saving as .json for easier reading
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(parsed_decrypted, f, indent=4, ensure_ascii=False)
            
            # Minimal log to mitmproxy console just to know it's working
            print(f"[+] Universe data captured: {filename}")

    except Exception:
        pass # Fail silently to keep mitmproxy flow smooth
