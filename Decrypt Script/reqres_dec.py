from mitmproxy import http
import json
import os

# Folder where packets will be saved
OUTPUT_DIR = "C:/Users/Administrator/Desktop/reqrespacket"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Unique flow ID to keep matching request/response
flow_counter = 0

def simple_string_decrypt(obfuscated: str) -> str:
    output = ""
    for i, ch in enumerate(obfuscated):
        code = ord(ch)
        if 32 <= code < 128:
            low_bits = (code ^ (i + 3)) & 0x1F
            code = (code & 0xFFFFFFE0) | low_bits
        output += chr(code)
    return output

def save_packet(kind: str, index: int, content: str):
    filename = f"packet_{index:04d}_{kind}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] Saved: {filename}")

def request(flow: http.HTTPFlow):
    global flow_counter
    if "/star/game" in flow.request.path and flow.request.method == "POST":
        try:
            data = flow.request.urlencoded_form.get("data", "")
            decrypted = simple_string_decrypt(data)
            save_packet("request", flow_counter, decrypted)
        except Exception as e:
            save_packet("request_error", flow_counter, f"[ERROR] {e}")

def response(flow: http.HTTPFlow):
    global flow_counter
    if "/star/game" in flow.request.path and flow.response.status_code == 200:
        try:
            text = flow.response.get_text()
            if text.startswith("{") and '"cmdName"' in text:
                # Response is already plain JSON
                save_packet("response", flow_counter, text)
            else:
                # Response might be encrypted
                json_body = json.loads(text)
                if "data" in json_body:
                    decrypted = simple_string_decrypt(json_body["data"])
                    save_packet("response", flow_counter, decrypted)
        except Exception as e:
            save_packet("response_error", flow_counter, f"[ERROR] {e}")

        # Only increment counter after both request + response handled
        flow_counter += 1
