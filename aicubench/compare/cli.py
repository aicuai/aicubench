"""
CLI interface for multi-model comparison
"""
import argparse
from pathlib import Path

from .runner import ComparisonRunner
from .models import BUILTIN_MODELS
from .grid import create_comparison_grid, create_benchmark_card


def main():
    parser = argparse.ArgumentParser(
        description="Run multi-model image generation comparison"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List models command
    list_parser = subparsers.add_parser("list", help="List available models")

    # Run comparison command
    run_parser = subparsers.add_parser("run", help="Run model comparison")
    run_parser.add_argument(
        "--models",
        "-m",
        type=str,
        required=True,
        help="Comma-separated list of model IDs (e.g., sdxl,animagine,flux1-schnell)",
    )
    run_parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Positive prompt text",
    )
    run_parser.add_argument(
        "--prompt-file",
        type=str,
        help="Path to prompt file",
    )
    run_parser.add_argument(
        "--negative",
        "-n",
        type=str,
        default="",
        help="Negative prompt text",
    )
    run_parser.add_argument(
        "--negative-file",
        type=str,
        help="Path to negative prompt file",
    )
    run_parser.add_argument(
        "--seed",
        "-s",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    run_parser.add_argument(
        "--url",
        type=str,
        default="http://127.0.0.1:8188",
        help="ComfyUI URL (default: http://127.0.0.1:8188)",
    )
    run_parser.add_argument(
        "--workflow-dir",
        type=str,
        default="workflows/api",
        help="Workflow directory (default: workflows/api)",
    )
    run_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output",
        help="Output directory (default: output)",
    )

    # Grid command
    grid_parser = subparsers.add_parser("grid", help="Create comparison grid image")
    grid_parser.add_argument(
        "input_dir",
        type=str,
        help="Directory containing generated images",
    )
    grid_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="comparison_grid.png",
        help="Output filename",
    )
    grid_parser.add_argument(
        "--cols",
        type=int,
        default=4,
        help="Number of columns (default: 4)",
    )
    grid_parser.add_argument(
        "--no-labels",
        action="store_true",
        help="Hide model labels",
    )

    args = parser.parse_args()

    if args.command == "list":
        print("Available models:")
        print("-" * 60)
        for model_id, model in BUILTIN_MODELS.items():
            print(f"  {model_id:20s} - {model.name}")
            print(f"  {'':20s}   Steps: {model.steps}, CFG: {model.cfg}")
            if model.license:
                print(f"  {'':20s}   License: {model.license}")
            print()

    elif args.command == "run":
        # Load prompts
        if args.prompt_file:
            positive = Path(args.prompt_file).read_text().strip()
        elif args.prompt:
            positive = args.prompt
        else:
            print("Error: --prompt or --prompt-file required")
            return 1

        if args.negative_file:
            negative = Path(args.negative_file).read_text().strip()
        else:
            negative = args.negative

        # Parse model IDs
        model_ids = [m.strip() for m in args.models.split(",")]

        # Run comparison
        runner = ComparisonRunner(
            comfyui_url=args.url,
            workflow_dir=Path(args.workflow_dir),
            output_dir=Path(args.output),
        )

        results = runner.run_comparison(
            model_ids=model_ids,
            positive=positive,
            negative=negative,
            seed=args.seed,
        )

        # Save results JSON
        output_path = Path(args.output) / "results.json"
        runner.save_results(results, output_path)

        # Download images and create benchmark card
        card_data = []
        images_dir = Path(args.output) / "images"
        for r in results:
            if r.success and r.filename:
                try:
                    local_path = images_dir / f"{r.model_id}_{r.seed}.png"
                    runner.save_image(r.filename, local_path)
                    model = BUILTIN_MODELS.get(r.model_id)
                    card_data.append({
                        "model_id": r.model_id,
                        "model_name": model.name if model else r.model_id,
                        "filename": r.filename,
                        "elapsed_time": r.elapsed_time,
                        "success": r.success,
                        "local_path": str(local_path),
                    })
                    print(f"Downloaded: {r.filename} -> {local_path}")
                except Exception as e:
                    print(f"Failed to download {r.filename}: {e}")

        if card_data:
            card_path = Path(args.output) / "benchmark_card.png"
            create_benchmark_card(
                results=card_data,
                image_dir=images_dir,
                output_path=card_path,
                prompt=positive,
                seed=args.seed,
            )

    elif args.command == "grid":
        # TODO: Implement grid from directory
        print("Grid command not fully implemented yet")
        return 1

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    exit(main())
