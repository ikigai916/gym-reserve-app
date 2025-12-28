from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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
    userId: Optional[str] = "unknown"
    user_name: Optional[str] = "不明"
    trainerId: Optional[str] = "unknown"
    date: str
    startTime: str
    endTime: Optional[str] = "--:--"
    courseMinutes: Optional[int] = 60
    status: str = "active"
    startAt: Optional[datetime] = None
    endAt: Optional[datetime] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config:
        from_attributes = True

class ReservationLegacy(BaseModel):
    """旧形式の予約データ (互換性のために残す)"""
    user_name: str
    date: str
