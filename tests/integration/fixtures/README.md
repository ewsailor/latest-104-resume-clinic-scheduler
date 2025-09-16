# 整合測試 Fixtures

本目錄包含整合測試專用的 fixtures 和測試資料。

## 目錄結構

```
tests/integration/fixtures/
├── __init__.py          # 模組初始化
├── database.py          # 資料庫相關 fixtures
├── services.py          # 服務層相關 fixtures
├── api.py              # API 相關 fixtures
├── test_data.py        # 測試資料相關 fixtures
└── README.md           # 本文件
```

## Fixtures 說明

### 資料庫 Fixtures (`database.py`)

#### `integration_db_engine`

- **用途**: 提供整合測試用的資料庫引擎
- **範圍**: `class` - 在整個測試類別中共享
- **特點**:
  - 使用記憶體 SQLite 資料庫
  - 自動建立和清理資料表
  - 測試結束後自動清理

#### `integration_db_session`

- **用途**: 提供整合測試用的資料庫會話
- **類型**: `Session`
- **特點**:
  - 基於 `integration_db_engine`
  - 測試結束後自動關閉會話
  - 適用於一般整合測試

#### `integration_db_session_with_rollback`

- **用途**: 提供會自動回滾的資料庫會話
- **類型**: `Session`
- **特點**:
  - 測試結束後自動回滾事務
  - 確保測試資料不會影響其他測試
  - 適用於測試事務回滾場景

### 服務層 Fixtures (`services.py`)

#### `schedule_service`

- **用途**: 提供 ScheduleService 實例
- **類型**: `ScheduleService`
- **特點**: 基本的服務實例，適用於服務層整合測試

#### `schedule_service_with_session`

- **用途**: 提供帶有資料庫會話的 ScheduleService 實例
- **類型**: `ScheduleService`
- **特點**: 包含資料庫會話的服務實例

### API Fixtures (`api.py`)

#### `integration_app`

- **用途**: 提供整合測試用的 FastAPI 應用程式
- **類型**: `FastAPI`
- **特點**: 完整的應用程式實例，包含所有路由和中間件

#### `integration_client`

- **用途**: 提供整合測試用的 API 客戶端
- **類型**: `TestClient`
- **特點**: 基於 `integration_app` 的測試客戶端

#### `integration_client_with_cleanup`

- **用途**: 提供帶有自動清理功能的 API 客戶端
- **類型**: `TestClient`
- **特點**: 測試結束後自動清理測試資料

### 測試資料 Fixtures (`test_data.py`)

#### `sample_users_data`

- **用途**: 提供範例使用者資料
- **類型**: `List[Dict[str, Any]]`
- **內容**: 包含 Giver、Taker、Admin 三種角色的使用者資料

#### `sample_schedule_data`

- **用途**: 提供單一範例時段資料
- **類型**: `Dict[str, Any]`
- **內容**: 基本的時段資料結構

#### `sample_schedules_data`

- **用途**: 提供多個範例時段資料
- **類型**: `List[Dict[str, Any]]`
- **內容**: 多個時段的測試資料

#### `sample_users`

- **用途**: 建立並儲存範例使用者到資料庫
- **類型**: `Dict[str, User]`
- **特點**: 實際的 User 物件，已儲存到資料庫

#### `sample_schedules`

- **用途**: 建立並儲存範例時段到資料庫
- **類型**: `List[Schedule]`
- **特點**: 實際的 Schedule 物件，已儲存到資料庫

#### `overlapping_schedule_data`

- **用途**: 提供重疊時段的測試資料
- **類型**: `Dict[str, Any]`
- **用途**: 測試時段重疊檢查功能

#### `booked_schedule_data`

- **用途**: 提供已預約時段的測試資料
- **類型**: `Dict[str, Any]`
- **用途**: 測試已預約時段的相關功能

## 使用範例

### 服務層整合測試

```python
class TestScheduleServiceIntegration:
    def test_create_schedule(
        self,
        integration_db_session,
        schedule_service,
        sample_users,
        sample_schedule_data
    ):
        """測試建立時段功能。"""
        # 使用 fixtures 進行測試
        result = schedule_service.create_schedule(
            integration_db_session,
            sample_schedule_data
        )
        assert result.id is not None
```

### API 整合測試

```python
class TestScheduleAPIIntegration:
    def test_create_schedule_api(
        self,
        integration_client,
        sample_schedule_data
    ):
        """測試建立時段 API。"""
        response = integration_client.post(
            "/api/schedules/",
            json=sample_schedule_data
        )
        assert response.status_code == 201
```

## 與單元測試 Fixtures 的差異

| 特性       | 單元測試 Fixtures  | 整合測試 Fixtures  |
| ---------- | ------------------ | ------------------ |
| **資料庫** | 簡單的記憶體資料庫 | 完整的資料庫環境   |
| **範圍**   | 通常為 `function`  | 通常為 `class`     |
| **複雜度** | 簡單、快速         | 複雜、完整         |
| **隔離性** | 高度隔離           | 適度隔離           |
| **真實性** | Mock 和模擬        | 真實的服務和資料庫 |

## 最佳實踐

1. **按功能分類**: 將相關的 fixtures 放在對應的文件中
2. **適當的範圍**: 根據測試需求選擇合適的 fixture 範圍
3. **資源清理**: 確保 fixtures 正確清理資源
4. **資料隔離**: 使用不同的 fixture 來避免測試間的資料污染
5. **文檔完整**: 為每個 fixture 提供詳細的說明和使用範例
