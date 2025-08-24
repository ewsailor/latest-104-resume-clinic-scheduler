# API 分層架構說明

## 概述

本專案採用**分層架構**設計，每層職責明確，確保程式碼的可維護性、可擴展性和可測試性。

### 資料流向

```
Client Request 客戶端發送 HTTP 請求
    ↓
Router Layer (路由層) routers/
    ↓
Middleware Layer (中介層) middleware/
    ↓
Validation & Dependency Layer (驗證 & 依賴注入) schemas/ dependencies/ utils/
    ↓
Service Layer (業務邏輯層) services/
    ↓
CRUD Layer (資料存取層) repositories/ crud/
    ↓
Model Layer (模型層) models/
    ↓
Database Layer (資料庫層)
    ↓
Response Layer (回應層) response_models/ exceptions/
    ↓
Client Response
```

---

## 🎯 各層詳細說明

### **第一層：路由層 (Router Layer)**

**職責**：請求解析與路由分發

**本專案中檔案**：`app/routers`

#### 核心功能

- **解析請求 (Parse Request)**：

  - 標頭 (`Headers`)：額外資訊，如 `JWT` 認證令牌、內容類型 (`Content-Type`) 等
  - 請求體 (`Request Body`)：`JSON` 格式資料 (`application/json`)、檔案上傳 (`multipart/form-data`) 等
  - 路徑參數 (`Path Params`)：指定某個資源的唯一 `ID`
  - 查詢參數 (`Query Params`)：篩選、搜尋、排序、分頁等

- **路由分發 (Route Dispatch)**：
  - 根據 `HTTP` 方法，呼叫對應的 `CRUD` 層函式
  - 依賴注入 (`Dependency Injection`)：統一管理物件需要的「依賴（如資料庫連線會話 `db: Session = Depends(get_db)`）」，需要時從外部用 `Depends()` 注入依賴，而不是在函式內部建立導致邏輯混亂

#### 範例程式碼

```python
@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedules(
    request: ScheduleCreateRequest,
    db: Session = Depends(get_db)  # 依賴注入
):
    # 路由層：解析請求，呼叫 Service 層
    return schedule_service.create_schedules(
        db=db,
        schedules=request.schedules,
        created_by=request.created_by,
        created_by_role=request.created_by_role
    )
```

---

### **第二層：中介層 (Middleware Layer)**

**職責**：橫切關注點處理

**本專案中檔案**：`app/middleware`

#### 核心功能

- **認證 (`Authentication`)**：確認請求者身份是誰

  - `JWT (JSON Web Token)` 令牌驗證：無狀態（`Stateless`）認證，無需查詢資料庫或快取來驗證使用者，有利後端服務的水平擴展、實現單點登入（`Single Sign-On, SSO`）
  - `Session` 管理：有狀態（`Stateful`）認證，伺服器可以隨時控制會話，適合銀行、醫療等對資料安全性要求極高的系統
  - `API Key` 驗證：系統間請求時，用固定金鑰認證，如後台與第三方服務間的溝通

- **授權 (`Authorization`)**：確認請求者的操作權限

  - 角色權限檢查 (`GIVER`, `TAKER`, `SYSTEM`)
  - 資源存取權限驗證：如使用者只能存取自己有權限的資源，如不能刪除別人的時段

- **中介邏輯 (`Middleware`)**：處理一些共通的、非核心的請求處理邏輯
  - `CORS`：處理跨域請求，允許不同來源的前端存取 `API`，如後端 `API` 可能在 `api.example.com`，而前端在 `app.example.com`
  - 請求速率限制 (`Rate Limiting`)：防止短時間內大量請求造成伺服器過載。如限制每個 `IP` 在 1 分鐘內最多發送 100 個請求
  - 日誌記錄 (`Request Logging`)：記錄每次請求的時間、方法、路徑、狀態碼等資訊，以利除錯、監控系統健康
  - 錯誤處理 (`Error Handling`)：將異常轉換成 `HTTP` 錯誤回應，如 `404 Not Found`

#### 範例程式碼

```python
# app/middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### **第三層：驗證層 (Validation Layer)**

**職責**：資料驗證與序列化

**本專案中檔案**：`app/schemas`

#### 核心功能

- **輸入驗證 (`Input Validation`)**：

  - 使用 `Pydantic` 模型驗證請求資料格式，防止非法資料進入 `CRUD` 層
  - 自訂驗證規則 (`Custom Validators`)：用 `@field_validator` 裝飾器為特定欄位定義更複雜的驗證邏輯，如檢查 `password` 是否符合複雜度要求

- **資料轉換 (`Data Transformation`)**：
  - 資料型別轉換：如字串轉日期、數字轉布林值，確保 CRUD 層與前端能一致處理資料
  - 請求資料序列化 (`Serialization`)：收到請求時，將前端送來的非 `Python` 格式（如 `JSON` 字串）資料，轉換成 `Python` 物件
  - 回應資料反序列化 (`Deserialization`)：送出回應前，資料庫查詢出的 `Python` 物件，轉換成可傳輸格式（如 `JSON` 字串）

Dependencies：例如 FastAPI Depends()，注入 DB session、目前使用者資訊。

#### 範例程式碼

```python
# app/schemas/schedule.py
from pydantic import BaseModel, Field, field_validator
from datetime import date, time

class ScheduleCreate(BaseModel):
    giver_id: int = Field(..., description="Giver ID", gt=0)
    schedule_date: date = Field(..., description="時段日期", alias="date")
    start_time: time = Field(..., description="開始時間")
    end_time: time = Field(..., description="結束時間")

    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        start_time = info.data.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('結束時間必須晚於開始時間')
        return v

class ScheduleCreateRequest(BaseModel):
    schedules: list[ScheduleCreate] = Field(..., description="要建立的時段列表")
    updated_by: int = Field(..., description="操作者 ID")
    updated_by_role: str = Field(..., description="操作者角色")

class ScheduleResponse(BaseModel):
    id: int
    giver_id: int
    schedule_date: date
    start_time: time
    end_time: time
    created_at: datetime
    created_by: int
    created_by_role: str
```

---

### **第四層：服務層 (Service Layer)**

**職責**：業務邏輯處理

**本專案中檔案**：`app/services`

#### 核心功能

Service Layer → 處理規則、檢查權限、組合多個 CRUD。
「新增預約」流程：Service 檢查時間是否衝突 → 呼叫 CRUD 插入資料 → 呼叫通知系統寄信。

- **業務邏輯 (`Business Logic`)**：處理應用程式核心的規則與流程

  - 複雜業務規則處理：如預約衝突檢查、時段重疊驗證
  - 多個 `CRUD` 操作的協調：如建立一個預約時，需同時更新 `schedules` 表、`notifications` 表等多個資料表
  - 外部服務整合：呼叫第三方 `API`、發送郵件、訊息推播等
  - 狀態管理：根據建立者角色決定時段狀態（GIVER → AVAILABLE，TAKER → PENDING）

- **事務管理 (`Transaction Management`)**：確保資料庫操作的一致性，避免部分操作成功、部分失敗造成資料不完整

  - 資料庫事務控制：將多個 CRUD 操作包成一個交易 (`Transaction`)，確保原子性
  - 回滾機制 (`Rollback`)：若中途有錯誤，整個事務自動回退，避免資料不一致
  - 錯誤處理：統一的錯誤處理和日誌記錄機制

- **快取管理 (`Cache Management`)**：提高查詢效能，減少資料庫負載
  - 查詢結果快取：將常用查詢結果暫存到快取系統（如 Redis），下次直接取快取
  - 快取失效策略：設計有效期或事件觸發失效，確保資料不會過時

#### 範例程式碼

```python
# app/services/schedule_service.py
from app.crud.schedule import ScheduleCRUD
from app.schemas import ScheduleData
from app.enums.models import UserRoleEnum, ScheduleStatusEnum
from app.utils.decorators import handle_crud_errors_with_rollback, log_operation

class ScheduleService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.schedule_crud = ScheduleCRUD()

    @handle_crud_errors_with_rollback("建立時段")
    @log_operation("建立時段")
    def create_schedules(
        self,
        db: Session,
        schedules: List[ScheduleData],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> List[Schedule]:
        """建立多個時段（業務邏輯層）"""
        # 記錄建立操作
        self.logger.info(
            f"使用者 {created_by} (角色: {created_by_role.value}) "
            f"正在建立 {len(schedules)} 個時段"
        )

        # 建立時段物件列表
        schedule_objects = self.create_schedule_objects(
            schedules, created_by, created_by_role
        )

        # 使用 CRUD 層建立時段
        created_schedules = self.schedule_crud.create_schedules(db, schedule_objects)

        self.logger.info(
            f"成功建立 {len(created_schedules)} 個時段，"
            f"ID範圍: {[s.id for s in created_schedules]}"
        )

        return created_schedules
```

---

### **第五層：CRUD 層 (CRUD Layer)**

CRUD Layer → 單純呼叫 ORM 做 Create/Read/Update/Delete。

- 專注資料庫操作。
- 只做單純的 `db.query(User).filter(...).all()` 或 `db.add(instance)`。
- 不含商業邏輯。
- 提供資料庫查詢優化工具。

**職責**：資料庫操作

**本專案中檔案**：`app/crud`

#### 核心功能

- **增查改刪 (`CRUD Operations`)**：

  - `create_*()` - 建立記錄
  - `get_*()` - 查詢記錄
  - `update_*()` - 更新記錄
  - `delete_*()` - 刪除記錄

- **查詢優化 (`Query Optimization`)**：
  - 索引使用：避免全表查詢，提高查詢速度
  - 分頁處理：資料量龐大時，不一次抓取所有資料，而是分頁查詢
  - 關聯查詢優化：處理一對多、多對多關聯時，合理使用 `JOIN` 或 `ORM` 的 `selectinload`、`joinedload`

#### 範例程式碼

```python
# app/crud/schedule.py
from sqlalchemy.orm import Session, joinedload
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate

class ScheduleCRUD:
    def create_schedules(
        self,
        db: Session,
        schedule_objects: list[Schedule],
    ) -> list[Schedule]:
        """建立多個時段"""
        # 批量新增到資料庫
        db.add_all(schedule_objects)
        db.commit()

        # 重新整理物件以取得 ID
        for schedule in schedule_objects:
            db.refresh(schedule)

        self.logger.info(
            f"成功建立 {len(schedule_objects)} 個時段，"
            f"ID範圍: {[s.id for s in schedule_objects]}"
        )
        return schedule_objects
```

---

### **第六層：模型層 (Model Layer)**

**職責**：資料結構定義

**本專案中檔案**：`app/models`

#### 核心功能

- **資料表對應 (`Table Mapping`)**：

  - 使用 `SQLAlchemy ORM` 定義資料表結構
  - 欄位名稱、型別、約束設定等

- **關聯定義 (`Relationship Definition`)**：

  - 主鍵 (`Primary Key, PK`)
  - 外鍵 (`Foreign Key, FK`)
  - 一對多、多對多關聯

- **審計追蹤 (`Audit Trail`)**：
  - 建立時間 (`created_at`)
  - 更新時間 (`updated_at`)
  - 操作者追蹤 (`created_by`, `updated_by`, `deleted_by`)
  - 角色追蹤 (`created_by_role`, `updated_by_role`, `deleted_by_role`)
  - 軟刪除 (`deleted_at`)

#### 範例程式碼

```python
# app/models/schedule.py
from sqlalchemy import Column, Integer, Date, Time, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
from app.enums.models import UserRoleEnum

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    giver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    taker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    schedule_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # 審計追蹤欄位
    created_at = Column(DateTime, default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_role = Column(Enum(UserRoleEnum), nullable=True)

    # 關聯定義
    giver = relationship("User", foreign_keys=[giver_id], lazy='joined')
    taker = relationship("User", foreign_keys=[taker_id], lazy='joined')
    created_by_user = relationship("User", foreign_keys=[created_by], lazy='joined')
```

---

### **第七層：資料庫層 (Database Layer)**

**職責**：資料持久化與存取

**本專案中檔案**：`app/models/database.py`

#### 核心功能

- **資料庫操作 (`Database Operations`)**：

  - `SQL`：執行所有 `CRUD` 操作的 `SQL` 語句，無論是 `ORM` 生成的還是手寫 `SQL`
  - 連線池管理：每次請求時，不是重新建立一個新的資料庫連線，造成效能損耗，而是從池子中借用一個現有的連線，使用完畢後再歸還
  - 事務處理：控制資料庫操作要麼都成功，要麼都失敗，符合 `ACID`（原子性、一致性、隔離性、持久性），如使用 `BEGIN`、`COMMIT`、`ROLLBACK`，確保資料一致性

- **效能優化 (`Performance Optimization`)**：
  - 索引設計：設計適當的單欄位或複合索引，加速查詢、排序或過濾操作
  - 查詢優化：調整 `SQL` 語法、使用 `JOIN`、子查詢或 `ORM` 預載入策略，減少不必要的資料庫存取
  - 資料庫分片：將大表分散到不同資料庫或表中，提高擴展性與效能，適用於超大規模資料

#### 範例程式碼（以下為範例，完整版請見）

```python
# app/models/database.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine
from app.core.settings import settings

# 建立基礎類別：所有資料表模型，都會繼承這個類別，避免重複的程式碼
Base = declarative_base()

def create_database_engine() -> tuple[Engine, sessionmaker]:
    """
    建立並初始化資料庫引擎和相關組件
    """

    DATABASE_URL = settings.mysql_connection_string

    # 建立資料庫引擎連線
    engine = create_engine(
        DATABASE_URL, # MySQL 連接字串
        echo=False, # 關閉 SQL 查詢日誌
        pool_pre_ping=True, # 啟用連線檢查，確保連線有效性
        pool_size=10, # 連線池大小
        max_overflow=10, # 最大溢出連線數（通常是 pool_size 的 1-2 倍）
        pool_timeout=30, # 連線超時時間（30秒）
        pool_recycle=3600, # 連線池回收時間（1小時）
        connect_args={ # pymysql 特定參數
            "charset": "utf8mb4", # 使用 utf8mb4 字符集
        },
    )

    # 建立 session 工廠：每次呼叫 SessionLocal()，就生成一個新 Session 實例，確保每個請求，都有一個獨立的資料庫連線，避免共用連線，導致資料庫操作錯亂
    SessionLocal = sessionmaker(
        bind=engine,  # 指定 Session 連線的資料庫引擎（engine）
        autocommit=False,  # 不自動提交，手動呼叫 .commit() 才會儲存資料
        autoflush=False,  # 不自動刷新、不自動將未提交的改動同步到資料庫，需手動呼叫 flush()
    )

    return engine, SessionLocal

# 程式啟動時，立即建立引擎和會話工廠
engine, SessionLocal = create_database_engine()

def get_db() -> Generator[Session, None, None]:
    """
    依賴注入：取得資料庫連線
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### **第八層：回應層 (Response Layer)**

**職責**：回應格式化與傳送

**本專案中檔案**：`app/routers`

#### 核心功能

- **回應格式化 (`Response Formatting`)**：

  - `JSON` 序列化：將業務邏輯的結果，如資料庫查詢出的 `Python` 物件，封裝轉換成可傳輸格式（如 `JSON` 字串）
  - 狀態碼 (`Status Code`) 設定：告訴客戶端本次請求的結果，如 `200 OK`、`201 Created`、`400 Bad Request`、`404 Not Found` 等
  - 標頭 (`Headers`) 設定：如 `Content-Type: application/json` 告訴客戶端回應的格式是 `JSON`

- **錯誤處理 (`Error Handling`)**：
  - 統一錯誤格式：所有類型的錯誤，都以固定的 `JSON` 格式回傳
  - 錯誤日誌記錄：將系統錯誤寫入日誌，用於問題追蹤與系統診斷
  - 使用者友善錯誤訊息：將錯誤訊息轉換為對客戶端有意義的訊息，如 "該電子信箱已被註冊"

#### 範例程式碼

```python
# app/routers/api/schedule.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services import schedule_service
from app.schemas.schedule import ScheduleCreateRequest, ScheduleResponse

router = APIRouter()

@router.post("/schedules", response_model=ScheduleResponse, status_code=201)
async def create_schedules(
    request: ScheduleCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        schedules = schedule_service.create_schedules(
            db=db,
            schedules=request.schedules,
            created_by=request.created_by,
            created_by_role=request.created_by_role
        )

        # 回應格式化
        return {
            "data": [schedule.to_dict() for schedule in schedules],
            "message": f"成功建立 {len(schedules)} 個時段",
            "status": "success"
        }

    except ValueError as e:
        # 統一錯誤處理
        raise HTTPException(
            status_code=400,
            detail={
                "error": "VALIDATION_ERROR",
                "message": str(e),
                "status": "error"
            }
        )
    except Exception as e:
        # 系統錯誤處理
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "建立時段時發生系統錯誤",
                "status": "error"
            }
        )
```

---

## 架構優點

### **1. 職責分離 (Separation of Concerns)**

- 每層只負責自己的職責
- 避免跨層直接呼叫
- 降低耦合度

### **2. 可測試性 (Testability)**

- 每層都可以獨立測試
- 使用依賴注入 (Dependency Injection)
- Mock 外部依賴

### **3. 可維護性 (Maintainability)**

- 清晰的程式碼結構
- 統一的命名規範
- 完整的文件說明

### **4. 可擴展性 (Scalability)**

- 模組化設計
- 插件化架構
- 水平擴展支援

---

## 相關文件

- [API 設計指南](./api-design.md)
