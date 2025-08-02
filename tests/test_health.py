import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.core import settings, get_project_version

# 導入測試常數
from tests.constants import (
    EXPECTED_STATUS_HEALTHY,
    EXPECTED_STATUS_UNHEALTHY,
    EXPECTED_UPTIME_RUNNING,
    EXPECTED_DATABASE_CONNECTED,
    EXPECTED_DATABASE_DISCONNECTED,
    EXPECTED_DATABASE_HEALTHY,
    EXPECTED_MESSAGE_READY,
    EXPECTED_MESSAGE_NOT_READY,
    EXPECTED_ERROR_MESSAGE,
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
    SIMULATED_VERSION_CHECK_ERROR,
    SIMULATED_DATABASE_CONNECTION_ERROR
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
    
    # 檢查時間戳是有效的整數
    assert isinstance(response_data["timestamp"], int)
    assert response_data["timestamp"] > 0

def test_liveness_probe_failure(mocker):
    """
    存活探測失敗時，應返回 500 狀態碼和錯誤詳情。
    """ 
    # 模擬 get_project_version 函式拋出異常
    mocker.patch(
        "app.routers.health.get_project_version",
        side_effect=Exception(SIMULATED_VERSION_CHECK_ERROR)
    )
    
    response = client.get("/healthz")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert "detail" in response.json()
    assert response.json()["detail"]["status"] == EXPECTED_STATUS_UNHEALTHY
    assert response.json()["detail"]["error"] == EXPECTED_ERROR_MESSAGE
    assert "timestamp" in response.json()["detail"]

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
    
    # 檢查時間戳是有效的整數
    assert isinstance(response_data["timestamp"], int)
    assert response_data["timestamp"] > 0

def test_readiness_probe_failure(mocker):
    """
    測試就緒探測失敗的情況（資料庫連線中斷）。
    """
    # 模擬資料庫連線失敗，讓 get_healthy_db 拋出 HTTPException
    mocker.patch(
        "app.models.database.engine.connect",
        side_effect=Exception(SIMULATED_DATABASE_CONNECTION_ERROR)
    )
    response = client.get("/readyz")
    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE
    assert "detail" in response.json()
    assert response.json()["detail"]["status"] == "error"
    assert response.json()["detail"]["database"] == EXPECTED_DATABASE_DISCONNECTED
    assert "timestamp" in response.json()["detail"]