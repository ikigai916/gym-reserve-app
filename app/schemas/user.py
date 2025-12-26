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

