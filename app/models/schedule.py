# """
# 時段相關的資料庫模型。

# 包含使用者、行程、歷史記錄、通知設定等模型，採用軟刪除和來源追蹤等最佳實踐。
# """

# # ===== 標準函式庫 =====
# from datetime import date, time, datetime  # 日期和時間處理
# from typing import Optional, List, Dict, Any  # 型別註解
# from enum import Enum  # 列舉類型

# # ===== 第三方套件 =====
# from sqlalchemy import (
#     Column, Integer, Date, Time, String, Text, DateTime, ForeignKey, 
#     Boolean, JSON, Enum as SQLEnum, CheckConstraint, Index
# )  # 資料庫欄位
# from sqlalchemy.ext.declarative import declarative_base  # 宣告式基類
# from sqlalchemy.orm import relationship, Mapped, mapped_column  # 關聯關係
# from sqlalchemy.sql import func  # SQL 函數

# # ===== 本地模組 =====
# from app.models.database import Base  # 資料庫基類


# # ===== 列舉定義 =====
# class UserStatus(str, Enum):
#     """使用者狀態列舉。"""
#     ACTIVE = "ACTIVE"
#     INACTIVE = "INACTIVE"
#     SUSPENDED = "SUSPENDED"


# class UserRole(str, Enum):
#     """使用者角色列舉。"""
#     USER = "USER"
#     ADMIN = "ADMIN"
#     MODERATOR = "MODERATOR"


# class ScheduleRole(str, Enum):
#     """行程角色列舉。"""
#     GIVER = "GIVER"
#     TAKER = "TAKER"


# class ScheduleStatus(str, Enum):
#     """行程狀態列舉。"""
#     DRAFT = "DRAFT"
#     AVAILABLE = "AVAILABLE"
#     PENDING = "PENDING"
#     ACCEPTED = "ACCEPTED"
#     REJECTED = "REJECTED"
#     CANCELLED = "CANCELLED"
#     COMPLETED = "COMPLETED"


# class MeetingType(str, Enum):
#     """會議類型列舉。"""
#     IN_PERSON = "IN_PERSON"
#     ONLINE = "ONLINE"
#     HYBRID = "HYBRID"


# class NotificationType(str, Enum):
#     """通知類型列舉。"""
#     EMAIL = "EMAIL"
#     SMS = "SMS"
#     PUSH = "PUSH"
#     WEBHOOK = "WEBHOOK"


# class NotificationChannel(str, Enum):
#     """通知管道列舉。"""
#     SCHEDULE_REMINDER = "SCHEDULE_REMINDER"
#     STATUS_CHANGE = "STATUS_CHANGE"
#     SYSTEM_ANNOUNCEMENT = "SYSTEM_ANNOUNCEMENT"


# # ===== 基礎模型類別 =====
# class TimestampMixin:
#     """時間戳記混入類別。"""
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime, 
#         default=func.now(), 
#         nullable=False, 
#         comment="建立時間"
#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime, 
#         default=func.now(), 
#         onupdate=func.now(), 
#         nullable=False, 
#         comment="更新時間"
#     )


# class SoftDeleteMixin:
#     """軟刪除混入類別。"""
#     deleted_at: Mapped[Optional[datetime]] = mapped_column(
#         DateTime, 
#         nullable=True, 
#         comment="軟刪除標記"
#     )


# class SourceMixin:
#     """來源追蹤混入類別。"""
#     source: Mapped[str] = mapped_column(
#         String(50), 
#         default="MANUAL", 
#         nullable=False, 
#         comment="資料來源"
#     )


# # ===== 使用者模型 =====
# class User(Base, TimestampMixin, SoftDeleteMixin, SourceMixin):
#     """
#     使用者資料表模型。
    
#     包含基本資訊、狀態管理、角色權限等。
#     """
#     __tablename__ = "users"
    
#     # 主鍵
#     id: Mapped[int] = mapped_column(
#         Integer, 
#         primary_key=True, 
#         autoincrement=True, 
#         comment="使用者 ID"
#     )
    
#     # 基本資訊
#     name: Mapped[str] = mapped_column(
#         String(100), 
#         nullable=False, 
#         comment="使用者姓名"
#     )
#     email: Mapped[str] = mapped_column(
#         String(191), 
#         nullable=False, 
#         unique=True, 
#         comment="電子信箱（唯一）"
#     )
#     phone: Mapped[Optional[str]] = mapped_column(
#         String(20), 
#         nullable=True, 
#         comment="電話號碼"
#     )
#     avatar_url: Mapped[Optional[str]] = mapped_column(
#         String(500), 
#         nullable=True, 
#         comment="頭像圖片 URL"
#     )
    
#     # 狀態和角色
#     status: Mapped[UserStatus] = mapped_column(
#         SQLEnum(UserStatus), 
#         default=UserStatus.ACTIVE, 
#         nullable=False, 
#         comment="使用者狀態"
#     )
#     role: Mapped[UserRole] = mapped_column(
#         SQLEnum(UserRole), 
#         default=UserRole.USER, 
#         nullable=False, 
#         comment="使用者角色"
#     )
    
#     # 關聯關係
#     giver_schedules: Mapped[List["Schedule"]] = relationship(
#         "Schedule", 
#         foreign_keys="Schedule.giver_id", 
#         back_populates="giver",
#         cascade="all, delete-orphan"
#     )
#     taker_schedules: Mapped[List["Schedule"]] = relationship(
#         "Schedule", 
#         foreign_keys="Schedule.taker_id", 
#         back_populates="taker"
#     )
#     notification_settings: Mapped[List["NotificationSetting"]] = relationship(
#         "NotificationSetting", 
#         back_populates="user",
#         cascade="all, delete-orphan"
#     )
#     schedule_history: Mapped[List["ScheduleHistory"]] = relationship(
#         "ScheduleHistory", 
#         back_populates="user"
#     )
    
#     # 索引
#     __table_args__ = (
#         Index("idx_email", "email"),
#         Index("idx_status", "status"),
#         Index("idx_deleted_at", "deleted_at"),
#         Index("idx_source", "source"),
#     )
    
#     def __repr__(self) -> str:
#         """字串表示。"""
#         return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


# # ===== 行程模型 =====
# class Schedule(Base, TimestampMixin, SoftDeleteMixin, SourceMixin):
#     """
#     行程資料表模型。
    
#     包含時段管理、狀態追蹤、會議資訊等。
#     """
#     __tablename__ = "schedules"
    
#     # 主鍵
#     id: Mapped[int] = mapped_column(
#         Integer, 
#         primary_key=True, 
#         autoincrement=True, 
#         comment="行程ID"
#     )
    
#     # 角色和狀態
#     role: Mapped[ScheduleRole] = mapped_column(
#         SQLEnum(ScheduleRole), 
#         nullable=False, 
#         comment="角色：GIVER=提供者、TAKER=預約者"
#     )
#     status: Mapped[ScheduleStatus] = mapped_column(
#         SQLEnum(ScheduleStatus), 
#         default=ScheduleStatus.DRAFT, 
#         nullable=False, 
#         comment="狀態"
#     )
    
#     # 關聯資訊
#     giver_id: Mapped[int] = mapped_column(
#         Integer, 
#         ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"), 
#         nullable=False, 
#         comment="Giver 使用者 ID"
#     )
#     taker_id: Mapped[Optional[int]] = mapped_column(
#         Integer, 
#         ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), 
#         nullable=True, 
#         comment="Taker 使用者 ID，可為 NULL"
#     )
    
#     # 時段資訊
#     date: Mapped[date] = mapped_column(
#         Date, 
#         nullable=False, 
#         comment="日期 (yyyy-mm-dd)"
#     )
#     start_time: Mapped[time] = mapped_column(
#         Time, 
#         nullable=False, 
#         comment="開始時間 (hh:mm)"
#     )
#     end_time: Mapped[time] = mapped_column(
#         Time, 
#         nullable=False, 
#         comment="結束時間 (hh:mm)"
#     )
#     timezone: Mapped[str] = mapped_column(
#         String(50), 
#         default="Asia/Taipei", 
#         nullable=False, 
#         comment="時區"
#     )
    
#     # 會議資訊
#     location: Mapped[Optional[str]] = mapped_column(
#         String(255), 
#         nullable=True, 
#         comment="地點（實體或線上）"
#     )
#     meeting_type: Mapped[MeetingType] = mapped_column(
#         SQLEnum(MeetingType), 
#         default=MeetingType.ONLINE, 
#         nullable=False, 
#         comment="會議類型"
#     )
#     meeting_url: Mapped[Optional[str]] = mapped_column(
#         String(500), 
#         nullable=True, 
#         comment="線上會議連結"
#     )
    
#     # 其他資訊
#     note: Mapped[Optional[str]] = mapped_column(
#         Text, 
#         nullable=True, 
#         comment="備註，可為空"
#     )
#     priority: Mapped[int] = mapped_column(
#         Integer, 
#         default=0, 
#         nullable=False, 
#         comment="優先級（0-9，數字越大優先級越高）"
#     )
#     tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(
#         JSON, 
#         nullable=True, 
#         comment="標籤（JSON 格式）"
#     )
    
#     # 關聯關係
#     giver: Mapped[User] = relationship(
#         "User", 
#         foreign_keys=[giver_id], 
#         back_populates="giver_schedules"
#     )
#     taker: Mapped[Optional[User]] = relationship(
#         "User", 
#         foreign_keys=[taker_id], 
#         back_populates="taker_schedules"
#     )
#     history: Mapped[List["ScheduleHistory"]] = relationship(
#         "ScheduleHistory", 
#         back_populates="schedule",
#         cascade="all, delete-orphan"
#     )
    
#     # 檢查約束
#     __table_args__ = (
#         CheckConstraint("start_time < end_time", name="chk_time_order"),
#         CheckConstraint("priority >= 0 AND priority <= 9", name="chk_priority_range"),
#         Index("idx_giver_id", "giver_id"),
#         Index("idx_taker_id", "taker_id"),
#         Index("idx_schedule_date", "date"),
#         Index("idx_schedule_status", "status"),
#         Index("idx_schedule_deleted_at", "deleted_at"),
#         Index("idx_schedule_date_status", "date", "status"),
#         Index("idx_schedule_giver_date", "giver_id", "date"),
#         Index("idx_schedule_taker_date", "taker_id", "date"),
#     )
    
#     def __repr__(self) -> str:
#         """字串表示。"""
#         return f"<Schedule(id={self.id}, role='{self.role}', date={self.date}, start_time={self.start_time}, end_time={self.end_time})>"


# # ===== 行程歷史記錄模型 =====
# class ScheduleHistory(Base):
#     """
#     行程歷史記錄表模型。
    
#     追蹤行程狀態變更和操作歷史。
#     """
#     __tablename__ = "schedule_history"
    
#     # 主鍵
#     id: Mapped[int] = mapped_column(
#         Integer, 
#         primary_key=True, 
#         autoincrement=True, 
#         comment="歷史記錄 ID"
#     )
    
#     # 關聯資訊
#     schedule_id: Mapped[int] = mapped_column(
#         Integer, 
#         ForeignKey("schedules.id", ondelete="CASCADE", onupdate="CASCADE"), 
#         nullable=False, 
#         comment="行程 ID"
#     )
#     user_id: Mapped[Optional[int]] = mapped_column(
#         Integer, 
#         ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), 
#         nullable=True, 
#         comment="操作使用者 ID"
#     )
    
#     # 操作資訊
#     action: Mapped[str] = mapped_column(
#         String(50), 
#         nullable=False, 
#         comment="操作類型（CREATE, UPDATE, DELETE, STATUS_CHANGE等）"
#     )
#     old_status: Mapped[Optional[ScheduleStatus]] = mapped_column(
#         SQLEnum(ScheduleStatus), 
#         nullable=True, 
#         comment="舊狀態"
#     )
#     new_status: Mapped[Optional[ScheduleStatus]] = mapped_column(
#         SQLEnum(ScheduleStatus), 
#         nullable=True, 
#         comment="新狀態"
#     )
#     changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(
#         JSON, 
#         nullable=True, 
#         comment="變更內容（JSON 格式）"
#     )
    
#     # 追蹤資訊
#     ip_address: Mapped[Optional[str]] = mapped_column(
#         String(45), 
#         nullable=True, 
#         comment="操作者 IP 位址"
#     )
#     user_agent: Mapped[Optional[str]] = mapped_column(
#         String(500), 
#         nullable=True, 
#         comment="使用者代理字串"
#     )
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime, 
#         default=func.now(), 
#         nullable=False, 
#         comment="記錄時間"
#     )
    
#     # 關聯關係
#     schedule: Mapped[Schedule] = relationship(
#         "Schedule", 
#         back_populates="history"
#     )
#     user: Mapped[Optional[User]] = relationship(
#         "User", 
#         back_populates="schedule_history"
#     )
    
#     # 索引
#     __table_args__ = (
#         Index("idx_schedule_id", "schedule_id"),
#         Index("idx_user_id", "user_id"),
#         Index("idx_action", "action"),
#         Index("idx_created_at", "created_at"),
#     )
    
#     def __repr__(self) -> str:
#         """字串表示。"""
#         return f"<ScheduleHistory(id={self.id}, schedule_id={self.schedule_id}, action='{self.action}')>"


# # ===== 通知設定模型 =====
# class NotificationSetting(Base, TimestampMixin):
#     """
#     通知設定表模型。
    
#     管理使用者的通知偏好設定。
#     """
#     __tablename__ = "notification_settings"
    
#     # 主鍵
#     id: Mapped[int] = mapped_column(
#         Integer, 
#         primary_key=True, 
#         autoincrement=True, 
#         comment="設定 ID"
#     )
    
#     # 關聯資訊
#     user_id: Mapped[int] = mapped_column(
#         Integer, 
#         ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), 
#         nullable=False, 
#         comment="使用者 ID"
#     )
    
#     # 通知設定
#     type: Mapped[NotificationType] = mapped_column(
#         SQLEnum(NotificationType), 
#         nullable=False, 
#         comment="通知類型（EMAIL, SMS, PUSH, WEBHOOK等）"
#     )
#     channel: Mapped[NotificationChannel] = mapped_column(
#         SQLEnum(NotificationChannel), 
#         nullable=False, 
#         comment="通知管道（SCHEDULE_REMINDER, STATUS_CHANGE, SYSTEM_ANNOUNCEMENT等）"
#     )
#     enabled: Mapped[bool] = mapped_column(
#         Boolean, 
#         default=True, 
#         nullable=False, 
#         comment="是否啟用"
#     )
#     settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
#         JSON, 
#         nullable=True, 
#         comment="通知設定（JSON 格式）"
#     )
    
#     # 關聯關係
#     user: Mapped[User] = relationship(
#         "User", 
#         back_populates="notification_settings"
#     )
    
#     # 索引和唯一約束
#     __table_args__ = (
#         Index("idx_user_id", "user_id"),
#         Index("idx_type", "type"),
#         Index("idx_enabled", "enabled"),
#         # 唯一約束：同一使用者的同一類型和管道只能有一個設定
#         {"sqlite_on_conflict": "REPLACE"},  # SQLite 支援
#     )
    
#     def __repr__(self) -> str:
#         """字串表示。"""
#         return f"<NotificationSetting(id={self.id}, user_id={self.user_id}, type='{self.type}', channel='{self.channel}')>" 