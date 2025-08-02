# 測試常數重構記錄

## 重構背景

根據用戶建議，將測試常數從傳統的扁平結構重構為物件結構，類似 JavaScript 的配置模式：

```javascript
const CONFIG = {
  INSTANCES: {
    GIVER_MODAL: null,
  },
};
```

## 重構前後對比

### 重構前（傳統扁平結構）

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
```

### 重構後（新式物件結構）

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
```

## 重構優勢

### 1. 更好的命名空間管理

```python
# 重構前
EXPECTED_STATUS_HEALTHY
EXPECTED_STATUS_UNHEALTHY
EXPECTED_DATABASE_CONNECTED

# 重構後
EXPECTED.STATUS.HEALTHY
EXPECTED.STATUS.UNHEALTHY
EXPECTED.DATABASE.CONNECTED
```

### 2. 更清晰的層次結構

```python
# 自動分組，無需手動管理
class EXPECTED:
    class STATUS:      # 狀態相關
    class UPTIME:      # 運行時間相關
    class DATABASE:    # 資料庫相關
    class MESSAGE:     # 訊息相關
```

### 3. 更簡潔的使用方式

```python
# 重構前
from tests.constants import (
    EXPECTED_STATUS_HEALTHY,
    EXPECTED_STATUS_UNHEALTHY,
    EXPECTED_UPTIME_RUNNING,
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR
)

# 重構後
from tests.constants import EXPECTED, HTTP
```

### 4. 更好的 IDE 支援

```python
# IDE 可以提供更好的自動完成
EXPECTED.STATUS.  # IDE 會顯示 HEALTHY, UNHEALTHY
EXPECTED.DATABASE.  # IDE 會顯示 CONNECTED, DISCONNECTED, HEALTHY
```

## 向後相容性

為了確保現有代碼不受影響，保留了傳統常數的別名：

```python
# 向後相容性別名
EXPECTED_STATUS_HEALTHY = EXPECTED.STATUS.HEALTHY
EXPECTED_STATUS_UNHEALTHY = EXPECTED.STATUS.UNHEALTHY
HTTP_200_OK = HTTP.OK
HTTP_500_INTERNAL_SERVER_ERROR = HTTP.INTERNAL_SERVER_ERROR
```

## 使用方式對比

### 新式物件結構（推薦）

```python
from tests.constants import EXPECTED, HTTP, TEST, SIMULATED

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == HTTP.OK
    assert response.json()["status"] == EXPECTED.STATUS.HEALTHY
    assert response.json()["uptime"] == EXPECTED.UPTIME.RUNNING
```

### 傳統方式（向後相容）

```python
from tests.constants import (
    EXPECTED_STATUS_HEALTHY,
    HTTP_200_OK
)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == HTTP_200_OK
    assert response.json()["status"] == EXPECTED_STATUS_HEALTHY
```

## 測試結果

### 新式物件結構測試

```bash
$ python scripts/run_tests.py tests/test_health_new_style.py -v
tests/test_health_new_style.py::test_liveness_probe_success_new_style PASSED
tests/test_health_new_style.py::test_liveness_probe_failure_new_style PASSED
tests/test_health_new_style.py::test_readiness_probe_success_new_style PASSED
tests/test_health_new_style.py::test_readiness_probe_failure_new_style PASSED
tests/test_health_new_style.py::test_constants_structure PASSED
```

### 傳統方式測試（向後相容）

```bash
$ python scripts/run_tests.py tests/test_health.py -v
tests/test_health.py::test_liveness_probe_success PASSED
tests/test_health.py::test_liveness_probe_failure PASSED
tests/test_health.py::test_readiness_probe_success PASSED
tests/test_health.py::test_readiness_probe_failure PASSED
```

## 遷移指南

### 1. 立即遷移（推薦）

```python
# 舊代碼
from tests.constants import EXPECTED_STATUS_HEALTHY, HTTP_200_OK

# 新代碼
from tests.constants import EXPECTED, HTTP
```

### 2. 漸進式遷移

可以混合使用兩種方式，逐步遷移：

```python
from tests.constants import EXPECTED, HTTP, EXPECTED_STATUS_HEALTHY

def test_example():
    # 新式用法
    assert response.status_code == HTTP.OK

    # 舊式用法（仍然可用）
    assert response.json()["status"] == EXPECTED_STATUS_HEALTHY
```

### 3. 批量遷移

可以使用 IDE 的重構功能批量替換：

```python
# 替換規則
EXPECTED_STATUS_HEALTHY → EXPECTED.STATUS.HEALTHY
EXPECTED_STATUS_UNHEALTHY → EXPECTED.STATUS.UNHEALTHY
HTTP_200_OK → HTTP.OK
HTTP_500_INTERNAL_SERVER_ERROR → HTTP.INTERNAL_SERVER_ERROR
```

## 未來擴展

### 添加新常數

```python
class EXPECTED:
    class STATUS:
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"
        # 新增
        WARNING = "warning"

    class DATABASE:
        CONNECTED = "connected"
        DISCONNECTED = "disconnected"
        HEALTHY = "healthy"
        # 新增
        SLOW = "slow"
```

### 添加新的常數類別

```python
class API:
    """API 相關常數"""

    class ENDPOINTS:
        HEALTH = "/healthz"
        READY = "/readyz"

    class METHODS:
        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
```

## 總結

這次重構成功實現了：

1. ✅ **更好的組織結構**：使用類別層次結構組織常數
2. ✅ **更簡潔的使用方式**：減少導入語句的複雜度
3. ✅ **更好的 IDE 支援**：提供更好的自動完成和錯誤檢查
4. ✅ **向後相容性**：現有代碼無需修改即可繼續使用
5. ✅ **未來擴展性**：容易添加新的常數和類別

這種物件結構的設計更符合現代 Python 開發的最佳實踐，也與 JavaScript 的配置模式保持一致。
