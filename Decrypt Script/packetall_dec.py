from mitmproxy import http
import json
import os
import uuid

# Folder to save packets
OUTPUT_DIR = r"C:\Users\Administrator\Desktop\Desktop2\logs2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def simple_string_decrypt(obfuscated: str) -> str:
    """
    Decrypts an obfuscated string using a character-by-character XOR operation.
    """
    output = ""
    for i, ch in enumerate(obfuscated):
        code = ord(ch)
        if 32 <= code < 128: # Only apply transformation to printable ASCII characters
            low_bits = (code ^ (i + 3)) & 0x1F # XOR with index+3 and mask lower 5 bits
            code = (code & 0xFFFFFFE0) | low_bits # Combine higher bits with new lower bits
        output += chr(code)
    return output

def response(flow: http.HTTPFlow):
    """
    Mitmproxy event handler for HTTP responses.
    Captures, decrypts, and saves all "/star/game" packet data.
    """
    # 1. Filter for game packets based on the request path
    if "/star/game" not in flow.request.path:
        return

    # Generate a unique ID for this flow attempt
    current_uuid = str(uuid.uuid4())

    try:
        # 2. Get the response text and attempt to parse it as JSON
        text = flow.response.get_text()
        json_body = json.loads(text)

        # 3. Check for the 'data' field, which contains the encrypted game data
        # Ensure 'data' exists and is a string, as expected for decryption
        if "data" not in json_body or not isinstance(json_body["data"], str):
            # This might be a /star/game response, but not one with encrypted 'data'
            # We can log this if we want to know about such cases, but not save it as a "game packet"
            print(f"[!] Info: /star/game packet {current_uuid} did not contain a string 'data' field. Skipping save.")
            return

        # 4. Decrypt the content of the 'data' field
        decrypted_data = simple_string_decrypt(json_body["data"])

        # 5. (Optional but recommended) Verify if the decrypted data is valid JSON
        # If it's not, it suggests an issue with decryption or an unexpected data format.
        # This will raise a JSONDecodeError if invalid, which our outer except will catch.
        parsed_decrypted = json.loads(decrypted_data)

        # We are now capturing *all* packets that pass the above checks.
        # No further filtering based on `cmdName` or other content is applied.

        # Construct filename and save the decrypted content
        # Using a distinct prefix 'gamepacket_' to differentiate from general 'packet_' if needed.
        filename = f"gamepacket_{current_uuid}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            # Use json.dumps to pretty-print the JSON, making it easier to read
            f.write(json.dumps(parsed_decrypted, indent=4, ensure_ascii=False) + "\n")

        print(f"[+] Saved game packet: {filename}")

    except json.JSONDecodeError as e:
        # Specific error for issues parsing JSON (either initial response or decrypted data)
        err_file = os.path.join(OUTPUT_DIR, f"error_json_decode_{current_uuid}.txt")
        with open(err_file, "w", encoding="utf-8") as f:
            f.write(f"[ERROR] JSON Decode Error for packet {current_uuid}: {e}\n")
            f.write(f"Problematic flow path: {flow.request.path}\n")
            f.write(f"Original response text (truncated, first 500 chars): {flow.response.get_text()[:500]}\n")
            try:
                # If the error was in decrypting and then loading `json_body["data"]`
                if "data" in json_body and isinstance(json_body["data"], str):
                    f.write(f"Original encrypted data (truncated, first 500 chars): {json_body['data'][:500]}\n")
            except NameError: # json_body might not be defined if error was earlier
                pass
        print(f"[!] Error saving JSON decode failure: error_json_decode_{current_uuid}.txt")

    except Exception as e:
        # Catch any other general errors during processing (e.g., decryption function issue)
        err_file = os.path.join(OUTPUT_DIR, f"error_processing_{current_uuid}.txt")
        with open(err_file, "w", encoding="utf-8") as f:
            f.write(f"[ERROR] General processing error for packet {current_uuid}: {e}\n")
            f.write(f"Problematic flow path: {flow.request.path}\n")
            try:
                raw_response_text = flow.response.get_text()
                f.write(f"Original response text (truncated, first 500 chars): {raw_response_text[:500]}\n")
                # Attempt to get encrypted data if json_body was successfully parsed
                if "json_body" in locals() and "data" in json_body and isinstance(json_body["data"], str):
                    f.write(f"Original encrypted data (truncated, first 500 chars): {json_body['data'][:500]}\n")
            except Exception as inner_e:
                f.write(f"Could not retrieve full response/data for error logging: {inner_e}\n")

        print(f"[!] Error saving general processing failure: error_processing_{current_uuid}.txt")
