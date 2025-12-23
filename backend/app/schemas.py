"""
Pydanticスキーマ定義
"""
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    """ユーザー作成スキーマ"""
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""

class UserResponse(BaseModel):
    """ユーザー応答スキーマ"""
    id: str
    name: str
    email: str
    phone: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True

