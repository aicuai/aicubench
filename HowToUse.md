# aicubench 使い方ガイド

aicubenchは、ComfyUIを活用した画像生成AIのベンチマーク・比較検証ツールです。
複数モデルの一括比較、パラメータ探索、結果レポートの自動化を実現します。

## 動作環境

- **macOS** (Apple Silicon / Intel) — Homebrew Python推奨
- **Windows 10/11** — Python公式インストーラー推奨
- **Python 3.8以上**
- **ComfyUI** が起動していること（CLI版 or Desktop版）

---

## クイックスタート（macOS）

### 1. インストール

macOS（Homebrew Python）ではシステムPythonへの直接インストールが制限されているため、仮想環境（venv）を使用します。

```bash
git clone https://github.com/aicuai/aicubench.git
cd aicubench
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

> **注意:** `pip install -e .` で `externally-managed-environment` エラーが出る場合は、`source .venv/bin/activate` で仮想環境が有効になっているか確認してください。シェルのプロンプトに `(.venv)` が表示されていればOKです。

以降、ターミナルを開き直した場合は毎回以下を実行してください：

```bash
cd aicubench
source .venv/bin/activate
```

### 2. ComfyUIの準備

aicubenchはComfyUI APIを利用します。ComfyUIが起動している必要があります。

**ComfyUI CLI版の場合：**

```bash
# ComfyUIを起動（デフォルト: http://127.0.0.1:8188）
cd /path/to/ComfyUI
python main.py
```

**ComfyUI Desktop（Mac版）の場合：**

ComfyUI Desktopアプリを起動するだけでOKです。デフォルトのAPIエンドポイントは `http://127.0.0.1:8000` です。

```bash
# Desktop版を使う場合は --url オプションでポートを指定
aicubench-compare run --models sdxl --prompt "test" --seed 42 --url http://127.0.0.1:8000
```

### 3. 基本的な使い方

```bash
# ベンチマーク実行
aicubench all --prompt "1girl" --it 10
```

---

## クイックスタート（Windows）

### 1. Pythonのインストール

[python.org](https://www.python.org/downloads/) から Python 3.8以上をダウンロード・インストールしてください。

> **重要:** インストール時に「**Add Python to PATH**」にチェックを入れてください。

### 2. インストール

コマンドプロンプト（cmd）または PowerShell で実行します。

**コマンドプロンプト (cmd) の場合：**

```cmd
git clone https://github.com/aicuai/aicubench.git
cd aicubench
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

**PowerShell の場合：**

```powershell
git clone https://github.com/aicuai/aicubench.git
cd aicubench
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

> **PowerShellでエラーが出る場合：** スクリプト実行ポリシーの制限により `Activate.ps1` が実行できないことがあります。その場合は管理者権限のPowerShellで `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` を実行してください。

以降、ターミナルを開き直した場合は毎回以下を実行してください：

```cmd
cd aicubench
.venv\Scripts\activate
```

### 3. ComfyUIの準備

**ComfyUI CLI版の場合：**

```cmd
cd \path\to\ComfyUI
python main.py
```

**ComfyUI Desktop（Windows版）の場合：**

ComfyUI Desktopアプリを起動するだけでOKです。デフォルトのAPIエンドポイントは `http://127.0.0.1:8188` です。

### 4. 基本的な使い方

```cmd
aicubench all --prompt "1girl" --it 10
```

---

## マルチモデル比較機能 (aicubench-compare)

Elena Bloom比較実験で使用した、複数モデルを同一プロンプトで一括比較する機能です。

### 利用可能なモデル一覧

```bash
aicubench-compare list
```

**ビルトインモデル:**

| ID | モデル名 | 特徴 |
|----|----------|------|
| `sdxl` | SDXL Base 1.0 | Stable Diffusion XL元祖 |
| `animagine` | ANIMAGINE XL 4.0 | アニメ特化SDXL |
| `flux1-schnell` | FLUX.1 Schnell | 高速4ステップ生成 (Apache 2.0) |
| `wai-illustrious` | WAI-illustrious + LoRA | Illustriousベース + 目強化LoRA |
| `z-image-turbo` | Z-Image-Turbo | Comfy-Org公式高速モデル |

### 比較実行

```bash
# 複数モデルで比較生成
aicubench-compare run \
    --models sdxl,animagine,flux1-schnell \
    --prompt "a beautiful anime girl with pink twin tails" \
    --seed 42

# プロンプトファイルを使用
aicubench-compare run \
    --models sdxl,animagine,flux1-schnell,wai-illustrious \
    --prompt-file prompts/elena-base.txt \
    --negative-file prompts/elena-negative.txt \
    --seed 42 \
    --output results/elena-comparison/
```

### パラメータ

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--models`, `-m` | カンマ区切りのモデルIDリスト | 必須 |
| `--prompt`, `-p` | ポジティブプロンプト | - |
| `--prompt-file` | プロンプトファイルパス | - |
| `--negative`, `-n` | ネガティブプロンプト | 空文字 |
| `--negative-file` | ネガティブプロンプトファイルパス | - |
| `--seed`, `-s` | ランダムシード | 42 |
| `--url` | ComfyUI URL | http://127.0.0.1:8188 |
| `--workflow-dir` | ワークフローJSONディレクトリ | workflows/api |
| `--output`, `-o` | 出力ディレクトリ | output |

### 比較グリッド画像の生成

```bash
aicubench-compare grid results/elena-comparison/ \
    --output comparison_grid.png \
    --cols 4
```

---

## ワークフローの準備

### API形式JSONの作成

1. ComfyUIで「設定」→「Enable Dev mode」を有効化
2. ワークフローを構築
3. 「Save (API Format)」で保存
4. `workflows/api/` ディレクトリに配置

### ワークフローの命名規則

```
workflows/api/
├── sdxl_api.json
├── animagine_api.json
├── flux1_schnell_api.json
├── wai_api.json
└── z_image_turbo_api.json
```

---

## カスタムモデルの追加

### YAMLでモデル定義

`models/configs/` にYAMLファイルを作成:

```yaml
# models/configs/my_custom_model.yaml
id: my-model
name: My Custom Model
workflow_file: my_model_api.json
checkpoint: my_model.safetensors

steps: 25
cfg: 7.0
sampler: euler
scheduler: normal
width: 1024
height: 1024

source_url: https://example.com/my-model
license: MIT
notes: My custom fine-tuned model
```

### Pythonで直接定義

```python
from aicubench.compare import ComparisonRunner, ModelConfig

custom_model = ModelConfig(
    id="my-model",
    name="My Custom Model",
    workflow_file="my_model_api.json",
    checkpoint="my_model.safetensors",
    steps=25,
    cfg=7.0,
)

runner = ComparisonRunner()
results = runner.run_comparison(
    model_ids=["sdxl", "my-model"],
    positive="your prompt here",
    seed=42,
    custom_models={"my-model": custom_model},
)
```

---

## プロンプトファイルの例

### prompts/elena-base.txt

```
masterpiece, best quality, solo, full body, sweet and gentle anime idol girl,
fluffy twin tails tied high with big pastel pink ribbons,
big bright sparkling pink eyes, highly detailed eyes,
wearing a goddess-inspired idol stage outfit in pastel pink and white,
white background, simple background
```

### prompts/elena-negative.txt

```
low quality, worst quality, bad anatomy, poorly drawn face,
deformed eyes, extra limbs, cropped, blurry,
watermark, text, nsfw
```

---

## 実行例

### シード探索（同一モデル、複数シード）

```python
from aicubench.compare import ComparisonRunner, BUILTIN_MODELS

runner = ComparisonRunner()

seeds = [42, 123, 456, 789, 1024]
model = BUILTIN_MODELS["animagine"]

for seed in seeds:
    result = runner.run_single(
        model=model,
        positive="your prompt",
        negative="",
        seed=seed,
    )
    print(f"Seed {seed}: {result.filename}")
```

### パラメータ探索（Steps/CFG変更）

```python
import copy
from aicubench.compare import ComparisonRunner, BUILTIN_MODELS

runner = ComparisonRunner()
base_model = BUILTIN_MODELS["flux1-schnell"]

# Steps探索
for steps in [4, 8, 12, 16, 20]:
    model = copy.copy(base_model)
    model.steps = steps
    result = runner.run_single(model, "your prompt", seed=42)
    print(f"Steps {steps}: {result.filename}")
```

---

## トラブルシューティング

### 仮想環境が有効になっていない

```
command not found: aicubench
```

→ 仮想環境を有効化してください。

- **macOS/Linux:** `source .venv/bin/activate`
- **Windows (cmd):** `.venv\Scripts\activate`
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`

プロンプトに `(.venv)` が表示されていれば有効化済みです。

### ComfyUIに接続できない

```
Queue error: [Errno 61] Connection refused       # macOS/Linux
Queue error: [WinError 10061] 接続が拒否されました  # Windows
```

→ ComfyUIが起動しているか確認してください。デフォルトポートは8188です（ComfyUI Desktop Macは8000）。

### ワークフローが見つからない

```
Workflow not found: workflows/api/xxx_api.json
```

→ `--workflow-dir` オプションでワークフローディレクトリを指定するか、ファイルを正しい場所に配置してください。

### モデルが見つからない

```
Model not found: xxx
```

→ `aicubench-compare list` でビルトインモデルを確認するか、カスタムモデルを定義してください。

---

## 関連リンク

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI API Documentation](https://docs.comfy.org/)
- [Elena Bloom 8モデル比較実験](https://comfyjapan.com/elena-comparison)
- [AiCuty Project](https://github.com/aicuai/AiCuty)

---

## ライセンス

Apache License 2.0
