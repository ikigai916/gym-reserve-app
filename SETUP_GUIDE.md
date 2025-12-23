# セットアップガイド（新しい技術スタック）

このガイドでは、新しい技術スタック（FastAPI + HTML + Alpine.js + Tailwind CSS）での開発環境構築手順を説明します。

## 前提条件

- Python 3.11以上
- Bun（JavaScriptパッケージマネージャー）
- Node.js（Bunのインストールに必要、またはBunがNode.js互換）

---

## ステップ1: Bunのインストール

### macOS / Linux
```bash
curl -fsSL https://bun.sh/install | bash
```

### Windows
```bash
powershell -c "irm bun.sh/install.ps1 | iex"
```

### 確認
```bash
bun --version
```

---

## ステップ2: バックエンド（FastAPI）のセットアップ

### 2-1. バックエンドディレクトリに移動
```bash
cd backend
```

### 2-2. Python仮想環境の作成（推奨）
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2-3. 必要なパッケージのインストール
```bash
pip install fastapi uvicorn[standard] python-dotenv
```

### 2-4. requirements.txtの作成
```bash
pip freeze > requirements.txt
```

または、以下の内容で `requirements.txt` を作成：

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
```

### 2-5. ディレクトリ構造の作成
```bash
mkdir -p app/routers
mkdir -p data
touch app/__init__.py
touch app/main.py
touch app/models.py
touch app/schemas.py
touch app/storage.py
touch app/routers/__init__.py
touch app/routers/reservations.py
touch app/routers/users.py
```

### 2-6. データディレクトリの初期化
```bash
# dataディレクトリに空のJSONファイルを作成
echo '[]' > data/reservations.json
echo '[]' > data/users.json
```

---

## ステップ3: フロントエンドのセットアップ

### 3-1. フロントエンドディレクトリに移動
```bash
cd ../frontend
```

### 3-2. Bunでpackage.jsonを初期化
```bash
bun init -y
```

### 3-3. Tailwind CSSのインストール
```bash
bun add -d tailwindcss
bun add -d @tailwindcss/forms  # フォームスタイリング用（オプション）
```

### 3-4. Tailwind CSS設定ファイルの作成
```bash
bunx tailwindcss init
```

### 3-5. 必要なディレクトリの作成
```bash
mkdir -p css js
touch index.html
touch css/style.css
touch js/app.js
touch js/utils.js
```

### 3-6. package.jsonにビルドスクリプトを追加

`package.json` を編集して以下のスクリプトを追加：

```json
{
  "scripts": {
    "build:css": "tailwindcss -i ./css/input.css -o ./css/style.css --watch",
    "build:css:prod": "tailwindcss -i ./css/input.css -o ./css/style.css --minify"
  }
}
```

### 3-7. Tailwind CSS入力ファイルの作成
```bash
# css/input.css を作成
cat > css/input.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF
```

### 3-8. tailwind.config.jsの設定

`tailwind.config.js` を編集：

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.html", "./js/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## ステップ4: 開発環境の起動

### バックエンドの起動（ターミナル1）
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

バックエンドは http://localhost:8000 で起動します。

### フロントエンドのTailwind CSSビルド（ターミナル2）
```bash
cd frontend
bun run build:css
```

### フロントエンドのサーバー起動（ターミナル3、またはPythonのHTTPサーバー）

#### オプション1: PythonのHTTPサーバー
```bash
cd frontend
python3 -m http.server 3000
```

#### オプション2: Bunのサーバー（開発用）
```bash
cd frontend
bunx serve . -p 3000
```

フロントエンドは http://localhost:3000 でアクセスできます。

---

## ステップ5: 初回のファイル作成

### backend/app/main.py の基本構造
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ジム予約管理システム API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "ジム予約管理システム API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### frontend/index.html の基本構造
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ジム予約管理システム</title>
    <link rel="stylesheet" href="/css/style.css">
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body>
    <div x-data="app()">
        <!-- アプリケーションコンテンツ -->
    </div>
    <script src="/js/utils.js"></script>
    <script src="/js/app.js"></script>
</body>
</html>
```

---

## トラブルシューティング

### Python仮想環境がアクティベートされない
```bash
# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Tailwind CSSがビルドされない
```bash
# Tailwind CSSを再インストール
cd frontend
bun remove tailwindcss
bun add -d tailwindcss
bunx tailwindcss init
```

### FastAPIのCORSエラー
`backend/app/main.py` の `allow_origins` にフロントエンドのURLが含まれているか確認してください。

---

## 次のステップ

1. `backend/app/main.py` を実装
2. `backend/app/routers/` にAPIエンドポイントを実装
3. `frontend/index.html` と `frontend/js/app.js` にフロントエンドロジックを実装
4. 仕様書（specification.md）に基づいて機能を実装

