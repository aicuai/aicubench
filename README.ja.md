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

### 3. 次回以降の起動方法

以降は以下で仮想環境を有効化：

```bash
source .venv/bin/activate
```

その後、以下のように実行可能です：

```bash
aicubench all --prompt "1girl" --it 10
```