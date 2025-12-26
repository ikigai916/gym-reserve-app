from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.cloud import firestore
from datetime import datetime
from typing import Optional
import os

# ユーザーデータの型定義（schemas.pyからインポート）
from app.schemas import UserCreate, UserResponse, ReservationCreate, ReservationResponse

app = FastAPI()

# CORS設定（フロントエンドからのアクセスを許可）
# 環境変数から許可するオリジンを取得（本番環境では適切なオリジンを設定）
# 開発環境のデフォルト値: localhost:8000, localhost:3000
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://localhost:3000,http://127.0.0.1:8000,http://127.0.0.1:3000"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # 許可されたオリジンのみ
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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

# 予約データの型定義（後方互換性のため残すが、ReservationCreate/Responseを使用推奨）
class Reservation(BaseModel):
    user_name: str
    date: str  # 例: "2024-12-25"

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
        
        # ロールが指定されていない場合はデフォルトでtrainee
        role = user.role if user.role else "trainee"
        
        user_data = {
            "name": user.name.strip(),
            "email": user.email.strip() if user.email else "",
            "phone": user.phone.strip() if user.phone else "",
            "role": role,
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
            role=user_data["role"],
            createdAt=user_data["createdAt"],
            updatedAt=user_data["updatedAt"]
        )
    except HTTPException:
        raise
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        print(f"Error creating user: {error_type}: {error_message}")
        import traceback
        traceback.print_exc()
        # 権限エラーの場合、より分かりやすいメッセージを返す
        if "Permission denied" in error_message or "permission" in error_message.lower():
            raise HTTPException(
                status_code=500, 
                detail=f"Firestoreへのアクセス権限がありません。Cloud Runのサービスアカウントに'Cloud Datastore User'ロールが必要です。エラー: {error_message}"
            )
        raise HTTPException(status_code=500, detail=f"ユーザー作成エラー ({error_type}): {error_message}")

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
        # 既存データとの互換性: roleフィールドがない場合はデフォルトでtrainee
        role = user_data.get("role", "trainee")
        return UserResponse(
            id=doc.id,
            name=user_data["name"],
            email=user_data.get("email", ""),
            phone=user_data.get("phone", ""),
            role=role,
            createdAt=user_data.get("createdAt", ""),
            updatedAt=user_data.get("updatedAt", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 予約を保存するAPI（新形式）
@app.post("/api/reservations", response_model=ReservationResponse)
async def create_reservation(res: ReservationCreate):
    """予約を作成"""
    try:
        # バリデーション
        if not res.userId or not res.date or not res.timeSlot:
            raise HTTPException(status_code=400, detail="userId、date、timeSlotは必須です")
        
        # ユーザー情報を取得（user_name用）
        user_doc = db.collection("users").document(res.userId).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        user_data = user_doc.to_dict()
        user_name = user_data.get("name", "")
        
        # 予約データを準備
        now = datetime.now().isoformat()
        reservation_data = {
            "userId": res.userId,
            "user_name": user_name,
            "date": res.date,
            "timeSlot": res.timeSlot,
            "status": "active",
            "trainerId": res.trainerId,
            "menuId": res.menuId,
            "userPlanId": res.userPlanId,
            "createdAt": now,
            "updatedAt": now
        }
        
        # Firestoreに保存
        doc_ref = db.collection("reservations").document()
        doc_ref.set(reservation_data)
        
        return ReservationResponse(
            id=doc_ref.id,
            userId=reservation_data["userId"],
            user_name=reservation_data["user_name"],
            date=reservation_data["date"],
            timeSlot=reservation_data["timeSlot"],
            status=reservation_data["status"],
            trainerId=reservation_data.get("trainerId"),
            menuId=reservation_data.get("menuId"),
            userPlanId=reservation_data.get("userPlanId"),
            createdAt=reservation_data["createdAt"],
            updatedAt=reservation_data["updatedAt"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約作成エラー: {str(e)}")

# 予約を保存するAPI（旧形式・後方互換性のため残す）
@app.post("/reservations")
async def create_reservation_legacy(res: Reservation):
    """予約を作成（旧形式・後方互換性のため）"""
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

# 予約一覧を取得するAPI（新形式）
@app.get("/api/reservations", response_model=list[ReservationResponse])
async def get_reservations(userId: Optional[str] = None, status: Optional[str] = None):
    """予約一覧を取得（フィルタリング対応）"""
    try:
        reservations_ref = db.collection("reservations")
        
        # フィルタリング（将来実装予定）
        # if userId:
        #     reservations_ref = reservations_ref.where("userId", "==", userId)
        # if status:
        #     reservations_ref = reservations_ref.where("status", "==", status)
        
        docs = reservations_ref.stream()
        reservations = []
        for doc in docs:
            data = doc.to_dict()
            # 既存データとの互換性: 新フィールドがない場合はデフォルト値を設定
            reservations.append(ReservationResponse(
                id=doc.id,
                userId=data.get("userId", ""),
                user_name=data.get("user_name", data.get("name", "")),  # 旧形式との互換性
                date=data.get("date", ""),
                timeSlot=data.get("timeSlot", ""),
                status=data.get("status", "active"),
                trainerId=data.get("trainerId"),
                menuId=data.get("menuId"),
                userPlanId=data.get("userPlanId"),
                createdAt=data.get("createdAt", ""),
                updatedAt=data.get("updatedAt", data.get("createdAt", ""))
            ))
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約取得エラー: {str(e)}")

# 予約一覧を取得するAPI（旧形式・後方互換性のため残す）
@app.get("/reservations")
async def get_reservations_legacy():
    """予約一覧を取得（旧形式・後方互換性のため）"""
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