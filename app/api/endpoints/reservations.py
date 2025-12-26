from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationLegacy
from app.core.database import db
from google.cloud import firestore

router = APIRouter()

@router.post("/", response_model=ReservationResponse)
async def create_reservation(res: ReservationCreate):
    """予約を作成"""
    try:
        if not res.userId or not res.date or not res.timeSlot:
            raise HTTPException(status_code=400, detail="userId、date、timeSlotは必須です")
        
        user_doc = db.collection("users").document(res.userId).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        user_data = user_doc.to_dict()
        user_name = user_data.get("name", "")
        
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
        
        doc_ref = db.collection("reservations").document()
        doc_ref.set(reservation_data)
        
        return ReservationResponse(
            id=doc_ref.id,
            **reservation_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約作成エラー: {str(e)}")

@router.get("/", response_model=List[ReservationResponse])
async def get_reservations(userId: Optional[str] = None, status: Optional[str] = None):
    """予約一覧を取得"""
    try:
        reservations_ref = db.collection("reservations")
        # 将来的にフィルタリングを追加可能
        docs = reservations_ref.stream()
        
        reservations = []
        for doc in docs:
            data = doc.to_dict()
            reservations.append(ReservationResponse(
                id=doc.id,
                userId=data.get("userId", ""),
                user_name=data.get("user_name", data.get("name", "")),
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

# 後方互換性のためのレガシーAPI
@router.post("/legacy")
async def create_reservation_legacy(res: ReservationLegacy):
    """予約を作成（旧形式）"""
    try:
        doc_ref = db.collection("reservations").document()
        doc_ref.set({
            "user_name": res.user_name,
            "date": res.date,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return {"message": "予約が完了しました！", "id": doc_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/legacy")
async def get_reservations_legacy():
    """予約一覧を取得（旧形式）"""
    docs = db.collection("reservations").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

