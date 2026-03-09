"""
Multi-model comparison runner
Based on elena-comparison/run_elena.py
"""
import json
import urllib.request
import urllib.error
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import ModelConfig, BUILTIN_MODELS


@dataclass
class GenerationResult:
    """Result of a single generation"""
    model_id: str
    seed: int
    filename: str
    prompt_id: str
    elapsed_time: float
    success: bool
    error: Optional[str] = None


class ComparisonRunner:
    """Run image generation across multiple models for comparison"""

    def __init__(
        self,
        comfyui_url: str = "http://127.0.0.1:8188",
        workflow_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        self.comfyui_url = comfyui_url.rstrip("/")
        self.workflow_dir = workflow_dir or Path("workflows/api")
        self.output_dir = output_dir or Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def queue_prompt(self, workflow: dict) -> str:
        """Queue a prompt to ComfyUI"""
        data = json.dumps({"prompt": workflow}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.comfyui_url}/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("prompt_id", "")
        except Exception as e:
            print(f"Queue error: {e}")
            return ""

    def get_history(self, prompt_id: str) -> dict:
        """Get execution history for a prompt"""
        try:
            with urllib.request.urlopen(
                f"{self.comfyui_url}/history/{prompt_id}", timeout=10
            ) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return {}

    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> str:
        """Wait for generation to complete and return output filename"""
        start = time.time()
        while time.time() - start < timeout:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        for img in node_output["images"]:
                            return img.get("filename", "")
                return ""
            print(".", end="", flush=True)
            time.sleep(2)
        return ""

    def download_image(self, filename: str, subfolder: str = "") -> bytes:
        """Download a generated image from ComfyUI"""
        params = f"filename={filename}"
        if subfolder:
            params += f"&subfolder={subfolder}"
        url = f"{self.comfyui_url}/view?{params}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read()

    def save_image(self, filename: str, dest_path: Path, subfolder: str = "") -> Path:
        """Download and save an image from ComfyUI to local path"""
        data = self.download_image(filename, subfolder)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(data)
        return dest_path

    def load_workflow(self, model: ModelConfig) -> dict:
        """Load and return workflow for a model"""
        workflow_path = self.workflow_dir / model.workflow_file
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")
        return json.loads(workflow_path.read_text())

    def inject_prompt(
        self,
        workflow: dict,
        model: ModelConfig,
        positive: str,
        negative: str,
        seed: int,
        output_prefix: str,
    ) -> dict:
        """Inject prompt and parameters into workflow"""
        # Find and update nodes by searching for common patterns
        for node_id, node in workflow.items():
            class_type = node.get("class_type", "")
            inputs = node.get("inputs", {})
            meta = node.get("_meta", {})
            title = meta.get("title", "").lower()

            # Positive prompt
            if class_type == "CLIPTextEncode":
                if "positive" in title or node_id == model.prompt_node:
                    inputs["text"] = positive
                elif "negative" in title or node_id == model.negative_node:
                    inputs["text"] = negative

            # Seed
            if class_type in ["KSampler", "SamplerCustomAdvanced"]:
                if "seed" in inputs:
                    inputs["seed"] = seed
                if "noise_seed" in inputs:
                    inputs["noise_seed"] = seed

            # Output prefix
            if class_type == "SaveImage":
                inputs["filename_prefix"] = output_prefix

        return workflow

    def run_single(
        self,
        model: ModelConfig,
        positive: str,
        negative: str = "",
        seed: int = 42,
    ) -> GenerationResult:
        """Run a single generation for one model"""
        start_time = time.time()

        try:
            workflow = self.load_workflow(model)
        except FileNotFoundError as e:
            return GenerationResult(
                model_id=model.id,
                seed=seed,
                filename="",
                prompt_id="",
                elapsed_time=0,
                success=False,
                error=str(e),
            )

        output_prefix = f"{model.id}_{seed:04d}"
        workflow = self.inject_prompt(
            workflow, model, positive, negative, seed, output_prefix
        )

        print(f"\n[{model.name}] Queueing... ", end="", flush=True)
        prompt_id = self.queue_prompt(workflow)

        if not prompt_id:
            return GenerationResult(
                model_id=model.id,
                seed=seed,
                filename="",
                prompt_id="",
                elapsed_time=time.time() - start_time,
                success=False,
                error="Failed to queue prompt",
            )

        print(f"OK ({prompt_id[:8]})")
        print(f"[{model.name}] Generating", end="", flush=True)

        filename = self.wait_for_completion(prompt_id)
        elapsed = time.time() - start_time

        if filename:
            print(f" Done! ({elapsed:.1f}s) -> {filename}")
            return GenerationResult(
                model_id=model.id,
                seed=seed,
                filename=filename,
                prompt_id=prompt_id,
                elapsed_time=elapsed,
                success=True,
            )
        else:
            print(" TIMEOUT or ERROR")
            return GenerationResult(
                model_id=model.id,
                seed=seed,
                filename="",
                prompt_id=prompt_id,
                elapsed_time=elapsed,
                success=False,
                error="Timeout or generation error",
            )

    def run_comparison(
        self,
        model_ids: List[str],
        positive: str,
        negative: str = "",
        seed: int = 42,
        custom_models: Optional[Dict[str, ModelConfig]] = None,
    ) -> List[GenerationResult]:
        """Run comparison across multiple models"""
        models = {**BUILTIN_MODELS, **(custom_models or {})}
        results = []

        print("=" * 60)
        print("Multi-Model Comparison")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Models: {', '.join(model_ids)}")
        print(f"Seed: {seed}")
        print("=" * 60)

        for model_id in model_ids:
            if model_id not in models:
                print(f"\n⚠️  Model not found: {model_id}")
                continue

            model = models[model_id]
            result = self.run_single(model, positive, negative, seed)
            results.append(result)

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        success_count = sum(1 for r in results if r.success)
        print(f"Successful: {success_count}/{len(results)}")

        for r in results:
            status = "✅" if r.success else "❌"
            print(f"  {status} {r.model_id}: {r.filename or r.error}")

        return results

    def save_results(self, results: List[GenerationResult], output_path: Path):
        """Save results to JSON"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "model_id": r.model_id,
                    "seed": r.seed,
                    "filename": r.filename,
                    "elapsed_time": r.elapsed_time,
                    "success": r.success,
                    "error": r.error,
                }
                for r in results
            ],
        }
        output_path.write_text(json.dumps(data, indent=2))
        print(f"\nResults saved to: {output_path}")
