"""
時段相關的 Pydantic 資料模型。

定義時段管理相關的請求和回應模型，包括使用者建立、時段建立和時段回應模型。
"""

from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRoleEnum


class UserCreate(BaseModel):
    """建立使用者的請求模型"""

    name: str = Field(..., description="使用者姓名")
    email: str = Field(..., description="電子信箱")


class ScheduleCreate(BaseModel):
    """建立時段的請求模型"""

    giver_id: int = Field(..., description="Giver ID")
    taker_id: Optional[int] = Field(None, description="Taker ID")
    schedule_date: date = Field(..., description="時段日期", alias="date")
    start_time: time = Field(..., description="開始時間")
    end_time: time = Field(..., description="結束時間")
    note: Optional[str] = Field(None, description="備註")
    status: str = Field(default="AVAILABLE", description="時段狀態")


class ScheduleCreateWithOperator(BaseModel):
    """帶有操作者資訊的建立時段請求模型"""

    schedules: List[ScheduleCreate] = Field(..., description="要建立的時段列表")
    operator_user_id: Optional[int] = Field(None, description="操作者的使用者 ID")
    operator_role: Optional[UserRoleEnum] = Field(None, description="操作者的角色")


class ScheduleUpdateWithOperator(BaseModel):
    """帶有操作者資訊的更新時段請求模型"""

    schedule_data: ScheduleCreate = Field(..., description="更新的時段資料")
    operator_user_id: Optional[int] = Field(None, description="操作者的使用者 ID")
    operator_role: Optional[UserRoleEnum] = Field(None, description="操作者的角色")


class ScheduleResponse(BaseModel):
    """時段回應模型"""

    id: int
    role: str = Field(
        description="建立者角色 (由 creator_role 屬性計算)", alias="creator_role"
    )
    giver_id: int
    taker_id: Optional[int]
    date: date
    start_time: time
    end_time: time
    note: Optional[str]
    status: str
    created_at: Optional[datetime]  # 改回 datetime 類型，因為資料庫現在儲存本地時間
    updated_at: Optional[datetime]  # 改回 datetime 類型，因為資料庫現在儲存本地時間
    updated_by: Optional[int] = Field(None, description="最後更新者的使用者 ID")
    updated_by_role: Optional[UserRoleEnum] = Field(
        None, description="最後更新者的角色"
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
