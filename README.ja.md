# AICU Bench 

| [English](README.md) | [日本語](README.ja.md) |

---
# これは何？

ComfyUIをはじめとする画像生成AIの環境を評価するためのデータを取得するベンチマークです。

本ベンチマークツールは、SD1.5モデルによる画像生成、およびGoogle Spreadsheetへの匿名ログ送信を行います。

**💡 データは匿名で送信・集計されます。**

## 🔧 クイックスタート (macOS)

M4 Macで開発していますが、WindowsやLinuxでも動くように設計はしています。

### 1. リポジトリをクローン

```bash
git clone https://github.com/yourname/aicubench.git
cd aicubench
```

### 2. セットアップスクリプトの実行

以下を実行することで:
- 仮想環境（`.venv`）の作成
- 有効化
- `aicubench` の編集可能モードでのインストール
- サンプルベンチマークの実行

```bash
bash scripts/setup.sh
```

### ⚠️ モデルのダウンロードについて

ComfyUI で利用する推奨モデルは `ComfyUI/models/` 以下に配置されます。
自動ダウンロード中に `wget: command not found` エラーが出る場合は `wget` をインストールするか、別途モデルを手動で配置してください。

推奨モデルの一覧は [Book-SD-MasterGuide/basemodels.txt](https://github.com/aicuai/Book-SD-MasterGuide/blob/main/basemodels.txt) に記載されています。

ダウンロードを中止したい場合は、`Ctrl+C` で強制終了できます。

### 3. 次回以降の起動方法

以降は以下で仮想環境を有効化：

```bash
source .venv/bin/activate
```

その後、以下のように実行可能です：

```bash
aicubench all --prompt "1girl" --it 10
```

### 📁 ダウンロードされたモデルの保存場所について

初期状態では ComfyUI のモデルは以下のように配置されます：

```
ComfyUI/
└── models/
    ├── checkpoints/
    │   └── v1-5-pruned-emaonly-fp16.safetensors
    ├── vae/
    └── ...
```

--nodelete オプションをつけて起動すると、ダウンロードしたファイルを残します。デフォルトではArtifactsに生成物やログを残す以外、ComfyUIディレクトリ以下は全て削除します。