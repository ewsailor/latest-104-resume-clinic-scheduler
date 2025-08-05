"""
使用者模型模組。

定義使用者資料表對應的 SQLAlchemy 模型。
"""

from datetime import datetime

# ===== 第三方套件 =====
from sqlalchemy import Column, DateTime, Integer, String

# ===== 本地模組 =====
from app.models.database import Base


class User(Base):
    """使用者資料表模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="使用者 ID")
    name = Column(String(100), nullable=False, comment="使用者姓名")
    email = Column(String(191), nullable=False, unique=True, comment="電子信箱（唯一）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="建立時間")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新時間"
    )
    deleted_at = Column(DateTime, nullable=True, comment="軟刪除標記")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
