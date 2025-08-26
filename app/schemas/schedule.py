"""
時段相關的 Pydantic 資料模型。

定義時段管理相關的請求和回應模型。
"""

# ===== 標準函式庫 =====
from datetime import date, datetime, time

# ===== 第三方套件 =====
from pydantic import BaseModel, ConfigDict, Field

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum


class ScheduleData(BaseModel):
    """單一時段資料模型"""

    giver_id: int = Field(..., description="Giver ID", gt=0)
    taker_id: int | None = Field(None, description="Taker ID（可選）", gt=0)
    status: ScheduleStatusEnum = Field(
        default=ScheduleStatusEnum.DRAFT,
        description="時段狀態（後端會根據操作者角色自動決定：GIVER→AVAILABLE，TAKER→PENDING，其他→DRAFT）",
    )
    schedule_date: date = Field(..., description="時段日期", alias="date")
    start_time: time = Field(..., description="開始時間")
    end_time: time = Field(..., description="結束時間")
    note: str | None = Field(None, description="備註（最多255字元）", max_length=255)


class ScheduleCreateRequest(BaseModel):
    """批量建立時段的 API 請求模型"""

    schedules: list[ScheduleData] = Field(..., description="要建立的時段列表")
    created_by: int = Field(..., description="建立者的使用者 ID（必填）")
    created_by_role: UserRoleEnum = Field(..., description="建立者的角色（必填）")


class ScheduleUpdateData(BaseModel):
    """部分更新時段的資料模型 - 所有欄位都是可選的"""

    giver_id: int | None = Field(None, description="Giver ID")
    taker_id: int | None = Field(None, description="Taker ID")
    status: ScheduleStatusEnum | None = Field(
        default=None,
        description="時段狀態（可選，如果不傳此欄位則不更新狀態，如果傳 null 則會拋出驗證錯誤）",
    )
    schedule_date: date | None = Field(None, description="時段日期", alias="date")
    start_time: time | None = Field(None, description="開始時間")
    end_time: time | None = Field(None, description="結束時間")
    note: str | None = Field(None, description="備註")


class ScheduleUpdateRequest(BaseModel):
    """完整更新時段的 API 請求模型（用於 PUT 方法）"""

    schedule: ScheduleData = Field(..., description="完整的時段資料（所有欄位必填）")
    updated_by: int = Field(..., description="操作者的使用者 ID（必填）")
    updated_by_role: UserRoleEnum = Field(..., description="操作者的角色（必填）")


class SchedulePartialUpdateRequest(BaseModel):
    """部分更新時段的 API 請求模型"""

    schedule: ScheduleUpdateData = Field(
        ..., description="要更新的時段資料（部分欄位）"
    )
    updated_by: int = Field(..., description="操作者的使用者 ID（必填）")
    updated_by_role: UserRoleEnum = Field(..., description="操作者的角色（必填）")


class ScheduleDeleteRequest(BaseModel):
    """刪除時段的 API 請求模型"""

    deleted_by: int = Field(..., description="刪除者的使用者 ID（必填）")
    deleted_by_role: UserRoleEnum = Field(..., description="刪除者的角色（必填）")


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
