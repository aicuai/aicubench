import subprocess
import os
import sys
import time
import json
import requests
import argparse
from pathlib import Path

COMFY_PORT = int(os.environ.get("COMFY_PORT", "8188"))
COMFY_DIR = os.environ.get("COMFY_DIR", "./ComfyUI")
DEFAULT_JSON = "3939.json"

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
    for _ in range(timeout * 2):  # check every 0.5s
        try:
            r = requests.get(f"http://127.0.0.1:{COMFY_PORT}")
            if r.status_code == 200:
                print("✅ ComfyUI is ready.")
                return True
        except Exception:
            time.sleep(0.5)
    print("❌ ComfyUI did not become ready in time.")
    return False

def trigger_prompt(prompt_json):
    print("🖼️ Sending prompt to ComfyUI...")
    try:
        payload = {"prompt": prompt_json}
        print("📤 Payload preview (truncated):", json.dumps(payload)[:500])
        r = requests.post(f"http://127.0.0.1:{COMFY_PORT}/prompt", json=payload)
        print(f"📬 Status: {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"❌ Error triggering prompt: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=str, default=DEFAULT_JSON, help="Path to prompt JSON file")
    args = parser.parse_args()

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        prompt_json = json.load(f)

    proc = start_comfyui()
    try:
        if wait_for_comfyui():
            trigger_prompt(prompt_json)
    finally:
        print("🛑 Shutting down ComfyUI...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == "__main__":
    main()