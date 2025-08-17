# API 設計原則

## 概述

本專案遵循 `RESTful` 原則設計 `API`，採用 `MVC` 分層架構設計，確保程式碼的可維護性、可擴展性、安全性

## `API` 組成元素

`API` 的核心組成元素主要分為 3 個：

- `URL` 路徑
- `HTTP` 方法 (`HTTP Methods`)
- 處理邏輯（函式）

### `API` 組成元素：1.`URL` 路徑

`URL` 路徑決定了 `API` 資源的位置與結構：

- 範例：`http://127.0.0.1:8000/api/v1/schedules?giver_id=123&date=2025-08-17&sort=desc&page=1&per_page=10`
- 說明：`api/v1/schedules` 路徑中，`ID` 是 123 的使用者，在 2025 年 8 月 17 日的所有行程，以倒序排列，取得第 1 頁，每頁顯示 10 筆資料

| 元件                          | 說明                                                     | 範例                                                                   |
| ----------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------- |
| **基礎 URL (`Base URL`)**     | 伺服器位址（協定 + 網域/主機 + Port）                    | `https://api.example.com` <br> `http://127.0.0.1:8000`                 |
| **基礎路徑 (`Base Path`)**    | 區分 API 與一般網頁服務                                  | `/api`                                                                 |
| **版本號 (`API Version`)**    | API 版本控制，方便升級而不影響舊版本                     | `/v1`                                                                  |
| **資源名稱 (`Resource`)**     | 代表操作的物件，使用**名詞、複數、小寫、連字號**         | `/schedules` <br> `/users` <br> `/givers`                              |
| **路徑參數 (`Path Params`)**  | 指定某個資源的唯一 ID，用 `{}` 表示                      | `/schedules/{schedule_id}` <br> `/users/{user_id}`                     |
| **查詢參數 (`Query Params`)** | 用來篩選、搜尋、排序、分頁，附加在 `?` 之後，以 `&` 分隔 | `/schedules?giver_id=123&date=2025-08-17&sort=desc&page=1&per_page=10` |

### `API` 組成元素：2.`HTTP` 方法 (`HTTP Methods`)

`HTTP` 方法決定了對資源的操作類型，常用的有：

- **`GET`**: 取得資源
- **`POST`**: 建立資源
- **`PATCH`**: 部分更新資源
- **`PUT`**: 完整更新資源
- **`DELETE`**: 刪除資源

### `API` 組成元素：3.處理邏輯（函式）

處理邏輯是 `API` 實際執行的核心，採用**分層架構**設計，每層職責明確：

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

#### **第一層：路由層 (Router Layer)**

**職責**：請求解析與路由分發

**本專案中檔案**：`app/routers`

- **解析請求 (Parse Request)**：
  - 標頭 (`Headers`)：額外資訊，如 `JWT` 認證令牌、內容類型 (`Content-Type`) 等
  - 請求體 (`Request Body`)：`JSON` 格式資料 (`application/json`)、檔案上傳 (`multipart/form-data`) 等
  - 路徑參數 (`Path Params`)：指定某個資源的唯一 `ID`
  - 查詢參數 (`Query Params`)：篩選、搜尋、排序、分頁等
- **路由分發 (Route Dispatch)**：
  - 根據 `HTTP` 方法，呼叫對應的 `CRUD` 層函式
  - 依賴注入 (`Dependency Injection`)：統一管理物件需要的「依賴（如資料庫連線會話 `db: Session = Depends(get_db)`）」，需要時從外部用 `Depends()` 注入依賴，而不是在函式內部建立導致邏輯混亂 

#### **第二層：中介層 (Middleware Layer)**

**職責**：橫切關注點處理

**本專案中檔案**：`app/middleware`

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

#### **第三層：驗證層 (Validation Layer)**

**職責**：資料驗證與序列化

**本專案中檔案**：`app/schemas`

- **輸入驗證 (`Input Validation`)**：
  - 使用 `Pydantic` 模型驗證請求資料格式，防止非法資料進入 `CRUD` 層
  - 自訂驗證規則 (`Custom Validators`)：用 `@field_validator` 裝飾器為特定欄位定義更複雜的驗證邏輯，如檢查 `password` 是否符合複雜度要求
- **資料轉換 (`Data Transformation`)**：
  - 資料型別轉換：如字串轉日期、數字轉布林值，確保 CRUD 層與前端能一致處理資料
  - 請求資料序列化 (`Serialization`)：收到請求時，將前端送來的非 `Python` 格式（如 `JSON` 字串）資料，轉換成 `Python` 物件
  - 回應資料反序列化 (`Deserialization`)：送出回應前，資料庫查詢出的 `Python` 物件，轉換成可傳輸格式（如 `JSON` 字串）

#### **【後續擴充】第四層：服務層 (Service Layer)**

**職責**：業務邏輯處理

**本專案中檔案**：【後續擴充】`app/services`

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

#### **第五層：CRUD 層 (CRUD Layer)**

**職責**：資料庫操作

**本專案中檔案**：`app/crud`

- **增查改刪 (`CRUD Operations`)**：
  - `create_*()` - 建立記錄
  - `get_*()` - 查詢記錄
  - `update_*()` - 更新記錄
  - `delete_*()` - 刪除記錄
- **查詢優化 (`Query Optimization`)**：
  - 索引使用：避免全表查詢，提高查詢速度
  - 分頁處理：資料量龐大時，不一次抓取所有資料，而是分頁查詢
  - 關聯查詢優化：處理一對多、多對多關聯時，合理使用 `JOIN` 或 `ORM` 的 `selectinload`、`joinedload`

#### **第六層：模型層 (Model Layer)**

**職責**：資料結構定義

**本專案中檔案**：`app/models`

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

#### **第七層：資料庫層 (Database Layer)**

**職責**：資料持久化與存取

**本專案中檔案**：`app/models/database.py`

- **資料庫操作 (`Database Operations`)**：
  - `SQL`：執行所有 `CRUD` 操作的 `SQL` 語句，無論是 `ORM` 生成的還是手寫 `SQL`
  - 連線池管理：每次請求時，不是重新建立一個新的資料庫連線，造成效能損耗，而是從池子中借用一個現有的連線，使用完畢後再歸還
  - 事務處理：控制資料庫操作要麼都成功，要麼都失敗，符合 `ACID`（原子性、一致性、隔離性、持久性），如使用 `BEGIN`、`COMMIT`、`ROLLBACK`，確保資料一致性
- **效能優化 (`Performance Optimization`)**：
  - 索引設計：設計適當的單欄位或複合索引，加速查詢、排序或過濾操作
  - 查詢優化：調整 `SQL` 語法、使用 `JOIN`、子查詢或 `ORM` 預載入策略，減少不必要的資料庫存取
  - 資料庫分片：將大表分散到不同資料庫或表中，提高擴展性與效能，適用於超大規模資料

#### **第八層：回應層 (Response Layer)**

**職責**：回應格式化與傳送

**本專案中檔案**：`app/routers`

- **回應格式化 (`Response Formatting`)**：
  - `JSON` 序列化：將業務邏輯的結果，如資料庫查詢出的 `Python` 物件，封裝轉換成可傳輸格式（如 `JSON` 字串）
  - 狀態碼 (`Status Code`) 設定：告訴客戶端本次請求的結果，如 `200 OK`、`201 Created`、`400 Bad Request`、`404 Not Found` 等
  - 標頭 (`Headers`) 設定：如 `Content-Type: application/json` 告訴客戶端回應的格式是 `JSON`
- **錯誤處理 (`Error Handling`)**：
  - 統一錯誤格式：所有類型的錯誤，都以固定的 `JSON` 格式回傳
  - 錯誤日誌記錄：將系統錯誤寫入日誌，用於問題追蹤與系統診斷
  - 使用者友善錯誤訊息：將錯誤訊息轉換為對客戶端有意義的訊息，如 "該電子信箱已被註冊"

## `API` 端點詳細文檔

## 狀態碼 (`Status Code`)

`HTTP` 狀態碼用於表示請求的處理結果：

- **成功狀態碼**
  - **`200 OK`**: 請求成功，且有回應內容
  - **`201 Created`**: 資源建立成功
  - **`204 No Content`**: 請求成功，但無回應內容
- 客戶端錯誤狀態碼
  - **`400 Bad Request`**: 請求格式錯誤
  - **`401 Unauthorized`**: 未授權，如未提供 `JWT`
  - **`403 Forbidden`**: 禁止訪問
  - **`404 Not Found`**: 資源不存在
  - **`422 Unprocessable Entity`**: 請求語義錯誤
- 伺服器錯誤狀態碼
  - **`500 Internal Server Error`**: 伺服器內部錯誤
  - **`503 Service Unavailable`**: 服務不可用

### 回應格式

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

### 1. 使用者管理 `API`

#### 1.1 取得使用者列表

**端點**: `GET /api/v1/users`

**描述**: 取得分頁的使用者列表

**查詢參數**:

- `page` (`int`, 可選): 頁碼，預設為 1
- `per_page` (`int`, 可選): 每頁數量，預設為 10，最大值為 100

**請求範例**:

```bash
GET /api/v1/users?page=1&per_page=20
```

**成功回應** (`200 OK`):

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
