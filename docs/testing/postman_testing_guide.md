# Postman 測試指南

## 概述

本指南將幫助您使用 Postman 測試 104 履歷診療室排程系統的 API 端點。

## 前置準備

### 1. 啟動應用程式

```bash
# 在專案根目錄執行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 確認服務運行

- 訪問 `http://localhost:8000/docs` 查看 Swagger UI
- 訪問 `http://localhost:8000/health` 檢查健康狀態

## API 端點總覽

### 基礎 URL

```
http://localhost:8000
```

### 主要端點分類

1. **健康檢查端點**

   - `GET /health` - 健康狀態檢查

2. **時段管理 API** (`/api/v1/schedules`)

   - `POST /api/v1/schedules` - 建立時段
   - `GET /api/v1/schedules` - 取得時段列表
   - `GET /api/v1/schedules/{id}` - 取得特定時段
   - `PATCH /api/v1/schedules/{id}` - 更新時段
   - `DELETE /api/v1/schedules/{id}` - 刪除時段

3. **Giver 管理 API** (`/api/v1/givers`)

   - `GET /api/v1/givers` - 取得 Giver 列表
   - `GET /api/v1/givers/{id}` - 取得特定 Giver
   - `GET /api/v1/givers/topics/{topic}` - 根據服務項目篩選
   - `GET /api/v1/givers/industries/{industry}` - 根據產業篩選
   - `GET /api/v1/givers/stats/count` - 取得 Giver 統計

4. **使用者管理 API** (`/api/v1/users`)
   - `GET /api/v1/users` - 取得使用者列表
   - `GET /api/v1/users/{id}` - 取得特定使用者
   - `POST /api/v1/users` - 建立使用者
   - `PUT /api/v1/users/{id}` - 更新使用者
   - `DELETE /api/v1/users/{id}` - 刪除使用者

## Postman 集合設定

### 1. 建立環境變數

在 Postman 中建立環境，設定以下變數：

| 變數名稱      | 初始值                  | 當前值                  |
| ------------- | ----------------------- | ----------------------- |
| `base_url`    | `http://localhost:8000` | `http://localhost:8000` |
| `api_version` | `v1`                    | `v1`                    |

### 2. 建立集合

建立名為 "104 Resume Clinic API" 的集合，並按以下結構組織：

```
104 Resume Clinic API/
├── Health Check/
│   └── Health Status
├── Schedules/
│   ├── Create Schedule
│   ├── Get All Schedules
│   ├── Get Schedule by ID
│   ├── Update Schedule
│   └── Delete Schedule
├── Givers/
│   ├── Get All Givers
│   ├── Get Giver by ID
│   ├── Get Givers by Topic
│   ├── Get Givers by Industry
│   └── Get Giver Stats
└── Users/
    ├── Get All Users
    ├── Get User by ID
    ├── Create User
    ├── Update User
    └── Delete User
```

## 詳細測試案例

### 1. 健康檢查

**請求名稱**: Health Status  
**方法**: GET  
**URL**: `{{base_url}}/health`

**預期回應**:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0"
}
```

### 2. 時段管理 API

#### 2.1 建立時段

**請求名稱**: Create Schedule  
**方法**: POST  
**URL**: `{{base_url}}/api/v1/schedules`  
**Headers**:

```
Content-Type: application/json
```

**Body** (raw JSON):

```json
{
  "schedules": [
    {
      "giver_id": 1,
      "date": "2024-01-20",
      "start_time": "09:00:00",
      "end_time": "10:00:00",
      "status": "AVAILABLE"
    }
  ],
  "operator_user_id": 1,
  "operator_role": "GIVER"
}
```

**預期回應** (201 Created):

```json
[
  {
    "id": 1,
    "giver_id": 1,
    "date": "2024-01-20",
    "start_time": "09:00:00",
    "end_time": "10:00:00",
    "status": "AVAILABLE",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### 2.2 取得時段列表

**請求名稱**: Get All Schedules  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/schedules`

**查詢參數** (可選):

- `giver_id`: 篩選特定 Giver 的時段
- `status_filter`: 篩選特定狀態的時段
- `page`: 頁碼 (預設: 1)
- `size`: 每頁數量 (預設: 10)

**範例 URL**: `{{base_url}}/api/v1/schedules?giver_id=1&status_filter=AVAILABLE&page=1&size=5`

#### 2.3 取得特定時段

**請求名稱**: Get Schedule by ID  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/schedules/1`

#### 2.4 更新時段

**請求名稱**: Update Schedule  
**方法**: PATCH  
**URL**: `{{base_url}}/api/v1/schedules/1`  
**Headers**:

```
Content-Type: application/json
```

**Body** (raw JSON):

```json
{
  "schedule_data": {
    "giver_id": 1,
    "date": "2024-01-21",
    "start_time": "10:00:00",
    "end_time": "11:00:00",
    "status": "BOOKED"
  },
  "operator_user_id": 1,
  "operator_role": "GIVER"
}
```

#### 2.5 刪除時段

**請求名稱**: Delete Schedule  
**方法**: DELETE  
**URL**: `{{base_url}}/api/v1/schedules/1`  
**Headers**:

```
Content-Type: application/json
```

**Body** (raw JSON):

```json
{
  "operator_user_id": 1,
  "operator_role": "GIVER"
}
```

### 3. Giver 管理 API

#### 3.1 取得 Giver 列表

**請求名稱**: Get All Givers  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/givers`

**查詢參數** (可選):

- `topic`: 根據服務項目篩選
- `industry`: 根據產業篩選
- `page`: 頁碼
- `size`: 每頁數量

#### 3.2 取得特定 Giver

**請求名稱**: Get Giver by ID  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/givers/1`

#### 3.3 根據服務項目篩選

**請求名稱**: Get Givers by Topic  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/givers/topics/履歷健診`

#### 3.4 根據產業篩選

**請求名稱**: Get Givers by Industry  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/givers/industries/電子資訊／軟體／半導體相關業`

#### 3.5 取得 Giver 統計

**請求名稱**: Get Giver Stats  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/givers/stats/count`

### 4. 使用者管理 API

#### 4.1 取得使用者列表

**請求名稱**: Get All Users  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/users`

#### 4.2 取得特定使用者

**請求名稱**: Get User by ID  
**方法**: GET  
**URL**: `{{base_url}}/api/v1/users/1`

#### 4.3 建立使用者

**請求名稱**: Create User  
**方法**: POST  
**URL**: `{{base_url}}/api/v1/users`  
**Headers**:

```
Content-Type: application/json
```

**Body** (raw JSON):

```json
{
  "name": "測試使用者",
  "email": "test@example.com",
  "phone": "0912345678",
  "role": "TAKER"
}
```

#### 4.4 更新使用者

**請求名稱**: Update User  
**方法**: PUT  
**URL**: `{{base_url}}/api/v1/users/1`  
**Headers**:

```
Content-Type: application/json
```

**Body** (raw JSON):

```json
{
  "name": "更新後的使用者名稱",
  "email": "updated@example.com",
  "phone": "0987654321",
  "role": "TAKER"
}
```

#### 4.5 刪除使用者

**請求名稱**: Delete User  
**方法**: DELETE  
**URL**: `{{base_url}}/api/v1/users/1`

## 錯誤處理測試

### 1. 驗證錯誤 (422)

**測試案例**: 建立時段時使用無效資料

```json
{
  "schedules": [
    {
      "giver_id": "invalid", // 應該是整數
      "date": "invalid-date", // 無效日期格式
      "start_time": "25:00:00", // 無效時間
      "end_time": "10:00:00",
      "status": "INVALID_STATUS" // 無效狀態
    }
  ],
  "operator_user_id": 1,
  "operator_role": "GIVER"
}
```

### 2. 資源不存在錯誤 (404)

**測試案例**: 取得不存在的時段

```
GET {{base_url}}/api/v1/schedules/999
```

### 3. 業務邏輯錯誤 (400)

**測試案例**: 建立重疊的時段

```json
{
  "schedules": [
    {
      "giver_id": 1,
      "date": "2024-01-20",
      "start_time": "09:00:00",
      "end_time": "10:00:00",
      "status": "AVAILABLE"
    },
    {
      "giver_id": 1,
      "date": "2024-01-20",
      "start_time": "09:30:00", // 與第一個時段重疊
      "end_time": "10:30:00",
      "status": "AVAILABLE"
    }
  ],
  "operator_user_id": 1,
  "operator_role": "GIVER"
}
```

## 測試腳本和自動化

### 1. Pre-request Scripts

在建立時段前，可以添加以下腳本來生成動態資料：

```javascript
// 生成明天的日期
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
const dateStr = tomorrow.toISOString().split("T")[0];

// 設定環境變數
pm.environment.set("test_date", dateStr);
pm.environment.set("test_giver_id", "1");
```

### 2. Tests Scripts

在每個請求後添加測試腳本：

```javascript
// 測試回應狀態碼
pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});

// 測試回應時間
pm.test("Response time is less than 2000ms", function () {
  pm.expect(pm.response.responseTime).to.be.below(2000);
});

// 測試回應格式
pm.test("Response has correct structure", function () {
  const jsonData = pm.response.json();
  pm.expect(jsonData).to.have.property("id");
  pm.expect(jsonData).to.have.property("giver_id");
});

// 儲存回應資料供後續使用
if (pm.response.code === 201) {
  const jsonData = pm.response.json();
  if (jsonData && jsonData.length > 0) {
    pm.environment.set("created_schedule_id", jsonData[0].id);
  }
}
```

### 3. 集合變數

設定集合層級的變數：

| 變數名稱           | 初始值 |
| ------------------ | ------ |
| `test_giver_id`    | `1`    |
| `test_user_id`     | `1`    |
| `test_schedule_id` | `1`    |

## 效能測試

### 1. 負載測試

使用 Postman Runner 進行負載測試：

1. 選擇集合
2. 設定迭代次數 (例如: 100)
3. 設定延遲 (例如: 100ms)
4. 執行測試

### 2. 監控指標

- 回應時間
- 成功率
- 錯誤率
- 吞吐量

## 常見問題排解

### 1. 連線問題

**問題**: 無法連接到 localhost:8000
**解決方案**:

- 確認應用程式是否正在運行
- 檢查防火牆設定
- 確認端口是否被佔用

### 2. CORS 錯誤

**問題**: 瀏覽器中出現 CORS 錯誤
**解決方案**:

- 確認 CORS 設定正確
- 使用 Postman 而非瀏覽器進行測試

### 3. 驗證錯誤

**問題**: 收到 422 驗證錯誤
**解決方案**:

- 檢查請求體格式
- 確認必填欄位都有提供
- 檢查資料型別是否正確

### 4. 資料庫錯誤

**問題**: 收到 500 內部錯誤
**解決方案**:

- 檢查資料庫連線
- 查看應用程式日誌
- 確認資料庫表結構

## 匯入 Postman 集合

您可以匯入以下 JSON 檔案到 Postman：

```json
{
  "info": {
    "name": "104 Resume Clinic API",
    "description": "104 履歷診療室排程系統 API 測試集合",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "item": [
        {
          "name": "Health Status",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/health",
              "host": ["{{base_url}}"],
              "path": ["health"]
            }
          }
        }
      ]
    }
  ]
}
```

## 總結

使用 Postman 測試您的 API 可以幫助您：

1. **驗證功能**: 確保所有端點按預期工作
2. **測試錯誤處理**: 確認錯誤回應格式正確
3. **效能測試**: 評估 API 的響應時間和穩定性
4. **文檔化**: 為團隊提供 API 使用範例
5. **自動化**: 建立可重複的測試流程

建議定期執行這些測試，特別是在部署新功能或修復錯誤後。
