# API 設計原則

## 概述

本專案遵循 `RESTful` 原則設計 API，採用分層架構設計，包含路由層、業務邏輯層和資料存取層，確保程式碼的可維護性、可擴展性、安全性

## 組成元素

API 的核心組成元素主要分為 3 個：
- URL 路徑
- HTTP 方法 (`HTTP Methods`)
- 處理邏輯（函式）

### 組成元素：URL 路徑

URL 路徑決定了 API 資源的位置與結構：
- 範例：http://127.0.0.1:8000/api/v1/schedules?giver_id=123&date=2025-08-17&sort=desc&page=1&per_page=10
- 說明：api/vi/schedules 路徑中，ID 是 123 的使用者，在 2025 年 8 月 17 日的所有行程，以倒序排列，取得第 1 頁，每頁顯示 10 筆資料

| 元件           | 說明             | 範例                    |
| --------------------- | -------------------------- | ------------------------------------------------------ |
| **基礎 URL (Base URL)**   | 伺服器位址（協定 + 網域/主機 + Port）   | `https://api.example.com` <br> `http://127.0.0.1:8000` |
| **基礎路徑 (Base Path)**    | 區分 API 與一般網頁服務             | `/api`                                                 |
| **版本號 (API Version)**   | API 版本控制，方便升級而不影響舊版本       | `/v1`                                                  |
| **資源名稱 (Resource)**     | 代表操作的物件，使用**名詞、複數、小寫、連字號** | `/schedules` <br> `/users` <br> `/givers`              |
| **路徑參數 (Path Params)**  | 指定某個資源的唯一 ID，用 `{}` 表示        | `/schedules/{schedule_id}` <br> `/users/{user_id}`     |
| **查詢參數 (Query Params)** | 用來篩選、搜尋、排序、分頁，附加在 `?` 之後，以 `&` 分隔          | `/schedules?giver_id=123&date=2025-08-17&sort=desc&page=1&per_page=10`              |

### 組成元素：HTTP 方法 (HTTP Methods)

HTTP 方法決了對資源的操作類型，常用的有：
- **`GET`**: 取得資源
- **`POST`**: 建立資源
- **`PUT`**: 完整更新資源
- **`PATCH`**: 部分更新資源
- **`DELETE`**: 刪除資源

### 組成元素：處理邏輯（函式）

處理邏輯是 API 實際執行的核心，常見步驟如下：
- **解析請求 (Parse Request)**：
  - 解析傳入請求的：
    - 標頭 (`Headers`)
    - 請求體 (`Request Body`)
    - 路徑參數 (`Path Params`)
    - 查詢參數 (`Query Params`) 
- **認證、授權、中介邏輯 (Authentication, Authorization, and Middleware)**：確保請求的合法性
  - **認證 (Authentication)**：確認請求者是誰，例如，驗證使用者令牌
  - **授權 (Authorization)**：確認請求者的操作權限
  - **中介邏輯 (Middleware)**：處理一些共通的、非核心的邏輯，比如請求壓縮、速率限制、緩存等，常使用 `CORS`
- **驗證資料 (Validate Data)**：
  - 在 `models` 層，藉 `SQLAlchemy ORM` 設定資料表欄位的屬性，使用**小寫、底線**。如：
    - **基本屬性**：資料型別 (`Type`)、備註 (`comment`)、別名 (`alias`) 等
    - **約束條件**：非負 (`unsigned`)、必填 (`nullable`)、預設值 (`default`)、唯一 (`unique`) 等
    - **關聯**：主鍵 (`Primary Key, PK`)、外鍵 (`Foreign Key, FK`)、關聯 (`relationship`) 等
    - **審計追蹤**：建立時間 (`created_at`)、更新時間 (`updated_at`)、最後更新的使用者 ID (`updated_by`)、最後更新者角色 (`updated_by_role`)、軟刪除 (`deleted_at`) 等
  - 在 `schema` 層，用 `Pydantic` 或自訂驗證，檢查傳入資料之正確性
  - 驗證失敗進行錯誤處理 (`Error Handling`)、日誌 (`Logging`) 顯示錯誤
- **執行業務邏輯 (Execute Business Logic)**：
  - 根據請求內容，執行操作：
    - 查詢或更新資料庫
    - 新增一筆資料
    - 呼叫其他服務
- **建立與設定回應 (Create and Set Response)**：
  - **建立回應 (Create Response)**：封裝業務邏輯的結果（如查詢到的資料），組成回傳資料的標準格式（如 JSON）
  - **設定回應 (Set Response)**：
    - 狀態碼 (`Status Code`)
    - 標頭 (`Headers`)
    - 確保回應與業務邏輯結果一致

### 2. 狀態碼使用

#### 成功狀態碼

- **200 OK**: 請求成功
- **201 Created**: 資源建立成功
- **204 No Content**: 請求成功但無回應內容

#### 客戶端錯誤

- **400 Bad Request**: 請求格式錯誤
- **401 Unauthorized**: 未授權
- **403 Forbidden**: 禁止訪問
- **404 Not Found**: 資源不存在
- **422 Unprocessable Entity**: 請求語義錯誤

#### 伺服器錯誤

- **500 Internal Server Error**: 伺服器內部錯誤
- **503 Service Unavailable**: 服務不可用

### 3. 回應格式

#### 成功回應

```json
{
  "data": {
    "id": 1,
    "name": "王零一",
    "email": "wang@example.com"
  },
  "message": "使用者建立成功"
}
```

#### 錯誤回應

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "資料驗證失敗",
    "details": [
      {
        "field": "email",
        "message": "電子郵件格式不正確"
      }
    ]
  }
}
```

## API 端點詳細文檔

### 1. 使用者管理 API

#### 1.1 取得使用者列表

**端點**: `GET /api/v1/users`

**描述**: 取得分頁的使用者列表

**查詢參數**:

- `page` (int, 可選): 頁碼，預設為 1
- `per_page` (int, 可選): 每頁數量，預設為 10，最大值為 100

**請求範例**:

```bash
GET /api/v1/users?page=1&per_page=20
```

**成功回應** (200 OK):

```json
{
  "results": [
    {
      "id": 1,
      "name": "王零一",
      "email": "wang@example.com",
      "role": "GIVER",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "total_pages": 3
}
```

**錯誤回應**:

- `500 Internal Server Error`: 伺服器內部錯誤

#### 1.2 建立使用者

**端點**: `POST /api/v1/users`

**描述**: 建立新的使用者帳戶

**請求體**:

```json
{
  "name": "王零一",
  "email": "wang@example.com",
  "role": "GIVER"
}
```

**成功回應** (201 Created):

```json
{
  "message": "使用者建立成功",
  "user": {
    "id": 1,
    "name": "王零一",
    "email": "wang@example.com",
    "role": "GIVER",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**錯誤回應**:

- `400 Bad Request`: 資料驗證失敗或使用者已存在
- `422 Unprocessable Entity`: 請求格式錯誤

### 2. 排程管理 API

#### 2.1 建立排程

**端點**: `POST /api/v1/schedules`

**描述**: 批量建立多個時段，需要提供操作者資訊以確保安全性和審計追蹤

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

**成功回應** (201 Created):

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
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "updated_by": 1,
    "updated_by_role": "GIVER",
    "deleted_at": null
  }
]
```

**錯誤回應**:

- `400 Bad Request`: 時段重疊、無效的狀態值或業務邏輯錯誤
- `422 Unprocessable Entity`: 請求格式錯誤

#### 2.2 取得排程列表

**端點**: `GET /api/v1/schedules`

**描述**: 取得排程列表，支援多種篩選條件

**查詢參數**:

- `giver_id` (int, 可選): 根據諮詢師 ID 篩選
- `taker_id` (int, 可選): 根據求職者 ID 篩選
- `status_filter` (string, 可選): 根據狀態篩選（AVAILABLE, PENDING, ACCEPTED, REJECTED, CANCELLED, COMPLETED）

**請求範例**:

```bash
GET /api/v1/schedules?giver_id=1&status_filter=AVAILABLE
```

**成功回應** (200 OK):

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
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "updated_by": 1,
    "updated_by_role": "GIVER",
    "deleted_at": null
  }
]
```

#### 2.3 取得特定排程

**端點**: `GET /api/v1/schedules/{id}`

**描述**: 根據 ID 取得特定排程的詳細資訊

**路徑參數**:

- `id` (int): 排程 ID

**請求範例**:

```bash
GET /api/v1/schedules/1
```

**成功回應** (200 OK):

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

**錯誤回應**:

- `404 Not Found`: 排程不存在

#### 2.4 更新排程

**端點**: `PUT /api/v1/schedules/{id}`

**描述**: 更新特定排程的資訊

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

**成功回應** (200 OK):

```json
{
  "id": 1,
  "creator_role": "GIVER",
  "giver_id": 1,
  "taker_id": 2,
  "status": "PENDING",
  "date": "2024-01-20",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "note": "已預約的履歷諮詢時段",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T11:00:00",
  "updated_by": 2,
  "updated_by_role": "TAKER",
  "deleted_at": null
}
```

**錯誤回應**:

- `400 Bad Request`: 資料驗證失敗或業務邏輯錯誤
- `404 Not Found`: 排程不存在
- `422 Unprocessable Entity`: 請求格式錯誤

#### 2.5 刪除排程

**端點**: `DELETE /api/v1/schedules/{id}`

**描述**: 軟刪除特定排程（標記為已刪除但不實際移除資料）

**路徑參數**:

- `id` (int): 排程 ID

**請求體**:

```json
{
  "updated_by": 1,
  "updated_by_role": "GIVER"
}
```

**成功回應** (204 No Content)

**錯誤回應**:

- `400 Bad Request`: 刪除失敗
- `404 Not Found`: 排程不存在

#### 2.6 取得諮詢師排程

**端點**: `GET /api/v1/schedules/giver/{giver_id}`

**描述**: 取得特定諮詢師的所有排程

**路徑參數**:

- `giver_id` (int): 諮詢師 ID

**成功回應** (200 OK):

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
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "updated_by": 1,
    "updated_by_role": "GIVER",
    "deleted_at": null
  }
]
```

#### 2.7 取得求職者排程

**端點**: `GET /api/v1/schedules/taker/{taker_id}`

**描述**: 取得特定求職者的所有排程

**路徑參數**:

- `taker_id` (int): 求職者 ID

**成功回應** (200 OK):

```json
[
  {
    "id": 1,
    "creator_role": "GIVER",
    "giver_id": 1,
    "taker_id": 2,
    "status": "PENDING",
    "date": "2024-01-20",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "note": "履歷諮詢時段",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T11:00:00",
    "updated_by": 2,
    "updated_by_role": "TAKER",
    "deleted_at": null
  }
]
```

### 3. 諮詢師管理 API

#### 3.1 取得諮詢師列表

**端點**: `GET /api/v1/givers`

**描述**: 取得分頁的諮詢師列表，支援按服務項目和產業篩選

**查詢參數**:

- `topic` (string, 可選): 根據服務項目篩選
- `industry` (string, 可選): 根據產業篩選
- `page` (int, 可選): 頁碼，預設為 1
- `per_page` (int, 可選): 每頁數量，預設為 12，最大值為 100

**請求範例**:

```bash
GET /api/v1/givers?topic=履歷諮詢&industry=科技業&page=1&per_page=10
```

**成功回應** (200 OK):

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

#### 3.2 取得特定諮詢師

**端點**: `GET /api/v1/givers/{id}`

**描述**: 取得特定諮詢師的詳細資訊

**路徑參數**:

- `id` (int): 諮詢師 ID

**成功回應** (200 OK):

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

**錯誤回應**:

- `404 Not Found`: 諮詢師不存在

#### 3.3 取得服務項目列表

**端點**: `GET /api/v1/givers/topics`

**描述**: 取得所有可用的服務項目列表

**成功回應** (200 OK):

```json
{
  "results": ["履歷諮詢", "面試技巧", "職涯規劃", "技能提升"],
  "total": 4,
  "description": "所有可用的服務項目列表"
}
```

#### 3.4 取得產業列表

**端點**: `GET /api/v1/givers/industries`

**描述**: 取得所有可用的產業列表

**成功回應** (200 OK):

```json
{
  "results": ["科技業", "金融業", "製造業", "服務業"],
  "total": 4,
  "description": "所有可用的產業列表"
}
```

## 資料模型說明

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

## 查詢參數

### 1. 分頁參數

```bash
GET /api/v1/users?page=1&size=10
```

### 2. 篩選參數

```bash
GET /api/v1/schedules?giver_id=1&status=AVAILABLE
```

### 3. 排序參數

```bash
GET /api/v1/users?sort=name&order=asc
```

## 資料驗證

### 1. 輸入驗證

- 使用 Pydantic 模型進行資料驗證
- 提供清楚的錯誤訊息
- 支援巢狀物件驗證

### 2. 業務邏輯驗證

- 檢查資料一致性
- 驗證業務規則
- 處理衝突情況

## 安全性

### 1. 認證和授權

- 使用 JWT Token 進行認證
- 實作角色基礎存取控制 (RBAC)
- 驗證 API 金鑰

### 2. 資料保護

- 使用 HTTPS 加密傳輸
- 驗證輸入資料
- 防止 SQL 注入攻擊

## 效能優化

### 1. 快取策略

- 使用 Redis 快取常用資料
- 實作 ETag 和 Last-Modified
- 設定適當的快取標頭

### 2. 資料庫優化

- 使用索引優化查詢
- 實作分頁避免大量資料載入
- 使用連線池管理資料庫連線

## 文檔和測試

### 1. API 文檔

- 使用 OpenAPI/Swagger 自動生成文檔
- 提供詳細的端點說明
- 包含請求和回應範例

### 2. 測試策略

- 單元測試驗證業務邏輯
- 整合測試驗證 API 端點
- 端到端測試驗證完整流程

## 版本控制

### 1. URL 版本控制

```bash
/api/v1/users
/api/v2/users
```

### 2. 向後相容性

- 保持舊版 API 的相容性
- 提供遷移指南
- 逐步淘汰舊版功能

## 監控和日誌

### 1. 監控指標

- API 回應時間
- 錯誤率
- 請求量

### 2. 日誌記錄

- 記錄所有 API 請求
- 記錄錯誤和異常
- 使用結構化日誌格式

## 使用指南

### 1. 快速開始

```bash
# 1. 啟動服務
uvicorn app.main:app --reload

# 2. 訪問 API 文檔
http://localhost:8000/docs

# 3. 建立使用者
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "王零一", "email": "wang@example.com", "role": "GIVER"}'

# 4. 建立排程
curl -X POST "http://localhost:8000/api/v1/schedules" \
  -H "Content-Type: application/json" \
  -d '{
    "schedules": [{
      "giver_id": 1,
      "date": "2024-01-20",
      "start_time": "14:00:00",
      "end_time": "15:00:00"
    }],
    "updated_by": 1,
    "updated_by_role": "GIVER"
  }'
```

### 2. 錯誤處理最佳實踐

```python
import requests

try:
    response = requests.post("/api/v1/schedules", json=schedule_data)
    response.raise_for_status()
    return response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("業務邏輯錯誤:", e.response.json())
    elif e.response.status_code == 422:
        print("資料驗證錯誤:", e.response.json())
    else:
        print("其他錯誤:", e.response.text)
except requests.exceptions.RequestException as e:
    print("網路錯誤:", str(e))
```

### 3. 分頁處理

```python
def get_all_schedules():
    all_schedules = []
    page = 1

    while True:
        response = requests.get(f"/api/v1/schedules?page={page}")
        data = response.json()

        all_schedules.extend(data["results"])

        if page >= data["total_pages"]:
            break

        page += 1

    return all_schedules
```

## 常見問題 (FAQ)

### Q1: 如何處理時段重疊問題？

A: 系統會自動檢查時段重疊，如果發現重疊會回傳 400 錯誤。建議在建立時段前先查詢現有時段。

### Q2: 狀態值為什麼要用大寫？

A: 為了保持與資料庫 ENUM 類型的一致性，所有狀態值都使用大寫格式。

### Q3: 如何實現軟刪除？

A: 系統使用 `deleted_at` 欄位標記刪除的記錄，實際資料仍保留在資料庫中。

### Q4: 如何處理時區問題？

A: 系統統一使用台灣時區 (Asia/Taipei)，所有時間欄位都儲存為本地時間。

### Q5: 如何擴展新的 API 端點？

A: 遵循現有的分層架構，在 `app/routers/api/` 中新增路由檔案，並在 `app/crud/` 中實作對應的 CRUD 操作。
