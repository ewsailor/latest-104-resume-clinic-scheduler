"""
健康檢查測試 - 新式物件結構常數使用範例

展示如何使用重構後的物件結構常數。
"""

import re

from fastapi.testclient import TestClient

from app.core import get_project_version, settings
from app.main import app

# 導入新式物件結構常數
from tests.constants import EXPECTED, HTTP, SIMULATED, TEST
from tests.logger import log_test_info

# 使用 FastAPI 的 TestClient 來模擬 HTTP 請求
client = TestClient(app)


def assert_timestamp_format(timestamp: str, context: str = ""):
    """
    驗證時間戳格式是否正確。

    Args:
        timestamp: 要驗證的時間戳字串
        context: 錯誤訊息上下文
    """
    assert isinstance(timestamp, str), f"{context}時間戳必須是字串類型"

    # 驗證時間戳格式：YYYY-MM-DDTHH:MM:SSZ
    timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    assert re.match(
        timestamp_pattern, timestamp
    ), f"{context}時間戳格式不正確: {timestamp}"


def test_liveness_probe_success_new_style():
    """
    測試存活探測，應總是成功。
    使用新式物件結構常數。
    """
    response = client.get("/healthz")
    assert response.status_code == HTTP.OK

    response_data = response.json()

    # 檢查必要欄位存在
    assert "status" in response_data
    assert "app_name" in response_data
    assert "version" in response_data
    assert "uptime" in response_data
    assert "timestamp" in response_data

    # 檢查欄位值（使用新式物件結構）
    assert response_data["status"] == EXPECTED.STATUS.HEALTHY
    assert response_data["uptime"] == EXPECTED.UPTIME.RUNNING

    # 檢查應用程式名稱和版本（使用實際設定值）
    assert response_data["app_name"] == settings.app_name
    assert response_data["version"] == get_project_version()

    # 檢查時間戳格式
    assert_timestamp_format(response_data["timestamp"], "存活探測 ")


def test_liveness_probe_failure_new_style(mocker):
    """
    存活探測失敗時，應返回 500 狀態碼和錯誤詳情。
    使用新式物件結構常數。
    """
    # 模擬 get_project_version 函式拋出異常
    mocker.patch(
        "app.routers.health.get_project_version",
        side_effect=Exception(SIMULATED.VERSION_CHECK_ERROR),
    )

    response = client.get("/healthz")
    assert response.status_code == HTTP.INTERNAL_SERVER_ERROR
    # 修正：使用 error.message 欄位而不是 detail
    response_data = response.json()
    assert "error" in response_data
    assert "message" in response_data["error"]
    error_message = response_data["error"]["message"]
    assert error_message["status"] == EXPECTED.STATUS.UNHEALTHY
    assert error_message["error"] == EXPECTED.MESSAGE.ERROR
    assert "timestamp" in error_message


def test_readiness_probe_success_new_style(mocker):
    """
    測試就緒探測成功的情況（資料庫連線正常）。
    使用新式物件結構常數。
    """
    # 模擬資料庫連線成功
    mocker.patch("app.models.database.get_healthy_db", return_value=True)
    response = client.get("/readyz")
    assert response.status_code == HTTP.OK

    response_data = response.json()

    # 檢查必要欄位存在
    assert "status" in response_data
    assert "database" in response_data
    assert "message" in response_data
    assert "timestamp" in response_data
    assert "checks" in response_data

    # 檢查欄位值（使用新式物件結構）
    assert response_data["status"] == EXPECTED.STATUS.HEALTHY
    assert response_data["database"] == EXPECTED.DATABASE.CONNECTED
    assert response_data["message"] == EXPECTED.MESSAGE.READY
    assert response_data["checks"]["database"] == EXPECTED.DATABASE.HEALTHY

    # 檢查時間戳格式
    assert_timestamp_format(response_data["timestamp"], "就緒探測 ")


def test_readiness_probe_failure_new_style(mocker):
    """
    測試就緒探測失敗的情況（資料庫連線中斷）。
    使用新式物件結構常數。
    """
    # 模擬資料庫連線失敗，讓 get_healthy_db 拋出 HTTPException
    mocker.patch(
        "app.models.database.engine.connect",
        side_effect=Exception(SIMULATED.DATABASE_CONNECTION_ERROR),
    )
    response = client.get("/readyz")
    assert response.status_code == HTTP.SERVICE_UNAVAILABLE
    # 修正：使用 error.message 欄位而不是 detail
    response_data = response.json()
    assert "error" in response_data
    assert "message" in response_data["error"]
    error_message = response_data["error"]["message"]
    assert error_message["status"] == "error"
    assert error_message["database"] == EXPECTED.DATABASE.DISCONNECTED
    assert "timestamp" in error_message


def test_constants_structure():
    """
    測試常數結構是否正確。
    """
    # 測試 EXPECTED 結構
    assert EXPECTED.STATUS.HEALTHY == "healthy"
    assert EXPECTED.STATUS.UNHEALTHY == "unhealthy"
    assert EXPECTED.UPTIME.RUNNING == "running"
    assert EXPECTED.DATABASE.CONNECTED == "connected"
    assert EXPECTED.DATABASE.DISCONNECTED == "disconnected"
    assert EXPECTED.DATABASE.HEALTHY == "healthy"
    assert (
        EXPECTED.MESSAGE.READY == "Application and database are ready to serve traffic."
    )
    assert (
        EXPECTED.MESSAGE.NOT_READY
        == "Database connection failed. Application is not ready."
    )
    assert EXPECTED.MESSAGE.ERROR == "Application health check failed"

    # 測試 HTTP 結構
    assert HTTP.OK == 200
    assert HTTP.INTERNAL_SERVER_ERROR == 500
    assert HTTP.SERVICE_UNAVAILABLE == 503

    # 測試 TEST 結構
    assert TEST.APP_NAME == "104 Resume Clinic Scheduler"
    assert TEST.VERSION == "0.1.0"
    assert TEST.TIMESTAMP == 1717334400
    assert TEST.CONFIG.TIMEOUT == 30
    assert TEST.CONFIG.RETRY_COUNT == 3

    # 測試 SIMULATED 結構
    assert SIMULATED.VERSION_CHECK_ERROR == "Simulated version check error"
    assert SIMULATED.DATABASE_CONNECTION_ERROR == "Database connection failed"
