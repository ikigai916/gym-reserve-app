#!/bin/bash

# ジム予約管理システム - 初期化スクリプト
# 新しい技術スタック（FastAPI + HTML + Alpine.js + Tailwind CSS）のセットアップ

set -e  # エラーが発生したら終了

echo "🚀 ジム予約管理システムの初期化を開始します..."

# 1. Bunのインストール確認
echo "📦 Bunの確認..."
if ! command -v bun &> /dev/null; then
    echo "❌ Bunがインストールされていません"
    echo "インストールコマンド: curl -fsSL https://bun.sh/install | bash"
    exit 1
fi
echo "✅ Bun: $(bun --version)"

# 2. Pythonの確認
echo "🐍 Pythonの確認..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3がインストールされていません"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 3. バックエンドのセットアップ
echo "🔧 バックエンド（FastAPI）のセットアップ..."
cd backend

# 仮想環境の作成
if [ ! -d "venv" ]; then
    echo "📦 Python仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境のアクティベート
echo "🔌 仮想環境をアクティベート中..."
source venv/bin/activate

# パッケージのインストール
echo "📥 依存パッケージをインストール中..."
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-dotenv

# ディレクトリ構造の作成
echo "📁 ディレクトリ構造を作成中..."
mkdir -p app/routers
mkdir -p data

# ファイルの作成
touch app/__init__.py
touch app/main.py
touch app/models.py
touch app/schemas.py
touch app/storage.py
touch app/routers/__init__.py
touch app/routers/reservations.py
touch app/routers/users.py

# データファイルの初期化
if [ ! -f "data/reservations.json" ]; then
    echo '[]' > data/reservations.json
fi
if [ ! -f "data/users.json" ]; then
    echo '[]' > data/users.json
fi

# requirements.txtの生成
echo "📝 requirements.txtを生成中..."
pip freeze > requirements.txt

echo "✅ バックエンドのセットアップ完了"

# 4. フロントエンドのセットアップ
cd ../frontend
echo "🎨 フロントエンドのセットアップ..."

# package.jsonの初期化（存在しない場合）
if [ ! -f "package.json" ]; then
    echo "📦 package.jsonを初期化中..."
    bun init -y
fi

# Tailwind CSSのインストール
echo "🎨 Tailwind CSSをインストール中..."
bun add -d tailwindcss @tailwindcss/forms || true

# Tailwind CSS設定ファイルの作成
if [ ! -f "tailwind.config.js" ]; then
    echo "⚙️ Tailwind CSS設定ファイルを作成中..."
    bunx tailwindcss init
fi

# ディレクトリ構造の作成
mkdir -p css js

# Tailwind CSS入力ファイルの作成
if [ ! -f "css/input.css" ]; then
    echo "📝 Tailwind CSS入力ファイルを作成中..."
    cat > css/input.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF
fi

# 初回ビルド
echo "🔨 Tailwind CSSをビルド中..."
bunx tailwindcss -i ./css/input.css -o ./css/style.css --minify || true

echo "✅ フロントエンドのセットアップ完了"

# 5. 完了メッセージ
cd ..
echo ""
echo "✨ セットアップが完了しました！"
echo ""
echo "📋 次のステップ:"
echo "1. バックエンドを起動:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "2. フロントエンドのTailwind CSSをビルド（別ターミナル）:"
echo "   cd frontend && bun run build:css"
echo ""
echo "3. フロントエンドサーバーを起動（別ターミナル）:"
echo "   cd frontend && python3 -m http.server 3000"
echo ""
echo "詳細は SETUP_GUIDE.md を参照してください。"

