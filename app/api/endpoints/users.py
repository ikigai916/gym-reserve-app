from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.database import db

router = APIRouter()

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

