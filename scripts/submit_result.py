import os
import json
import requests
from pathlib import Path
from datetime import datetime
import uuid

ARTIFACTS_DIR = Path("Artifacts")
BENCHMARK_LOG = ARTIFACTS_DIR / "benchmark_summary.json"
GPU_INFO_FILE = ARTIFACTS_DIR / "gpu_info.json"
LAST_SUCCESS_FILE = ARTIFACTS_DIR / "last_success.json"
SUBMIT_MARKER = ARTIFACTS_DIR / ".submitted"
GAS_ENDPOINT = os.environ.get("GAS_ENDPOINT", "https://script.google.com/macros/s/AKfycbzgjRG-ebQxZDF6sdJwCGGZj3JMYF8nqNYQ4dCvMHuxlm8AKxp1zI_-N2NSVMB4eoG9/exec")


def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def submit_to_gas():
    if not BENCHMARK_LOG.exists():
        print(f"❌ Benchmark result not found: {BENCHMARK_LOG}")
        return

    if SUBMIT_MARKER.exists():
        print("ℹ️ Submission already completed. Skipping.")
        return

    with open(BENCHMARK_LOG, 'r', encoding='utf-8') as f:
        data = json.load(f)

    submission_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{os.uname().nodename}-{datetime.utcnow().isoformat()}"))
    data['uuid'] = submission_id

    if GPU_INFO_FILE.exists() and GPU_INFO_FILE.stat().st_size > 0:
        try:
            with open(GPU_INFO_FILE, 'r', encoding='utf-8') as gf:
                gpu_info = json.load(gf)
                data['gpu_info'] = gpu_info
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse gpu_info.json: {e}")
    else:
        print("⚠️ GPU_INFO_FILE is missing or empty.")

    if LAST_SUCCESS_FILE.exists() and LAST_SUCCESS_FILE.stat().st_size > 0:
        try:
            with open(LAST_SUCCESS_FILE, 'r', encoding='utf-8') as lf:
                last_prompt = json.load(lf)
                data['last_prompt'] = last_prompt.get("workflow")
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse last_success.json: {e}")
    else:
        print("⚠️ LAST_SUCCESS_FILE is missing or empty.")

    data['timestamp'] = datetime.utcnow().isoformat()
    data['schema_version'] = "1.1"

    flat = flatten_dict(data)
    print(f"🌐 Submitting to GAS ({GAS_ENDPOINT})...")
    try:
        response = requests.post(GAS_ENDPOINT, json=flat)
        if response.status_code == 200:
            print("✅ Submission successful.")
            SUBMIT_MARKER.touch()
        else:
            print(f"⚠️ Submission failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error submitting to GAS: {e}")


if __name__ == "__main__":
    submit_to_gas()
