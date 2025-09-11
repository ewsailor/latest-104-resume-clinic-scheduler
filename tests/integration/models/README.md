# Models 整合測試

本目錄包含 SQLAlchemy 模型的整合測試，測試模型之間的關聯、資料庫操作和模型方法。

## 測試範圍

- **User 模型整合測試** (`test_user_integration.py`)

  - 使用者 CRUD 操作
  - 使用者屬性驗證
  - 使用者關聯查詢

- **Schedule 模型整合測試** (`test_schedule_integration.py`)

  - 時段 CRUD 操作
  - 時段狀態管理
  - 時段關聯查詢

- **模型關聯整合測試** (`test_model_relationships_integration.py`)

  - User-Schedule 關聯
  - 反向關聯查詢
  - 關聯資料完整性

- **資料庫操作整合測試** (`test_database_operations_integration.py`)

  - 事務處理
  - 外鍵約束
  - 索引效能

- **模型方法整合測試** (`test_model_methods_integration.py`)
  - 模型屬性方法
  - 序列化方法
  - 業務邏輯方法

## 執行測試

```bash
# 執行所有 models 整合測試
pytest tests/integration/models/

# 執行特定測試檔案
pytest tests/integration/models/test_user_integration.py

# 執行特定測試方法
pytest tests/integration/models/test_user_integration.py::TestUserIntegration::test_user_crud_operations
```

## 測試資料

測試使用記憶體 SQLite 資料庫，確保測試的獨立性和速度。每個測試都會建立乾淨的資料庫環境。
