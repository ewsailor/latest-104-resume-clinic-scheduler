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


# ===== 測試用 Giver 資料 =====
MOCK_GIVERS = [
    {
        "id": 1,
        "name": "王零一",
        "title": "Python 工程師",
        "company": "王零一-資訊科技公司",
        "consulted": "106 人",
        "average_responding_time": "2 天",
        "experience": "4 年",
        "image": "https://randomuser.me/api/portraits/men/1.jpg",
        "giverCard__topic": [
            "履歷健診",
            "模擬面試",
            "職涯諮詢",
            "職業/產業經驗分享",
            "英文履歷健診",
            "英文模擬面試",
        ],
    },
    {
        "id": 2,
        "name": "王零二",
        "title": "前端工程師",
        "company": "王零二-網路科技公司",
        "consulted": "89 人",
        "average_responding_time": "1 天",
        "experience": "3 年",
        "image": "https://randomuser.me/api/portraits/men/2.jpg",
        "giverCard__topic": ["履歷健診", "模擬面試", "職涯諮詢", "前端技術分享"],
    },
    {
        "id": 3,
        "name": "王零三",
        "title": "後端工程師",
        "company": "王零三-軟體科技公司",
        "consulted": "156 人",
        "average_responding_time": "3 天",
        "experience": "5 年",
        "image": "https://randomuser.me/api/portraits/men/3.jpg",
        "giverCard__topic": [
            "履歷健診",
            "模擬面試",
            "職涯諮詢",
            "後端技術分享",
            "系統架構設計",
        ],
    },
    {
        "id": 4,
        "name": "王零四",
        "title": "全端工程師",
        "company": "王零四-數位科技公司",
        "consulted": "203 人",
        "average_responding_time": "1 天",
        "experience": "6 年",
        "image": "https://randomuser.me/api/portraits/men/4.jpg",
        "giverCard__topic": [
            "履歷健診",
            "模擬面試",
            "職涯諮詢",
            "全端技術分享",
            "專案管理",
            "團隊領導",
        ],
    },
]


# ===== API 端點 =====
@router.get("/givers")
async def get_givers():
    """
    取得 Giver 列表。

    Returns:
        dict: 包含 Giver 列表的回應
    """
    return {
        "results": MOCK_GIVERS,
        "total": len(MOCK_GIVERS),
        "page": 1,
        "per_page": len(MOCK_GIVERS),
    }


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


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, db=Depends(get_db)):
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
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="時段不存在"
            )
        return ScheduleResponse.model_validate(schedule)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢時段失敗: {str(e)}",
        )


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int, schedule_update: ScheduleCreate, db=Depends(get_db)
):
    """
    更新時段。

    Args:
        schedule_id: 時段 ID
        schedule_update: 更新的時段資料
        db: 資料庫會話依賴注入

    Returns:
        ScheduleResponse: 更新後的時段資料

    Raises:
        HTTPException: 當時段不存在或更新失敗時拋出錯誤
    """
    try:
        # 轉換為字典格式
        update_data = schedule_update.model_dump()
        # 移除 date 欄位的別名
        if "date" in update_data:
            update_data["schedule_date"] = update_data.pop("date")

        updated_schedule = schedule_crud.update_schedule(db, schedule_id, **update_data)
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
async def delete_schedule(schedule_id: int, db=Depends(get_db)):
    """
    刪除時段。

    Args:
        schedule_id: 時段 ID
        db: 資料庫會話依賴注入

    Returns:
        dict: 刪除成功的訊息

    Raises:
        HTTPException: 當時段不存在或刪除失敗時拋出錯誤
    """
    try:
        success = schedule_crud.delete_schedule(db, schedule_id)
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
