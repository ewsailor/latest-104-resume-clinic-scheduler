# API 端點參考文檔

## 快速查詢表格

### 使用者管理端點

| 方法 | 端點            | 描述           | 狀態碼 |
| ---- | --------------- | -------------- | ------ |
| GET  | `/api/v1/users` | 取得使用者列表 | 200    |
| POST | `/api/v1/users` | 建立使用者     | 201    |

### 排程管理端點

| 方法   | 端點                                 | 描述           | 狀態碼 |
| ------ | ------------------------------------ | -------------- | ------ |
| GET    | `/api/v1/schedules`                  | 取得排程列表   | 200    |
| POST   | `/api/v1/schedules`                  | 建立排程       | 201    |
| GET    | `/api/v1/schedules/{id}`             | 取得特定排程   | 200    |
| PATCH  | `/api/v1/schedules/{id}`             | 更新排程       | 200    |
| DELETE | `/api/v1/schedules/{id}`             | 刪除排程       | 204    |
| GET    | `/api/v1/schedules/giver/{giver_id}` | 取得諮詢師排程 | 200    |
| GET    | `/api/v1/schedules/taker/{taker_id}` | 取得求職者排程 | 200    |

### 諮詢師管理端點

| 方法 | 端點                        | 描述             | 狀態碼 |
| ---- | --------------------------- | ---------------- | ------ |
| GET  | `/api/v1/givers`            | 取得諮詢師列表   | 200    |
| GET  | `/api/v1/givers/{id}`       | 取得特定諮詢師   | 200    |
| GET  | `/api/v1/givers/topics`     | 取得服務項目列表 | 200    |
| GET  | `/api/v1/givers/industries` | 取得產業列表     | 200    |

## 詳細端點說明

### 使用者管理

#### GET /api/v1/users

取得分頁的使用者列表

**查詢參數**:

- `page` (int, 可選): 頁碼，預設為 1
- `per_page` (int, 可選): 每頁數量，預設為 10，最大值為 100

**回應格式**:

```json
{
  "results": [
    {
      "id": 1,
      "name": "王零一",
      "email": "wang@example.com",
      "role": "GIVER",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "total_pages": 3
}
```

#### POST /api/v1/users

建立新的使用者帳戶

**請求體**:

```json
{
  "name": "王零一",
  "email": "wang@example.com",
  "role": "GIVER"
}
```

**回應格式**:

```json
{
  "message": "使用者建立成功",
  "user": {
    "id": 1,
    "name": "王零一",
    "email": "wang@example.com",
    "role": "GIVER",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 排程管理

#### GET /api/v1/schedules

取得排程列表，支援多種篩選條件

**查詢參數**:

- `giver_id` (int, 可選): 根據諮詢師 ID 篩選
- `taker_id` (int, 可選): 根據求職者 ID 篩選
- `status_filter` (string, 可選): 根據狀態篩選

**回應格式**:

```json
[
  {
    "id": 1,
    "creator_role": "GIVER",
    "giver_id": 1,
    "taker_id": null,
    "status": "AVAILABLE",
    "date": "2024-01-20",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "note": "履歷諮詢時段",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "updated_by": 1,
    "updated_by_role": "GIVER",
    "deleted_at": null
  }
]
```

#### POST /api/v1/schedules

批量建立多個時段

**請求體**:

```json
{
  "schedules": [
    {
      "giver_id": 1,
      "taker_id": null,
      "status": "AVAILABLE",
      "date": "2024-01-20",
      "start_time": "14:00:00",
      "end_time": "15:00:00",
      "note": "履歷諮詢時段"
    }
  ],
  "updated_by": 1,
  "updated_by_role": "GIVER"
}
```

**回應格式**:

```json
[
  {
    "id": 1,
    "creator_role": "GIVER",
    "giver_id": 1,
    "taker_id": null,
    "status": "AVAILABLE",
    "date": "2024-01-20",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "note": "履歷諮詢時段",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "updated_by": 1,
    "updated_by_role": "GIVER",
    "deleted_at": null
  }
]
```

#### GET /api/v1/schedules/{id}

根據 ID 取得特定排程的詳細資訊

**路徑參數**:

- `id` (int): 排程 ID

**回應格式**:

```json
{
  "id": 1,
  "creator_role": "GIVER",
  "giver_id": 1,
  "taker_id": null,
  "status": "AVAILABLE",
  "date": "2024-01-20",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "note": "履歷諮詢時段",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "updated_by": 1,
  "updated_by_role": "GIVER",
  "deleted_at": null
}
```

#### PATCH /api/v1/schedules/{id}

更新特定排程的資訊

**路徑參數**:

- `id` (int): 排程 ID

**請求體**:

```json
{
  "schedule_data": {
    "giver_id": 1,
    "taker_id": 2,
    "status": "PENDING",
    "date": "2024-01-20",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "note": "已預約的履歷諮詢時段"
  },
  "updated_by": 2,
  "updated_by_role": "TAKER"
}
```

#### DELETE /api/v1/schedules/{id}

軟刪除特定排程

**路徑參數**:

- `id` (int): 排程 ID

**請求體**:

```json
{
  "updated_by": 1,
  "updated_by_role": "GIVER"
}
```

#### GET /api/v1/schedules/giver/{giver_id}

取得特定諮詢師的所有排程

**路徑參數**:

- `giver_id` (int): 諮詢師 ID

#### GET /api/v1/schedules/taker/{taker_id}

取得特定求職者的所有排程

**路徑參數**:

- `taker_id` (int): 求職者 ID

### 諮詢師管理

#### GET /api/v1/givers

取得分頁的諮詢師列表

**查詢參數**:

- `topic` (string, 可選): 根據服務項目篩選
- `industry` (string, 可選): 根據產業篩選
- `page` (int, 可選): 頁碼，預設為 1
- `per_page` (int, 可選): 每頁數量，預設為 12，最大值為 100

**回應格式**:

```json
{
  "results": [
    {
      "id": 1,
      "name": "王零一",
      "title": "資深軟體工程師",
      "company": "科技公司",
      "industry": "科技業",
      "topics": ["履歷諮詢", "面試技巧"],
      "experience_years": 5,
      "rating": 4.8,
      "avatar": "https://example.com/avatar1.jpg"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "total_pages": 3
}
```

#### GET /api/v1/givers/{id}

取得特定諮詢師的詳細資訊

**路徑參數**:

- `id` (int): 諮詢師 ID

**回應格式**:

```json
{
  "id": 1,
  "name": "王零一",
  "title": "資深軟體工程師",
  "company": "科技公司",
  "industry": "科技業",
  "topics": ["履歷諮詢", "面試技巧"],
  "experience_years": 5,
  "rating": 4.8,
  "avatar": "https://example.com/avatar1.jpg",
  "bio": "擁有 5 年軟體開發經驗，專精於後端開發...",
  "available_schedules": [
    {
      "date": "2024-01-20",
      "start_time": "14:00:00",
      "end_time": "15:00:00"
    }
  ]
}
```

#### GET /api/v1/givers/topics

取得所有可用的服務項目列表

**回應格式**:

```json
{
  "results": ["履歷諮詢", "面試技巧", "職涯規劃", "技能提升"],
  "total": 4,
  "description": "所有可用的服務項目列表"
}
```

#### GET /api/v1/givers/industries

取得所有可用的產業列表

**回應格式**:

```json
{
  "results": ["科技業", "金融業", "製造業", "服務業"],
  "total": 4,
  "description": "所有可用的產業列表"
}
```

## 錯誤代碼參考

### HTTP 狀態碼

#### 成功狀態碼 (2xx)

| 狀態碼 | 描述       | 使用場景             |
| ------ | ---------- | -------------------- |
| 200    | OK         | 請求成功、更新成功   |
| 201    | Created    | 資源建立成功         |
| 204    | No Content | 請求成功但無回應內容 |

#### 客戶端錯誤 (4xx)

| 狀態碼 | 描述                 | 使用場景                            |
| ------ | -------------------- | ----------------------------------- |
| 400    | Bad Request          | 請求格式錯誤或業務邏輯錯誤          |
| 401    | Unauthorized         | 未授權，如未提供 `JWT`、尚未登入    |
| 403    | Forbidden            | 禁止訪問，如權限不足                |
| 404    | Not Found            | 資源不存在                          |
| 409    | Conflict             | 資源衝突，如時段重疊                |
| 422    | Unprocessable Entity | 請求語義錯誤、Pydantic 資料驗證失敗 |

#### 伺服器錯誤 (5xx)

| 狀態碼 | 描述                  | 使用場景                     |
| ------ | --------------------- | ---------------------------- |
| 500    | Internal Server Error | 伺服器內部錯誤，如資料庫錯誤 |
| 503    | Service Unavailable   | 服務不可用，如維護或超載     |

### 錯誤代碼常數對應表 (按架構層級分類)

#### RouterErrorCode (API 路由層)

| 錯誤代碼常數                           | HTTP 狀態碼 | 描述               | 使用場景               |
| -------------------------------------- | ----------- | ------------------ | ---------------------- |
| `RouterErrorCode.BAD_REQUEST`          | 400         | 路由參數格式錯誤   | 請求參數格式不正確     |
| `RouterErrorCode.INVALID_METHOD`       | 400         | 不支援的 HTTP 方法 | 使用不支援的 HTTP 方法 |
| `RouterErrorCode.AUTHENTICATION_ERROR` | 401         | 路由層認證失敗     | 未提供或無效的認證資訊 |
| `RouterErrorCode.AUTHORIZATION_ERROR`  | 403         | 路由層權限不足     | 已認證但無權限執行操作 |
| `RouterErrorCode.ENDPOINT_NOT_FOUND`   | 404         | API 端點不存在     | 訪問不存在的 API 端點  |
| `RouterErrorCode.VALIDATION_ERROR`     | 422         | 路由層資料驗證失敗 | Pydantic 驗證錯誤      |

#### ServiceErrorCode (業務邏輯層)

| 錯誤代碼常數                            | HTTP 狀態碼 | 描述         | 使用場景                 |
| --------------------------------------- | ----------- | ------------ | ------------------------ |
| `ServiceErrorCode.BUSINESS_LOGIC_ERROR` | 400         | 業務邏輯錯誤 | 時段重疊、無效操作等     |
| `ServiceErrorCode.SCHEDULE_OVERLAP`     | 400         | 時段重疊     | 預約時段與現有時段衝突   |
| `ServiceErrorCode.INVALID_OPERATION`    | 400         | 無效操作     | 不允許的業務操作         |
| `ServiceErrorCode.USER_NOT_FOUND`       | 404         | 使用者不存在 | 查詢不存在的使用者       |
| `ServiceErrorCode.SCHEDULE_NOT_FOUND`   | 404         | 時段不存在   | 查詢不存在的時段         |
| `ServiceErrorCode.CONFLICT`             | 409         | 業務邏輯衝突 | 重複的 email、資源衝突等 |

#### CRUDErrorCode (資料存取層)

| 錯誤代碼常數                         | HTTP 狀態碼 | 描述              | 使用場景                 |
| ------------------------------------ | ----------- | ----------------- | ------------------------ |
| `CRUDErrorCode.BAD_REQUEST`          | 400         | CRUD 操作參數錯誤 | 資料庫操作參數不正確     |
| `CRUDErrorCode.RECORD_NOT_FOUND`     | 404         | 資料庫記錄不存在  | 查詢不存在的資料庫記錄   |
| `CRUDErrorCode.CONSTRAINT_VIOLATION` | 409         | 資料庫約束違反    | 唯一性約束、外鍵約束違反 |
| `CRUDErrorCode.DATABASE_ERROR`       | 500         | 資料庫操作失敗    | 資料庫連線或查詢錯誤     |
| `CRUDErrorCode.CONNECTION_ERROR`     | 500         | 資料庫連線錯誤    | 資料庫連線中斷或超時     |

#### CORSErrorCode (跨域請求層)

| 錯誤代碼常數                       | HTTP 狀態碼 | 描述              | 使用場景                   |
| ---------------------------------- | ----------- | ----------------- | -------------------------- |
| `CORSErrorCode.ORIGIN_NOT_ALLOWED` | 403         | 來源網域不被允許  | 來自不被允許的網域         |
| `CORSErrorCode.METHOD_NOT_ALLOWED` | 403         | HTTP 方法不被允許 | 跨域請求使用不被允許的方法 |
| `CORSErrorCode.HEADER_NOT_ALLOWED` | 403         | 請求標頭不被允許  | 跨域請求包含不被允許的標頭 |

#### SystemErrorCode (通用錯誤)

| 錯誤代碼常數                          | HTTP 狀態碼 | 描述           | 使用場景                 |
| ------------------------------------- | ----------- | -------------- | ------------------------ |
| `SystemErrorCode.INTERNAL_ERROR`      | 500         | 內部伺服器錯誤 | 未預期的系統錯誤         |
| `SystemErrorCode.SERVICE_UNAVAILABLE` | 503         | 服務不可用     | 系統維護或外部服務不可用 |

### 錯誤代碼使用範例

#### 1. 按層級使用錯誤代碼

```python
from app.errors import (
    RouterErrorCode,
    ServiceErrorCode,
    CRUDErrorCode,
    CORSErrorCode,
    SystemErrorCode
)

# Router 層錯誤
raise ValidationError("參數驗證失敗", error_code=RouterErrorCode.VALIDATION_ERROR)

# Service 層錯誤
raise BusinessLogicError("時段重疊", error_code=ServiceErrorCode.SCHEDULE_OVERLAP)

# CRUD 層錯誤
raise DatabaseError("資料庫連線失敗", error_code=CRUDErrorCode.CONNECTION_ERROR)

# CORS 層錯誤
raise AuthorizationError("來源網域不被允許", error_code=CORSErrorCode.ORIGIN_NOT_ALLOWED)

# 系統層錯誤
raise ServiceUnavailableError("服務暫時不可用", error_code=SystemErrorCode.SERVICE_UNAVAILABLE)
```

#### 2. 使用整合的 ErrorCode 類別

```python
from app.errors import ErrorCode

# 透過整合類別訪問各層級錯誤代碼
raise ValidationError("參數驗證失敗", error_code=ErrorCode.ROUTER.VALIDATION_ERROR)
raise BusinessLogicError("時段重疊", error_code=ErrorCode.SERVICE.SCHEDULE_OVERLAP)
raise DatabaseError("資料庫連線失敗", error_code=ErrorCode.CRUD.CONNECTION_ERROR)
```

#### 3. 向後相容性使用

```python
from app.errors import ErrorCode

# 舊的錯誤代碼仍然可用
raise ValidationError("參數驗證失敗", error_code=ErrorCode.VALIDATION_ERROR)
raise BusinessLogicError("時段重疊", error_code=ErrorCode.SCHEDULE_OVERLAP)
raise DatabaseError("資料庫連線失敗", error_code=ErrorCode.DATABASE_ERROR)
```

### 常見錯誤回應

#### 400 Bad Request - 業務邏輯錯誤

```json
{
  "detail": "時段重疊：2024-01-20 14:00:00 到 15:00:00 與現有時段衝突"
}
```

#### 422 Unprocessable Entity - 資料驗證錯誤

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "schedules"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

#### 404 Not Found - 資源不存在

```json
{
  "detail": "排程不存在"
}
```

## 資料類型定義

### 排程狀態 (ScheduleStatusEnum)

- `DRAFT`: 草稿狀態
- `AVAILABLE`: 可預約狀態
- `PENDING`: 等待確認狀態
- `ACCEPTED`: 已接受狀態
- `REJECTED`: 已拒絕狀態
- `CANCELLED`: 已取消狀態
- `COMPLETED`: 已完成狀態

### 使用者角色 (UserRoleEnum)

- `GIVER`: 諮詢師角色
- `TAKER`: 求職者角色
- `ADMIN`: 管理員角色

### 日期時間格式

- 日期: `YYYY-MM-DD` (例如: `2024-01-20`)
- 時間: `HH:MM:SS` (例如: `14:00:00`)
- 日期時間: `YYYY-MM-DDTHH:MM:SSZ` (例如: `2024-01-15T10:30:00Z`)

## 開發者工具

### cURL 範例

#### 建立使用者

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "王零一",
    "email": "wang@example.com",
    "role": "GIVER"
  }'
```

#### 建立排程

```bash
curl -X POST "http://localhost:8000/api/v1/schedules" \
  -H "Content-Type: application/json" \
  -d '{
    "schedules": [{
      "giver_id": 1,
      "date": "2024-01-20",
      "start_time": "14:00:00",
      "end_time": "15:00:00",
      "note": "履歷諮詢時段"
    }],
    "updated_by": 1,
    "updated_by_role": "GIVER"
  }'
```

#### 查詢排程

```bash
curl -X GET "http://localhost:8000/api/v1/schedules?giver_id=1&status_filter=AVAILABLE"
```

### Python 範例

#### 使用 requests 庫

```python
import requests

# 建立使用者
response = requests.post(
    "http://localhost:8000/api/v1/users",
    json={
        "name": "王零一",
        "email": "wang@example.com",
        "role": "GIVER"
    }
)
print(response.json())

# 建立排程
response = requests.post(
    "http://localhost:8000/api/v1/schedules",
    json={
        "schedules": [{
            "giver_id": 1,
            "date": "2024-01-20",
            "start_time": "14:00:00",
            "end_time": "15:00:00"
        }],
        "updated_by": 1,
        "updated_by_role": "GIVER"
    }
)
print(response.json())
```

#### 使用 httpx 庫 (異步)

```python
import httpx
import asyncio

async def create_schedule():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/schedules",
            json={
                "schedules": [{
                    "giver_id": 1,
                    "date": "2024-01-20",
                    "start_time": "14:00:00",
                    "end_time": "15:00:00"
                }],
                "updated_by": 1,
                "updated_by_role": "GIVER"
            }
        )
        return response.json()

# 執行
result = asyncio.run(create_schedule())
print(result)
```

## 測試端點

### 健康檢查

```bash
curl -X GET "http://localhost:8000/health"
```

### API 文檔

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 版本資訊

- API 版本: v1
- 最後更新: 2024-01-15
- 支援的內容類型: `application/json`
- 編碼: UTF-8
