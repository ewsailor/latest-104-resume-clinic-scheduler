"""
時段管理 API 路由模組。

提供時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

# 移除 List import，因為 Python 3.9+ 可以直接使用 list[]

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status  # 路由和錯誤處理
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.crud import schedule_crud  # CRUD 操作
from app.models.database import get_db  # 資料庫連接
from app.schemas import (  # 資料模型
    ScheduleCreateRequest,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleResponse,
)
from app.utils.error_handler import (
    APIError,
    ErrorMessages,
    create_http_exception_from_api_error,
    get_schedule_create_responses,
    get_schedule_delete_responses,
    get_schedule_detail_responses,
    get_schedule_list_responses,
    get_schedule_update_responses,
    safe_execute,
)

# 建立路由器
router = APIRouter(prefix="/api/v1", tags=["Schedules"])


# ===== API 端點 =====


@router.post(
    "/schedules",
    response_model=list[ScheduleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="建立多個時段",
    description="Giver 新增自己的可預約時間，供 Taker 選擇預約。支援批量建立多個時段。",
    responses=get_schedule_create_responses(),
)
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
    try:
        # 業務邏輯
        # 使用 CRUD 層建立時段，傳遞建立者資訊
        schedule_objects = schedule_crud.create_schedules(
            db,
            request.schedules,
            created_by=request.created_by,
            created_by_role=request.created_by_role,
        )

        # 格式轉換：將 Python 物件（如 SQLAlchemy 模型）轉換為 Pydantic 模型
        return [
            ScheduleResponse.model_validate(schedule) for schedule in schedule_objects
        ]

    except APIError as e:
        # 自定義業務錯誤：時段重疊、使用者不存在等
        # 不需要回滾，因為還沒開始修改資料庫
        raise create_http_exception_from_api_error(e)
    except Exception as e:
        # 其他未預期的系統錯誤，如資料庫連線失敗、記憶體不足等
        # 需要回滾，因為可能已經部分修改了資料庫
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ErrorMessages.SCHEDULE_CREATE_FAILED}: {str(e)}",
        )


@router.get(
    "/schedules",
    response_model=list[ScheduleResponse],
    status_code=status.HTTP_200_OK,
    summary="取得時段列表",
    description="取得時段列表，可選擇性地根據 giver_id、taker_id 和 status 進行篩選。支援多種篩選條件組合查詢。",
    responses=get_schedule_list_responses(),
)
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
    try:
        schedules = schedule_crud.get_schedules(db, giver_id, taker_id, status_filter)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    except APIError as e:
        raise create_http_exception_from_api_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ErrorMessages.SCHEDULE_LIST_QUERY_FAILED}: {str(e)}",
        )


@router.get(
    "/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
    summary="取得單一時段",
    description="根據時段 ID 取得單一時段的詳細資料。",
    responses=get_schedule_detail_responses(),
)
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
    try:
        schedule = schedule_crud.get_schedule_by_id(db, schedule_id)
        return ScheduleResponse.model_validate(schedule)

    except APIError as e:
        raise create_http_exception_from_api_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ErrorMessages.SCHEDULE_DETAIL_QUERY_FAILED}: {str(e)}",
        )


@router.patch(
    "/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
    summary="更新時段",
    description="部分更新指定的時段資料，只需要提供要更新的欄位。所有的時段更新操作都需要提供操作者資訊以確保安全性和審計追蹤。",
    responses=get_schedule_update_responses(),
)
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
    try:
        # 轉換為字典格式，只包含非 None 的欄位
        update_data = request.schedule.model_dump(exclude_none=True)
        # 處理 date 欄位的別名 - 將 date 轉換為 schedule_date
        if "date" in update_data:
            update_data["schedule_date"] = update_data.pop("date")

        updated_schedule = schedule_crud.update_schedule(
            db,
            schedule_id,
            updated_by=request.updated_by,
            updated_by_role=request.updated_by_role,
            **update_data,  # 字典解包：傳遞更新資料
        )
        if not updated_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="時段不存在"
            )
        return ScheduleResponse.model_validate(updated_schedule)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{ErrorMessages.SCHEDULE_UPDATE_FAILED}: {str(e)}",
        )


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除時段",
    description="刪除指定的時段。所有的時段刪除操作都需要提供操作者資訊以確保安全性和審計追蹤。",
    responses=get_schedule_delete_responses(),
)
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
    try:
        success = schedule_crud.delete_schedule(
            db,
            schedule_id,
            deleted_by=request.deleted_by,
            deleted_by_role=request.deleted_by_role,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="時段不存在"
            )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{ErrorMessages.SCHEDULE_DELETE_FAILED}: {str(e)}",
        )
