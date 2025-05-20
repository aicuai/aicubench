# 🧪 aicubench

aicubench is an open, standard benchmark toolset for PAISC workloads (Image, Video, Audio, Speech-to-Text, LLM) across platforms (Mac/Windows/Linux) and models (Stable Diffusion, AnimateDiff, Style-Bert-VITS2, Whisper, etc.).

This repository allows reproducible benchmarking using real-world prompts and datasets from Hugging Face AICU/aicubench, with results exportable to HTML and JSON for public publishing.

## 🔧 Quick Start (macOS)

### 1. Clone the repository

```bash
git clone https://github.com/yourname/aicubench.git
cd aicubench
```

### 2. Run the setup script

This will:
- Create a virtual environment (`.venv`)
- Activate it
- Install `aicubench` in editable mode
- Run a sample benchmark

```bash
bash scripts/setup.sh
```

### 3. Next time activation

To use `aicubench` later:

```bash
source .venv/bin/activate
```


Then you can run a basic test (ComfyUI must be running in background):

```bash
aicubench all --prompt "1girl" --it 10
```


### ⚠️ ComfyUI Integration Notes

`aicubench` will automatically:
- Clone ComfyUI into the `ComfyUI/` directory
- Download recommended model checkpoints into `ComfyUI/models/checkpoints/`
- Launch ComfyUI in headless mode on port `8181`
- Attempt inference via the ComfyUI API

No manual launch of ComfyUI is required. If ComfyUI fails to start properly, a message will be shown in the terminal.

Example logs:

```
⏱ Measuring initial ComfyUI startup time...
🚀 Launching ComfyUI headless server...
🚀 ComfyUI started in 10.01 seconds
🧠 Placeholder: Load checkpoints into memory...
🖼️ Triggering inference via ComfyUI API...
❌ Failed to trigger inference: HTTPConnectionPool(host='127.0.0.1', port=8181): Max retries exceeded...
```

This likely means the server was not ready yet. You may try re-running `aicubench` after a short delay.

### 🧼 Cleaning Up

To re-run benchmarks from a clean state, you can use the cleanup script:

```bash
bash scripts/clean.sh
```

This will delete:
- The `ComfyUI/` directory (including all models)
- Any temporary files

The next run of `aicubench` will automatically reinitialize everything.


🖼 Benchmark Targets
	•	Image generation: Stable Diffusion 1.5, SDXL, FLUX.1
	•	Video generation: AnimateDiff, Wan2.1, HunyuanVideo
	•	Audio synthesis: Style-Bert VITS2
	•	Speech-to-text: Whisper, Audapolis
	•	LLMs: SOTA models evaluated on MMLU, GSM8K, etc.

⸻

📦 Installation (Alternative)

To install via pip (editable mode):

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .


⸻

⚖️ License

This project is licensed under the Apache License 2.0. See LICENSE for details.
