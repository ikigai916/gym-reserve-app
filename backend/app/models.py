"""
データモデル定義
"""
from datetime import datetime
from typing import Optional

class User:
    """ユーザーモデル"""
    def __init__(
        self,
        id: str,
        name: str,
        email: str = "",
        phone: str = "",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }

