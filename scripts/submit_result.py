import json
import requests
from pathlib import Path

GAS_ENDPOINT = "https://script.google.com/macros/s/AKfycbwJrEtqFu2cW-rFqBqXRIIEsuuajH-of5PUlYha97yOaRQ1681-T3xSfEHInlbW5dPT/exec"
DEFAULT_RESULT_PATH = "Artifacts/benchmark_summary.json"

def flatten_json(y, prefix=''):
    """Flatten nested JSON for spreadsheet use."""
    out = {}
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], f'{name}{a}_')
        elif isinstance(x, list):
            for i, a in enumerate(x):
                flatten(a, f'{name}{i}_')
        else:
            out[name[:-1]] = x
    flatten(y, prefix)
    return out

def submit_benchmark_result(path=DEFAULT_RESULT_PATH):
    result_path = Path(path)
    if not result_path.exists():
        print(f"❌ Benchmark result not found: {result_path}")
        return

    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat_data = flatten_json(data)
    try:
        r = requests.post(GAS_ENDPOINT, json=flat_data)
        print(f"📡 Submitted to GAS. Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"❌ Failed to submit to GAS: {e}")

if __name__ == "__main__":
    submit_benchmark_result()
