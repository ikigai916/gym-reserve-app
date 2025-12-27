# ジム予約管理システム (FastAPI + Firestore)

ジムの時間枠を予約・管理するためのWebアプリケーションです。本プロジェクトは、Google Cloud Run へのデプロイを想定した FastAPI バックエンドと、Firestore を使用したデータ永続化を備えています。

## 機能

- 予約可能な時間枠の表示
- 予約の作成（名前、日付、時間枠）
- 予約一覧の確認
- 予約のキャンセル
- Firestore によるリアルタイムデータ管理

## 技術スタック

- **バックエンド**: Python 3.11 + FastAPI
- **データベース**: Google Cloud Firestore
- **サーバー**: Uvicorn
- **フロントエンド**: HTML/JavaScript (app/static 配下に配置)
- **インフラ**: Google Cloud Run (Docker)

## セットアップ

### 1. 依存関係のインストール

ローカルで実行する場合は、仮想環境を作成してインストールすることを推奨します。

```bash
python -m venv venv
source venv/bin/bin/activate  # Windowsの場合は venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Google Cloud 認証設定

Firestore を使用するため、Google Cloud の認証情報が必要です。

```bash
gcloud auth application-default login
```

## 起動方法

### 方法1: Python で直接起動 (開発用)

ホットリロード（コード変更の自動反映）が有効なため、開発に最適です。

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
起動後、ブラウザで `http://localhost:8000` にアクセスしてください。

### 方法2: Docker を使用して起動

本番環境に近い状態で動作確認ができます。

```bash
# イメージのビルド
docker build -t reseve-app .

# コンテナの起動
# (認証情報をマウントし、環境変数を指定して実行します)
docker run -p 8080:8080 \
  -v "$HOME/.config/gcloud:/root/.config/gcloud" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json \
  -e GOOGLE_CLOUD_PROJECT="gym-reserve-app" \
  --name reseve-container \
  reseve-app
```
起動後、ブラウザで `http://localhost:8080` にアクセスしてください。

## 開発用ドキュメント

ドキュメントは役割に応じて `docs/strategy/` (攻め) と `docs/management/` (守り) に分類されています。

### 攻めのドキュメント (Strategy)
- [要件定義 (REQUIREMENTS.md)](./docs/strategy/REQUIREMENTS.md)
- [詳細仕様 (SPECIFICATION.md)](./docs/strategy/SPECIFICATION.md)
- [重要度・順序 (PRIORITY.md)](./docs/strategy/PRIORITY.md)
- [アーキテクチャ仕様 (ARCHITECTURE.md)](./docs/strategy/ARCHITECTURE.md)

### 守りのドキュメント (Management)
- [進捗管理 (PROGRESS.md)](./docs/management/PROGRESS.md)
- [実装ログ (IMPLEMENTATION_LOG.md)](./docs/management/IMPLEMENTATION_LOG.md) ※開発時に毎回参照
- [問題・解決・背景 (TROUBLESHOOTING_HISTORY.md)](./docs/management/TROUBLESHOOTING_HISTORY.md)
- [テスト仕様 (TESTING.md)](./docs/management/TESTING.md)
- [運用手順 (OPERATIONS.md)](./docs/management/OPERATIONS.md)

その他の詳細なルールは [DEVELOPMENT_RULES.md](./docs/development/DEVELOPMENT_RULES.md) を参照してください。

## データの保存場所

データは Google Cloud Firestore に保存されます。接続設定は `app/core/database.py` を参照してください。
