#!/bin/bash

# activate Python environment if needed
# source venv/bin/activate

# Install dependencies
pip install -e .

# Run benchmark with default options
aicubench all --prompt "1girl" --nprompt "worst quality" --ar 1024x1024 --it 100 --label "mac128GB"