from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

class UserCreate(BaseModel):
    """ユーザー作成スキーマ"""
    name: str
    email: EmailStr
    password: str = Field(..., max_length=72)
    phone: Optional[str] = ""
    role: Optional[Literal["trainer", "trainee"]] = "trainee"

class UserLogin(BaseModel):
    """ログイン用スキーマ"""
    email: EmailStr
    password: str = Field(..., max_length=72)

class Token(BaseModel):
    """トークン応答スキーマ"""
    access_token: str
    token_type: str
    user: "UserResponse"

class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    """ユーザー応答スキーマ"""
    id: str
    name: str
    email: str
    phone: str
    role: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True

# Tokenクラスの中でUserResponseを使用しているため再掲
Token.model_rebuild()
