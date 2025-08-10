"""
時段資料模型。

定義時段相關的資料庫模型和結構。
"""

from typing import Any, Dict

# ===== 第三方套件 =====
from sqlalchemy import (  # 資料庫欄位類型
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Time,
)
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

# ===== 本地模組 =====
from app.models.database import Base  # 資料庫基類
from app.models.enums import ScheduleStatusEnum, UserRoleEnum
from app.utils.timezone import get_local_now_naive  # 本地時間函數


class Schedule(Base):  # type: ignore[misc]
    """
    諮詢時段資料模型。

    用於管理諮詢時段的預約和媒合系統，支援雙向時段提供機制：

    - **Giver 主動提供時段**：諮詢師提供可諮詢的時間段
    - **Taker 主動提供時段**：求職者提供希望諮詢的時間段，等待 Giver 確認

    主要功能：
    - 時段建立與管理
    - 預約狀態追蹤
    - 角色權限控制
    - 軟刪除支援
    """

    __tablename__ = "schedules"

    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="諮詢時段 ID",
    )
    giver_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.id", ondelete="RESTRICT"),  # 保護：不能刪除有時段的 Giver
        nullable=False,
        comment="Giver 使用者 ID",
    )
    taker_id = Column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id", ondelete="SET NULL"
        ),  # 靈活：Taker 刪除時設為 NULL（時段變可預約）
        nullable=True,
        comment="Taker 使用者 ID，可為 NULL（表示 Giver 提供時段供 Taker 預約）",
    )
    status = Column(
        Enum(ScheduleStatusEnum),
        nullable=False,
        default=ScheduleStatusEnum.DRAFT,
        comment="諮詢時段狀態",
    )
    date = Column(Date, nullable=False, comment="日期")
    start_time = Column(Time, nullable=False, comment="開始時間")
    end_time = Column(Time, nullable=False, comment="結束時間")
    note = Column(String(255), nullable=True, comment="備註，可為空")

    # ===== 審計欄位 =====
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
        ForeignKey("users.id", ondelete="SET NULL"),  # 指向 users 表
        nullable=True,
        comment="最後更新的使用者 ID，可為 NULL（表示系統自動更新）",
    )
    updated_by_role = Column(
        Enum(UserRoleEnum),
        nullable=True,
        comment="最後更新者角色",
    )

    # ===== 系統欄位 =====
    deleted_at = Column(DateTime, nullable=True, comment="軟刪除標記（本地時間）")

    giver = relationship("User", foreign_keys=[giver_id], lazy='joined')
    taker = relationship("User", foreign_keys=[taker_id], lazy='joined')
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy='joined')

    @property
    def creator_role(self):
        """建立者角色（向後相容屬性）"""
        return self.updated_by_role

    @property
    def is_active(self) -> bool:
        """檢查記錄是否有效（未刪除）"""
        return self.deleted_at is None

    @property
    def is_deleted(self) -> bool:
        """檢查記錄是否已刪除"""
        return self.deleted_at is not None

    @property
    def is_available(self) -> bool:
        """檢查時段是否可預約"""
        return (
            self.is_active
            and self.status == ScheduleStatusEnum.AVAILABLE
            and self.taker_id is None
        )

    def __repr__(self) -> str:
        """字串表示"""
        return (
            f"<Schedule(id={self.id}, giver_id={self.giver_id}, "
            f"date={self.date}, status={self.status})>"
        )

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
                "creator_role": self.creator_role,  # 向後相容：建立者角色
                "giver_id": self._safe_getattr('giver_id'),
                "taker_id": self._safe_getattr('taker_id'),
                "status": self._safe_getattr('status'),
                "date": self._format_datetime(self._safe_getattr('date')),
                "start_time": self._format_datetime(self._safe_getattr('start_time')),
                "end_time": self._format_datetime(self._safe_getattr('end_time')),
                "note": self._safe_getattr('note'),
                "created_at": self._format_datetime(self._safe_getattr('created_at')),
                "updated_at": self._format_datetime(self._safe_getattr('updated_at')),
                "updated_by": self._safe_getattr('updated_by'),
                "updated_by_role": self._safe_getattr('updated_by_role'),
                "updated_by_user": (
                    self._safe_getattr('updated_by_user').name
                    if self._safe_getattr('updated_by_user')
                    else None
                ),
                "deleted_at": self._format_datetime(self._safe_getattr('deleted_at')),
                # 便利屬性
                "is_active": self.is_active,
                "is_deleted": self.is_deleted,
                "is_available": self.is_available,
            }
        except Exception as e:
            # 記錄錯誤但不中斷程式執行
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Schedule.to_dict() 錯誤: {e}", exc_info=True)

            # 返回基本資訊，避免 API 完全失敗
            return {
                "id": self._safe_getattr('id'),
                "creator_role": self.creator_role,
                "giver_id": self._safe_getattr('giver_id'),
                "taker_id": self._safe_getattr('taker_id'),
                "status": self._safe_getattr('status', 'unknown'),
                "date": self._format_datetime(self._safe_getattr('date')),
                "start_time": self._format_datetime(self._safe_getattr('start_time')),
                "end_time": self._format_datetime(self._safe_getattr('end_time')),
                "note": self._safe_getattr('note', ''),
                "error": "資料序列化時發生錯誤",
            }
