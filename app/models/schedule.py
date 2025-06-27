# 使用 SQLAlchemy ORM（物件關聯對應）定義資料庫結構
from sqlalchemy import Column, Integer, String, Date, Time
from .database import Base  # 從 database.py 引入統一的 Base 類別

# 定義資料表模型，繼承 Base 類別：Schedule 與資料庫對應（SQLAlchemy 模型）
class Schedule(Base):
    # 定義資料表名稱為 "schedules"，這是資料庫中的資料表名稱
    __tablename__ = "schedules"

    # 定義資料表欄位
    id = Column(Integer, primary_key=True, index=True)  # 主鍵，自動遞增
    name = Column(String, nullable=False)  # 預約人姓名，不允許為空
    date = Column(Date, index=True)  # 日期，格式：YYYY-MM-DD
    weekday = Column(String)  # 星期
    start_time = Column(Time)  # 開始時間，格式：HH:MM
    end_time = Column(Time)  # 結束時間，格式：HH:MM
    note = Column(String, nullable=True)  # 備註，允許欄位為空值
