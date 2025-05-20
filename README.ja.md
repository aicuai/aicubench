## 🔧 クイックスタート (macOS)

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
    │   └── v1-5-pruned-emaonly.ckpt
    ├── vae/
    └── ...
```

※ `aicubench/models/` 以下にダウンロードされてしまう場合は、ComfyUI の `models/` フォルダに移動してください。