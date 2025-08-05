"""
時段資料模型。

定義時段相關的資料庫模型和結構。
"""

from datetime import datetime  # 日期時間處理

# ===== 第三方套件 =====
from sqlalchemy import Column, Date, DateTime, Integer, String, Time  # 資料庫欄位類型

# ===== 本地模組 =====
from app.models.database import Base  # 資料庫基類


class Schedule(Base):
    """
    時段資料模型。

    儲存 Giver 提供的諮詢時段資訊。
    """

    __tablename__ = "schedules"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True, comment="時段 ID")

    # 角色和關聯
    role = Column(
        String(10),
        nullable=False,
        default="GIVER",
        comment="角色：GIVER=提供者、TAKER=預約者",
    )
    giver_id = Column(Integer, nullable=False, comment="Giver ID")
    taker_id = Column(Integer, nullable=True, comment="Taker ID，可為 NULL")

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
    created_at = Column(DateTime, default=datetime.utcnow, comment="建立時間")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新時間"
    )
    deleted_at = Column(DateTime, nullable=True, comment="軟刪除標記")

    def __repr__(self):
        """字串表示"""
        return (
            f"<Schedule(id={self.id}, giver_id={self.giver_id}, "
            f"date={self.date}, status={self.status})>"
        )

    def to_dict(self):
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
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
