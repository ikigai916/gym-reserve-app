# ジム予約管理システム - 最小構成

このディレクトリには、最小構成のファイルセットが含まれています。

## ファイル構成

```
reseve/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py          # FastAPIアプリケーション（/healthエンドポイント）
│   └── requirements.txt     # Python依存パッケージ
├── frontend/
│   └── index.html           # Alpine.jsでHello Worldを表示
├── Dockerfile               # GCP Cloud Run用のDockerfile
└── README_MINIMAL.md        # このファイル
```

## 技術スタック

- **Backend**: Python (FastAPI)
- **Frontend**: HTML + Alpine.js + Tailwind CSS (CDN)
- **Package Manager**: Bun（将来的に使用）

## セットアップ

### 1. バックエンドの起動

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

バックエンドAPI: http://localhost:8000

### 2. フロントエンドの確認

ブラウザで以下にアクセス:
- http://localhost:8000/index.html（FastAPI経由）
- または、`frontend/index.html`を直接開く

### 3. APIエンドポイントの確認

- `GET /` - ルートエンドポイント
- `GET /health` - ヘルスチェックエンドポイント

## Dockerビルドと実行

### ビルド

```bash
docker build -f Dockerfile -t gym-reservation .
```

### 実行

```bash
docker run -p 8000:8000 gym-reservation
```

### 確認

- API: http://localhost:8000/health
- フロントエンド: http://localhost:8000/index.html

## GCP Cloud Runへのデプロイ

詳細は `DEPLOYMENT.md` を参照してください。

基本的な流れ:
1. Artifact RegistryにDockerイメージをプッシュ
2. Cloud Runサービスを作成・デプロイ
3. サービスURLでアクセス

## 次のステップ

この最小構成から、仕様書（specification.md）に基づいて機能を実装していきます。

