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
    updated_by = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),  # 自我參考
        nullable=True,
        comment="最後更新的使用者 ID，可為 NULL（表示系統自動更新）",
    )
    deleted_at = Column(DateTime, nullable=True, comment="軟刪除標記（本地時間）")

    # 正向關係：從 updated_by 找到最後更新此使用者的使用者
    updated_by_user = relationship("User", remote_side=[id])
    # 反向關係：此使用者最後更新過的使用者列表 (只讀，避免衝突)
    updated_users = relationship(
        "User", remote_side=[updated_by], viewonly=True, overlaps="updated_by_user"
    )

    def __repr__(self) -> str:
        """字串表示，用於除錯和日誌"""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    def _format_datetime(self, dt) -> str | None:
        """格式化日期時間為 ISO 字串，如果為 None 則返回 None"""
        return dt.isoformat() if dt else None

    def _safe_getattr(self, attr_name: str, default=None):
        """安全地取得物件屬性，避免 AttributeError"""
        try:
            return getattr(self, attr_name, default)
        except Exception:
            return default

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式，用於 API 和資料傳輸給前端"""
        try:
            return {
                "id": self._safe_getattr('id'),
                "name": self._safe_getattr('name'),
                "email": self._safe_getattr('email'),
                "created_at": self._format_datetime(self._safe_getattr('created_at')),
                "updated_at": self._format_datetime(self._safe_getattr('updated_at')),
                "updated_by": self._safe_getattr('updated_by'),
                "deleted_at": self._format_datetime(self._safe_getattr('deleted_at')),
            }
        except Exception as e:
            # 記錄錯誤但不中斷程式執行
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"User.to_dict() 錯誤: {e}", exc_info=True)

            # 返回基本資訊，避免 API 完全失敗
            return {
                "id": self._safe_getattr('id'),
                "name": self._safe_getattr('name', '未知'),
                "email": self._safe_getattr('email', '未知'),
                "error": "資料序列化時發生錯誤",
            }
