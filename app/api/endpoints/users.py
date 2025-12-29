from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.core.database import db
from app.core.auth import get_current_user, get_password_hash, verify_password

from google.cloud.firestore_v1.base_query import FieldFilter

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user.get("email", ""),
        phone=current_user.get("phone", ""),
        role=current_user.get("role", "trainee"),
        createdAt=current_user.get("createdAt", ""),
        updatedAt=current_user.get("updatedAt", "")
    )

@router.patch("/me", response_model=UserResponse)
async def update_me(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """現在のユーザー情報を更新"""
    try:
        user_id = current_user["id"]
        doc_ref = db.collection("users").document(user_id)
        
        update_data = {}
        if user_update.name is not None:
            if not user_update.name.strip():
                raise HTTPException(status_code=400, detail="名前は空にできません")
            update_data["name"] = user_update.name.strip()
        
        if user_update.email is not None:
            update_data["email"] = user_update.email.strip() if user_update.email.strip() else ""
        
        if user_update.phone is not None:
            update_data["phone"] = user_update.phone.strip() if user_update.phone.strip() else ""
        
        update_data["updatedAt"] = datetime.now().isoformat()
        
        doc_ref.update(update_data)
        
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        
        return UserResponse(
            id=updated_doc.id,
            name=updated_data["name"],
            email=updated_data.get("email", ""),
            phone=updated_data.get("phone", ""),
            role=updated_data.get("role", "trainee"),
            createdAt=updated_data.get("createdAt", ""),
            updatedAt=updated_data.get("updatedAt", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プロフィール更新エラー: {str(e)}")

@router.put("/me/password")
async def update_password(pw_update: UserPasswordUpdate, current_user: dict = Depends(get_current_user)):
    """パスワードを更新"""
    try:
        user_id = current_user["id"]
        doc_ref = db.collection("users").document(user_id)
        
        # 現在のパスワードを確認
        user_doc = doc_ref.get()
        user_data = user_doc.to_dict()
        
        if not verify_password(pw_update.current_password, user_data["hashed_password"]):
            raise HTTPException(status_code=400, detail="現在のパスワードが正しくありません")
        
        # 新しいパスワードをハッシュ化して保存
        new_hashed_password = get_password_hash(pw_update.new_password)
        doc_ref.update({
            "hashed_password": new_hashed_password,
            "updatedAt": datetime.now().isoformat()
        })
        
        return {"status": "success", "message": "パスワードを更新しました"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"パスワード更新エラー: {str(e)}")

@router.get("/", response_model=List[UserResponse])
async def get_users(role: str = None):
    """ユーザー一覧を取得（ロールでフィルタリング可能）"""
    try:
        query = db.collection("users")
        if role:
            query = query.where(filter=FieldFilter("role", "==", role))
        
        docs = query.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            results.append(UserResponse(id=doc.id, **data))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """ユーザーを作成"""
    try:
        if not user.name or not user.name.strip():
            raise HTTPException(status_code=400, detail="名前は必須です")
        
        users_collection = db.collection("users")
        now = datetime.now().isoformat()
        role = user.role if user.role else "trainee"
        
        user_data = {
            "name": user.name.strip(),
            "email": user.email.strip() if user.email else "",
            "phone": user.phone.strip() if user.phone else "",
            "role": role,
            "createdAt": now,
            "updatedAt": now
        }
        
        doc_ref = users_collection.document()
        doc_ref.set(user_data)
        
        return UserResponse(
            id=doc_ref.id,
            **user_data
        )
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        if "Permission denied" in error_message or "permission" in error_message.lower():
            raise HTTPException(
                status_code=500, 
                detail=f"Firestoreアクセス権限エラー: {error_message}"
            )
        raise HTTPException(status_code=500, detail=f"ユーザー作成エラー: {error_message}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """ユーザー情報を取得"""
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        user_data = doc.to_dict()
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

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """ユーザー情報を更新"""
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        update_data = {}
        if user_update.name is not None:
            if not user_update.name.strip():
                raise HTTPException(status_code=400, detail="名前は空にできません")
            update_data["name"] = user_update.name.strip()
        
        if user_update.email is not None:
            update_data["email"] = user_update.email.strip() if user_update.email.strip() else ""
        
        if user_update.phone is not None:
            update_data["phone"] = user_update.phone.strip() if user_update.phone.strip() else ""
        
        update_data["updatedAt"] = datetime.now().isoformat()
        doc_ref.update(update_data)
        
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        role = updated_data.get("role", "trainee")
        
        return UserResponse(
            id=updated_doc.id,
            name=updated_data["name"],
            email=updated_data.get("email", ""),
            phone=updated_data.get("phone", ""),
            role=role,
            createdAt=updated_data.get("createdAt", ""),
            updatedAt=updated_data.get("updatedAt", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザー更新エラー: {str(e)}")


