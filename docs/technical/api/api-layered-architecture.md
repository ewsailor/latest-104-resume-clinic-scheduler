# API 分層架構說明

## 概述

本專案採用**分層架構**設計，每層職責明確，確保程式碼的可維護性、可擴展性和可測試性。

### 資料流向

```
Client Request
    ↓
Router Layer (第一層：路由層)
    ↓
Middleware Layer (第二層：中介層)
    ↓
Validation Layer (第三層：驗證層)
    ↓
Service Layer (第四層：服務層)
    ↓
CRUD Layer (第五層：CRUD 層)
    ↓
Model Layer (第六層：模型層)
    ↓
Database Layer (第七層：資料庫層)
    ↓
Response Layer (第八層：回應層)
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
    # 路由層：解析請求，呼叫 CRUD 層
    return schedule_crud.create_schedules(
        db=db,
        schedules=request.schedules,
        updated_by=request.updated_by,
        updated_by_role=request.updated_by_role
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
```

---

### **【後續擴充】第四層：服務層 (Service Layer)**

**職責**：業務邏輯處理

**本專案中檔案**：【後續擴充】`app/services`

#### 核心功能

- **業務邏輯 (`Business Logic`)**：處理應用程式核心的規則與流程

  - 複雜業務規則處理：如預約衝突檢查
  - 多個 `CRUD` 操作的協調：如建立一個預約時，需同時更新 `schedules` 表、`notifications` 表等多個資料表
  - 外部服務整合：呼叫第三方 `API`、發送郵件、訊息推播等

- **事務管理 (`Transaction Management`)**：確保資料庫操作的一致性，避免部分操作成功、部分失敗造成資料不完整

  - 資料庫事務控制：將多個 CRUD 操作包成一個交易 (`Transaction`)，確保原子性
  - 回滾機制 (`Rollback`)：若中途有錯誤，整個事務自動回退，避免資料不一致

- **快取管理 (`Cache Management`)**：提高查詢效能，減少資料庫負載
  - 查詢結果快取：將常用查詢結果暫存到快取系統（如 Redis），下次直接取快取
  - 快取失效策略：設計有效期或事件觸發失效，確保資料不會過時

#### 範例程式碼

```python
# app/services/schedule_service.py (待建立)
class ScheduleService:
    def create_schedule_with_notification(self, schedule_data, user_id):
        # 業務邏輯：建立時段並發送通知
        with db.transaction():
            # 1. 建立時段
            schedule = self.crud.create_schedule(schedule_data)

            # 2. 發送通知
            self.notification_service.send_schedule_created_notification(schedule)

            # 3. 更新統計資料
            self.stats_service.update_user_stats(user_id)

        return schedule
```

---

### **第五層：CRUD 層 (CRUD Layer)**

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
# app/crud/crud_schedule.py
class ScheduleCRUD:
    def get_schedules(self, db: Session, giver_id: int | None = None) -> list[Schedule]:
        query = db.query(Schedule).options(
            *self._get_schedule_query_options()  # 使用 joinedload 優化
        )

        if giver_id:
            query = query.filter(Schedule.giver_id == giver_id)

        return query.all()

    def _get_schedule_query_options(self, include_relations: list[str] | None = None):
        """統一的關聯載入選項管理"""
        if include_relations is None:
            include_relations = ['giver', 'taker', 'created_by_user']

        relation_mapping = {
            'giver': joinedload(Schedule.giver),
            'taker': joinedload(Schedule.taker),
            'created_by_user': joinedload(Schedule.created_by_user),
        }

        return [relation_mapping[rel] for rel in include_relations if rel in relation_mapping]
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
class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    giver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    taker_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 審計追蹤欄位
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
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

#### 範例程式碼

```python
# app/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 資料庫連線設定
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # 連線池大小
    max_overflow=30,  # 最大溢出連線數
    pool_pre_ping=True,  # 連線前檢查
    pool_recycle=3600,  # 連線回收時間
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
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
@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedules(request: ScheduleCreateRequest, db: Session = Depends(get_db)):
    try:
        schedules = schedule_crud.create_schedules(
            db=db,
            schedules=request.schedules,
            updated_by=request.updated_by,
            updated_by_role=request.updated_by_role
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
