from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.cloud import firestore
import os

app = FastAPI()

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# フロントエンドの静的ファイルを配信
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
frontend_path = os.path.join(base_dir, "frontend")
if not os.path.exists(frontend_path):
    frontend_path = "/app/frontend"

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Firestore クライアントの初期化
db = firestore.Client()

# 予約データの型定義
class Reservation(BaseModel):
    user_name: str
    date: str  # 例: "2024-12-25"

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gym-reservation-api"}

# 予約を保存するAPI
@app.post("/reservations")
async def create_reservation(res: Reservation):
    try:
        # 'reservations' というコレクションに保存
        doc_ref = db.collection("reservations").document()
        doc_ref.set({
            "user_name": res.user_name,
            "date": res.date,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return {"message": "予約が完了しました！", "id": doc_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 予約一覧を取得するAPI（カレンダー表示用）
@app.get("/reservations")
async def get_reservations():
    docs = db.collection("reservations").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@app.get("/")
def serve_index():
    """フロントエンドのindex.htmlを配信"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found"}

@app.get("/index.html")
def serve_index_html():
    """フロントエンドのindex.htmlを配信"""
    return serve_index()

@app.get("/login.html")
def serve_login():
    """ログインページを配信"""
    login_path = os.path.join(frontend_path, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"error": "Login page not found"}