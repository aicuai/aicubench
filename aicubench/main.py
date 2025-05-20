import subprocess
import os
import sys
import time
import urllib.request
import atexit
import platform

def ensure_build_tools():
    system = platform.system()
    print(f"🖥 Detected platform: {system}")
    if system == "Darwin":
        print("🔧 Checking macOS build tools for sentencepiece...")
        try:
            subprocess.run(["brew", "--version"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["brew", "install", "cmake", "pkg-config", "coreutils"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to verify or install Homebrew tools.")
            sys.exit(1)
    elif system == "Linux":
        if "COLAB_GPU" in os.environ:
            print("🔧 Installing Linux build tools for Google Colab...")
            try:
                subprocess.run(["apt-get", "update"], check=True)
                subprocess.run(["apt-get", "install", "-y", "cmake", "pkg-config"], check=True)
            except subprocess.CalledProcessError:
                print("❌ Failed to install required build tools on Colab.")
                sys.exit(1)
        else:
            print("ℹ️ Linux platform detected. Please ensure cmake and pkg-config are installed.")
    elif system == "Windows":
        print("⚠️ Windows detected. Please manually install CMake and ensure `sentencepiece` can compile.")
    else:
        print(f"⚠️ Unknown platform: {system}. Proceed with caution.")

COMFY_DIR = os.environ.get("COMFY_DIR", "./ComfyUI")
COMFY_PORT = int(os.environ.get("COMFY_PORT", "8188"))
BASEMODELS_TXT_URL = "https://raw.githubusercontent.com/aicuai/Book-SD-MasterGuide/main/basemodels.txt"

# Check for --nodelete option
NO_DELETE = "--nodelete" in sys.argv

def clean():
    if NO_DELETE:
        print("⚠️ Skipping cleanup due to --nodelete option.")
        return
    print("🧹 Cleaning up...")
    try:
        subprocess.run(["bash", "scripts/clean.sh"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Cleanup failed: {e}")

atexit.register(clean)

def clone_comfyui():
    if not os.path.isdir(COMFY_DIR):
        try:
            print("📥 Cloning ComfyUI repository...")
            subprocess.run([
                "git", "clone", "https://github.com/comfyanonymous/ComfyUI.git", COMFY_DIR
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone ComfyUI: {e}")
            sys.exit(1)
    else:
        print("✅ ComfyUI already exists.")

def test_comfyui_start():
    print("⚡ Testing initial ComfyUI startup before downloading models...")
    proc = start_comfyui()
    for _ in range(20):
        try:
            import requests
            r = requests.get(f"http://127.0.0.1:{COMFY_PORT}")
            if r.status_code == 200:
                proc.terminate()
                print("✅ ComfyUI test startup succeeded.")
                return
        except Exception:
            time.sleep(0.5)
    print("❌ ComfyUI test startup failed.")
    proc.terminate()
    clean()
    sys.exit(1)

def download_recommended_models():
    print("⬇️ Downloading recommended models...")
    try:
        with urllib.request.urlopen(BASEMODELS_TXT_URL) as response:
            lines = response.read().decode().splitlines()
            for line in lines:
                if line.strip().startswith("wget"):
                    print(f"🌐 {line}")
                    parts = line.strip().split()
                    if "-c" in parts and "-P" in parts:
                        url = parts[parts.index("-c") + 1]
                        dest_dir = parts[parts.index("-P") + 1]
                        filename = os.path.basename(url)
                        if "models" in dest_dir and not dest_dir.startswith(COMFY_DIR):
                            dest_dir = os.path.join(COMFY_DIR, dest_dir)
                        os.makedirs(dest_dir, exist_ok=True)
                        dest_path = os.path.join(dest_dir, filename)
                        try:
                            start = time.time()
                            urllib.request.urlretrieve(url, dest_path)
                            elapsed = time.time() - start
                            print(f"✅ Downloaded to {dest_path} in {elapsed:.2f} seconds")
                        except Exception as e:
                            print(f"❌ Download failed for {url}: {e}")
                    else:
                        print("⚠️ Malformed wget line, skipping:", line)
    except Exception as e:
        print(f"❌ Failed to download models: {e}")
        sys.exit(1)

def install_comfy_requirements():
    print("📦 Installing ComfyUI requirements...")
    req_file = os.path.join(COMFY_DIR, "requirements.txt")
    if os.path.isfile(req_file):
        if sys.version_info >= (3, 12):
            print("❌ Python 3.13+ is not supported for sentencepiece. Please use Python 3.11.")
            sys.exit(1)
        subprocess.run(["pip", "install", "-r", req_file], check=True)
    else:
        print(f"⚠️ requirements.txt not found in {COMFY_DIR}")

def start_comfyui():
    print("🚀 Launching ComfyUI headless server...")
    main_py_path = os.path.join(COMFY_DIR, "main.py")
    if not os.path.isfile(main_py_path):
        print(f"❌ Error: main.py not found in {COMFY_DIR}")
        sys.exit(1)
    return subprocess.Popen(
        ["python", "main.py", "--listen", "127.0.0.1", "--port", str(COMFY_PORT)],
        cwd=COMFY_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def measure_startup_time():
    print("⏱ Measuring initial ComfyUI startup time...")
    start = time.time()
    process = start_comfyui()
    for _ in range(20):
        try:
            import requests
            r = requests.get(f"http://127.0.0.1:{COMFY_PORT}")
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    else:
        print("❌ ComfyUI failed to start.")
        clean()
        sys.exit(1)
    elapsed = time.time() - start
    print(f"🚀 ComfyUI started in {elapsed:.2f} seconds")
    return process

def trigger_inference():
    import requests
    import json

    print("🖼️ Triggering inference via ComfyUI API...")
    payload = {
        "prompt": {
            "1": {
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "width": 512,
                    "height": 512,
                    "positive": "1girl",
                    "negative": "",
                },
                "class_type": "KSampler"
            }
        }
    }

    try:
        r = requests.post(f"http://127.0.0.1:{COMFY_PORT}/prompt", json=payload)
        print(f"✅ Inference triggered, status code: {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"❌ Failed to trigger inference: {e}")

def main():
    ensure_build_tools()
    print("🚀 Starting AICU benchmark workflow...")
    clone_comfyui()
    clone_comfyui()
    install_comfy_requirements()
    test_comfyui_start()
    download_recommended_models()
    process = measure_startup_time()
    print("🧠 Placeholder: Load checkpoints into memory...")
    try:
        trigger_inference()
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
    finally:
        print("🛑 Shutting down ComfyUI...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    main()