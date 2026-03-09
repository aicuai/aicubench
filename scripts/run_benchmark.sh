#!/bin/bash

# activate Python environment
source .venv/bin/activate

# Install dependencies (if needed)
pip install -e .

# Run benchmark with default options
aicubench all --prompt "1girl" --nprompt "worst quality" --ar 1024x1024 --it 100 --label "mac128GB"