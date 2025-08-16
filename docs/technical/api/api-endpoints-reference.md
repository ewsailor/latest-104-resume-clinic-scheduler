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
      "created_at": "2024-01-15T10:30:00"
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
    "created_at": "2024-01-15T10:30:00"
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
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
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
  "operator_user_id": 1,
  "operator_role": "GIVER"
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
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
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
  "operator_user_id": 2,
  "operator_role": "TAKER"
}
```

#### DELETE /api/v1/schedules/{id}

軟刪除特定排程

**路徑參數**:

- `id` (int): 排程 ID

**請求體**:

```json
{
  "operator_user_id": 1,
  "operator_role": "GIVER"
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

| 狀態碼 | 描述                  | 使用場景                   |
| ------ | --------------------- | -------------------------- |
| 200    | OK                    | 請求成功                   |
| 201    | Created               | 資源建立成功               |
| 204    | No Content            | 請求成功但無回應內容       |
| 400    | Bad Request           | 請求格式錯誤或業務邏輯錯誤 |
| 401    | Unauthorized          | 未授權                     |
| 403    | Forbidden             | 禁止訪問                   |
| 404    | Not Found             | 資源不存在                 |
| 422    | Unprocessable Entity  | 請求語義錯誤               |
| 500    | Internal Server Error | 伺服器內部錯誤             |
| 503    | Service Unavailable   | 服務不可用                 |

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
- 日期時間: `YYYY-MM-DDTHH:MM:SS` (例如: `2024-01-15T10:30:00`)

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
    "operator_user_id": 1,
    "operator_role": "GIVER"
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
        "operator_user_id": 1,
        "operator_role": "GIVER"
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
                "operator_user_id": 1,
                "operator_role": "GIVER"
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
