"""
測試常數模組

包含所有測試中使用的常數值，確保測試的一致性和可維護性。
使用物件結構組織常數，提供更好的命名空間管理。
"""


# ===== 健康檢查相關常數 =====
class EXPECTED:
    """預期值常數類別"""

    class STATUS:
        """狀態相關常數"""

        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"

    class UPTIME:
        """運行時間相關常數"""

        RUNNING = "running"

    class DATABASE:
        """資料庫狀態相關常數"""

        CONNECTED = "connected"
        DISCONNECTED = "disconnected"
        HEALTHY = "healthy"

    class MESSAGE:
        """訊息相關常數"""

        READY = "Application and database are ready to serve traffic."
        NOT_READY = "Database connection failed. Application is not ready."
        ERROR = "Application health check failed"


# ===== HTTP 狀態碼常數 =====
class HTTP:
    """HTTP 狀態碼常數類別"""

    # 成功狀態碼
    OK = 200
    CREATED = 201
    NO_CONTENT = 204

    # 客戶端錯誤狀態碼
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405

    # 伺服器錯誤狀態碼
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503


# ===== 測試資料常數 =====
class TEST:
    """測試資料常數類別"""

    APP_NAME = "104 Resume Clinic Scheduler"
    VERSION = "0.1.0"
    TIMESTAMP = 1717334400

    class CONFIG:
        """測試配置常數"""

        TIMEOUT = 30  # 測試超時時間（秒）
        RETRY_COUNT = 3  # 測試重試次數


# ===== 錯誤訊息常數 =====
class SIMULATED:
    """模擬錯誤訊息常數類別"""

    VERSION_CHECK_ERROR = "Simulated version check error"
    DATABASE_CONNECTION_ERROR = "Database connection failed"


# ===== 向後相容性別名 =====
# 為了保持向後相容性，保留原有的常數名稱
EXPECTED_STATUS_HEALTHY = EXPECTED.STATUS.HEALTHY
EXPECTED_STATUS_UNHEALTHY = EXPECTED.STATUS.UNHEALTHY
EXPECTED_UPTIME_RUNNING = EXPECTED.UPTIME.RUNNING
EXPECTED_DATABASE_CONNECTED = EXPECTED.DATABASE.CONNECTED
EXPECTED_DATABASE_DISCONNECTED = EXPECTED.DATABASE.DISCONNECTED
EXPECTED_DATABASE_HEALTHY = EXPECTED.DATABASE.HEALTHY
EXPECTED_MESSAGE_READY = EXPECTED.MESSAGE.READY
EXPECTED_MESSAGE_NOT_READY = EXPECTED.MESSAGE.NOT_READY
EXPECTED_ERROR_MESSAGE = EXPECTED.MESSAGE.ERROR

HTTP_200_OK = HTTP.OK
HTTP_500_INTERNAL_SERVER_ERROR = HTTP.INTERNAL_SERVER_ERROR
HTTP_503_SERVICE_UNAVAILABLE = HTTP.SERVICE_UNAVAILABLE

TEST_APP_NAME = TEST.APP_NAME
TEST_VERSION = TEST.VERSION
TEST_TIMESTAMP = TEST.TIMESTAMP
TEST_TIMEOUT = TEST.CONFIG.TIMEOUT
TEST_RETRY_COUNT = TEST.CONFIG.RETRY_COUNT

SIMULATED_VERSION_CHECK_ERROR = SIMULATED.VERSION_CHECK_ERROR
SIMULATED_DATABASE_CONNECTION_ERROR = SIMULATED.DATABASE_CONNECTION_ERROR
