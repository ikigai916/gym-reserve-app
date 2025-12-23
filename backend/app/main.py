"""
FastAPI アプリケーション - 最小構成
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os
import uvicorn
from datetime import datetime

from app.schemas import UserCreate, UserResponse
from app.storage import load_users, save_users

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

@app.get("/login.html")
def serve_login():
    """ログインページを配信（開発用）"""
    login_path = os.path.join(frontend_path, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"error": "Login page not found"}

# ユーザー作成API
@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate):
    """ユーザーを作成または取得"""
    if not user.name or not user.name.strip():
        raise HTTPException(status_code=400, detail="名前は必須です")
    
    users = load_users()
    
    # メールアドレスがある場合、重複チェック
    if user.email:
        existing_user = next((u for u in users if u.get("email") == user.email), None)
        if existing_user:
            raise HTTPException(status_code=409, detail="このメールアドレスは既に登録されています")
    
    # 新規ユーザーを作成
    new_user = {
        "id": str(int(datetime.now().timestamp() * 1000)),  # ミリ秒タイムスタンプをIDとして使用
        "name": user.name.strip(),
        "email": user.email.strip() if user.email else "",
        "phone": user.phone.strip() if user.phone else "",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_users(users)
    
    return UserResponse(**new_user)

# ユーザー取得API
@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    """ユーザー情報を取得"""
    users = load_users()
    user = next((u for u in users if u.get("id") == user_id), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    return UserResponse(**user)

if __name__ == "__main__":
    # Cloud Run が指定するポート番号を取得（デフォルトは 8080）
    port = int(os.environ.get("PORT", 8080))
    # すべてのIPアドレス（0.0.0.0）で、指定されたポートで起動
    uvicorn.run(app, host="0.0.0.0", port=port)