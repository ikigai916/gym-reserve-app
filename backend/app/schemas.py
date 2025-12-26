"""
Pydanticスキーマ定義
"""
from pydantic import BaseModel
from typing import Optional, Literal

class UserCreate(BaseModel):
    """ユーザー作成スキーマ"""
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    role: Optional[Literal["trainer", "trainee"]] = "trainee"  # デフォルトはtrainee

class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    # roleは更新しない（セキュリティ上の理由）

class UserResponse(BaseModel):
    """ユーザー応答スキーマ"""
    id: str
    name: str
    email: str
    phone: str
    role: str  # trainer または trainee
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True

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

