# ===== 標準函式庫 =====
from datetime import datetime, timezone
import re

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.core import get_project_version, settings
from app.main import app

# 導入測試常數
from tests.constants import (
    EXPECTED_DATABASE_CONNECTED,
    EXPECTED_DATABASE_DISCONNECTED,
    EXPECTED_DATABASE_HEALTHY,
    EXPECTED_ERROR_MESSAGE,
    EXPECTED_MESSAGE_READY,
    EXPECTED_STATUS_HEALTHY,
    EXPECTED_STATUS_UNHEALTHY,
    EXPECTED_UPTIME_RUNNING,
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
    SIMULATED_VERSION_CHECK_ERROR,
)

# 使用 FastAPI 的 TestClient 來模擬 HTTP 請求
client = TestClient(app)


def test_liveness_probe_success():
    """
    測試存活探測，應總是成功。
    """
    response = client.get("/healthz")
    assert response.status_code == HTTP_200_OK

    response_data = response.json()

    # 檢查必要欄位存在
    assert "status" in response_data
    assert "app_name" in response_data
    assert "version" in response_data
    assert "uptime" in response_data
    assert "timestamp" in response_data

    # 檢查欄位值
    assert response_data["status"] == EXPECTED_STATUS_HEALTHY
    assert response_data["uptime"] == EXPECTED_UPTIME_RUNNING

    # 檢查應用程式名稱和版本（使用實際設定值）
    assert response_data["app_name"] == settings.app_name
    assert response_data["version"] == get_project_version()

    # 檢查時間戳是有效的 ISO 格式字串
    assert isinstance(response_data["timestamp"], str)
    # 驗證時間戳格式：YYYY-MM-DDTHH:MM:SSZ
    timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    assert re.match(
        timestamp_pattern, response_data["timestamp"]
    ), f"時間戳格式不正確: {response_data['timestamp']}"

    # 驗證時間戳是合理的（不超過當前時間太多）
    try:
        timestamp_dt = datetime.strptime(
            response_data["timestamp"], "%Y-%m-%dT%H:%M:%SZ"
        )
        timestamp_dt = timestamp_dt.replace(tzinfo=timezone.utc)  # 添加 UTC 時區資訊
        current_dt = datetime.now(timezone.utc)
        time_diff = abs((timestamp_dt - current_dt).total_seconds())
        assert time_diff < 60, f"時間戳與當前時間差異過大: {time_diff}秒"
    except ValueError as e:
        pytest.fail(f"無法解析時間戳: {e}")


def test_liveness_probe_failure(mocker):
    """
    存活探測失敗時，應返回 500 狀態碼和錯誤詳情。
    """
    # 模擬 get_project_version 函式拋出異常
    mocker.patch(
        "app.routers.health.get_project_version",
        side_effect=Exception(SIMULATED_VERSION_CHECK_ERROR),
    )

    response = client.get("/healthz")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    response_data = response.json()
    # 修正：使用 error.message 欄位而不是 detail
    assert "error" in response_data
    assert "message" in response_data["error"]
    # 檢查錯誤訊息內容
    error_message = response_data["error"]["message"]
    assert "status" in error_message
    assert "error" in error_message
    assert error_message["status"] == EXPECTED_STATUS_UNHEALTHY
    assert error_message["error"] == EXPECTED_ERROR_MESSAGE
    assert "timestamp" in error_message

    # 檢查時間戳是有效的 ISO 格式字串
    assert isinstance(error_message["timestamp"], str)
    # 驗證時間戳格式：YYYY-MM-DDTHH:MM:SSZ
    timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    assert re.match(
        timestamp_pattern, error_message["timestamp"]
    ), f"時間戳格式不正確: {error_message['timestamp']}"


def test_readiness_probe_success(mocker):
    """
    測試就緒探測成功的情況（資料庫連線正常）。
    """
    # 模擬資料庫連線成功
    mocker.patch("app.models.database.get_healthy_db", return_value=True)
    response = client.get("/readyz")
    assert response.status_code == HTTP_200_OK

    response_data = response.json()

    # 檢查必要欄位存在
    assert "status" in response_data
    assert "database" in response_data
    assert "message" in response_data
    assert "timestamp" in response_data
    assert "checks" in response_data

    # 檢查欄位值
    assert response_data["status"] == EXPECTED_STATUS_HEALTHY
    assert response_data["database"] == EXPECTED_DATABASE_CONNECTED
    assert response_data["message"] == EXPECTED_MESSAGE_READY
    assert response_data["checks"]["database"] == EXPECTED_DATABASE_HEALTHY

    # 檢查時間戳是有效的 ISO 格式字串
    assert isinstance(response_data["timestamp"], str)
    # 驗證時間戳格式：YYYY-MM-DDTHH:MM:SSZ
    timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    assert re.match(
        timestamp_pattern, response_data["timestamp"]
    ), f"時間戳格式不正確: {response_data['timestamp']}"


def test_readiness_probe_failure(mocker):
    """
    測試就緒探測失敗的情況（資料庫連線中斷）。
    """
    # 模擬資料庫連線失敗
    from sqlalchemy.exc import OperationalError

    mocker.patch(
        "app.models.database.engine.connect",
        side_effect=OperationalError("Connection failed", None, None),
    )

    response = client.get("/readyz")
    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE
    response_data = response.json()
    # 修正：使用 error.message 欄位而不是 detail
    assert "error" in response_data
    assert "message" in response_data["error"]
    # 檢查錯誤訊息內容
    error_message = response_data["error"]["message"]
    assert "status" in error_message
    assert "database" in error_message
    assert error_message["status"] == "error"
    assert error_message["database"] == EXPECTED_DATABASE_DISCONNECTED
    assert "timestamp" in error_message

    # 檢查時間戳是有效的 ISO 格式字串
    assert isinstance(error_message["timestamp"], str)
    # 驗證時間戳格式：YYYY-MM-DDTHH:MM:SSZ
    timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    assert re.match(
        timestamp_pattern, error_message["timestamp"]
    ), f"時間戳格式不正確: {error_message['timestamp']}"
