# 測試管理指南

## 📁 測試目錄結構

```
tests/
├── unit/                      # 單元測試
│   ├── models/                # 資料模型測試
│   │   ├── test_user.py       # 使用者模型測試
│   │   ├── test_schedule.py   # 排程模型測試
│   │   └── test_database.py   # 資料庫模型測試
│   ├── crud/                  # CRUD 操作測試
│   │   ├── test_crud_user.py  # 使用者 CRUD 測試
│   │   └── test_crud_schedule.py # 排程 CRUD 測試
│   ├── utils/                 # 工具函數測試
│   │   ├── test_model_helpers.py # 模型輔助工具測試
│   │   ├── test_timezone.py   # 時區工具測試
│   │   └── test_config.py     # 配置測試
│   └── middleware/            # 中間件測試
│       └── test_cors.py       # CORS 中間件測試
├── integration/               # 整合測試
│   ├── api/                   # API 端點測試
│   │   ├── test_users_api.py  # 使用者 API 測試
│   │   ├── test_givers_api.py # 諮詢師 API 測試
│   │   ├── test_schedule_api.py # 排程 API 測試
│   │   ├── test_health.py     # 健康檢查 API 測試
│   │   └── test_main.py       # 主要路由測試
│   └── database/              # 資料庫整合測試
│       └── test_database_integration.py
├── e2e/                       # 端到端測試
│   ├── test_user_workflow.py  # 使用者工作流程測試
│   └── test_schedule_workflow.py # 排程工作流程測試
├── fixtures/                  # 測試資料和 Fixtures
│   ├── test_data.py           # 測試資料
│   ├── factories.py           # 工廠函數
│   └── mocks.py               # Mock 物件
├── conftest.py                # Pytest 配置
├── constants.py               # 測試常數
└── README.md                  # 本文件
```

## 🏷️ 命名規範

### 1. 檔案命名規則

```
test_[類型]_[功能]_[範圍].py
```

**範例：**

- `test_unit_user_model.py` - 單元測試：使用者模型
- `test_integration_schedule_api.py` - 整合測試：排程 API
- `test_e2e_user_registration.py` - 端到端測試：使用者註冊

### 2. 測試函數命名規則

```
test_[功能]_[條件]_[預期結果]
```

**範例：**

- `test_create_user_with_valid_data_returns_success()`
- `test_create_user_with_duplicate_email_returns_error()`
- `test_get_schedules_by_giver_id_returns_filtered_results()`

### 3. 測試類別命名規則

```
Test[功能][範圍]
```

**範例：**

- `TestUserModel` - 使用者模型測試類別
- `TestScheduleAPI` - 排程 API 測試類別
- `TestDatabaseIntegration` - 資料庫整合測試類別

## 🧪 測試類型說明

### 單元測試 (Unit Tests)

- **目的**: 測試個別函數、類別或模組的功能
- **範圍**: 隔離的程式碼單元
- **執行速度**: 快速
- **依賴**: 最小化外部依賴

### 整合測試 (Integration Tests)

- **目的**: 測試多個組件之間的互動
- **範圍**: API 端點、資料庫操作
- **執行速度**: 中等
- **依賴**: 可能依賴資料庫或其他服務

### 端到端測試 (E2E Tests)

- **目的**: 測試完整的用戶工作流程
- **範圍**: 從用戶操作到系統回應的完整流程
- **執行速度**: 較慢
- **依賴**: 完整的系統環境

## 🔧 執行測試

### 執行所有測試

```bash
pytest
```

### 執行特定類型的測試

```bash
# 單元測試
pytest tests/unit/

# 整合測試
pytest tests/integration/

# 端到端測試
pytest tests/e2e/
```

### 執行特定模組的測試

```bash
# 使用者相關測試
pytest tests/unit/models/test_user.py
pytest tests/integration/api/test_users_api.py

# 排程相關測試
pytest tests/unit/crud/test_crud_schedule.py
pytest tests/integration/api/test_schedule_api.py
```

### 執行測試並生成覆蓋率報告

```bash
pytest --cov=app --cov-report=html
```

## 📋 測試最佳實踐

### 1. 測試結構

```python
def test_function_name():
    """測試描述"""
    # Arrange (準備)
    input_data = "test_data"

    # Act (執行)
    result = function_to_test(input_data)

    # Assert (驗證)
    assert result == expected_output
```

### 2. 使用 Fixtures

```python
@pytest.fixture
def sample_user():
    """提供測試用的使用者資料"""
    return User(
        name="測試使用者",
        email="test@example.com"
    )

def test_create_user(sample_user):
    """測試建立使用者"""
    # 使用 fixture 提供的資料
    assert sample_user.name == "測試使用者"
```

### 3. 使用 Mock

```python
def test_external_api_call(mocker):
    """測試外部 API 呼叫"""
    # Mock 外部 API
    mock_api = mocker.patch('app.utils.external_api.call')
    mock_api.return_value = {"status": "success"}

    # 執行測試
    result = function_that_calls_api()

    # 驗證結果
    assert result["status"] == "success"
    mock_api.assert_called_once()
```

### 4. 資料庫測試

```python
def test_create_schedule(db_session):
    """測試建立排程"""
    # 準備測試資料
    schedule_data = ScheduleData(
        giver_id=1,
        schedule_date=date(2024, 1, 1),
        start_time=time(9, 0),
        end_time=time(10, 0)
    )

    # 執行測試
    schedule = schedule_crud.create_schedule(db_session, schedule_data)

    # 驗證結果
    assert schedule.giver_id == 1
    assert schedule.schedule_date == date(2024, 1, 1)
```

## 🎯 測試覆蓋率目標

- **單元測試**: 90% 以上
- **整合測試**: 80% 以上
- **端到端測試**: 關鍵流程 100%

## 📝 維護指南

### 新增測試

1. 根據測試類型選擇適當的目錄
2. 使用一致的命名規範
3. 撰寫清晰的測試描述
4. 確保測試的可重複性

### 更新測試

1. 當功能變更時，同步更新相關測試
2. 保持測試資料的一致性
3. 定期清理過時的測試

### 測試資料管理

1. 使用 fixtures 提供測試資料
2. 避免硬編碼測試資料
3. 確保測試資料的隔離性
