# GitHub CLI インストール手順

## 方法1: Homebrewを使用（推奨）

### ステップ1: Homebrewのインストール（まだインストールしていない場合）

ターミナルで以下を実行：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

インストール中にパスワードの入力が求められる場合があります。

### ステップ2: PATHの設定（必要に応じて）

Homebrewのインストール後に、ターミナルに表示される指示に従ってPATHを設定してください。

通常は以下のようなコマンドが表示されます：
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### ステップ3: GitHub CLIのインストール

```bash
brew install gh
```

### ステップ4: GitHub CLIの認証

```bash
gh auth login
```

認証方法を選択します：
- GitHub.com を選択
- HTTPS または SSH を選択（通常はHTTPS推奨）
- 認証方法を選択：
  - **GitHub.com** を選択（ブラウザで認証する方法が簡単）
  - 認証コードをコピーしてブラウザで認証

---

## 方法2: 直接ダウンロード（Homebrewを使わない場合）

### macOSの場合

1. [GitHub CLIのリリースページ](https://github.com/cli/cli/releases)から最新のmacOS用バイナリをダウンロード
2. ダウンロードした`.pkg`ファイルを実行してインストール
3. ターミナルで認証：
   ```bash
   gh auth login
   ```

---

## インストール後の確認

インストールが完了したら、以下でバージョンを確認：

```bash
gh --version
```

認証が完了したら、以下でリポジトリ情報を確認：

```bash
gh repo view
```

---

## Issueの作成

インストールと認証が完了したら、以下でIssueを作成できます：

```bash
cd /Users/tmk916u/reseve
gh issue create --title "ネットワーク接続ができない" --body "$(cat ISSUE_TEMPLATE_NETWORK.md)"
```

または、Claude Codeのカスタムコマンドを使用：

```
/github:issue-from-request "ネットワーク接続ができない 画面実装"
```


