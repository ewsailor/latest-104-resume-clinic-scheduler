"""
使用者模型模組。

定義使用者資料表對應的 SQLAlchemy 模型。
"""

from typing import Any

# ===== 第三方套件 =====
from sqlalchemy import Column, DateTime, Index, String
from sqlalchemy.dialects.mysql import INTEGER

# ===== 本地模組 =====
from app.models.database import Base
from app.utils.model_helpers import format_datetime, safe_getattr  # 模型輔助工具
from app.utils.timezone import get_local_now_naive  # 本地時間函數


class User(Base):  # type: ignore[misc]
    """使用者資料表模型"""

    __tablename__ = "users"

    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="使用者 ID",
    )
    name = Column(String(100), nullable=False, comment="使用者姓名")
    email = Column(String(191), nullable=False, unique=True, comment="電子信箱（唯一）")
    created_at = Column(
        DateTime,
        default=get_local_now_naive,
        nullable=False,
        comment="建立時間（本地時間）",
    )
    updated_at = Column(
        DateTime,
        default=get_local_now_naive,
        onupdate=get_local_now_naive,
        nullable=False,
        comment="更新時間（本地時間）",
    )
    deleted_at = Column(DateTime, nullable=True, comment="軟刪除標記（本地時間）")

    __table_args__ = (Index('idx_users_created_at', 'created_at'),)

    def __repr__(self) -> str:
        """字串表示，用於除錯和日誌"""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典格式，用於 API 和資料傳輸給前端"""
        try:
            return {
                "id": safe_getattr(self, 'id'),
                "name": safe_getattr(self, 'name'),
                "email": safe_getattr(self, 'email'),
                "created_at": format_datetime(safe_getattr(self, 'created_at')),
                "updated_at": format_datetime(safe_getattr(self, 'updated_at')),
                "deleted_at": format_datetime(safe_getattr(self, 'deleted_at')),
            }
        except Exception as e:
            # 記錄錯誤但不中斷程式執行
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"User.to_dict() 錯誤: {e}", exc_info=True)

            # 返回基本資訊，避免 API 完全失敗
            return {
                "id": safe_getattr(self, 'id'),
                "name": safe_getattr(self, 'name', '未知'),
                "email": safe_getattr(self, 'email', '未知'),
                "error": "資料序列化時發生錯誤",
            }
