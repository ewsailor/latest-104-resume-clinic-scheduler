"""時段管理 API 路由模組。

提供時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.decorators import handle_api_errors_async
from app.models.database import get_db
from app.schemas import (
    ScheduleCreateRequest,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleResponse,
)
from app.services import schedule_service

router = APIRouter(prefix="/api/v1", tags=["Schedules"])


@router.post(
    "/schedules",
    response_model=list[ScheduleResponse],
    status_code=status.HTTP_201_CREATED,
)
@handle_api_errors_async()
async def create_schedules(
    request: ScheduleCreateRequest,
    db: Session = Depends(get_db),
) -> list[ScheduleResponse]:
    """建立多個時段。"""
    # 驗證每個時段的時間邏輯
    for schedule in request.schedules:
        if schedule.start_time >= schedule.end_time:
            raise HTTPException(status_code=400, detail="開始時間必須早於結束時間")

    schedules = schedule_service.create_schedules(
        db,
        request.schedules,
        created_by=request.created_by,
        created_by_role=request.created_by_role,
    )

    # 格式轉換：將 Python 物件（如 SQLAlchemy 模型）轉換為 Pydantic 模型
    return [ScheduleResponse.model_validate(schedule) for schedule in schedules]


@router.get(
    "/schedules",
    response_model=list[ScheduleResponse],
    status_code=status.HTTP_200_OK,
)
@handle_api_errors_async()
async def list_schedules(
    giver_id: int | None = None,
    taker_id: int | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
) -> list[ScheduleResponse]:
    """取得時段列表。"""
    schedules = schedule_service.list_schedules(
        db,
        giver_id,
        taker_id,
        status_filter,
    )

    return [ScheduleResponse.model_validate(schedule) for schedule in schedules]


@router.get(
    "/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
)
@handle_api_errors_async()
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
) -> ScheduleResponse:
    """根據 ID 取得單一時段。"""
    schedule = schedule_service.get_schedule(db, schedule_id)

    return ScheduleResponse.model_validate(schedule)


@router.patch(
    "/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
)
@handle_api_errors_async()
async def update_schedule(
    schedule_id: int,
    request: SchedulePartialUpdateRequest,
    db: Session = Depends(get_db),
) -> ScheduleResponse:
    """部分更新時段。"""
    # 將 Pydantic 模型的物件，轉換為字典格式，只包含非 None 的欄位，避免把「空值」也更新到資料庫
    update_data = request.schedule.model_dump(exclude_none=True)
    # 處理 date 欄位的別名 - 將 date 轉換為 schedule_date，以符合資料庫或後端函式期望的欄位名稱
    if "date" in update_data:
        update_data["schedule_date"] = update_data.pop("date")

    schedule = schedule_service.update_schedule(
        db,
        schedule_id,
        updated_by=request.updated_by,
        updated_by_role=request.updated_by_role,
        **update_data,  # 字典解包：傳遞更新資料
    )

    return ScheduleResponse.model_validate(schedule)


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@handle_api_errors_async()
async def delete_schedule(
    schedule_id: int,
    request: ScheduleDeleteRequest,
    db: Session = Depends(get_db),
) -> None:
    """刪除時段。"""
    result = schedule_service.delete_schedule(
        db,
        schedule_id,
        deleted_by=request.deleted_by,
        deleted_by_role=request.deleted_by_role,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="時段不存在或無法刪除"
        )
