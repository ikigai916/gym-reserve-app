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

