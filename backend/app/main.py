"""
FastAPI アプリケーション - 最小構成
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn

app = FastAPI(
    title="ジム予約管理システム API",
    description="ジムの予約を管理するAPI",
    version="1.0.0"
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# フロントエンドの静的ファイルを配信（開発用）
# 本番環境では、フロントエンドは別のCDNやサービスでホスティングすることが一般的です
# Docker内では/app/frontend、開発環境では../frontend
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
frontend_path = os.path.join(base_dir, "frontend")
if not os.path.exists(frontend_path):
    # Docker内でのパスを試す
    frontend_path = "/app/frontend"

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    """ルートエンドポイント"""
    return {"message": "ジム予約管理システム API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok", "service": "gym-reservation-api"}

@app.get("/index.html")
def serve_index():
    """フロントエンドのindex.htmlを配信（開発用）"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found"}

if __name__ == "__main__":
    # Cloud Run が指定するポート番号を取得（デフォルトは 8080）
    port = int(os.environ.get("PORT", 8080))
    # すべてのIPアドレス（0.0.0.0）で、指定されたポートで起動
    uvicorn.run(app, host="0.0.0.0", port=port)