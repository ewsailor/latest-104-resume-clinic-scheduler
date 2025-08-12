# API 設計原則與文檔

## 概述

本專案遵循 RESTful API 設計原則，提供一致、可預測的 API 介面。API 採用分層架構設計，包含路由層、業務邏輯層和資料存取層，確保程式碼的可維護性和可擴展性。

## 設計原則

### 1. RESTful 設計

#### 資源命名

- 使用名詞而非動詞
- 使用複數形式
- 使用小寫字母和連字號

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

#### HTTP 方法使用

- **GET**: 取得資源
- **POST**: 建立資源
- **PUT**: 更新資源（完整更新）
- **PATCH**: 部分更新資源
- **DELETE**: 刪除資源

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

**端點**: `GET /api/users`

**描述**: 取得分頁的使用者列表

**查詢參數**:

- `page` (int, 可選): 頁碼，預設為 1
- `per_page` (int, 可選): 每頁數量，預設為 10，最大值為 100

**請求範例**:

```bash
GET /api/users?page=1&per_page=20
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

**端點**: `POST /api/users`

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

**端點**: `POST /api/schedules`

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
  "operator_user_id": 1,
  "operator_role": "GIVER"
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

**端點**: `GET /api/schedules`

**描述**: 取得排程列表，支援多種篩選條件

**查詢參數**:

- `giver_id` (int, 可選): 根據諮詢師 ID 篩選
- `taker_id` (int, 可選): 根據求職者 ID 篩選
- `status_filter` (string, 可選): 根據狀態篩選（AVAILABLE, PENDING, ACCEPTED, REJECTED, CANCELLED, COMPLETED）

**請求範例**:

```bash
GET /api/schedules?giver_id=1&status_filter=AVAILABLE
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

**端點**: `GET /api/schedules/{id}`

**描述**: 根據 ID 取得特定排程的詳細資訊

**路徑參數**:

- `id` (int): 排程 ID

**請求範例**:

```bash
GET /api/schedules/1
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

**端點**: `PUT /api/schedules/{id}`

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
  "operator_user_id": 2,
  "operator_role": "TAKER"
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

**端點**: `DELETE /api/schedules/{id}`

**描述**: 軟刪除特定排程（標記為已刪除但不實際移除資料）

**路徑參數**:

- `id` (int): 排程 ID

**請求體**:

```json
{
  "operator_user_id": 1,
  "operator_role": "GIVER"
}
```

**成功回應** (204 No Content)

**錯誤回應**:

- `400 Bad Request`: 刪除失敗
- `404 Not Found`: 排程不存在

#### 2.6 取得諮詢師排程

**端點**: `GET /api/schedules/giver/{giver_id}`

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

**端點**: `GET /api/schedules/taker/{taker_id}`

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

**端點**: `GET /api/givers`

**描述**: 取得分頁的諮詢師列表，支援按服務項目和產業篩選

**查詢參數**:

- `topic` (string, 可選): 根據服務項目篩選
- `industry` (string, 可選): 根據產業篩選
- `page` (int, 可選): 頁碼，預設為 1
- `per_page` (int, 可選): 每頁數量，預設為 12，最大值為 100

**請求範例**:

```bash
GET /api/givers?topic=履歷諮詢&industry=科技業&page=1&per_page=10
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

**端點**: `GET /api/givers/{id}`

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

**端點**: `GET /api/givers/topics`

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

**端點**: `GET /api/givers/industries`

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
GET /api/users?page=1&size=10
```

### 2. 篩選參數

```bash
GET /api/schedules?giver_id=1&status=AVAILABLE
```

### 3. 排序參數

```bash
GET /api/users?sort=name&order=asc
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
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "王零一", "email": "wang@example.com", "role": "GIVER"}'

# 4. 建立排程
curl -X POST "http://localhost:8000/api/schedules" \
  -H "Content-Type: application/json" \
  -d '{
    "schedules": [{
      "giver_id": 1,
      "date": "2024-01-20",
      "start_time": "14:00:00",
      "end_time": "15:00:00"
    }],
    "operator_user_id": 1,
    "operator_role": "GIVER"
  }'
```

### 2. 錯誤處理最佳實踐

```python
import requests

try:
    response = requests.post("/api/schedules", json=schedule_data)
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
        response = requests.get(f"/api/schedules?page={page}")
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
