from fastapi import FastAPI, Request, Body, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import giver, taker, chat, match, admin
from sqlalchemy.orm import Session  # 引入 SQLAlchemy 的 Session 類別，用於資料庫操作
from app.models.database import SessionLocal  # 引入資料庫 session 工廠：從 database.py 引入 SessionLocal 用於資料庫操作
from app.models.schedule import Schedule  # 引入資料表模型：從 app/models/schedule.py 檔案中匯入 Schedule 類別
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time, datetime, timedelta
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    BatchScheduleCreate,
    ScheduleResponse  # 用於回傳排程資料
)
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Clinic Scheduler", version="1.0.0") # 定義叫 app 的 FastAPI 應用實例，所有 API 路由（像 /, /users, /products）都掛在這個 app 上。

# 全域變數記錄啟動時間
last_reload_time = datetime.now()
logger.info(f"🚀 FastAPI 啟動時間：{last_reload_time}")

# 星期名稱轉換常數
WEEKDAY_MAP = {
    'Monday': '星期一',
    'Tuesday': '星期二',
    'Wednesday': '星期三',
    'Thursday': '星期四',
    'Friday': '星期五',
    'Saturday': '星期六',
    'Sunday': '星期日'
}

WEEKDAY_MAP_REVERSE = {v: k for k, v in WEEKDAY_MAP.items()}

# 資料庫依賴
def get_db():
    logger.info("get_db() called: 建立資料庫連線")
    db = SessionLocal()  # 建立資料庫連線：每次操作資料庫，會透過 SessionLocal() 建立一個 session 實例（db）來操作。
    try:
        logger.info("get_db() yield: 傳遞資料庫連線給處理函式")
        yield db  # 傳給處理請求的函式使用，執行查詢/新增/修改操作，每次請求建立一個 session，避免多個使用者共享同一個連線
    finally:
        logger.info("get_db() cleanup: 關閉資料庫連線")
        db.close()  # 每次請求結束後，無論有沒有錯誤發生，都自動關閉 session 連線，避免資源浪費、外洩

# 工具函數
def convert_weekday_to_english(weekday: str) -> str:
    """將中文星期轉換為英文"""
    logger.info(f"convert_weekday_to_english() called: {weekday}")
    result = WEEKDAY_MAP_REVERSE.get(weekday, weekday)
    logger.info(f"convert_weekday_to_english() result: {result}")
    return result

def convert_weekday_to_chinese(weekday: str) -> str:
    """將英文星期轉換為中文"""
    logger.info(f"convert_weekday_to_chinese() called: {weekday}")
    result = WEEKDAY_MAP.get(weekday, weekday)
    logger.info(f"convert_weekday_to_chinese() result: {result}")
    return result

def format_time_for_response(time_obj) -> str:
    """格式化時間物件為字串"""
    logger.info(f"format_time_for_response() called: {time_obj}")
    if hasattr(time_obj, 'strftime'):
        result = time_obj.strftime('%H:%M')
    else:
        result = str(time_obj)
    logger.info(f"format_time_for_response() result: {result}")
    return result

def format_date_for_response(date_obj) -> str:
    """格式化日期物件為字串"""
    logger.info(f"format_date_for_response() called: {date_obj}")
    if hasattr(date_obj, 'isoformat'):
        result = date_obj.isoformat()
    else:
        result = str(date_obj)
    logger.info(f"format_date_for_response() result: {result}")
    return result

def check_schedule_overlap(db: Session, schedule_date: date, start_time: time, end_time: time, exclude_id: Optional[int] = None) -> bool:
    """檢查排程時間是否重疊"""
    logger.info(f"check_schedule_overlap() called: date={schedule_date}, start={start_time}, end={end_time}, exclude_id={exclude_id}")
    query = db.query(Schedule).filter(
        Schedule.date == schedule_date,
        (
            (Schedule.start_time <= start_time) & (Schedule.end_time > start_time)
        ) | 
        (
            (Schedule.start_time < end_time) & (Schedule.end_time >= end_time)
        ) |
        (
            (Schedule.start_time >= start_time) & (Schedule.end_time <= end_time)
        )
    )
    
    if exclude_id:
        query = query.filter(Schedule.id != exclude_id)
    
    result = query.first() is not None
    logger.info(f"check_schedule_overlap() result: {result}")
    return result

def schedule_to_response_dict(schedule: Schedule) -> dict:
    """將 Schedule 物件轉換為回應字典"""
    logger.info(f"schedule_to_response_dict() called: schedule_id={schedule.id}")
    result = {
        "id": schedule.id,
        "name": schedule.name,
        "date": format_date_for_response(schedule.date),
        "weekday": convert_weekday_to_chinese(schedule.weekday),
        "start": format_time_for_response(schedule.start_time),
        "end": format_time_for_response(schedule.end_time),
        "note": schedule.note
    }
    logger.info(f"schedule_to_response_dict() result: {result}")
    return result

# 掛載路由
app.include_router(giver.router)
app.include_router(taker.router)
app.include_router(chat.router)
app.include_router(match.router)
app.include_router(admin.router)

# 掛載靜態資料夾（CSS、JS 會從 /static/ 讀取）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 設定 Jinja2 模板資料夾，供 HTML 頁面渲染使用。
templates = Jinja2Templates(directory="app/templates")

# 根路由
@app.get("/", response_class=HTMLResponse)  # 有人用 GET 方法請求網站根目錄（例如 http://127.0.0.1:8000/）時，執行函式 read_index(request: Request)。  
async def read_index(request: Request):
    logger.info("read_index() called: 處理根路由請求")
    logger.info(f"read_index() request: {request.url}")
    result = templates.TemplateResponse("index.html", {"request": request})
    logger.info("read_index() completed: 返回 HTML 模板")
    return result

@app.get("/reload-check")
def reload_check():
    logger.info("reload_check() called: 檢查應用程式重載狀態")
    result = {"reloaded_at": last_reload_time.isoformat()}
    logger.info(f"reload_check() result: {result}")
    return result

# ===== CRUD API ===== 
@app.get("/schedules")
def list_schedules(db: Session = Depends(get_db)):
    """Read All：取得所有排程。"""
    try:
        schedules = db.query(Schedule).order_by(Schedule.date, Schedule.start_time).all()
        return [schedule_to_response_dict(s) for s in schedules]
    except Exception as e:
        logger.error(f"Error listing schedules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取得排程列表時發生錯誤"
        )

@app.get("/schedules/{id}")
def read_schedule(id: int, db: Session = Depends(get_db)):
    """Read One：根據 id 回傳單一排程。"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule_to_response_dict(schedule)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading schedule {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取得排程時發生錯誤"
        )

@app.post("/schedules", response_model=ScheduleResponse)  # 回傳排程資料：ScheduleResponse 的資料格式，用於驗證輸入資料
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    """Create：新增一筆排程。"""
    logger.info(f"Creating schedule: {schedule.dict()}")
    
    try:
        # 檢查時間重疊
        if check_schedule_overlap(db, schedule.date, schedule.start, schedule.end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"時間 {schedule.date} {schedule.start}-{schedule.end} 與已預約時間重疊，請重新選擇時間"
            )
        
        # 轉換星期名稱
        weekday = convert_weekday_to_english(schedule.weekday)
        
        # 建立新排程
        new_schedule = Schedule(
            name=schedule.name,
            date=schedule.date,
            weekday=weekday,  # 儲存英文星期名稱
            start_time=schedule.start,  # 直接使用字串格式的時間
            end_time=schedule.end,      # 直接使用字串格式的時間
            note=schedule.note
        )
        print(f"Created new schedule object: {new_schedule.__dict__}")
        db.add(new_schedule)  # 將新的排程物件，新增到資料庫中
        
        db.commit()  # 提交資料庫的改動，將新的排程物件，新增到資料庫中
        db.refresh(new_schedule)  # 更新排程物件，將資料庫的資料，轉換為排程物件的資料
        
        logger.info(f"Successfully created schedule with ID: {new_schedule.id}")
        return schedule_to_response_dict(new_schedule)
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:  # 如果發生錯誤，則回傳錯誤訊息
        logger.error(f"Error creating schedule: {str(e)}")
        db.rollback()  # 如果發生錯誤，則回滾資料庫的改動
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立預約時發生錯誤：{str(e)}"
        )

@app.post("/schedules/batch", status_code=status.HTTP_201_CREATED, response_model=List[ScheduleResponse])  # 回傳排程資料：List[ScheduleResponse] 的資料格式，用於驗證輸入資料
async def create_batch_schedules(batch_schedule: BatchScheduleCreate, db: Session = Depends(get_db)):
    """Create Batch：批量建立排程。"""
    logger.info(f"Creating batch schedules: {batch_schedule.dict()}")
    
    try:
        created_schedules = []
        # 定義英文星期順序
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        start_weekday_num = batch_schedule.start_date.weekday()  # 0=Monday
        
        for week in range(batch_schedule.weeks):
            for weekday in batch_schedule.weekdays:
                weekday_num = weekday_order.index(weekday)
                # 計算本週的目標 weekday 距離 start_date 的天數
                days_delta = (weekday_num - start_weekday_num) % 7 + week * 7
                target_date = batch_schedule.start_date + timedelta(days=days_delta)

                # 檢查時間衝突
                if check_schedule_overlap(db, target_date, batch_schedule.start_time, batch_schedule.end_time):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"時間 {target_date} {batch_schedule.start_time}-{batch_schedule.end_time} 與已預約時間重疊，請重新選擇時間"
                    )
                
                new_schedule = Schedule(
                    name=batch_schedule.name,
                    date=target_date,
                    weekday=weekday,
                    start_time=batch_schedule.start_time,
                    end_time=batch_schedule.end_time,
                    note=batch_schedule.note
                )
                db.add(new_schedule)
                created_schedules.append(new_schedule)
        
        if not created_schedules:
            return []
        
        db.commit()
        for schedule in created_schedules:
            db.refresh(schedule)
        
        # 按日期排序
        created_schedules.sort(key=lambda s: s.date)
        
        logger.info(f"Successfully created {len(created_schedules)} batch schedules")
        return [schedule_to_response_dict(s) for s in created_schedules]
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error creating batch schedules: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立批量預約時發生錯誤：{str(e)}"
        )

@app.patch("/schedules/{id}")
def update_schedule(id: int, schedule: ScheduleUpdate, db: Session = Depends(get_db)):
    """Patch：局部排程更新。"""
    logger.info(f"Updating schedule {id}: {schedule.dict(exclude_unset=True)}")
    
    try:
        db_schedule = db.query(Schedule).filter(Schedule.id == id).first()
        if not db_schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        # 檢查更新後的時間是否重疊
        new_date = schedule.date if schedule.date is not None else db_schedule.date
        new_start = schedule.start if schedule.start is not None else db_schedule.start_time
        new_end = schedule.end if schedule.end is not None else db_schedule.end_time
        
        if check_schedule_overlap(db, new_date, new_start, new_end, exclude_id=id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"更新後的時間與已預約時間重疊，請重新選擇時間"
            )
        
        # 更新欄位
        update_data = schedule.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'start':
                setattr(db_schedule, 'start_time', value)
            elif field == 'end':
                setattr(db_schedule, 'end_time', value)
            elif field == 'weekday':
                setattr(db_schedule, field, convert_weekday_to_english(value))
            else:
                setattr(db_schedule, field, value)
        
        db.commit()
        db.refresh(db_schedule)
        
        logger.info(f"Successfully updated schedule {id}")
        return schedule_to_response_dict(db_schedule)
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error updating schedule {id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新排程時發生錯誤：{str(e)}"
        )

@app.delete("/schedules/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(id: int, db: Session = Depends(get_db)):
    """Delete：刪除排程。"""
    logger.info(f"Deleting schedule {id}")
    
    try:
        db_schedule = db.query(Schedule).filter(Schedule.id == id).first()
        if not db_schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        db.delete(db_schedule)
        db.commit()
        
        logger.info(f"Successfully deleted schedule {id}")
        return
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error deleting schedule {id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除排程時發生錯誤：{str(e)}"
        )