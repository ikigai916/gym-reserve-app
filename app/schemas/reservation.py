from pydantic import BaseModel
from typing import Optional

class ReservationCreate(BaseModel):
    """予約作成スキーマ"""
    userId: str
    date: str  # YYYY-MM-DD形式
    timeSlot: str  # 例: "09:00-10:00"
    trainerId: Optional[str] = None  # トレーナーID（将来必須化予定）
    menuId: Optional[str] = None  # メニューID（将来必須化予定）
    userPlanId: Optional[str] = None  # ユーザープランID（将来必須化予定）

class ReservationResponse(BaseModel):
    """予約応答スキーマ"""
    id: str
    userId: str
    user_name: str  # 表示用の予約者名
    date: str
    timeSlot: str
    status: str  # active/cancelled
    trainerId: Optional[str] = None
    menuId: Optional[str] = None
    userPlanId: Optional[str] = None
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True

class ReservationLegacy(BaseModel):
    """旧形式の予約データ"""
    user_name: str
    date: str

