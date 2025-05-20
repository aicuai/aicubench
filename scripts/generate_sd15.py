import subprocess
import os
import sys
import time
import json
import requests
import argparse
from pathlib import Path

COMFY_PORT = int(os.environ.get("COMFY_PORT", "8188"))
DEFAULT_JSON = "3939API.json"
COMFY_URL = f"http://127.0.0.1:{COMFY_PORT}"
COMFY_DIR = os.environ.get("COMFY_DIR", "./ComfyUI")

def start_comfyui():
    print("🚀 Starting ComfyUI headless server...")
    return subprocess.Popen(
        ["python", "main.py", "--listen", "127.0.0.1", "--port", str(COMFY_PORT)],
        cwd=COMFY_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def wait_for_comfyui(timeout=20):
    print("⏳ Waiting for ComfyUI to be ready...")
    for _ in range(timeout * 2):
        try:
            r = requests.get(f"{COMFY_URL}")
            if r.status_code == 200:
                print("✅ ComfyUI is ready.")
                return True
        except Exception:
            time.sleep(0.5)
    print("❌ ComfyUI did not become ready in time.")
    return False

def queue_prompt(prompt):
    payload = {"prompt": prompt}
    print("📤 Sending prompt to ComfyUI...")
    print(f"📤 Payload preview (truncated): {json.dumps(payload)[:500]}")
    try:
        r = requests.post(f"{COMFY_URL}/prompt", json=payload)
        print(f"📬 Status: {r.status_code}")
        print(r.text)
        return r
    except Exception as e:
        print(f"❌ Failed to send prompt: {e}")
        return None

def wait_for_completion(prompt_id, timeout=120, poll_interval=2):
    print(f"⏳ Waiting for completion of prompt ID {prompt_id}...")
    elapsed = 0
    while elapsed < timeout:
        try:
            r = requests.get(f"{COMFY_URL}/history/{prompt_id}")
            if r.status_code == 200:
                data = r.json()
                if "outputs" in data.get(prompt_id, {}):
                    print("✅ Prompt processing completed.")
                    return data
            else:
                print(f"⚠️ Unexpected status code {r.status_code} while polling.")
        except Exception as e:
            print(f"⚠️ Error while polling for completion: {e}")
        time.sleep(poll_interval)
        elapsed += poll_interval
    print("❌ Timeout waiting for prompt completion.")
    return None

def download_images(history_data):
    images_saved = 0
    prompt_outputs = next(iter(history_data.values()), {})
    output_dir = Path("output_images")
    output_dir.mkdir(exist_ok=True)

    for node_id, output_data in prompt_outputs.get("outputs", {}).items():
        if "images" in output_data:
            for img in output_data["images"]:
                filename = img.get("filename")
                subfolder = img.get("subfolder", "")
                folder_type = img.get("type", "")
                if not filename:
                    continue
                try:
                    params = {
                        "filename": filename,
                        "subfolder": subfolder,
                        "type": folder_type,
                    }
                    r = requests.get(f"{COMFY_URL}/view", params=params)
                    if r.status_code == 200:
                        image_path = output_dir / filename
                        with open(image_path, "wb") as f:
                            f.write(r.content)
                        images_saved += 1
                    else:
                        print(f"⚠️ Failed to download {filename}, status code {r.status_code}")
                except Exception as e:
                    print(f"⚠️ Error downloading {filename}: {e}")
    return images_saved

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=str, default=DEFAULT_JSON, help="Path to prompt JSON file")
    args = parser.parse_args()

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        prompt = json.load(f)

    proc = start_comfyui()
    try:
        if wait_for_comfyui():
            response = queue_prompt(prompt)
            if response is not None:
                try:
                    resp_json = response.json()
                    prompt_id = resp_json.get("prompt_id")
                    if prompt_id:
                        history_data = wait_for_completion(prompt_id)
                        if history_data:
                            images_saved = download_images(history_data)
                            elapsed_time = time.time() - start_time
                            print(f"🖼️ Saved {images_saved} image(s) in {elapsed_time:.2f} seconds.")
                        else:
                            print("❌ No history data received.")
                    else:
                        print("❌ No prompt_id found in response.")
                except Exception as e:
                    print(f"❌ Failed to process response JSON: {e}")
    finally:
        print("🛑 Shutting down ComfyUI...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == "__main__":
    main()