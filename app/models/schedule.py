"""
時段資料模型。

定義時段相關的資料庫模型和結構。
"""

from typing import Any

# ===== 第三方套件 =====
from sqlalchemy import (  # 資料庫欄位類型
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Time,
)
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from app.enums.models import ScheduleStatusEnum, UserRoleEnum

# ===== 本地模組 =====
from app.models.database import Base  # 資料庫基類
from app.utils.model_helpers import format_datetime, safe_getattr  # 模型輔助工具
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
    created_by = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),  # 指向 users 表
        nullable=True,
        comment="建立者的使用者 ID，可為 NULL（表示系統自動建立）",
    )
    created_by_role = Column(
        Enum(UserRoleEnum),
        nullable=True,
        comment="建立者角色",
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
    deleted_by = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),  # 指向 users 表
        nullable=True,
        comment="刪除者的使用者 ID，可為 NULL（表示系統自動刪除）",
    )
    deleted_by_role = Column(
        Enum(UserRoleEnum),
        nullable=True,
        comment="刪除者角色",
    )

    giver = relationship("User", foreign_keys=[giver_id], lazy='joined')
    taker = relationship("User", foreign_keys=[taker_id], lazy='joined')
    created_by_user = relationship("User", foreign_keys=[created_by], lazy='joined')
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy='joined')
    deleted_by_user = relationship("User", foreign_keys=[deleted_by], lazy='joined')

    __table_args__ = (
        Index('idx_schedule_giver_date', 'giver_id', 'date', 'start_time'),
        Index('idx_schedule_taker_date', 'taker_id', 'date', 'start_time'),
        Index('idx_schedule_status', 'status'),
        Index('idx_schedule_giver_time', 'giver_id', 'start_time', 'end_time'),
    )

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

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典格式，用於 API 和資料傳輸給前端"""
        try:
            return {
                "id": safe_getattr(self, 'id'),
                "giver_id": safe_getattr(self, 'giver_id'),
                "taker_id": safe_getattr(self, 'taker_id'),
                "status": safe_getattr(self, 'status'),
                "date": format_datetime(safe_getattr(self, 'date')),
                "start_time": format_datetime(safe_getattr(self, 'start_time')),
                "end_time": format_datetime(safe_getattr(self, 'end_time')),
                "note": safe_getattr(self, 'note'),
                "created_at": format_datetime(safe_getattr(self, 'created_at')),
                "created_by": safe_getattr(self, 'created_by'),
                "created_by_role": safe_getattr(self, 'created_by_role'),
                "created_by_user": (
                    safe_getattr(self, 'created_by_user').name
                    if safe_getattr(self, 'created_by_user')
                    else None
                ),
                "updated_at": format_datetime(safe_getattr(self, 'updated_at')),
                "updated_by": safe_getattr(self, 'updated_by'),
                "updated_by_role": safe_getattr(self, 'updated_by_role'),
                "updated_by_user": (
                    safe_getattr(self, 'updated_by_user').name
                    if safe_getattr(self, 'updated_by_user')
                    else None
                ),
                "deleted_at": format_datetime(safe_getattr(self, 'deleted_at')),
                "deleted_by": safe_getattr(self, 'deleted_by'),
                "deleted_by_role": safe_getattr(self, 'deleted_by_role'),
                "deleted_by_user": (
                    safe_getattr(self, 'deleted_by_user').name
                    if safe_getattr(self, 'deleted_by_user')
                    else None
                ),
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
                "id": safe_getattr(self, 'id'),
                "giver_id": safe_getattr(self, 'giver_id'),
                "taker_id": safe_getattr(self, 'taker_id'),
                "status": safe_getattr(self, 'status', 'unknown'),
                "date": format_datetime(safe_getattr(self, 'date')),
                "start_time": format_datetime(safe_getattr(self, 'start_time')),
                "end_time": format_datetime(safe_getattr(self, 'end_time')),
                "note": safe_getattr(self, 'note', ''),
                "error": "資料序列化時發生錯誤",
            }
