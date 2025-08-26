"""
時段管理 API 路由模組。

提供時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.decorators import handle_api_errors

# ===== 本地模組 =====
from app.models.database import get_db
from app.schemas import (
    ScheduleCreateRequest,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleResponse,
)
from app.services import schedule_service

# 建立路由器
router = APIRouter(prefix="/api/v1", tags=["Schedules"])


# ===== API 端點 =====


@router.post(
    "/schedules",
    response_model=list[ScheduleResponse],
    status_code=status.HTTP_201_CREATED,
)
@handle_api_errors()  # 自動檢測為 POST 方法，使用 201 狀態碼
async def create_schedules(
    request: ScheduleCreateRequest, db: Session = Depends(get_db)
) -> list[ScheduleResponse]:
    """
    建立多個時段。

    接收時段列表和操作者資訊，並批量建立到資料庫中。
    所有的時段建立操作，都需要提供操作者資訊，以確保安全性和審計追蹤。

    Args:
        request: 包含時段列表和操作者資訊的請求
        db: 資料庫會話依賴注入

    Returns:
        list[ScheduleResponse]: 建立成功的時段列表

    Raises:
        HTTPException: 當建立失敗時拋出對應的 HTTP 錯誤
    """
    # 業務邏輯
    # 使用 SERVICE 層建立時段，傳遞建立者資訊
    schedule_objects = schedule_service.create_schedules(
        db,
        request.schedules,
        created_by=request.created_by,
        created_by_role=request.created_by_role,
    )

    # 格式轉換：將 Python 物件（如 SQLAlchemy 模型）轉換為 Pydantic 模型
    return [ScheduleResponse.model_validate(schedule) for schedule in schedule_objects]


@router.get(
    "/schedules",
    response_model=list[ScheduleResponse],
    status_code=status.HTTP_200_OK,
)
@handle_api_errors()  # 自動檢測為 GET 方法，使用 200 狀態碼
async def get_schedules(
    giver_id: int | None = None,
    taker_id: int | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
) -> list[ScheduleResponse]:
    """
    取得時段列表。

    可選擇性地根據 giver_id、taker_id 和 status 進行篩選。

    Args:
        giver_id: 可選的 Giver ID 篩選條件
        taker_id: 可選的 Taker ID 篩選條件
        status_filter: 可選的狀態篩選條件
        db: 資料庫會話依賴注入

    Returns:
        list[ScheduleResponse]: 符合條件的時段列表

    Raises:
        HTTPException: 當查詢失敗時拋出對應的 HTTP 錯誤
    """
    schedules = schedule_service.get_schedules(db, giver_id, taker_id, status_filter)
    return [ScheduleResponse.model_validate(schedule) for schedule in schedules]


@router.get(
    "/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
)
@handle_api_errors()  # 自動檢測為 GET 方法，使用 200 狀態碼
async def get_schedule(
    schedule_id: int, db: Session = Depends(get_db)
) -> ScheduleResponse:
    """
    根據 ID 取得單一時段。

    Args:
        schedule_id: 時段 ID
        db: 資料庫會話依賴注入

    Returns:
        ScheduleResponse: 時段資料

    Raises:
        HTTPException: 當時段不存在時拋出 404 錯誤
    """
    schedule = schedule_service.get_schedule_by_id(db, schedule_id)
    return ScheduleResponse.model_validate(schedule)


@router.patch(
    "/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
)
@handle_api_errors()  # 自動檢測為 PATCH 方法，使用 200 狀態碼
async def update_schedule(
    schedule_id: int,
    request: SchedulePartialUpdateRequest,
    db: Session = Depends(get_db),
) -> ScheduleResponse:
    """
    部分更新時段。

    更新指定的時段資料，只需要提供要更新的欄位。
    所有的時段更新操作，都需要提供操作者資訊，以確保安全性和審計追蹤。

    Args:
        schedule_id: 時段 ID
        request: 包含更新資料和操作者資訊的請求
        db: 資料庫會話依賴注入

    Returns:
        ScheduleResponse: 更新後的時段資料

    Raises:
        HTTPException: 當時段不存在或更新失敗時拋出錯誤
    """
    # 將 Pydantic 模型的物件，轉換為字典格式，只包含非 None 的欄位，避免把「空值」也更新到資料庫
    update_data = request.schedule.model_dump(exclude_none=True)
    # 處理 date 欄位的別名 - 將 date 轉換為 schedule_date，以符合資料庫或後端函式期望的欄位名稱
    if "date" in update_data:
        update_data["schedule_date"] = update_data.pop("date")

    updated_schedule = schedule_service.update_schedule(
        db,
        schedule_id,
        updated_by=request.updated_by,
        updated_by_role=request.updated_by_role,
        **update_data,  # 字典解包：傳遞更新資料
    )
    return ScheduleResponse.model_validate(updated_schedule)


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@handle_api_errors()  # 自動檢測為 DELETE 方法，使用 204 狀態碼
async def delete_schedule(
    schedule_id: int, request: ScheduleDeleteRequest, db: Session = Depends(get_db)
) -> None:
    """
    刪除時段。

    刪除指定的時段。
    所有的時段刪除操作，都需要提供操作者資訊，以確保安全性和審計追蹤。

    Args:
        schedule_id: 時段 ID
        request: 包含操作者資訊的請求
        db: 資料庫會話依賴注入

    Returns:
        None

    Raises:
        HTTPException: 當時段不存在或刪除失敗時拋出錯誤
    """
    success = schedule_service.delete_schedule(
        db,
        schedule_id,
        deleted_by=request.deleted_by,
        deleted_by_role=request.deleted_by_role,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="時段不存在或無法刪除"
        )
