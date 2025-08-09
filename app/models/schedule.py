"""
時段資料模型。

定義時段相關的資料庫模型和結構。
"""

from typing import Any, Dict

# ===== 第三方套件 =====
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Time,
)  # 資料庫欄位類型
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

# ===== 本地模組 =====
from app.models.database import Base  # 資料庫基類
from app.utils.timezone import get_local_now_naive  # 本地時間函數


class Schedule(Base):  # type: ignore[misc]
    """
    時段資料模型。

    儲存 Giver 提供的諮詢時段資訊。
    """

    __tablename__ = "schedules"

    # 主鍵
    id = Column(INTEGER(unsigned=True), primary_key=True, index=True, comment="時段 ID")

    # 角色和關聯
    role = Column(
        String(10),
        nullable=False,
        default="GIVER",
        comment="角色：GIVER=提供者、TAKER=預約者",
    )
    giver_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="Giver ID",
    )
    taker_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.id"),
        nullable=True,
        comment="Taker ID，可為 NULL",
    )

    # 時段資訊
    date = Column(Date, nullable=False, comment="時段日期")
    start_time = Column(Time, nullable=False, comment="開始時間")
    end_time = Column(Time, nullable=False, comment="結束時間")
    note = Column(String(255), nullable=True, comment="備註")

    # 狀態管理
    status = Column(
        String(20),
        default="DRAFT",
        comment="時段狀態",
    )

    # 時間戳記
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
    updated_by_role = Column(
        Enum("GIVER", "TAKER", "SYSTEM", name="user_role_enum"),
        nullable=True,
        comment="最後更新者的角色：GIVER、TAKER 或 SYSTEM",
    )
    deleted_at = Column(DateTime, nullable=True, comment="軟刪除標記")

    # 關聯關係
    giver = relationship("User", foreign_keys=[giver_id])
    taker = relationship("User", foreign_keys=[taker_id])
    updated_by_user = relationship("User", foreign_keys=[updated_by])

    def __repr__(self) -> str:
        """字串表示"""
        return (
            f"<Schedule(id={self.id}, giver_id={self.giver_id}, "
            f"date={self.date}, status={self.status})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "role": self.role,
            "giver_id": self.giver_id,
            "taker_id": self.taker_id,
            "date": self.date.isoformat() if self.date else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "note": self.note,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "updated_by_role": self.updated_by_role,
            "updated_by_user": (
                self.updated_by_user.name if self.updated_by_user else None
            ),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
