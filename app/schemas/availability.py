from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AvailabilityBase(BaseModel):
    """稼働枠の基本スキーマ"""
    startAt: datetime
    endAt: datetime

class AvailabilityCreate(BaseModel):
    """稼働枠作成（一括登録用）"""
    trainerId: str
    slots: List[AvailabilityBase]

class AvailabilityResponse(BaseModel):
    """稼働枠応答"""
    id: str
    trainerId: str
    startAt: datetime
    endAt: datetime
    isBooked: bool

    class Config:
        from_attributes = True

class AvailabilityQuery(BaseModel):
    """稼働枠検索クエリ"""
    trainerId: Optional[str] = None
    date: str  # YYYY-MM-DD

