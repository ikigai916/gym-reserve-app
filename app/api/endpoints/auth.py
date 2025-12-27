from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from google.cloud.firestore_v1.base_query import FieldFilter
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.core.database import db
from app.core.auth import get_password_hash, verify_password, create_access_token

# ロガーの設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    """新規会員登録"""
    logger.info(f"Signup attempt for email: {user.email}")
    try:
        users_collection = db.collection("users")
        
        # すでにメールアドレスが使われていないかチェック
        logger.info("Checking if email already exists in Firestore...")
        existing_users = users_collection.where(filter=FieldFilter("email", "==", user.email.strip())).limit(1).get()
        logger.info("Firestore query for existing users completed.")
        
        if len(list(existing_users)) > 0:
            logger.warning(f"Signup failed: Email {user.email} already exists.")
            raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")
        
        now = datetime.now().isoformat()
        hashed_password = get_password_hash(user.password)
        
        user_data = {
            "name": user.name.strip(),
            "email": user.email.strip(),
            "phone": user.phone.strip() if user.phone else "",
            "password": hashed_password,
            "role": user.role if user.role else "trainee",
            "createdAt": now,
            "updatedAt": now
        }
        
        logger.info("Creating new user in Firestore...")
        doc_ref = users_collection.document()
        doc_ref.set(user_data)
        logger.info(f"User created successfully with ID: {doc_ref.id}")
        
        user_response = UserResponse(
            id=doc_ref.id,
            **{k: v for k, v in user_data.items() if k != "password"}
        )
        
        access_token = create_access_token(data={"sub": doc_ref.id, "role": user_data["role"]})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"サインアップエラー: {str(e)}")

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """ログイン"""
    logger.info(f"Login attempt for email: {login_data.email}")
    try:
        users_collection = db.collection("users")
        
        # メールアドレスでユーザーを検索
        logger.info("Searching for user in Firestore...")
        query = users_collection.where(filter=FieldFilter("email", "==", login_data.email.strip())).limit(1).get()
        users = list(query)
        logger.info(f"Firestore query completed. Found {len(users)} user(s).")
        
        if len(users) == 0:
            logger.warning(f"Login failed: User {login_data.email} not found.")
            raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
        
        user_doc = users[0]
        user_data = user_doc.to_dict()
        
        # パスワードの検証
        if not verify_password(login_data.password, user_data["password"]):
            logger.warning(f"Login failed: Incorrect password for {login_data.email}.")
            raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
        
        user_response = UserResponse(
            id=user_doc.id,
            **{k: v for k, v in user_data.items() if k != "password"}
        )
        
        access_token = create_access_token(data={"sub": user_doc.id, "role": user_data["role"]})
        
        logger.info(f"User {login_data.email} logged in successfully.")
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ログインエラー: {str(e)}")

