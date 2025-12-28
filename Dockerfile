# Python 3.11 のベースイメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Cloud Run の $PORT 環境変数を使用して起動
# ポートはデフォルトで8080を使用（Cloud Run側で設定可能）
ENV PORT=8080
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info
