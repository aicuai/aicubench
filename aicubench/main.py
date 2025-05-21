import subprocess
import os
import sys
import time
import urllib.request
import atexit
import platform
import json
from pathlib import Path

COMFY_DIR = os.environ.get("COMFY_DIR", "./ComfyUI")
COMFY_PORT = int(os.environ.get("COMFY_PORT", "8188"))
BASEMODELS_TXT_URL = "https://raw.githubusercontent.com/aicuai/Book-SD-MasterGuide/main/basemodels.txt"
WORKFLOW_DIR = Path("workflows")
WORKFLOW_TEMPLATE = "sd15-{i:02}.json"

NO_DELETE = "--nodelete" in sys.argv

GPU_INFO_PATH = Path("Artifacts/gpu_info.json")
LAST_SUCCESS_PATH = Path("Artifacts/last_success.json")

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

def clean():
    if NO_DELETE:
        print("⚠️ Skipping cleanup due to --nodelete option.")
        return
    print("🧹 Cleaning up...")
    try:
        subprocess.run(["bash", "scripts/clean.sh"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Cleanup failed: {e}")

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

def get_gpu_info():
    import platform
    import json
    result = {"platform": platform.system()}
    try:
        if result["platform"] == "Linux":
            info = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"], encoding="utf-8")
            result["nvidia-smi"] = info.strip()
        elif result["platform"] == "Darwin":
            try:
                import tensorflow as tf
                gpus = tf.config.list_physical_devices("GPU")
                result["tensorflow"] = [str(g) for g in gpus]
            except Exception as e:
                result["tensorflow"] = str(e)
    except Exception as e:
        result["error"] = str(e)
    GPU_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)
    GPU_INFO_PATH.write_text(json.dumps(result, indent=2))
    return result

def main():
    ensure_build_tools()
    print("🚀 Starting AICU benchmark workflow...")
    clone_comfyui()
    clone_comfyui()
    install_comfy_requirements()
    download_recommended_models()
    get_gpu_info()

    process = measure_startup_time()
    print("🧠 Placeholder: Load checkpoints into memory...")

    import requests
    last_success = ""

    for i in range(100):
        json_file = WORKFLOW_DIR / f"sd15-{i:02}.json"
        if not json_file.exists():
            if last_success:
                json_file = Path(last_success)
                print(f"⚠️ JSON file not found: using fallback {json_file.name}")
            else:
                print(f"❌ JSON file not found and no fallback available: {json_file.name}")
                continue

        print(f"🧠 Launching benchmark script for {json_file.name}...")
        try:
            subprocess.run(["python", "scripts/generate_sd15.py", "--json", str(json_file)], check=True)
            LAST_SUCCESS_PATH.write_text(json_file.name)
            last_success = str(json_file)
            subprocess.run(["python", "scripts/submit_result.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Benchmark subprocess failed: {e}")

    print("🛑 Shutting down ComfyUI...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

    print("✅ AICU benchmark workflow completed.")

    if not NO_DELETE:
        clean()

if __name__ == "__main__":
    main()
