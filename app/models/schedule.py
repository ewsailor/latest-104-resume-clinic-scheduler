"""時段資料模型。

定義時段資料表對應的 SQLAlchemy ORM 模型。
"""

# ===== 標準函式庫 =====
import logging
from typing import Any

# ===== 第三方套件 =====
from sqlalchemy import (
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

# ===== 本地模組 =====
# 絕對路徑導入（跨模組）
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.utils.model_helpers import format_datetime, safe_getattr
from app.utils.timezone import get_local_now_naive

# 相對路徑導入（同模組）
from .database import Base


class Schedule(Base):  # type: ignore[misc,valid-type]
    """諮詢時段資料模型。"""

    __tablename__ = "schedules"

    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="諮詢時段 ID",
    )
    giver_id = Column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),  # 保護：不能刪除有時段的 Giver
        nullable=False,
        comment="Giver 使用者 ID",
    )
    taker_id = Column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),  # 靈活：Taker 刪除時設為 NULL（時段變可預約）
        nullable=True,
        comment="Taker 使用者 ID，可為 NULL（表示 Giver 提供時段供 Taker 預約）",
    )
    status: "Column[ScheduleStatusEnum]" = Column(
        Enum(ScheduleStatusEnum),
        nullable=False,
        default=ScheduleStatusEnum.DRAFT,
        comment="諮詢時段狀態",
    )
    date = Column(
        Date,
        nullable=False,
        comment="日期",
    )
    start_time = Column(
        Time,
        nullable=False,
        comment="開始時間",
    )
    end_time = Column(
        Time,
        nullable=False,
        comment="結束時間",
    )
    note = Column(
        String(255),
        nullable=True,
        comment="備註，可為空",
    )

    # ===== 審計欄位 =====
    created_at = Column(
        DateTime,
        default=get_local_now_naive,
        nullable=False,
        comment="建立時間（本地時間）",
    )
    created_by = Column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),  # 指向 users 表
        nullable=True,
        comment="建立者的使用者 ID，可為 NULL（表示系統自動建立）",
    )
    created_by_role: "Column[UserRoleEnum]" = Column(
        Enum(UserRoleEnum),
        nullable=False,
        default=UserRoleEnum.SYSTEM,
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
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),  # 指向 users 表
        nullable=True,
        comment="最後更新的使用者 ID，可為 NULL（表示系統自動更新）",
    )
    updated_by_role: "Column[UserRoleEnum]" = Column(
        Enum(UserRoleEnum),
        nullable=False,
        default=UserRoleEnum.SYSTEM,
        comment="最後更新者角色",
    )

    # ===== 系統欄位 =====
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="軟刪除標記（本地時間）",
    )
    deleted_by = Column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),  # 指向 users 表
        nullable=True,
        comment="刪除者的使用者 ID，可為 NULL（表示系統自動刪除）",
    )
    deleted_by_role: "Column[UserRoleEnum]" = Column(
        Enum(UserRoleEnum),
        nullable=True,
        comment="刪除者角色，可為 NULL（未刪除時）",
    )

    # ===== 反向關聯 =====
    # 高頻使用：使用 lazy="join" 每次查詢都會載入關聯資料，避免 N+1 問題
    giver = relationship(
        "User",
        foreign_keys=[giver_id],
        back_populates="giver_schedules",
        lazy="joined",
    )
    taker = relationship(
        "User",
        foreign_keys=[taker_id],
        back_populates="taker_schedules",
        lazy="joined",
    )
    # 審計欄位低頻使用：使用 lazy="select" 需要時再載入
    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_schedules",
        lazy="select",
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_schedules",
        lazy="select",
    )
    deleted_by_user = relationship(
        "User",
        foreign_keys=[deleted_by],
        back_populates="deleted_schedules",
        lazy="select",
    )

    __table_args__ = (
        Index("idx_schedule_giver_date", "giver_id", "date", "start_time"),
        Index("idx_schedule_taker_date", "taker_id", "date", "start_time"),
        Index("idx_schedule_status", "status"),
        Index("idx_schedule_giver_time", "giver_id", "start_time", "end_time"),
    )

    @property
    def is_active(self) -> bool:
        """檢查記錄是否有效（未刪除）。"""
        return self.deleted_at is None

    @property
    def is_deleted(self) -> bool:
        """檢查記錄是否已刪除。"""
        return self.deleted_at is not None

    @property
    def is_available(self) -> bool:
        """檢查時段是否可預約。"""
        return bool(  # type: ignore
            self.is_active
            and self.status == ScheduleStatusEnum.AVAILABLE
            and self.taker_id is None
        )

    def __repr__(self) -> str:
        """字串表示。"""
        return (
            f"<Schedule(id={self.id}, giver_id={self.giver_id}, "
            f"date={self.date}, status={self.status})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典格式，用於 API 和資料傳輸給前端。"""
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
