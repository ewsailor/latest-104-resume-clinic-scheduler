from fastapi import FastAPI, Request, Body, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import giver, taker, chat, match, admin
from sqlalchemy.orm import Session  # 引入 SQLAlchemy 的 Session 類別，用於資料庫操作
from app.models.database import SessionLocal  # 引入資料庫 session 工廠：從 database.py 引入 SessionLocal 用於資料庫操作
from app.models.schedule import Schedule  # 引入資料表模型：從 app/models/schedule.py 檔案中匯入 Schedule 類別
from pydantic import BaseModel
from typing import List
from datetime import date, time, datetime, timedelta
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    BatchScheduleCreate,
    ScheduleResponse  # 用於回傳排程資料
)

app = FastAPI()  # 定義叫 app 的 FastAPI 應用實例，所有 API 路由（像 /, /users, /products）都掛在這個 app 上。

# 全域變數記錄啟動時間
last_reload_time = datetime.now()
print(f"🚀 FastAPI 啟動時間：{last_reload_time}")

# 取得 SQLAlchemy 的資料庫 session。
def get_db():
    db = SessionLocal()  # 建立資料庫連線：每次操作資料庫，會透過 SessionLocal() 建立一個 session 實例（db）來操作。
    try:
        yield db  # 傳給處理請求的函式使用，執行查詢/新增/修改操作，每次請求建立一個 session，避免多個使用者共享同一個連線
    finally:
        db.close()  # 每次請求結束後，無論有沒有錯誤發生，都自動關閉 session 連線，避免資源浪費、外洩

# 掛載自訂路由（API）
app.include_router(giver.router)
app.include_router(taker.router)
app.include_router(chat.router)
app.include_router(match.router)
app.include_router(admin.router)

# 掛載靜態資料夾（CSS、JS 會從 /static/ 讀取）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 設定 Jinja2 模板資料夾，供 HTML 頁面渲染使用。
templates = Jinja2Templates(directory="app/templates")

# 星期名稱轉換
WEEKDAY_MAP = {
    'Monday': '星期一',
    'Tuesday': '星期二',
    'Wednesday': '星期三',
    'Thursday': '星期四',
    'Friday': '星期五',
    'Saturday': '星期六',
    'Sunday': '星期日'
}

WEEKDAY_MAP_REVERSE = {
    '星期一': 'Monday',
    '星期二': 'Tuesday',
    '星期三': 'Wednesday',
    '星期四': 'Thursday',
    '星期五': 'Friday',
    '星期六': 'Saturday',
    '星期日': 'Sunday'
}

# 根路由：當使用者訪問根目錄 /，渲染 HTML。
@app.get("/", response_class=HTMLResponse)  # 有人用 GET 方法請求網站根目錄（例如 http://127.0.0.1:8000/）時，執行函式 read_index(request: Request)。    
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/reload-check")
def reload_check():
    return {
        "reloaded_at": last_reload_time.isoformat()
    }

# ===== CRUD API =====
# Read All：取得所有排程。
@app.get("/schedules")
def list_schedules(db: Session = Depends(get_db)):
    schedules = db.query(Schedule).order_by(Schedule.date, Schedule.start_time).all()
    return [{
        "id": s.id,
        "name": s.name,
        "date": s.date,
        "weekday": WEEKDAY_MAP.get(s.weekday, s.weekday),  # 轉換為中文星期名稱
        "start": s.start_time.strftime('%H:%M') if hasattr(s.start_time, 'strftime') else s.start_time,
        "end": s.end_time.strftime('%H:%M') if hasattr(s.end_time, 'strftime') else s.end_time,
        "note": s.note
    } for s in schedules]

# Read One：根據 id 回傳單一排程。
@app.get("/schedules/{id}")
def read_schedule(id: int, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.id == id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {
        "id": schedule.id,
        "name": schedule.name,
        "date": schedule.date,
        "weekday": schedule.weekday,
        "start": schedule.start_time,
        "end": schedule.end_time,
        "note": schedule.note
    }

# Create：新增一筆排程。
@app.post("/schedules", response_model=ScheduleResponse)  # 回傳排程資料：ScheduleResponse 的資料格式，用於驗證輸入資料
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    print(f"Received schedules data: {[s.dict() for s in schedule]}")
    try:
        # 檢查是否已存在相同的預約時間
        existing_schedule = db.query(Schedule).filter(
            Schedule.date == schedule.date,
            (
                (Schedule.start_time <= schedule.start) & 
                (Schedule.end_time > schedule.start)
            ) | 
            (
                (Schedule.start_time < schedule.end) & 
                (Schedule.end_time >= schedule.end)
            ) |
            (
                (Schedule.start_time >= schedule.start) & 
                (Schedule.end_time <= schedule.end)
            )
        ).first()
        
        if existing_schedule:
            print(f"Schedule overlaps with existing schedule: {schedule.dict()}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"時間 {schedule.date} {schedule.start}-{schedule.end} 與已預約時間重疊，請重新選擇時間"
            )
        
        # 將中文星期轉換為英文
        weekday = schedule.weekday
        if weekday in WEEKDAY_MAP_REVERSE:
            weekday = WEEKDAY_MAP_REVERSE[weekday]
            
        # 建立新的排程物件：將輸入的資料，轉換為資料庫的資料格式
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
        
        return {
            "id": new_schedule.id,
            "name": new_schedule.name,
            "date": new_schedule.date.isoformat() if hasattr(new_schedule.date, 'isoformat') else new_schedule.date,
            "weekday": WEEKDAY_MAP.get(new_schedule.weekday, new_schedule.weekday),  # 轉換為中文星期名稱
            "start": new_schedule.start_time.strftime('%H:%M') if hasattr(new_schedule.start_time, 'strftime') else new_schedule.start_time,
            "end": new_schedule.end_time.strftime('%H:%M') if hasattr(new_schedule.end_time, 'strftime') else new_schedule.end_time,
            "note": new_schedule.note
        }
    except Exception as e:  # 如果發生錯誤，則回傳錯誤訊息
        print(f"Error creating schedule: {str(e)}")
        db.rollback()  # 如果發生錯誤，則回滾資料庫的改動
        if isinstance(e, HTTPException):
            raise e  # 如果發生 HTTPException，則直接回傳錯誤訊息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立預約時發生錯誤：{str(e)}"
        )

@app.post("/schedules/batch", status_code=status.HTTP_201_CREATED, response_model=List[ScheduleResponse])  # 回傳排程資料：List[ScheduleResponse] 的資料格式，用於驗證輸入資料
async def create_batch_schedules(batch_schedule: BatchScheduleCreate, db: Session = Depends(get_db)):
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

                schedule = ScheduleCreate(
                    name=batch_schedule.name,
                    date=target_date,
                    weekday=weekday,
                    start=batch_schedule.start_time,
                    end=batch_schedule.end_time,
                    note=batch_schedule.note,
                    startMinutes=batch_schedule.start_time.hour * 60 + batch_schedule.start_time.minute,
                    endMinutes=batch_schedule.end_time.hour * 60 + batch_schedule.end_time.minute
                )
                # 檢查時間衝突
                existing_schedule = db.query(Schedule).filter(
                    Schedule.date == schedule.date,
                    (
                        (Schedule.start_time <= schedule.start) & 
                        (Schedule.end_time > schedule.start)
                    ) | 
                    (
                        (Schedule.start_time < schedule.end) & 
                        (Schedule.end_time >= schedule.end)
                    ) |
                    (
                        (Schedule.start_time >= schedule.start) & 
                        (Schedule.end_time <= schedule.end)
                    )
                ).first()
                if existing_schedule:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"時間 {schedule.date} {schedule.start}-{schedule.end} 與已預約時間重疊，請重新選擇時間"
                    )
                new_schedule = Schedule(
                    name=schedule.name,
                    date=schedule.date,
                    weekday=schedule.weekday,
                    start_time=schedule.start,
                    end_time=schedule.end,
                    note=schedule.note
                )
                db.add(new_schedule)
                created_schedules.append(new_schedule)
        if not created_schedules:
            return []
        db.commit()
        for schedule in created_schedules:
            db.refresh(schedule)
        # 排序 created_schedules 依照日期
        created_schedules.sort(key=lambda s: s.date)
        return [{
            "id": s.id,
            "name": s.name,
            "date": s.date.isoformat() if hasattr(s.date, 'isoformat') else s.date,
            "weekday": WEEKDAY_MAP.get(s.weekday, s.weekday),
            "start": s.start_time.strftime('%H:%M') if hasattr(s.start_time, 'strftime') else s.start_time,
            "end": s.end_time.strftime('%H:%M') if hasattr(s.end_time, 'strftime') else s.end_time,
            "note": s.note
        } for s in created_schedules]
    except Exception as e:
        print(f"Error creating batch schedules: {str(e)}")
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立批量預約時發生錯誤：{str(e)}"
        )

# Patch：局部排程更新。
@app.patch("/schedules/{id}")
def update_schedule(id: int, schedule: ScheduleUpdate, db: Session = Depends(get_db)):
    db_schedule = db.query(Schedule).filter(Schedule.id == id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule.name is not None:
        db_schedule.name = schedule.name
    if schedule.date is not None:
        db_schedule.date = schedule.date
    if schedule.weekday is not None:
        db_schedule.weekday = schedule.weekday
    if schedule.start is not None:
        db_schedule.start_time = schedule.start
    if schedule.end is not None:
        db_schedule.end_time = schedule.end
    if schedule.note is not None:
        db_schedule.note = schedule.note
    
    db.commit()
    return {
        "id": db_schedule.id,
        "name": db_schedule.name,
        "date": db_schedule.date,
        "weekday": db_schedule.weekday,
        "start": db_schedule.start_time,
        "end": db_schedule.end_time,
        "note": db_schedule.note
    }

# Delete：刪除排程。
@app.delete("/schedules/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(id: int, db: Session = Depends(get_db)):
    db_schedule = db.query(Schedule).filter(Schedule.id == id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(db_schedule)
    db.commit()
    return