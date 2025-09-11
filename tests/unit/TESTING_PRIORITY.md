# 測試優先級指南

## 高優先級（必須測試）✅ 已完成

### 業務邏輯

- [x] `app/crud/schedule.py` - 資料庫操作邏輯
- [x] `app/services/schedule.py` - 業務服務邏輯
- [x] `app/models/schedule.py` - 資料模型
- [x] `app/models/user.py` - 資料模型

### 核心功能

- [x] `app/core/settings.py` - 應用程式配置
- [x] `app/enums/*.py` - 枚舉定義
- [x] `app/decorators/*.py` - 裝飾器功能

### 工具函數

- [x] `app/utils/model_helpers.py` - 模型輔助工具
- [x] `app/utils/timezone.py` - 時區處理工具

### 錯誤處理

- [x] `app/errors/exceptions.py` - 自定義異常
- [x] `app/errors/formatters.py` - 錯誤格式化
- [x] `app/errors/handlers.py` - 錯誤處理器
- [x] `app/errors/error_codes/*.py` - 錯誤代碼常數

## 中優先級（建議測試）✅ 已完成

### API 路由

- [x] `app/routers/api/schedule.py` - API 端點
- [x] `app/routers/health.py` - 健康檢查
- [x] `app/routers/main.py` - 主路由

### 中間件

- [x] `app/middleware/cors.py` - CORS 中間件
- [x] `app/middleware/error_handler.py` - 錯誤處理中間件

### Schema

- [x] `app/schemas/schedule.py` - Pydantic 模型

### 服務層

- [x] `app/services/schedule.py` - 時段服務邏輯

## 低優先級（可選測試）

### 配置和初始化

- [ ] `app/factory.py` - 應用程式工廠
- [ ] `app/main.py` - 應用程式入口點

### 靜態檔案

- [ ] `app/templates/index.html` - HTML 模板（通常不需要測試）

## 測試統計

### 已完成測試

- **總測試數量**: 550+ 個測試
- **通過**: 540+ 個
- **跳過**: 10 個
- **失敗**: 0 個

### 測試覆蓋範圍

- ✅ **CRUD 層**: 完整覆蓋
- ✅ **核心功能**: 完整覆蓋
- ✅ **工具函數**: 完整覆蓋
- ✅ **錯誤處理**: 完整覆蓋
- ✅ **裝飾器**: 完整覆蓋
- ✅ **枚舉**: 完整覆蓋
- ✅ **中間件**: 完整覆蓋（CORS + 錯誤處理）
- ✅ **資料模型**: 完整覆蓋（Schedule + User + Database）
- ✅ **API 路由**: 完整覆蓋（Main + Health + Schedule API）
- ✅ **Schema**: 完整覆蓋（Schedule）
- ✅ **服務層**: 完整覆蓋（Schedule Service）
- ✅ **工具函數**: 完整覆蓋（Model Helpers + Timezone）

## 測試建議

### 1. 優先測試業務邏輯

- CRUD 操作
- 業務服務
- 資料模型

### 2. 測試核心功能

- 配置管理
- 枚舉定義
- 裝飾器

### 3. 測試工具函數

- 工具函數
- 輔助函數

### 4. 可選測試

- API 路由（通常用整合測試）
- 中間件（通常用整合測試）
- Schema（通常用整合測試）

## 測試覆蓋率目標

- **高優先級檔案**: 90%+ 覆蓋率 ✅ 已達成
- **中優先級檔案**: 70%+ 覆蓋率 ✅ 已達成
- **低優先級檔案**: 50%+ 覆蓋率（可選）

## 測試類型建議

### 單元測試 (Unit Tests) ✅ 已完成

- 業務邏輯
- 工具函數
- 核心功能
- 錯誤處理

### 整合測試 (Integration Tests) ⚠️ 待完成

- API 路由
- 中間件
- 資料庫操作

### 端到端測試 (E2E Tests) ⚠️ 待完成

- 完整用戶流程
- API 端點整合
