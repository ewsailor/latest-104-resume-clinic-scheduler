# app/schemas/schedule.py
from pydantic import BaseModel, validator
from datetime import date, time
from typing import List, Optional

# Pydantic models for schedule：驗證 API 請求/回應的輸入格式，確保輸入資料正確。
class ScheduleBase(BaseModel):
    """基礎排程模型，包含共同欄位"""
    name: str
    note: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    """建立新排程時的資料驗證"""
    date: date
    weekday: str
    start: time  # 使用 time 型別
    end: time    # 使用 time 型別
    startMinutes: int
    endMinutes: int

    class Config:
        from_attributes = True

class ScheduleUpdate(ScheduleBase):
    """更新排程時的資料驗證"""
    date: Optional[date] = None
    weekday: Optional[str] = None
    start: Optional[time] = None
    end: Optional[time] = None
    startMinutes: Optional[int] = None
    endMinutes: Optional[int] = None

class BatchScheduleCreate(ScheduleBase):
    """批量建立排程時的資料驗證"""
    start_date: date
    weeks: int
    weekdays: List[str]  # 例如 ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    start_time: time
    end_time: time

class ScheduleResponse(ScheduleBase):
    """API 回應的資料模型"""
    id: int
    date: date
    weekday: str
    start: time
    end: time

    class Config:
        from_attributes = True
        
# class ScheduleBase(BaseModel):
#     """基礎排程模型，包含共同欄位"""
#     name: str
#     note: Optional[str] = None

# class ScheduleCreate(ScheduleBase):
#     """建立新排程時的資料驗證"""
#     date: date
#     weekday: str
#     start: time
#     end: time
#     startMinutes: int
#     endMinutes: int

#     class Config:
#         from_attributes = True

# class ScheduleUpdate(ScheduleBase):
#     """更新排程時的資料驗證"""
#     date: Optional[date] = None
#     weekday: Optional[str] = None
#     start: Optional[time] = None
#     end: Optional[time] = None
#     startMinutes: Optional[int] = None
#     endMinutes: Optional[int] = None

# class BatchScheduleCreate(ScheduleBase):
#     """批量建立排程時的資料驗證"""
#     start_date: date
#     weeks: int
#     weekdays: List[str]
#     start_time: time
#     end_time: time

# class ScheduleResponse(ScheduleBase):
#     """API 回應的資料模型"""
#     id: int
#     date: date
#     weekday: str
#     start_time: time
#     end_time: time

#     class Config:
#         from_attributes = True
