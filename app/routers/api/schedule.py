"""
時段管理 API 路由模組。

提供時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

from datetime import date, datetime, time  # 日期時間處理
from typing import List, Optional  # 型別提示

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status  # 路由和錯誤處理
from pydantic import BaseModel, Field  # 資料驗證

from app.models.database import get_db  # 資料庫連接

# ===== 本地模組 =====
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型

# 建立路由器
router = APIRouter(prefix="/api", tags=["Schedules"])


# ===== 資料模型 =====
class UserCreate(BaseModel):
    """建立使用者的請求模型"""

    name: str = Field(..., description="使用者姓名")
    email: str = Field(..., description="電子信箱")


class ScheduleCreate(BaseModel):
    """建立時段的請求模型"""

    giver_id: int = Field(..., description="Giver ID")
    schedule_date: date = Field(..., description="時段日期", alias="date")
    start_time: time = Field(..., description="開始時間")
    end_time: time = Field(..., description="結束時間")
    note: Optional[str] = Field(None, description="備註")
    status: str = Field(default="AVAILABLE", description="時段狀態")
    role: str = Field(default="GIVER", description="角色")


class ScheduleResponse(BaseModel):
    """時段回應模型"""

    id: int
    role: str
    giver_id: int
    taker_id: Optional[int]
    date: date
    start_time: time
    end_time: time
    note: Optional[str]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


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
        # 檢查 email 是否已存在
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="此電子信箱已被使用"
            )

        # 建立新使用者
        new_user = User(name=user.name, email=user.email)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "使用者建立成功", "user": new_user.to_dict()}

    except HTTPException:
        raise
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
        # 建立時段物件列表
        schedule_objects = []
        for schedule_data in schedules:
            schedule = Schedule(
                giver_id=schedule_data.giver_id,
                date=schedule_data.schedule_date,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
                note=schedule_data.note,
                status=schedule_data.status,
                role=schedule_data.role,
            )
            schedule_objects.append(schedule)

        # 批量新增到資料庫
        db.add_all(schedule_objects)
        db.commit()

        # 重新整理物件以取得 ID
        for schedule in schedule_objects:
            db.refresh(schedule)

        # 回傳建立的時段
        return schedule_objects

    except Exception as e:
        # 回滾資料庫交易
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
        status: 可選的狀態篩選條件
        db: 資料庫會話依賴注入

    Returns:
        List[ScheduleResponse]: 符合條件的時段列表
    """
    try:
        # 建立查詢
        query = db.query(Schedule)

        # 套用篩選條件
        if giver_id is not None:
            query = query.filter(Schedule.giver_id == giver_id)

        if status_filter is not None:
            query = query.filter(Schedule.status == status_filter)

        # 執行查詢
        schedules = query.all()

        return schedules

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢時段失敗: {str(e)}",
        )
