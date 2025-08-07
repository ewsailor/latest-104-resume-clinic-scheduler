"""
時段管理 API 路由模組。

提供時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

from typing import List, Optional  # 型別提示

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status  # 路由和錯誤處理

# ===== 本地模組 =====
from app.crud import schedule_crud  # CRUD 操作
from app.models.database import get_db  # 資料庫連接
from app.schemas import ScheduleCreate, ScheduleResponse, UserCreate  # 資料模型

# 建立路由器
router = APIRouter(prefix="/api", tags=["Schedules"])


# ===== API 端點 =====
@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db=Depends(get_db)):
    """
    建立使用者。

    Args:
        user: 使用者資料
        db: 資料庫會話依賴注入

    Returns:
        dict: 建立成功的使用者資訊
    """
    try:
        # 使用 CRUD 層建立使用者
        new_user = schedule_crud.create_user(db, user)
        return {"message": "使用者建立成功", "user": new_user.to_dict()}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"建立使用者失敗: {str(e)}"
        )


@router.post(
    "/schedules",
    response_model=List[ScheduleResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_schedules(schedules: List[ScheduleCreate], db=Depends(get_db)):
    """
    建立多個時段。

    接收時段列表並批量建立到資料庫中。

    Args:
        schedules: 要建立的時段列表
        db: 資料庫會話依賴注入

    Returns:
        List[ScheduleResponse]: 建立成功的時段列表

    Raises:
        HTTPException: 當建立失敗時拋出 400 錯誤
    """
    try:
        # 使用 CRUD 層建立時段
        schedule_objects = schedule_crud.create_schedules(db, schedules)

        # 轉換為回應格式 - 使用 model_validate 替代 from_orm
        return [
            ScheduleResponse.model_validate(schedule) for schedule in schedule_objects
        ]

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"建立時段失敗: {str(e)}"
        )


@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    giver_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db=Depends(get_db),
):
    """
    取得時段列表。

    可選擇性地根據 giver_id 和 status 進行篩選。

    Args:
        giver_id: 可選的 Giver ID 篩選條件
        status_filter: 可選的狀態篩選條件
        db: 資料庫會話依賴注入

    Returns:
        List[ScheduleResponse]: 符合條件的時段列表
    """
    try:
        # 使用 CRUD 層查詢時段
        schedules = schedule_crud.get_schedules(db, giver_id, status_filter)
        # 轉換為回應格式 - 使用 model_validate 替代 from_orm
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢時段失敗: {str(e)}",
        )
