#!/bin/bash

echo "🧼 Cleaning up aicubench environment..."

# Delete ComfyUI directory
if [ -d "ComfyUI" ]; then
  echo "🗑 Deleting ComfyUI directory..."
  rm -rf ComfyUI
else
  echo "✅ No ComfyUI directory to delete."
fi

# Delete models directory inside ComfyUI if it exists
if [ -d "ComfyUI/models" ]; then
  echo "🗑 Deleting models directory inside ComfyUI..."
  rm -rf ComfyUI/models
else
  echo "✅ No models directory inside ComfyUI to delete."
fi

# Delete temporary output if defined
if [ -d "output" ]; then
  echo "🗑 Deleting output directory..."
  rm -rf output
fi

echo "✅ Cleanup complete."