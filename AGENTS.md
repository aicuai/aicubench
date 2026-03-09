# AGENTS.md - aicubench

このドキュメントはAIエージェント（Claude Code等）がaicubenchリポジトリで作業する際のガイドラインです。

## プロジェクト概要

aicubenchは、ComfyUI APIを活用した画像生成AIのベンチマーク・比較検証ツールです。

**主な機能:**
- ComfyUI環境の自動セットアップ
- 複数モデルの一括比較実行
- パラメータ探索（シード、Steps、CFG）
- 結果のJSON/グリッド画像出力
- Google Sheetsへの匿名ベンチマーク送信

## ディレクトリ構成

```
aicubench/
├── aicubench/              # メインパッケージ
│   ├── __init__.py
│   ├── main.py             # 基本ベンチマーク実行
│   └── compare/            # マルチモデル比較モジュール
│       ├── __init__.py
│       ├── models.py       # モデル定義
│       ├── runner.py       # 実行エンジン
│       ├── grid.py         # グリッド画像生成
│       └── cli.py          # CLI
├── benchmarks/             # ベンチマーク定義
│   ├── system_info.py
│   ├── utils.py
│   └── image.py
├── models/
│   └── configs/            # カスタムモデルYAML
├── prompts/                # プロンプトファイル
├── scripts/                # セットアップ・ユーティリティ
├── workflows/              # ComfyUI APIワークフロー
│   └── api/                # API形式JSON
├── Artifacts/              # 実行結果・ログ
├── HowToUse.md             # 日本語使い方ガイド
├── README.md               # English README
├── README.ja.md            # 日本語README
└── pyproject.toml          # パッケージ設定
```

## 開発ガイドライン

### コーディング規約

- Python 3.8+ 互換
- 型ヒントを推奨
- docstringは日本語または英語
- 依存関係は `pyproject.toml` で管理

### 新しいモデルの追加

1. `aicubench/compare/models.py` の `BUILTIN_MODELS` に定義を追加
2. または `models/configs/` にYAMLファイルを作成
3. 対応するAPI形式ワークフローを `workflows/api/` に配置

```python
# models.py への追加例
"new-model": ModelConfig(
    id="new-model",
    name="New Model Name",
    workflow_file="new_model_api.json",
    checkpoint="new_model.safetensors",
    steps=20,
    cfg=7.0,
    sampler="euler",
    scheduler="normal",
    width=1024,
    height=1024,
)
```

### ワークフローの作成

1. ComfyUIで「Enable Dev mode」を有効化
2. ワークフローを構築
3. 「Save (API Format)」で保存
4. 必要なノードID:
   - プロンプト注入用: `CLIPTextEncode` ノード
   - シード注入用: `KSampler` または同等ノード
   - 出力: `SaveImage` ノード

### テスト

```bash
# インストール
pip install -e .

# 基本テスト（ComfyUI起動中）
aicubench-compare list

# 比較実行テスト
aicubench-compare run --models sdxl --prompt "test" --seed 42
```

## ComfyUI API連携

### エンドポイント

- `POST /prompt` - ジョブキューイング
- `GET /history/{prompt_id}` - 実行結果取得
- `GET /` - サーバー状態確認

### デフォルトURL

- ローカル: `http://127.0.0.1:8188`
- ComfyUI Desktop (Mac): `http://127.0.0.1:8000`

## 注意事項

### モデルファイル

- 大容量モデル（数GB）はgit管理外
- HuggingFaceやCivitaiからのダウンロードが必要
- ライセンスを確認すること（商用利用可否）

### 破壊的操作の禁止

- `Artifacts/` 内の既存結果を上書きしない
- `scripts/clean.sh` は慎重に使用

### ライセンス

Apache License 2.0

## 関連リンク

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI API Docs](https://docs.comfy.org/)
- [Elena Bloom比較実験](https://github.com/aicuai/AiCuty)
