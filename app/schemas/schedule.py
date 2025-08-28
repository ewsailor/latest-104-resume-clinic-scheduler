"""時段相關的 Pydantic 資料模型。

定義時段管理相關的請求和回應模型。
"""

# ===== 標準函式庫 =====
from datetime import date, datetime, time

# ===== 第三方套件 =====
from pydantic import BaseModel, ConfigDict, Field

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum


class ScheduleBase(BaseModel):
    """單一時段資料模型。"""

    giver_id: int = Field(..., description="Giver ID", gt=0, example=1)
    taker_id: int | None = Field(None, description="Taker ID（可選）", example=2)
    status: ScheduleStatusEnum = Field(
        default=ScheduleStatusEnum.DRAFT,
        description="時段狀態（後端會根據操作者角色自動決定：GIVER→AVAILABLE，TAKER→PENDING，其他→DRAFT）",
        example=ScheduleStatusEnum.AVAILABLE,
    )
    schedule_date: date = Field(
        ..., description="時段日期", alias="date", example=date(2025, 9, 15)
    )
    start_time: time = Field(..., description="開始時間", example=time(9, 0))
    end_time: time = Field(..., description="結束時間", example=time(10, 0))
    note: str | None = Field(
        None,
        description="備註（最多255字元）",
        max_length=255,
        example="下週要面試，希望能請教面試技巧",
    )


class ScheduleCreateRequest(BaseModel):
    """批量建立時段的 API 請求模型。"""

    schedules: list[ScheduleBase] = Field(
        ...,
        description="要建立的時段列表",
        min_length=1,
        example=[
            {
                "giver_id": 1,
                "taker_id": 2,
                "status": "AVAILABLE",
                "date": "2025-09-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "note": "下週要面試，希望能請教面試技巧",
            }
        ],
    )
    created_by: int = Field(..., description="建立者的 ID（必填）", gt=0, example=1)
    created_by_role: UserRoleEnum = Field(
        ..., description="建立者角色（必填）", example=UserRoleEnum.GIVER
    )


class ScheduleUpdateData(BaseModel):
    """部分更新時段的資料模型 - 所有欄位都是可選的。"""

    giver_id: int | None = Field(None, description="Giver ID", example=1)
    taker_id: int | None = Field(None, description="Taker ID", example=2)
    status: ScheduleStatusEnum | None = Field(
        default=None,
        description="時段狀態（可選，如果不傳此欄位則不更新狀態，如果傳 null 則會拋出驗證錯誤）",
        example=ScheduleStatusEnum.PENDING,
    )
    schedule_date: date | None = Field(
        None, description="時段日期", alias="date", example=date(2025, 9, 16)
    )
    start_time: time | None = Field(None, description="開始時間", example=time(14, 0))
    end_time: time | None = Field(None, description="結束時間", example=time(15, 0))
    note: str | None = Field(
        None, description="備註", max_length=255, example="模擬面試諮詢"
    )


class ScheduleUpdateRequest(BaseModel):
    """完整更新時段的 API 請求模型（用於 PUT 方法）。"""

    schedule: ScheduleBase = Field(
        ...,
        description="完整的時段資料（所有欄位必填）",
        example={
            "giver_id": 1,
            "taker_id": 2,
            "status": "PENDING",
            "date": "2025-09-17",
            "start_time": "16:00:00",
            "end_time": "17:00:00",
            "note": "職涯諮詢",
        },
    )
    updated_by: int = Field(..., description="最後更新者的 ID（必填）", gt=0, example=1)
    updated_by_role: UserRoleEnum = Field(
        ..., description="最後更新者的角色（必填）", example=UserRoleEnum.TAKER
    )


class SchedulePartialUpdateRequest(BaseModel):
    """部分更新時段的 API 請求模型。"""

    schedule: ScheduleUpdateData = Field(
        ...,
        description="要更新的時段資料（部分欄位）",
        example={"status": "PENDING", "note": "更新備註"},
    )
    updated_by: int = Field(..., description="最後更新者的 ID（必填）", gt=0, example=1)
    updated_by_role: UserRoleEnum = Field(
        ..., description="最後更新者的角色（必填）", example=UserRoleEnum.TAKER
    )


class ScheduleDeleteRequest(BaseModel):
    """刪除時段的 API 請求模型。"""

    deleted_by: int = Field(..., description="刪除者的 ID（必填）", gt=0, example=1)
    deleted_by_role: UserRoleEnum = Field(
        ..., description="刪除者角色（必填）", example=UserRoleEnum.GIVER
    )


class ScheduleResponse(BaseModel):
    """時段回應模型。"""

    id: int = Field(..., description="時段 ID", gt=0, example=1)
    giver_id: int = Field(..., description="Giver ID", gt=0, example=1)
    taker_id: int | None = Field(None, description="Taker ID", example=2)
    status: ScheduleStatusEnum = Field(
        ..., description="時段狀態", example=ScheduleStatusEnum.AVAILABLE
    )
    schedule_date: date = Field(
        ..., description="時段日期", alias="date", example=date(2025, 9, 15)
    )
    start_time: time = Field(..., description="開始時間", example=time(9, 0))
    end_time: time = Field(..., description="結束時間", example=time(10, 0))
    note: str | None = Field(
        None, description="備註", max_length=255, example="履歷健診諮詢"
    )
    created_at: datetime = Field(
        ..., description="建立時間（本地時間）", example=datetime(2025, 9, 15, 9, 0)
    )
    created_by: int | None = Field(None, description="建立者的 ID", example=1)
    created_by_role: UserRoleEnum | None = Field(
        None, description="建立者角色", example=UserRoleEnum.GIVER
    )
    updated_at: datetime = Field(
        ..., description="更新時間（本地時間）", example=datetime(2025, 9, 15, 9, 0)
    )
    updated_by: int | None = Field(None, description="最後更新者的 ID", example=1)
    updated_by_role: UserRoleEnum | None = Field(
        None, description="最後更新者的角色", example=UserRoleEnum.GIVER
    )
    deleted_at: datetime | None = Field(
        None, description="軟刪除標記（本地時間）", example=None
    )
    deleted_by: int | None = Field(None, description="刪除者的 ID", example=None)
    deleted_by_role: UserRoleEnum | None = Field(
        None, description="刪除者角色", example=None
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
