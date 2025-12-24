from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.cloud import firestore
from datetime import datetime
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
# 認証情報が設定されていない場合でも、エラーメッセージを表示する
try:
    db = firestore.Client()
    print("Firestore client initialized successfully")
except Exception as e:
    print(f"⚠️  Error initializing Firestore client: {e}")
    print("⚠️  Firestore認証情報を設定してください:")
    print("    gcloud auth application-default login")
    # 開発環境では、エラーを表示して続行（本番環境では適切に処理）
    raise

# 予約データの型定義
class Reservation(BaseModel):
    user_name: str
    date: str  # 例: "2024-12-25"

# ユーザーデータの型定義
class UserCreate(BaseModel):
    name: str
    email: str = ""
    phone: str = ""

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    createdAt: str
    updatedAt: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gym-reservation-api"}

# ユーザー作成API
@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """ユーザーを作成"""
    try:
        if not user.name or not user.name.strip():
            raise HTTPException(status_code=400, detail="名前は必須です")
        
        print(f"Creating user: {user.name}, email: {user.email}")
        
        # Firestoreにユーザーを保存
        users_collection = db.collection("users")
        
        # メールアドレスがある場合、重複チェック（タイムアウト対策のため、一旦コメントアウト）
        # 注意: 本番環境では重複チェックを有効にすることを推奨
        # if user.email:
        #     print(f"Checking for existing email: {user.email}")
        #     from google.cloud.firestore_v1.base_query import FieldFilter
        #     try:
        #         existing_users = list(
        #             users_collection.where(filter=FieldFilter("email", "==", user.email)).limit(1).stream()
        #         )
        #         if existing_users:
        #             print(f"Email already exists")
        #             raise HTTPException(status_code=409, detail="このメールアドレスは既に登録されています")
        #     except Exception as e:
        #         print(f"Warning: Email duplicate check failed: {e}")
        #         # 重複チェックが失敗しても続行（開発環境向け）
        
        # 新しいユーザードキュメントを作成
        now = datetime.now().isoformat()
        
        user_data = {
            "name": user.name.strip(),
            "email": user.email.strip() if user.email else "",
            "phone": user.phone.strip() if user.phone else "",
            "createdAt": now,
            "updatedAt": now
        }
        
        print(f"Saving user data to Firestore: {user_data}")
        doc_ref = users_collection.document()
        doc_ref.set(user_data)
        print(f"User created with ID: {doc_ref.id}")
        
        # レスポンスを返す
        return UserResponse(
            id=doc_ref.id,
            name=user_data["name"],
            email=user_data["email"],
            phone=user_data["phone"],
            createdAt=user_data["createdAt"],
            updatedAt=user_data["updatedAt"]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"ユーザー作成エラー: {str(e)}")

# ユーザー取得API
@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """ユーザー情報を取得"""
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        user_data = doc.to_dict()
        return UserResponse(
            id=doc.id,
            name=user_data["name"],
            email=user_data.get("email", ""),
            phone=user_data.get("phone", ""),
            createdAt=user_data.get("createdAt", ""),
            updatedAt=user_data.get("updatedAt", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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