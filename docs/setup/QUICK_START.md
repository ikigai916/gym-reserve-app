# クイックスタートガイド

## セットアップ方法

### 方法1: 自動セットアップスクリプト（推奨）

```bash
./INIT_COMMANDS.sh
```

### 方法2: 手動セットアップ

詳細な手順は `SETUP_GUIDE.md` を参照してください。

---

## セットアップ後の起動方法

### 1. バックエンド（FastAPI）の起動

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

バックエンドAPI: http://localhost:8000

### 2. フロントエンドのTailwind CSSビルド（別ターミナル）

```bash
cd frontend
bun run build:css
```

このコマンドは `--watch` モードで実行され、ファイル変更を監視します。

### 3. フロントエンドサーバーの起動（別ターミナル）

```bash
cd frontend
python3 -m http.server 3000
```

フロントエンド: http://localhost:3000

---

## 開発時のワークフロー

1. **バックエンドの変更**: `uvicorn` の `--reload` オプションにより自動リロードされます
2. **フロントエンドHTML/JSの変更**: ブラウザをリロード
3. **Tailwind CSSクラスの変更**: `build:css` が自動で検知して再ビルド

---

## 主要コマンド一覧

### バックエンド

```bash
# 仮想環境のアクティベート
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# サーバー起動
uvicorn app.main:app --reload
```

### フロントエンド

```bash
# Tailwind CSSの開発用ビルド（ウォッチモード）
bun run build:css

# Tailwind CSSの本番用ビルド
bun run build:css:prod
```

---

## ディレクトリ構造の概要

```
backend/
  app/
    main.py          # FastAPIアプリケーション
    models.py        # データモデル
    schemas.py       # Pydanticスキーマ
    storage.py       # データ永続化
    routers/         # APIルーター
  data/              # JSONデータファイル

frontend/
  index.html         # メインHTML
  css/
    input.css        # Tailwind CSS入力
    style.css        # ビルド後のCSS
  js/
    app.js           # Alpine.jsアプリケーション
    utils.js         # ユーティリティ
```

