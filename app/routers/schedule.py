# """
# 時段相關的 API 路由。
# """

# # ===== 標準函式庫 =====
# from datetime import date, time  # 日期和時間處理
# from typing import List  # 列表型別

# # ===== 第三方套件 =====
# from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI 核心
# from sqlalchemy.orm import Session  # 資料庫會話

# # ===== 本地模組 =====
# from app.models.database import get_db  # 資料庫會話依賴
# from app.models.schedule import Schedule  # 資料庫模型
# from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleListResponse  # 資料驗證


# # 建立路由器
# router = APIRouter(prefix="/api/v1/schedule", tags=["行程管理"])


# @router.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
# async def create_schedule(
#     schedule: ScheduleCreate,
#     db: Session = Depends(get_db)
# ):
#     """
#     建立新的行程。

#     Args:
#         schedule: 行程資料。
#         db: 資料庫會話。

#     Returns:
#         ScheduleResponse: 建立的行程資料。
#     """
#     print(f"建立行程：{schedule}")

#     # 檢查時段是否重疊
#     existing_schedule = db.query(Schedule).filter(
#         Schedule.date == schedule.date,
#         Schedule.start_time < schedule.end_time,
#         Schedule.end_time > schedule.start_time,
#         Schedule.giver_id == schedule.giver_id
#     ).first()

#     if existing_schedule:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"時段重疊：{existing_schedule.start_time} - {existing_schedule.end_time}"
#         )

#     # 建立新的行程
#     db_schedule = Schedule(
#         date=schedule.date,
#         start_time=schedule.start_time,
#         end_time=schedule.end_time,
#         role=schedule.role,
#         giver_id=schedule.giver_id,
#         taker_id=schedule.taker_id,
#         status=schedule.status,
#         note=schedule.note
#     )

#     # 儲存到資料庫
#     db.add(db_schedule)
#     db.commit()
#     db.refresh(db_schedule)

#     print(f"行程建立成功：ID {db_schedule.id}")

#     return ScheduleResponse(
#         id=db_schedule.id,
#         role=db_schedule.role,
#         status=db_schedule.status,
#         giver_id=db_schedule.giver_id,
#         taker_id=db_schedule.taker_id,
#         date=db_schedule.date,
#         start_time=db_schedule.start_time,
#         end_time=db_schedule.end_time,
#         note=db_schedule.note,
#         created_at=db_schedule.created_at.isoformat()
#     )


# @router.get("/schedules", response_model=ScheduleListResponse)
# async def get_schedules(
#     date_from: date = None,
#     date_to: date = None,
#     giver_id: int = None,
#     role: str = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     取得行程列表。

#     Args:
#         date_from: 開始日期。
#         date_to: 結束日期。
#         giver_id: Giver ID。
#         role: 角色 (GIVER/TAKER)。
#         db: 資料庫會話。

#     Returns:
#         ScheduleListResponse: 行程列表。
#     """
#     print(f"查詢行程：date_from={date_from}, date_to={date_to}, giver_id={giver_id}, role={role}")

#     # 建立查詢
#     query = db.query(Schedule)

#     # 套用篩選條件
#     if date_from:
#         query = query.filter(Schedule.date >= date_from)
#     if date_to:
#         query = query.filter(Schedule.date <= date_to)
#     if giver_id:
#         query = query.filter(Schedule.giver_id == giver_id)
#     if role:
#         query = query.filter(Schedule.role == role)

#     # 排序
#     query = query.order_by(Schedule.date, Schedule.start_time)

#     # 執行查詢
#     schedules = query.all()

#     print(f"查詢到 {len(schedules)} 個行程")

#     return ScheduleListResponse(
#         schedules=[
#             ScheduleResponse(
#                 id=schedule.id,
#                 role=schedule.role,
#                 status=schedule.status,
#                 giver_id=schedule.giver_id,
#                 taker_id=schedule.taker_id,
#                 date=schedule.date,
#                 start_time=schedule.start_time,
#                 end_time=schedule.end_time,
#                 note=schedule.note,
#                 created_at=schedule.created_at.isoformat()
#             )
#             for schedule in schedules
#         ],
#         total=len(schedules)
#     )


# @router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
# async def get_schedule(
#     schedule_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     取得特定行程。

#     Args:
#         schedule_id: 行程 ID。
#         db: 資料庫會話。

#     Returns:
#         ScheduleResponse: 行程資料。
#     """
#     print(f"查詢行程 ID：{schedule_id}")

#     schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()

#     if not schedule:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"行程 ID {schedule_id} 不存在"
#         )

#     return ScheduleResponse(
#         id=schedule.id,
#         role=schedule.role,
#         status=schedule.status,
#         giver_id=schedule.giver_id,
#         taker_id=schedule.taker_id,
#         date=schedule.date,
#         start_time=schedule.start_time,
#         end_time=schedule.end_time,
#         note=schedule.note,
#         created_at=schedule.created_at.isoformat()
#     )


# @router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_schedule(
#     schedule_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     刪除行程。

#     Args:
#         schedule_id: 行程 ID。
#         db: 資料庫會話。
#     """
#     print(f"刪除行程 ID：{schedule_id}")

#     schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()

#     if not schedule:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"行程 ID {schedule_id} 不存在"
#         )

#     db.delete(schedule)
#     db.commit()

#     print(f"行程 ID {schedule_id} 刪除成功")
