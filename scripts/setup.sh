#!/bin/bash

echo "🔧 Creating virtual environment..."
python3 -m venv .venv

echo "📦 Activating virtual environment..."
source .venv/bin/activate

echo "⬇️ Installing aicubench in editable mode..."
python3 -m pip install -e .

echo "🚀 Running initial aicubench test..."
aicubench all --it 5 --prompt "1girl" --ar 1024x1024

echo "✅ Done. To activate again later, run: source .venv/bin/activate"