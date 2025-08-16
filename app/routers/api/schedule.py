"""
時段管理 API 路由模組。

提供時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

from typing import List  # 保留 List，因為 FastAPI response_model 需要

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status  # 路由和錯誤處理
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.crud import schedule_crud  # CRUD 操作
from app.models.database import get_db  # 資料庫連接
from app.schemas import (  # 資料模型
    ScheduleCreateWithOperator,
    ScheduleDeleteWithOperator,
    SchedulePartialUpdateWithOperator,
    ScheduleResponse,
)
from app.utils.error_handler import (
    APIError,
    BusinessLogicError,
    DatabaseError,
    NotFoundError,
    create_http_exception_from_api_error,
    safe_execute,
)

# 建立路由器
router = APIRouter(prefix="/api/v1", tags=["Schedules"])


# ===== API 端點 =====


@router.post(
    "/schedules",
    response_model=List[ScheduleResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_schedules(
    request: ScheduleCreateWithOperator, db: Session = Depends(get_db)
) -> list[ScheduleResponse]:
    """
    建立多個時段。

    接收時段列表和操作者資訊並批量建立到資料庫中。
    所有的時段建立操作都需要提供操作者資訊以確保安全性和審計追蹤。

    Args:
        request: 包含時段列表和操作者資訊的請求
        db: 資料庫會話依賴注入

    Returns:
        list[ScheduleResponse]: 建立成功的時段列表

    Raises:
        HTTPException: 當建立失敗時拋出 400 錯誤
    """
    try:
        # 使用 CRUD 層建立時段，傳遞操作者資訊
        schedule_objects = schedule_crud.create_schedules(
            db,
            request.schedules,
            operator_user_id=request.operator_user_id,
            operator_role=request.operator_role,
        )

        # 轉換為回應格式
        return [
            ScheduleResponse.model_validate(schedule) for schedule in schedule_objects
        ]

    except APIError as e:
        # 處理自定義 API 錯誤
        raise create_http_exception_from_api_error(e)
    except Exception as e:
        # 處理其他未預期的錯誤
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立時段時發生內部錯誤: {str(e)}",
        )


@router.get("/schedules", response_model=List[ScheduleResponse])
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
    """
    try:
        # 使用 CRUD 層查詢時段
        schedules = schedule_crud.get_schedules(db, giver_id, taker_id, status_filter)
        # 轉換為回應格式 - 使用 model_validate 替代 from_orm
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    except APIError as e:
        # 處理自定義 API 錯誤
        raise create_http_exception_from_api_error(e)
    except Exception as e:
        # 處理其他未預期的錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢時段失敗: {str(e)}",
        )


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
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
        # 處理自定義 API 錯誤
        raise create_http_exception_from_api_error(e)
    except Exception as e:
        # 處理其他未預期的錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢時段失敗: {str(e)}",
        )


@router.patch("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    request: SchedulePartialUpdateWithOperator,
    db: Session = Depends(get_db),
) -> ScheduleResponse:
    """
    部分更新時段。

    更新指定的時段資料，只需要提供要更新的欄位。
    所有的時段更新操作都需要提供操作者資訊以確保安全性和審計追蹤。

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
        update_data = request.schedule_data.model_dump(exclude_none=True)
        # 處理 date 欄位的別名 - 將 date 轉換為 schedule_date
        if "date" in update_data:
            update_data["schedule_date"] = update_data.pop("date")

        updated_schedule = schedule_crud.update_schedule(
            db,
            schedule_id,
            updated_by_user_id=request.operator_user_id,
            operator_role=request.operator_role,
            **update_data,
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
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"更新時段失敗: {str(e)}"
        )


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int, request: ScheduleDeleteWithOperator, db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    刪除時段。

    刪除指定的時段。
    所有的時段刪除操作都需要提供操作者資訊以確保安全性和審計追蹤。

    Args:
        schedule_id: 時段 ID
        request: 包含操作者資訊的請求
        db: 資料庫會話依賴注入

    Returns:
        dict: 刪除成功的訊息

    Raises:
        HTTPException: 當時段不存在或刪除失敗時拋出錯誤
    """
    try:
        success = schedule_crud.delete_schedule(
            db,
            schedule_id,
            operator_user_id=request.operator_user_id,
            operator_role=request.operator_role,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="時段不存在"
            )
        return {"message": "時段刪除成功"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"刪除時段失敗: {str(e)}"
        )
