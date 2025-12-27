from pydantic import BaseModel
from typing import Optional, List

class ReservationCreate(BaseModel):
    """予約作成スキーマ"""
    trainerId: str
    date: str  # YYYY-MM-DD
    startTime: str  # HH:mm
    courseMinutes: int  # 60, 90, 120...
    startAt: Optional[str] = None # ISO形式の開始日時 (UTC)

class ReservationResponse(BaseModel):
    """予約応答スキーマ"""
    id: str
    userId: str
    user_name: str
    trainerId: str
    date: str
    startTime: str
    endTime: str
    courseMinutes: int
    status: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True

class ReservationLegacy(BaseModel):
    """旧形式の予約データ (互換性のために残す)"""
    user_name: str
    date: str
