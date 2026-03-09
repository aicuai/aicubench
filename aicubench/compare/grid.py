"""
Comparison grid image generator
Based on elena-comparison/combine_images.py
"""
import platform
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None


def get_font(size: int):
    """Get a font, with fallback to default"""
    if ImageFont is None:
        return None

    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    return ImageFont.load_default()


def get_environment_info() -> str:
    """Get current environment info as a single-line string"""
    import psutil
    system = platform.system()
    machine = platform.machine()
    node = platform.node()
    ram_gb = psutil.virtual_memory().total / (1024 ** 3)

    if system == "Darwin":
        os_label = f"macOS {platform.mac_ver()[0]}"
    elif system == "Windows":
        os_label = f"Windows {platform.version()}"
    else:
        os_label = f"{system} {platform.release()}"

    return f"{os_label} / {machine} / RAM {ram_gb:.0f}GB / {node}"


def create_comparison_grid(
    images: List[Tuple[str, str, Path]],  # List of (id, name, path)
    output_path: Path,
    cell_width: int = 512,
    cell_height: int = 768,
    label_height: int = 40,
    cols: int = 4,
    show_labels: bool = True,
    bg_color: str = "#FFFFFF",
    label_bg_color: str = "#333333",
    label_text_color: str = "#FFFFFF",
) -> bool:
    """Create a comparison grid from multiple images"""
    if Image is None:
        print("Error: Pillow is required. Install with: pip install Pillow")
        return False

    rows = (len(images) + cols - 1) // cols

    # Canvas size
    total_width = cell_width * cols
    total_height = (cell_height + (label_height if show_labels else 0)) * rows

    # Create canvas
    canvas = Image.new("RGB", (total_width, total_height), bg_color)
    draw = ImageDraw.Draw(canvas)
    font = get_font(24)

    for idx, (model_id, model_name, img_path) in enumerate(images):
        col = idx % cols
        row = idx // cols

        # Position calculation
        x = col * cell_width
        y = row * (cell_height + (label_height if show_labels else 0))

        # Load image
        if not img_path.exists():
            print(f"Warning: {img_path} not found, skipping")
            continue

        img = Image.open(img_path)

        # Resize maintaining aspect ratio
        img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)

        # Center offset
        offset_x = (cell_width - img.width) // 2
        offset_y = (cell_height - img.height) // 2

        # Paste image
        canvas.paste(img, (x + offset_x, y + offset_y))

        # Draw label
        if show_labels:
            label_y = y + cell_height
            # Label background
            draw.rectangle(
                [x, label_y, x + cell_width, label_y + label_height],
                fill=label_bg_color,
            )
            # Text
            label_text = f"{model_id}. {model_name}"
            bbox = draw.textbbox((0, 0), label_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (cell_width - text_width) // 2
            text_y = label_y + (label_height - (bbox[3] - bbox[1])) // 2
            draw.text((text_x, text_y), label_text, fill=label_text_color, font=font)

        print(f"Added: {model_id}. {model_name}")

    # Save
    canvas.save(output_path, "PNG", optimize=True)
    print(f"\nSaved: {output_path}")
    print(f"Size: {total_width}x{total_height}")
    return True


def create_benchmark_card(
    results: List[Dict[str, Any]],
    image_dir: Path,
    output_path: Path,
    prompt: str = "",
    seed: int = 42,
    cell_width: int = 512,
    cell_height: int = 768,
    cols: int = 0,
) -> bool:
    """Create a benchmark result card with images, model info, times, and environment.

    results: list of dicts with keys: model_id, model_name, filename, elapsed_time, success, local_path
    """
    if Image is None:
        print("Error: Pillow is required. Install with: pip install Pillow")
        return False

    # Filter to successful results with images
    valid = [r for r in results if r.get("success") and r.get("local_path")]
    if not valid:
        print("No successful results to combine.")
        return False

    # Auto cols: all in one row if <= 5, otherwise 4
    if cols <= 0:
        cols = len(valid) if len(valid) <= 5 else 4
    rows = (len(valid) + cols - 1) // cols

    # Layout sizes
    padding = 20
    header_height = 100
    label_height = 60
    footer_height = 80

    grid_width = cell_width * cols
    grid_height = (cell_height + label_height) * rows
    total_width = grid_width + padding * 2
    total_height = header_height + grid_height + footer_height + padding * 2

    # Fonts
    font_title = get_font(28)
    font_info = get_font(18)
    font_label = get_font(20)
    font_time = get_font(16)
    font_footer = get_font(14)

    # Create canvas
    canvas = Image.new("RGB", (total_width, total_height), "#1a1a2e")
    draw = ImageDraw.Draw(canvas)

    # === Header ===
    env_info = get_environment_info()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    draw.text(
        (padding, padding),
        "aicubench - Model Comparison",
        fill="#e94560",
        font=font_title,
    )
    draw.text(
        (padding, padding + 36),
        f"{env_info}  |  {timestamp}  |  Seed: {seed}",
        fill="#aaaaaa",
        font=font_info,
    )
    # Separator line
    draw.line(
        [(padding, header_height - 4), (total_width - padding, header_height - 4)],
        fill="#333355",
        width=2,
    )

    # === Image grid ===
    grid_y_start = header_height

    for idx, r in enumerate(valid):
        col = idx % cols
        row = idx // cols

        x = padding + col * cell_width
        y = grid_y_start + row * (cell_height + label_height)

        # Load image
        img_path = Path(r["local_path"])
        if not img_path.exists():
            continue

        img = Image.open(img_path)
        img.thumbnail((cell_width - 8, cell_height - 8), Image.Resampling.LANCZOS)

        # Center
        offset_x = (cell_width - img.width) // 2
        offset_y = (cell_height - img.height) // 2
        canvas.paste(img, (x + offset_x, y + offset_y))

        # Label background
        label_y = y + cell_height
        draw.rectangle(
            [x, label_y, x + cell_width, label_y + label_height],
            fill="#16213e",
        )

        # Model name
        model_name = r.get("model_name", r["model_id"])
        draw.text(
            (x + 8, label_y + 4),
            model_name,
            fill="#e94560",
            font=font_label,
        )

        # Elapsed time
        elapsed = r.get("elapsed_time", 0)
        time_text = f"{elapsed:.1f}s"
        bbox = draw.textbbox((0, 0), time_text, font=font_time)
        time_w = bbox[2] - bbox[0]
        draw.text(
            (x + cell_width - time_w - 8, label_y + 6),
            time_text,
            fill="#00ff88",
            font=font_time,
        )

        # Model ID
        draw.text(
            (x + 8, label_y + 32),
            r["model_id"],
            fill="#888888",
            font=font_time,
        )

    # === Footer ===
    footer_y = grid_y_start + grid_height + 8
    draw.line(
        [(padding, footer_y), (total_width - padding, footer_y)],
        fill="#333355",
        width=2,
    )

    if prompt:
        # Truncate long prompts
        display_prompt = prompt if len(prompt) <= 120 else prompt[:117] + "..."
        draw.text(
            (padding, footer_y + 8),
            f"Prompt: {display_prompt}",
            fill="#888888",
            font=font_footer,
        )

    total_time = sum(r.get("elapsed_time", 0) for r in valid)
    summary = f"{len(valid)} models  |  Total: {total_time:.1f}s  |  github.com/aicuai/aicubench"
    bbox = draw.textbbox((0, 0), summary, font=font_footer)
    summary_w = bbox[2] - bbox[0]
    draw.text(
        (total_width - padding - summary_w, footer_y + 8),
        summary,
        fill="#666666",
        font=font_footer,
    )

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG", optimize=True)
    print(f"\nBenchmark card saved: {output_path}")
    print(f"Size: {total_width}x{total_height}")
    return True
