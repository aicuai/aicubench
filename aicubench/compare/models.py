"""
Model configuration for multi-model comparison
"""
import json
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class ModelConfig:
    """Configuration for a single model"""
    id: str
    name: str
    workflow_file: str
    checkpoint: Optional[str] = None
    loras: List[Dict[str, Any]] = field(default_factory=list)

    # Sampling parameters
    steps: int = 20
    cfg: float = 7.0
    sampler: str = "euler"
    scheduler: str = "normal"

    # Image settings
    width: int = 1024
    height: int = 1024

    # Node mappings for dynamic injection
    prompt_node: str = "positive"
    negative_node: str = "negative"
    seed_node: str = "sampler"
    output_prefix: str = ""

    # Metadata
    source_url: Optional[str] = None
    license: Optional[str] = None
    notes: Optional[str] = None


def load_model_config(path: Path) -> ModelConfig:
    """Load model configuration from YAML file"""
    with open(path) as f:
        data = yaml.safe_load(f)
    return ModelConfig(**data)


def load_all_models(config_dir: Path) -> Dict[str, ModelConfig]:
    """Load all model configurations from a directory"""
    models = {}
    for path in config_dir.glob("*.yaml"):
        config = load_model_config(path)
        models[config.id] = config
    return models


# Built-in model configurations
BUILTIN_MODELS = {
    "sdxl": ModelConfig(
        id="sdxl",
        name="SDXL Base 1.0",
        workflow_file="00_sdxl_api.json",
        checkpoint="sd_xl_base_1.0.safetensors",
        steps=28,
        cfg=7.0,
        sampler="dpmpp_2m_sde",
        scheduler="karras",
        width=832,
        height=1216,
        source_url="https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0",
        license="CreativeML Open RAIL++-M",
    ),
    "animagine": ModelConfig(
        id="animagine",
        name="ANIMAGINE XL 4.0",
        workflow_file="03_animagine_api.json",
        checkpoint="animagine-xl-4.0-opt.safetensors",
        steps=28,
        cfg=5.0,
        sampler="euler",
        scheduler="normal",
        width=832,
        height=1216,
        source_url="https://huggingface.co/cagliostrolab/animagine-xl-4.0",
        license="Fair AI Public License 1.0-SD",
    ),
    "flux1-schnell": ModelConfig(
        id="flux1-schnell",
        name="FLUX.1 Schnell",
        workflow_file="04_flux_api.json",
        checkpoint="flux1-schnell-fp8.safetensors",
        steps=4,
        cfg=1.0,
        sampler="euler",
        scheduler="simple",
        width=768,
        height=1152,
        source_url="https://huggingface.co/black-forest-labs/FLUX.1-schnell",
        license="Apache 2.0",
        notes="Distilled model, 4 steps recommended. CFG=1 means no negative prompt.",
    ),
    "wai-illustrious": ModelConfig(
        id="wai-illustrious",
        name="WAI-illustrious + LoRA",
        workflow_file="05_wai_api.json",
        checkpoint="waiNSFWIllustrious_v140.safetensors",
        loras=[
            {"name": "Niji_anime_illustrious_SDXL.safetensors", "strength": 1.0},
            {"name": "EnchantingEyes_illustriousXL_v10.safetensors", "strength": 0.7},
        ],
        steps=28,
        cfg=7.0,
        width=832,
        height=1216,
        source_url="https://civitai.com/models/827184/wai-nsfw-illustrious",
    ),
    "mellow-pencil": ModelConfig(
        id="mellow-pencil",
        name="Mellow Pencil XL",
        workflow_file="06_mellow_pencil_api.json",
        checkpoint="mellow_pencil-XL-v1.0.0.safetensors",
        steps=28,
        cfg=7.0,
        sampler="dpmpp_2m_sde",
        scheduler="karras",
        width=832,
        height=1216,
        source_url="https://civitai.com/models/456141/mellow-pencil-xl",
        license="CreativeML Open RAIL++-M",
        notes="Pencil sketch style SDXL model",
    ),
    "z-image-turbo": ModelConfig(
        id="z-image-turbo",
        name="Z-Image-Turbo",
        workflow_file="07_z_image_turbo_api.json",
        checkpoint="z_image_turbo_bf16.safetensors",
        steps=4,
        cfg=1.0,
        sampler="res_multistep",
        scheduler="simple",
        width=832,
        height=1216,
        source_url="https://huggingface.co/Comfy-Org/z_image_turbo",
        notes="Uses Qwen 3 4B text encoder. CFG=1 recommended.",
    ),
}
