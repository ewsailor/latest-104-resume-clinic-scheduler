# 測試常數使用指南

## 概述

本專案使用集中化的測試常數管理，確保測試的一致性和可維護性。所有測試常數都定義在 `tests/constants.py` 中。

## 常數模組結構

### 新式物件結構（推薦）

使用類別結構組織常數，類似 JavaScript 的物件配置：

```python
# 健康檢查相關常數
class EXPECTED:
    class STATUS:
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"

    class UPTIME:
        RUNNING = "running"

    class DATABASE:
        CONNECTED = "connected"
        DISCONNECTED = "disconnected"
        HEALTHY = "healthy"

    class MESSAGE:
        READY = "Application and database are ready to serve traffic."
        NOT_READY = "Database connection failed. Application is not ready."
        ERROR = "Application health check failed"

# HTTP 狀態碼常數
class HTTP:
    OK = 200
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

# 測試資料常數
class TEST:
    APP_NAME = "104 Resume Clinic Scheduler"
    VERSION = "0.1.0"
    TIMESTAMP = 1717334400

    class CONFIG:
        TIMEOUT = 30
        RETRY_COUNT = 3

# 錯誤訊息常數
class SIMULATED:
    VERSION_CHECK_ERROR = "Simulated version check error"
    DATABASE_CONNECTION_ERROR = "Database connection failed"
```

### 傳統扁平結構（向後相容）

為了保持向後相容性，仍然提供傳統的扁平常數：

```python
# 健康檢查相關常數
EXPECTED_STATUS_HEALTHY = "healthy"
EXPECTED_STATUS_UNHEALTHY = "unhealthy"
EXPECTED_UPTIME_RUNNING = "running"
EXPECTED_DATABASE_CONNECTED = "connected"
EXPECTED_DATABASE_DISCONNECTED = "disconnected"
EXPECTED_DATABASE_HEALTHY = "healthy"
EXPECTED_MESSAGE_READY = "Application and database are ready to serve traffic."
EXPECTED_MESSAGE_NOT_READY = "Database connection failed. Application is not ready."
EXPECTED_ERROR_MESSAGE = "Application health check failed"

# HTTP 狀態碼常數
HTTP_200_OK = 200
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_503_SERVICE_UNAVAILABLE = 503

# 測試資料常數
TEST_APP_NAME = "104 Resume Clinic Scheduler"
TEST_VERSION = "0.1.0"
TEST_TIMESTAMP = 1717334400

# 錯誤訊息常數
SIMULATED_VERSION_CHECK_ERROR = "Simulated version check error"
SIMULATED_DATABASE_CONNECTION_ERROR = "Database connection failed"
```

## 使用方式

### 1. 導入常數（新式物件結構 - 推薦）

```python
# 導入整個常數類別
from tests.constants import EXPECTED, HTTP, TEST, SIMULATED

# 或者導入特定類別
from tests.constants import EXPECTED, HTTP
```

### 2. 在測試中使用（新式物件結構）

```python
def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/healthz")

    # 使用物件結構常數
    assert response.status_code == HTTP.OK
    assert response.json()["status"] == EXPECTED.STATUS.HEALTHY
    assert response.json()["uptime"] == EXPECTED.UPTIME.RUNNING
```

### 3. 模擬錯誤時使用（新式物件結構）

```python
def test_health_check_failure(mocker):
    """測試健康檢查失敗"""
    mocker.patch(
        "app.core.get_project_version",
        side_effect=Exception(SIMULATED.VERSION_CHECK_ERROR)
    )

    response = client.get("/healthz")
    assert response.status_code == HTTP.INTERNAL_SERVER_ERROR
    assert response.json()["detail"]["status"] == EXPECTED.STATUS.UNHEALTHY
```

### 4. 導入常數（傳統方式 - 向後相容）

```python
from tests.constants import (
    EXPECTED_STATUS_HEALTHY,
    HTTP_200_OK,
    SIMULATED_VERSION_CHECK_ERROR
)
```

### 5. 在測試中使用（傳統方式）

```python
def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/healthz")

    # 使用傳統常數
    assert response.status_code == HTTP_200_OK
    assert response.json()["status"] == EXPECTED_STATUS_HEALTHY
```

## 最佳實踐

### 1. 使用新式物件結構（推薦）

✅ **推薦**：

```python
from tests.constants import EXPECTED, HTTP

def test_example():
    response = client.get("/healthz")
    assert response.status_code == HTTP.OK
    assert response.json()["status"] == EXPECTED.STATUS.HEALTHY
    assert response.json()["uptime"] == EXPECTED.UPTIME.RUNNING
```

### 2. 避免硬編碼值

❌ **不推薦**：

```python
def test_example():
    response = client.get("/healthz")
    assert response.status_code == 200  # 硬編碼
    assert response.json()["status"] == "healthy"  # 硬編碼
```

✅ **推薦**：

```python
from tests.constants import HTTP, EXPECTED

def test_example():
    response = client.get("/healthz")
    assert response.status_code == HTTP.OK
    assert response.json()["status"] == EXPECTED.STATUS.HEALTHY
```

### 3. 使用描述性常數名稱

```python
# 好的命名（新式物件結構）
EXPECTED.STATUS.HEALTHY = "healthy"
HTTP.INTERNAL_SERVER_ERROR = 500

# 好的命名（傳統方式）
EXPECTED_STATUS_HEALTHY = "healthy"
HTTP_500_INTERNAL_SERVER_ERROR = 500

# 避免的命名
STATUS_OK = "healthy"
CODE_500 = 500
```

### 4. 按功能分組常數

```python
# 新式物件結構（自動分組）
class EXPECTED:
    class STATUS:
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"

    class DATABASE:
        CONNECTED = "connected"
        DISCONNECTED = "disconnected"

# 傳統方式（手動分組）
# 健康檢查相關
EXPECTED_STATUS_HEALTHY = "healthy"
EXPECTED_STATUS_UNHEALTHY = "unhealthy"

# HTTP 狀態碼
HTTP_200_OK = 200
HTTP_500_INTERNAL_SERVER_ERROR = 500
```

## 添加新常數

當需要添加新的測試常數時：

1. **在 `tests/constants.py` 中添加**：

   ```python
   # 新功能相關常數
   NEW_FEATURE_STATUS_ACTIVE = "active"
   NEW_FEATURE_STATUS_INACTIVE = "inactive"
   ```

2. **在測試檔案中導入**：

   ```python
   from tests.constants import (
       NEW_FEATURE_STATUS_ACTIVE,
       NEW_FEATURE_STATUS_INACTIVE
   )
   ```

3. **在測試中使用**：
   ```python
   def test_new_feature():
       response = client.get("/new-feature")
       assert response.json()["status"] == NEW_FEATURE_STATUS_ACTIVE
   ```

## 常數命名規範

### 1. 預期值常數

- 使用 `EXPECTED_` 前綴
- 例如：`EXPECTED_STATUS_HEALTHY`

### 2. HTTP 狀態碼常數

- 使用 `HTTP_` 前綴
- 例如：`HTTP_200_OK`

### 3. 測試資料常數

- 使用 `TEST_` 前綴
- 例如：`TEST_APP_NAME`

### 4. 錯誤訊息常數

- 使用 `SIMULATED_` 前綴（用於模擬錯誤）
- 例如：`SIMULATED_VERSION_CHECK_ERROR`

## 維護注意事項

1. **保持常數值的一致性**：確保所有測試使用相同的常數值
2. **定期檢查未使用的常數**：移除不再使用的常數
3. **更新文檔**：當添加新常數時，更新相關文檔
4. **版本控制**：常數的變更應該在 commit 訊息中說明

## 相關文件

- [測試架構指南](../README.md#測試)
- [Python-Multipart 遷移記錄](python_multipart_migration.md)
