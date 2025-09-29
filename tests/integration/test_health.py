"""健康檢查路由整合測試。

測試健康檢查端點的完整流程，包括存活探測和就緒探測。
"""

# ===== 標準函式庫 =====
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.main import app


class TestHealthRoutes:
    """健康檢查路由整合測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    def test_liveness_probe_success(self, client):
        """測試存活探測 - 成功。"""
        # GIVEN：應用程式正常運行

        # WHEN：呼叫存活探測端點
        response = client.get("/healthz")

        # THEN：確認返回健康狀態
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_liveness_probe_structure(self, client):
        """測試存活探測 - 回應結構。"""
        # GIVEN：應用程式正常運行

        # WHEN：呼叫存活探測端點
        response = client.get("/healthz")

        # THEN：確認回應結構正確
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert isinstance(data["status"], str)

    @patch('app.routers.health.check_db_connection')
    def test_readiness_probe_success(self, mock_db_check, client):
        """測試就緒探測 - 成功。"""
        # GIVEN：資料庫連線正常
        mock_db_check.return_value = None  # check_db_connection 沒有回傳值

        # WHEN：呼叫就緒探測端點
        response = client.get("/readyz")

        # THEN：確認返回健康狀態
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
        mock_db_check.assert_called_once()

    @patch('app.routers.health.check_db_connection')
    def test_readiness_probe_database_failure(self, mock_db_check, client):
        """測試就緒探測 - 資料庫連線失敗。"""
        # GIVEN：資料庫連線失敗
        mock_db_check.side_effect = Exception("Database connection failed")

        # WHEN：呼叫就緒探測端點
        response = client.get("/readyz")

        # THEN：確認返回服務不可用狀態
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json() == {"detail": "Service Unavailable"}
        mock_db_check.assert_called_once()

    def test_readiness_probe_structure(self, client):
        """測試就緒探測 - 回應結構。"""
        # GIVEN：應用程式和資料庫正常運行

        # WHEN：呼叫就緒探測端點
        response = client.get("/readyz")

        # THEN：確認回應結構正確
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert isinstance(data["status"], str)

    def test_health_endpoints_headers(self, client):
        """測試健康檢查端點 - HTTP 標頭。"""
        # GIVEN：應用程式正常運行

        # WHEN：呼叫健康檢查端點
        liveness_response = client.get("/healthz")
        readiness_response = client.get("/readyz")

        # THEN：確認 HTTP 標頭正確
        assert liveness_response.status_code == status.HTTP_200_OK
        assert readiness_response.status_code == status.HTTP_200_OK

        # 確認 Content-Type 標頭
        assert liveness_response.headers["content-type"] == "application/json"
        assert readiness_response.headers["content-type"] == "application/json"

    def test_health_endpoints_methods(self, client):
        """測試健康檢查端點 - HTTP 方法。"""
        # GIVEN：應用程式正常運行

        # WHEN：使用不支援的 HTTP 方法呼叫
        post_response = client.post("/healthz")
        put_response = client.put("/readyz")

        # THEN：確認返回方法不允許錯誤
        assert post_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert put_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
