# Python 3.11 のベースイメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# requirements.txtをコピーしてパッケージをインストール
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# アプリケーションコードをコピー
# app/ フォルダ全体をコピーします（static も含む）
COPY app /app/app

# Cloud Run のデフォルトポート 8080 を公開設定にする
EXPOSE 8080

# ヘルスチェックのポートも 8080 に変更
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# uvicornの起動コマンド
# app.main:app を指定
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
