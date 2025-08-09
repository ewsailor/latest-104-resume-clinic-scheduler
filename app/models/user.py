"""
使用者模型模組。

定義使用者資料表對應的 SQLAlchemy 模型。
"""

from typing import Any, Dict

# ===== 第三方套件 =====
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

# ===== 本地模組 =====
from app.models.database import Base
from app.utils.timezone import get_local_now_naive  # 本地時間函數


class User(Base):  # type: ignore[misc]
    """使用者資料表模型"""

    __tablename__ = "users"

    id = Column(
        INTEGER(unsigned=True), primary_key=True, index=True, comment="使用者 ID"
    )
    name = Column(String(100), nullable=False, comment="使用者姓名")
    email = Column(String(191), nullable=False, unique=True, comment="電子信箱（唯一）")
    created_at = Column(DateTime, default=get_local_now_naive, comment="建立時間")
    updated_at = Column(
        DateTime,
        default=get_local_now_naive,
        onupdate=get_local_now_naive,
        comment="更新時間",
    )
    updated_by = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="最後更新者的使用者 ID，可為 NULL（表示系統自動更新）",
    )
    deleted_at = Column(DateTime, nullable=True, comment="軟刪除標記")

    # 關聯關係 - 指向最後更新此使用者的使用者
    updated_by_user = relationship("User", remote_side=[id])
    # 反向關聯 - 此使用者最後更新過的使用者列表 (只讀，避免衝突)
    updated_users = relationship(
        "User", remote_side=[updated_by], viewonly=True, overlaps="updated_by_user"
    )

    # 與 Schedule 的關聯關係
    # 暫時註解避免循環依賴問題
    # given_schedules = relationship(
    #     "Schedule",
    #     foreign_keys="Schedule.giver_id",
    #     back_populates="giver",
    #     lazy="select"
    # )
    # taken_schedules = relationship(
    #     "Schedule",
    #     foreign_keys="Schedule.taker_id",
    #     back_populates="taker",
    #     lazy="select"
    # )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "updated_by_user": (
                self.updated_by_user.name if self.updated_by_user else None
            ),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
