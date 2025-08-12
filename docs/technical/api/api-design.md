# API 設計原則

## 概述

本專案遵循 RESTful API 設計原則，提供一致、可預測的 API 介面。

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

## API 端點設計

### 1. 使用者管理

```bash
# 使用者端點
GET    /api/users              # 取得使用者列表
POST   /api/users              # 建立使用者
GET    /api/users/{id}         # 取得特定使用者
PUT    /api/users/{id}         # 更新使用者
DELETE /api/users/{id}         # 刪除使用者
```

### 2. 排程管理

```bash
# 排程端點
GET    /api/schedules                    # 取得排程列表
POST   /api/schedules                    # 建立排程
GET    /api/schedules/{id}               # 取得特定排程
PUT    /api/schedules/{id}               # 更新排程
DELETE /api/schedules/{id}               # 刪除排程
GET    /api/schedules/giver/{giver_id}   # 取得諮詢師排程
GET    /api/schedules/taker/{taker_id}   # 取得求職者排程
```

### 3. 諮詢師管理

```bash
# 諮詢師端點
GET    /api/givers              # 取得諮詢師列表
POST   /api/givers              # 建立諮詢師
GET    /api/givers/{id}         # 取得特定諮詢師
PUT    /api/givers/{id}         # 更新諮詢師
DELETE /api/givers/{id}         # 刪除諮詢師
```

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
