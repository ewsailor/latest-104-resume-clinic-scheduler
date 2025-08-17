"""
時段相關的 Pydantic 資料模型。

定義時段管理相關的請求和回應模型。
"""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ScheduleStatusEnum, UserRoleEnum


class ScheduleCreate(BaseModel):
    """建立時段的請求模型"""

    giver_id: int = Field(..., description="Giver ID", gt=0)
    taker_id: int | None = Field(None, description="Taker ID（可選）", gt=0)
    status: ScheduleStatusEnum | None = Field(
        default=None,
        description="時段狀態（可選，後端會根據操作者角色自動決定：GIVER→AVAILABLE，TAKER→PENDING，其他→DRAFT）",
    )
    schedule_date: date = Field(..., description="時段日期", alias="date")
    start_time: time = Field(..., description="開始時間")
    end_time: time = Field(..., description="結束時間")
    note: str | None = Field(None, description="備註（最多100字）", max_length=100)


class ScheduleCreateWithOperator(BaseModel):
    """帶有操作者資訊的建立時段請求模型"""

    schedules: list[ScheduleCreate] = Field(..., description="要建立的時段列表")
    updated_by: int = Field(..., description="操作者的使用者 ID（必填）")
    updated_by_role: UserRoleEnum = Field(..., description="操作者的角色（必填）")


class ScheduleUpdate(BaseModel):
    """部分更新時段的請求模型 - 所有欄位都是可選的"""

    giver_id: int | None = Field(None, description="Giver ID")
    taker_id: int | None = Field(None, description="Taker ID")
    status: ScheduleStatusEnum | None = Field(None, description="時段狀態")
    schedule_date: date | None = Field(None, description="時段日期", alias="date")
    start_time: time | None = Field(None, description="開始時間")
    end_time: time | None = Field(None, description="結束時間")
    note: str | None = Field(None, description="備註")


class ScheduleUpdateWithOperator(BaseModel):
    """帶有操作者資訊的完整更新時段請求模型（用於 PUT 方法）"""

    schedule_data: ScheduleCreate = Field(
        ..., description="完整的時段資料（所有欄位必填）"
    )
    updated_by: int = Field(..., description="操作者的使用者 ID（必填）")
    updated_by_role: UserRoleEnum = Field(..., description="操作者的角色（必填）")


class SchedulePartialUpdateWithOperator(BaseModel):
    """帶有操作者資訊的部分更新時段請求模型"""

    schedule_data: ScheduleUpdate = Field(
        ..., description="要更新的時段資料（部分欄位）"
    )
    updated_by: int = Field(..., description="操作者的使用者 ID（必填）")
    updated_by_role: UserRoleEnum = Field(..., description="操作者的角色（必填）")


class ScheduleDeleteWithOperator(BaseModel):
    """帶有操作者資訊的刪除時段請求模型"""

    updated_by: int = Field(..., description="操作者的使用者 ID（必填）")
    updated_by_role: UserRoleEnum = Field(..., description="操作者的角色（必填）")


class ScheduleResponse(BaseModel):
    """時段回應模型"""

    id: int
    giver_id: int
    taker_id: int | None
    status: ScheduleStatusEnum
    date: date
    start_time: time
    end_time: time
    note: str | None
    created_at: datetime  # 建立時間（本地時間）
    created_by: int | None = Field(None, description="建立者的使用者 ID")
    created_by_role: UserRoleEnum | None = Field(None, description="建立者角色")
    updated_at: datetime  # 更新時間（本地時間）
    updated_by: int | None = Field(None, description="最後更新者的使用者 ID")
    updated_by_role: UserRoleEnum | None = Field(None, description="最後更新者的角色")
    deleted_at: datetime | None = Field(None, description="軟刪除標記（本地時間）")
    deleted_by: int | None = Field(None, description="刪除者的使用者 ID")
    deleted_by_role: UserRoleEnum | None = Field(None, description="刪除者角色")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
