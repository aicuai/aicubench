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

Then you can run:

```bash
aicubench all --prompt "1girl" --it 10
```


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

⸻

README.ja.md には上記の内容を日本語で翻訳して記載可能です。必要であれば翻訳も行います。続きを希望されますか？