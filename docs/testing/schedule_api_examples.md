# Schedules API 測試範例

## 概述

本文檔提供 104 履歷診療室排程系統 Schedules API 的正確使用範例。

## API 端點

### 基礎 URL

```
http://localhost:8000/api/v1
```

## 測試案例

### 1. 建立時段 (POST /schedules)

**請求**:

```http
POST /api/v1/schedules
Content-Type: application/json
```

**請求體**:

```json
{
  "schedules": [
    {
      "giver_id": 1,
      "taker_id": null,
      "status": "AVAILABLE",
      "date": "2025-09-20",
      "start_time": "14:00:00",
      "end_time": "15:00:00",
      "note": "測試時段1"
    }
  ],
  "created_by": 1,
  "created_by_role": "GIVER"
}
```

**預期回應** (201 Created):

```json
[
  {
    "id": 1,
    "giver_id": 1,
    "taker_id": null,
    "status": "AVAILABLE",
    "date": "2025-09-20",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "note": "測試時段1",
    "created_at": "2025-08-26T18:55:16",
    "created_by": 1,
    "created_by_role": "GIVER",
    "updated_at": "2025-08-26T18:55:16",
    "updated_by": 1,
    "updated_by_role": "GIVER",
    "deleted_at": null,
    "deleted_by": null,
    "deleted_by_role": null
  }
]
```

### 2. 取得時段列表 (GET /schedules)

**請求**:

```http
GET /api/v1/schedules
```

**查詢參數** (可選):

- `giver_id`: 篩選特定 Giver 的時段
- `taker_id`: 篩選特定 Taker 的時段
- `status_filter`: 篩選特定狀態的時段

**範例**:

```http
GET /api/v1/schedules?giver_id=1&status_filter=AVAILABLE
```

**預期回應** (200 OK):

```json
[
  {
    "id": 1,
    "giver_id": 1,
    "taker_id": null,
    "status": "AVAILABLE",
    "date": "2025-09-20",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "note": "測試時段1",
    "created_at": "2025-08-26T18:55:16",
    "created_by": 1,
    "created_by_role": "GIVER",
    "updated_at": "2025-08-26T18:55:16",
    "updated_by": 1,
    "updated_by_role": "GIVER",
    "deleted_at": null,
    "deleted_by": null,
    "deleted_by_role": null
  }
]
```

### 3. 取得特定時段 (GET /schedules/{id})

**請求**:

```http
GET /api/v1/schedules/1
```

**預期回應** (200 OK):

```json
{
  "id": 1,
  "giver_id": 1,
  "taker_id": null,
  "status": "AVAILABLE",
  "date": "2025-09-20",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "note": "測試時段1",
  "created_at": "2025-08-26T18:55:16",
  "created_by": 1,
  "created_by_role": "GIVER",
  "updated_at": "2025-08-26T18:55:16",
  "updated_by": 1,
  "updated_by_role": "GIVER",
  "deleted_at": null,
  "deleted_by": null,
  "deleted_by_role": null
}
```

### 4. 更新時段 (PATCH /schedules/{id})

**請求**:

```http
PATCH /api/v1/schedules/1
Content-Type: application/json
```

**請求體**:

```json
{
  "schedule": {
    "status": "ACCEPTED",
    "note": "已預約"
  },
  "updated_by": 1,
  "updated_by_role": "GIVER"
}
```

**預期回應** (200 OK):

```json
{
  "id": 1,
  "giver_id": 1,
  "taker_id": null,
  "status": "ACCEPTED",
  "date": "2025-09-20",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "note": "已預約",
  "created_at": "2025-08-26T18:55:16",
  "created_by": 1,
  "created_by_role": "GIVER",
  "updated_at": "2025-08-26T18:58:11",
  "updated_by": 1,
  "updated_by_role": "GIVER",
  "deleted_at": null,
  "deleted_by": null,
  "deleted_by_role": null
}
```

### 5. 刪除時段 (DELETE /schedules/{id})

**請求**:

```http
DELETE /api/v1/schedules/1
Content-Type: application/json
```

**請求體**:

```json
{
  "deleted_by": 1,
  "deleted_by_role": "GIVER"
}
```

**預期回應** (204 No Content):

```json
// 無回應內容
```

## 錯誤處理範例

### 1. 驗證錯誤 (422)

**錯誤請求**:

```json
{
  "schedules": [
    {
      "giver_id": "invalid", // 應該是整數
      "date": "invalid-date", // 無效日期格式
      "start_time": "25:00:00", // 無效時間
      "end_time": "10:00:00"
    }
  ],
  "created_by": 1,
  "created_by_role": "GIVER"
}
```

**錯誤回應**:

```json
{
  "error": {
    "code": "ROUTER_VALIDATION_ERROR",
    "message": "請求資料驗證失敗",
    "status_code": 422,
    "timestamp": "2025-08-26T11:10:47Z",
    "details": [
      {
        "type": "int_parsing",
        "loc": ["body", "schedules", 0, "giver_id"],
        "msg": "Input should be a valid integer, unable to parse string as an integer",
        "input": "invalid"
      },
      {
        "type": "date_from_datetime_parsing",
        "loc": ["body", "schedules", 0, "date"],
        "msg": "Input should be a valid date or datetime, invalid character in year",
        "input": "invalid-date",
        "ctx": {
          "error": "invalid character in year"
        }
      },
      {
        "type": "time_parsing",
        "loc": ["body", "schedules", 0, "start_time"],
        "msg": "Input should be in a valid time format, hour value is outside expected range of 0-23",
        "input": "25:00:00",
        "ctx": {
          "error": "hour value is outside expected range of 0-23"
        }
      }
    ]
  }
}
```

### 2. 資源不存在 (404)

**請求**:

```http
GET /api/v1/schedules/999
```

**錯誤回應**:

```json
{
  "error": {
    "code": "SERVICE_SCHEDULE_NOT_FOUND",
    "message": "時段不存在: ID=999",
    "status_code": 404,
    "timestamp": "2025-08-26T11:16:35Z",
    "details": {}
  }
}
```

### 3. 資源衝突錯誤 (409)

**重疊時段請求**:

```http
POST /api/v1/schedules
```

```json
{
  "schedules": [
    {
      "giver_id": 1,
      "date": "2025-09-20",
      "start_time": "14:00:00",
      "end_time": "15:00:00",
      "status": "AVAILABLE"
    },
    {
      "giver_id": 1,
      "date": "2025-09-20",
      "start_time": "14:30:00",
      "end_time": "15:30:00",
      "status": "AVAILABLE"
    }
  ],
  "created_by": 1,
  "created_by_role": "GIVER"
}
```

**錯誤回應**:

```json
{
  "error": {
    "code": "SERVICE_SCHEDULE_OVERLAP",
    "message": "時段重疊：檢測到 2 個重疊時段",
    "status_code": 409,
    "timestamp": "2025-08-26T10:58:11Z",
    "details": {}
  }
}
```

## 錯誤回應格式說明

### 錯誤回應結構

所有的錯誤回應都遵循以下統一格式：

```json
{
  "error": {
    "code": "錯誤代碼",
    "message": "錯誤訊息",
    "status_code": HTTP狀態碼,
    "timestamp": "錯誤發生時間",
    "details": [
      // 詳細錯誤資訊陣列
    ]
  }
}
```

### 驗證錯誤類型

#### 1. 整數解析錯誤 (int_parsing)

```json
{
  "type": "int_parsing",
  "loc": ["body", "schedules", 0, "giver_id"],
  "msg": "Input should be a valid integer, unable to parse string as an integer",
  "input": "invalid"
}
```

#### 2. 日期解析錯誤 (date_from_datetime_parsing)

```json
{
  "type": "date_from_datetime_parsing",
  "loc": ["body", "schedules", 0, "date"],
  "msg": "Input should be a valid date or datetime, invalid character in year",
  "input": "invalid-date",
  "ctx": {
    "error": "invalid character in year"
  }
}
```

#### 3. 時間解析錯誤 (time_parsing)

```json
{
  "type": "time_parsing",
  "loc": ["body", "schedules", 0, "start_time"],
  "msg": "Input should be in a valid time format, hour value is outside expected range of 0-23",
  "input": "25:00:00",
  "ctx": {
    "error": "hour value is outside expected range of 0-23"
  }
}
```

#### 4. 缺少欄位錯誤 (missing)

```json
{
  "type": "missing",
  "loc": ["body", "schedules", 0, "giver_id"],
  "msg": "Field required",
  "input": {
    // 實際輸入的資料
  }
}
```

#### 5. 字串長度錯誤 (string_too_long)

```json
{
  "type": "string_too_long",
  "loc": ["body", "schedules", 0, "note"],
  "msg": "String should have at most 255 characters",
  "input": "很長的備註...",
  "ctx": {
    "max_length": 255
  }
}
```

### 常見驗證規則

#### 日期格式

- **正確格式**: `YYYY-MM-DD` (例如: `2025-09-20`)
- **錯誤格式**: `invalid-date`, `20/09/2025`, `2025.09.20`

#### 時間格式

- **正確格式**: `HH:MM:SS` (例如: `14:00:00`)
- **錯誤格式**: `25:00:00`, `14:00`, `2:00 PM`

#### 整數格式

- **正確格式**: 數字 (例如: `1`, `123`)
- **錯誤格式**: `"1"`, `"invalid"`, `1.5`

#### 字串長度限制

- **note 欄位**: 最多 255 字元
- **其他字串欄位**: 根據資料庫定義

### 錯誤代碼說明

| 錯誤代碼                       | 說明             | HTTP 狀態碼 |
| ------------------------------ | ---------------- | ----------- |
| `ROUTER_VALIDATION_ERROR`      | 請求資料驗證失敗 | 422         |
| `SERVICE_SCHEDULE_NOT_FOUND`   | 時段不存在       | 404         |
| `SERVICE_USER_NOT_FOUND`       | 使用者不存在     | 404         |
| `CRUD_DATABASE_ERROR`          | 資料庫操作失敗   | 500         |
| `SERVICE_SCHEDULE_OVERLAP`     | 時段重疊         | 409         |
| `SERVICE_BUSINESS_LOGIC_ERROR` | 業務邏輯錯誤     | 400         |

### 錯誤處理架構

本系統採用分層錯誤處理架構：

1. **Service 層**: 拋出自定義 `APIError`
2. **Router 層**: 使用 `@handle_api_errors()` 裝飾器
3. **Middleware 層**: 全域錯誤處理中間件統一格式化

**錯誤處理流程**:

```
Service 層拋出 APIError
    ↓
Router 層裝飾器傳遞錯誤
    ↓
Middleware 層統一格式化
    ↓
返回標準化錯誤回應
```

### 錯誤狀態碼說明

本系統嚴格遵循 HTTP 狀態碼標準：

- **200 OK**: 成功回應
- **201 Created**: 資源建立成功
- **204 No Content**: 刪除成功（無回應內容）
- **400 Bad Request**: 業務邏輯錯誤（如時段重疊）
- **401 Unauthorized**: 認證失敗
- **403 Forbidden**: 權限不足
- **404 Not Found**: 資源不存在（如時段不存在）
- **409 Conflict**: 資源衝突（如重複 email）
- **422 Unprocessable Entity**: 資料驗證失敗
- **500 Internal Server Error**: 內部伺服器錯誤

### 錯誤處理最佳實踐

#### 1. 前端驗證

在發送請求前，先在前端進行基本驗證：

```javascript
// 驗證日期格式
function isValidDate(dateString) {
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date);
}

// 驗證時間格式
function isValidTime(timeString) {
  const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/;
  return timeRegex.test(timeString);
}

// 驗證整數
function isValidInteger(value) {
  return Number.isInteger(Number(value)) && Number(value) > 0;
}
```

#### 2. 錯誤訊息本地化

根據錯誤類型顯示適當的用戶友好訊息：

```javascript
function getErrorMessage(error) {
  const errorMap = {
    int_parsing: "請輸入有效的數字",
    date_from_datetime_parsing: "請輸入正確的日期格式 (YYYY-MM-DD)",
    time_parsing: "請輸入正確的時間格式 (HH:MM:SS)",
    missing: "此欄位為必填",
    string_too_long: "字串長度超出限制",
  };

  return errorMap[error.type] || "資料格式錯誤";
}
```

#### 3. 錯誤日誌記錄

在後端記錄詳細的錯誤資訊：

```python
# 記錄驗證錯誤
logger.warning(f"驗證錯誤: {error_details}")
logger.info(f"用戶輸入: {user_input}")
```

## Postman 測試腳本

### Pre-request Script

```javascript
// 生成明天的日期
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
const dateStr = tomorrow.toISOString().split("T")[0];

// 設定環境變數
pm.environment.set("test_date", dateStr);
pm.environment.set("test_giver_id", "1");
```

### Tests Script

```javascript
// 測試回應狀態碼
pm.test("Status code is 201", function () {
  pm.response.to.have.status(201);
});

// 測試回應時間
pm.test("Response time is less than 2000ms", function () {
  pm.expect(pm.response.responseTime).to.be.below(2000);
});

// 測試回應格式
pm.test("Response has correct structure", function () {
  const jsonData = pm.response.json();
  pm.expect(jsonData).to.be.an("array");
  if (jsonData.length > 0) {
    pm.expect(jsonData[0]).to.have.property("id");
    pm.expect(jsonData[0]).to.have.property("giver_id");
  }
});

// 儲存回應資料供後續使用
if (pm.response.code === 201) {
  const jsonData = pm.response.json();
  if (jsonData && jsonData.length > 0) {
    pm.environment.set("created_schedule_id", jsonData[0].id);
  }
}
```

## 常見問題排解

### 1. JSON 解析錯誤

- 確保 JSON 格式正確
- 檢查是否有多餘的逗號
- 確保所有字串都用雙引號包圍

### 2. 驗證錯誤

- 檢查必填欄位是否都有提供
- 確認資料型別是否正確
- 檢查日期和時間格式

### 3. 業務邏輯錯誤

- 檢查時段是否重疊
- 確認操作者權限
- 驗證時段狀態是否有效
