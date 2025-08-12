# API 最佳實踐指南

## 概述

本指南提供開發和維護 RESTful API 的最佳實踐建議，基於本專案的實際經驗和業界標準。

## 設計原則

### 1. RESTful 設計原則

#### 資源導向設計
- 使用名詞而非動詞來命名資源
- 使用複數形式表示資源集合
- 保持 URL 結構簡潔明瞭

```bash
# ✅ 正確
GET /api/schedules
POST /api/users
PUT /api/givers/123

# ❌ 錯誤
GET /api/get-schedules
POST /api/create-user
PUT /api/update-giver/123
```

#### HTTP 方法語義
- **GET**: 安全且冪等，用於取得資源
- **POST**: 非冪等，用於建立資源
- **PUT**: 冪等，用於完整更新資源
- **PATCH**: 冪等，用於部分更新資源
- **DELETE**: 冪等，用於刪除資源

### 2. 狀態碼使用原則

#### 成功狀態碼
- **200 OK**: 請求成功，返回資源內容
- **201 Created**: 資源建立成功，返回新建立的資源
- **204 No Content**: 請求成功但無回應內容（如刪除操作）

#### 客戶端錯誤
- **400 Bad Request**: 請求格式錯誤或業務邏輯錯誤
- **401 Unauthorized**: 需要認證但未提供或認證失敗
- **403 Forbidden**: 已認證但無權限訪問
- **404 Not Found**: 請求的資源不存在
- **422 Unprocessable Entity**: 請求語義正確但無法處理

#### 伺服器錯誤
- **500 Internal Server Error**: 伺服器內部錯誤
- **503 Service Unavailable**: 服務暫時不可用

## 資料模型設計

### 1. 一致性原則

#### 命名規範
- 使用 snake_case 命名資料庫欄位
- 使用 camelCase 命名 JSON 回應欄位
- 保持命名的一致性和可讀性

```python
# 資料庫模型
class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True)
    giver_id = Column(Integer, ForeignKey("users.id"))
    schedule_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# Pydantic 模型
class ScheduleResponse(BaseModel):
    id: int
    giverId: int = Field(alias="giver_id")
    scheduleDate: date = Field(alias="schedule_date")
    startTime: time = Field(alias="start_time")
    endTime: time = Field(alias="end_time")
    createdAt: datetime = Field(alias="created_at")
```

#### 資料類型一致性
- 使用 ENUM 確保狀態值的一致性
- 統一日期時間格式
- 保持數值類型的精確性

```python
from enum import Enum

class ScheduleStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
```

### 2. 驗證和錯誤處理

#### 輸入驗證
- 使用 Pydantic 進行資料驗證
- 提供清楚的錯誤訊息
- 驗證業務邏輯規則

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date, time

class ScheduleCreate(BaseModel):
    giver_id: int = Field(..., gt=0, description="Giver ID")
    schedule_date: date = Field(..., description="時段日期")
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

#### 錯誤回應格式
- 提供一致的錯誤回應格式
- 包含錯誤代碼和詳細訊息
- 支援多語言錯誤訊息

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "資料驗證失敗",
    "details": [
      {
        "field": "end_time",
        "message": "結束時間必須晚於開始時間",
        "value": "14:00:00"
      }
    ]
  }
}
```

## 安全性最佳實踐

### 1. 認證和授權

#### JWT Token 認證
- 使用安全的 JWT 實作
- 設定適當的過期時間
- 實作 Token 刷新機制

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="無效的認證憑證")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="認證憑證已過期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="無效的認證憑證")
```

#### 角色基礎存取控制 (RBAC)
- 實作細粒度的權限控制
- 驗證操作者的角色和權限
- 記錄所有敏感操作

```python
from enum import Enum
from fastapi import HTTPException, status

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    GIVER = "GIVER"
    TAKER = "TAKER"

def require_role(required_role: UserRole):
    def role_checker(current_user_role: UserRole = Depends(get_current_user_role)):
        if current_user_role != required_role and current_user_role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail=f"需要 {required_role} 角色才能執行此操作"
            )
        return current_user_role
    return role_checker
```

### 2. 資料保護

#### 輸入驗證和清理
- 驗證所有輸入資料
- 防止 SQL 注入攻擊
- 使用參數化查詢

```python
# ✅ 正確 - 使用參數化查詢
def get_schedules_by_giver(db: Session, giver_id: int):
    return db.query(Schedule).filter(Schedule.giver_id == giver_id).all()

# ❌ 錯誤 - 容易受到 SQL 注入攻擊
def get_schedules_by_giver_unsafe(db: Session, giver_id: str):
    return db.execute(f"SELECT * FROM schedules WHERE giver_id = {giver_id}")
```

#### 敏感資料處理
- 加密敏感資料
- 使用 HTTPS 傳輸
- 實作資料遮罩

```python
from pydantic import SecretStr

class UserCreate(BaseModel):
    name: str
    email: str
    password: SecretStr  # 自動遮罩密碼
```

## 效能優化

### 1. 資料庫優化

#### 索引策略
- 為常用查詢欄位建立索引
- 使用複合索引優化多欄位查詢
- 定期分析查詢效能

```sql
-- 為常用查詢建立索引
CREATE INDEX idx_schedules_giver_date ON schedules(giver_id, schedule_date);
CREATE INDEX idx_schedules_status ON schedules(status);
CREATE INDEX idx_schedules_created_at ON schedules(created_at);
```

#### 查詢優化
- 使用分頁避免大量資料載入
- 實作延遲載入 (Lazy Loading)
- 使用連線池管理資料庫連線

```python
def get_schedules_paginated(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    giver_id: Optional[int] = None
):
    query = db.query(Schedule)
    
    if giver_id:
        query = query.filter(Schedule.giver_id == giver_id)
    
    return query.offset(skip).limit(limit).all()
```

### 2. 快取策略

#### Redis 快取
- 快取常用查詢結果
- 實作快取失效策略
- 使用快取標頭

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 嘗試從快取取得結果
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 執行函數並快取結果
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

#### HTTP 快取
- 使用 ETag 和 Last-Modified 標頭
- 設定適當的快取控制標頭
- 實作條件請求

```python
from fastapi import Response
from datetime import datetime

@router.get("/api/schedules")
async def get_schedules(response: Response, db: Session = Depends(get_db)):
    schedules = schedule_crud.get_schedules(db)
    
    # 設定快取標頭
    response.headers["ETag"] = f'"{hash(str(schedules))}"'
    response.headers["Last-Modified"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers["Cache-Control"] = "public, max-age=300"
    
    return schedules
```

## 監控和日誌

### 1. 結構化日誌

#### 日誌格式
- 使用結構化日誌格式 (JSON)
- 包含必要的上下文資訊
- 設定適當的日誌級別

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_request(self, method: str, path: str, status_code: int, duration: float):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "message": f"{method} {path} - {status_code}"
        }
        self.logger.info(json.dumps(log_entry))
```

#### 錯誤追蹤
- 記錄詳細的錯誤資訊
- 包含堆疊追蹤
- 實作錯誤報告機制

```python
import traceback
from fastapi import HTTPException

@router.post("/api/schedules")
async def create_schedules(request: ScheduleCreateWithOperator, db: Session = Depends(get_db)):
    try:
        return schedule_crud.create_schedules(db, request.schedules)
    except Exception as e:
        # 記錄詳細錯誤資訊
        logger.error(f"建立排程失敗: {str(e)}")
        logger.error(f"堆疊追蹤: {traceback.format_exc()}")
        
        # 回傳適當的錯誤回應
        raise HTTPException(
            status_code=500,
            detail="建立排程時發生內部錯誤"
        )
```

### 2. 效能監控

#### 關鍵指標
- API 回應時間
- 請求量和錯誤率
- 資料庫查詢效能
- 記憶體和 CPU 使用率

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    
    # 記錄效能指標
    logger.info(f"請求處理時間: {process_time:.3f}秒")
    
    return response
```

## 測試策略

### 1. 單元測試

#### 測試覆蓋率
- 確保高測試覆蓋率
- 測試邊界條件
- 測試錯誤情況

```python
import pytest
from unittest.mock import Mock, patch

def test_create_schedule_success():
    # 準備測試資料
    mock_db = Mock()
    schedule_data = ScheduleCreate(
        giver_id=1,
        schedule_date=date(2024, 1, 20),
        start_time=time(14, 0),
        end_time=time(15, 0)
    )
    
    # 模擬資料庫操作
    mock_schedule = Mock()
    mock_schedule.id = 1
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    # 執行測試
    result = schedule_crud.create_schedule(mock_db, schedule_data)
    
    # 驗證結果
    assert result.id == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```

### 2. 整合測試

#### API 端點測試
- 測試完整的 API 流程
- 驗證請求和回應格式
- 測試錯誤處理

```python
from fastapi.testclient import TestClient

def test_create_schedules_api():
    client = TestClient(app)
    
    # 準備測試資料
    schedule_data = {
        "schedules": [{
            "giver_id": 1,
            "date": "2024-01-20",
            "start_time": "14:00:00",
            "end_time": "15:00:00"
        }],
        "operator_user_id": 1,
        "operator_role": "GIVER"
    }
    
    # 執行 API 請求
    response = client.post("/api/schedules", json=schedule_data)
    
    # 驗證回應
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["giver_id"] == 1
```

### 3. 端到端測試

#### 完整流程測試
- 測試真實的使用場景
- 驗證系統整合
- 測試效能和穩定性

```python
import asyncio
import httpx

async def test_complete_schedule_flow():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # 1. 建立使用者
        user_response = await client.post("/api/users", json={
            "name": "測試使用者",
            "email": "test@example.com",
            "role": "GIVER"
        })
        assert user_response.status_code == 201
        user_id = user_response.json()["user"]["id"]
        
        # 2. 建立排程
        schedule_response = await client.post("/api/schedules", json={
            "schedules": [{
                "giver_id": user_id,
                "date": "2024-01-20",
                "start_time": "14:00:00",
                "end_time": "15:00:00"
            }],
            "operator_user_id": user_id,
            "operator_role": "GIVER"
        })
        assert schedule_response.status_code == 201
        
        # 3. 查詢排程
        schedules_response = await client.get(f"/api/schedules?giver_id={user_id}")
        assert schedules_response.status_code == 200
        schedules = schedules_response.json()
        assert len(schedules) == 1
```

## 版本控制策略

### 1. URL 版本控制

#### 版本命名
- 使用語義化版本控制
- 保持向後相容性
- 提供遷移指南

```python
# 版本 1 API
@router.get("/api/v1/schedules")
async def get_schedules_v1():
    pass

# 版本 2 API (新功能)
@router.get("/api/v2/schedules")
async def get_schedules_v2():
    pass
```

### 2. 向後相容性

#### 相容性原則
- 保持舊版 API 的相容性
- 逐步淘汰舊版功能
- 提供遷移工具

```python
# 支援舊版格式
@router.post("/api/schedules")
async def create_schedules(request: Union[ScheduleCreateWithOperator, ScheduleCreateLegacy]):
    if isinstance(request, ScheduleCreateLegacy):
        # 轉換舊版格式
        request = convert_legacy_format(request)
    
    return schedule_crud.create_schedules(request)
```

## 部署和維護

### 1. 環境配置

#### 配置管理
- 使用環境變數管理配置
- 支援多環境部署
- 實作配置驗證

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. 健康檢查

#### 健康檢查端點
- 檢查資料庫連線
- 檢查外部服務狀態
- 提供詳細的健康狀態

```python
@router.get("/health")
async def health_check():
    try:
        # 檢查資料庫連線
        db = next(get_db())
        db.execute("SELECT 1")
        
        # 檢查 Redis 連線
        redis_client.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "healthy",
                "redis": "healthy"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
```

## 總結

遵循這些最佳實踐可以確保 API 的：

1. **可維護性**: 清晰的程式碼結構和文檔
2. **安全性**: 適當的認證、授權和資料保護
3. **效能**: 優化的查詢和快取策略
4. **可靠性**: 完善的錯誤處理和監控
5. **可擴展性**: 模組化設計和版本控制

持續改進和監控是保持 API 品質的關鍵。
