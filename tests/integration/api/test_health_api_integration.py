"""
Health API 路由整合測試模組。

測試健康檢查相關的 API 端點，包括存活探測和準備就緒探測。
"""

# ===== 標準函式庫 =====
import re
from unittest.mock import patch

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import OperationalError

# ===== 本地模組 =====
from app.core import get_project_version, settings
from app.main import app


class TestHealthAPIIntegration:
    """Health API 整合測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    def test_liveness_probe_success(self, client: TestClient):
        """測試存活探測成功。"""
        response = client.get("/healthz")

        assert response.status_code == 200
        response_data = response.json()

        # 檢查必要欄位存在
        required_fields = [
            "message",
            "status",
            "app_name",
            "version",
            "timestamp",
            "checks",
        ]
        for field in required_fields:
            assert field in response_data, f"缺少必要欄位: {field}"

        # 檢查欄位值
        assert response_data["message"] == "應用程式存活、正常運行"
        assert response_data["status"] == "healthy"
        assert response_data["app_name"] == settings.app_name
        assert response_data["version"] == get_project_version()

        # 檢查時間戳格式
        timestamp = response_data["timestamp"]
        assert isinstance(timestamp, str)
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        assert re.match(timestamp_pattern, timestamp), f"時間戳格式不正確: {timestamp}"

        # 檢查 checks 結構
        assert "application" in response_data["checks"]
        assert response_data["checks"]["application"] == "healthy"

    def test_liveness_probe_with_fail_parameter(self, client: TestClient):
        """測試存活探測失敗參數。"""
        response = client.get("/healthz?fail=true")

        assert response.status_code == 500
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 500
        assert (
            "存活探測檢查錯誤：應用程式異常、未正常運行"
            in response_data["error"]["message"]
        )

    def test_readiness_probe_success(self, client: TestClient):
        """測試準備就緒探測成功。"""
        response = client.get("/readyz")

        assert response.status_code == 200
        response_data = response.json()

        # 檢查必要欄位存在
        required_fields = [
            "message",
            "status",
            "app_name",
            "version",
            "timestamp",
            "checks",
        ]
        for field in required_fields:
            assert field in response_data, f"缺少必要欄位: {field}"

        # 檢查欄位值
        assert response_data["message"] == "應用程式準備就緒"
        assert response_data["status"] == "healthy"
        assert response_data["app_name"] == settings.app_name
        assert response_data["version"] == get_project_version()

        # 檢查時間戳格式
        timestamp = response_data["timestamp"]
        assert isinstance(timestamp, str)
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        assert re.match(timestamp_pattern, timestamp), f"時間戳格式不正確: {timestamp}"

        # 檢查 checks 結構
        assert "application" in response_data["checks"]
        assert "database" in response_data["checks"]
        assert response_data["checks"]["application"] == "healthy"
        assert response_data["checks"]["database"] == "healthy"

    def test_readiness_probe_with_fail_parameter(self, client: TestClient):
        """測試準備就緒探測失敗參數。"""
        response = client.get("/readyz?fail=true")

        assert response.status_code == 503
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 503
        assert "準備就緒探測檢查錯誤" in response_data["error"]["message"]

    def test_readiness_probe_with_db_fail_parameter(self, client: TestClient):
        """測試準備就緒探測資料庫失敗參數。"""
        response = client.get("/readyz?db_fail=true")

        assert response.status_code == 503
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 503
        assert "資料庫連線失敗錯誤" in response_data["error"]["message"]

    @patch("app.routers.health.check_db_connection")
    def test_readiness_probe_database_connection_failure(
        self, mock_check_db, client: TestClient
    ):
        """測試準備就緒探測資料庫連線失敗。"""
        # 模擬資料庫連線失敗
        mock_check_db.side_effect = OperationalError("Connection failed", None, None)

        response = client.get("/readyz")

        assert response.status_code == 503
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "資料庫連線失敗" in response_data["error"]["message"]

    def test_health_endpoints_response_format_consistency(self, client: TestClient):
        """測試健康檢查端點回應格式的一致性。"""
        endpoints = [
            ("/healthz", False),  # 不應該失敗
            ("/readyz", False),  # 不應該失敗
        ]

        for endpoint, should_fail in endpoints:
            response = client.get(endpoint)

            if should_fail:
                assert response.status_code >= 400
                response_data = response.json()
                assert "error" in response_data
            else:
                assert response.status_code == 200
                response_data = response.json()

                # 檢查成功回應的格式一致性
                required_fields = [
                    "message",
                    "status",
                    "app_name",
                    "version",
                    "timestamp",
                    "checks",
                ]
                for field in required_fields:
                    assert (
                        field in response_data
                    ), f"端點 {endpoint} 缺少必要欄位: {field}"

                # 檢查時間戳格式
                timestamp = response_data["timestamp"]
                assert isinstance(timestamp, str)
                timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
                assert re.match(
                    timestamp_pattern, timestamp
                ), f"端點 {endpoint} 時間戳格式不正確: {timestamp}"

    def test_health_endpoints_timestamp_consistency(self, client: TestClient):
        """測試健康檢查端點時間戳的一致性。"""
        # 連續呼叫兩個端點
        response1 = client.get("/healthz")
        response2 = client.get("/readyz")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # 檢查時間戳格式一致性
        timestamp1 = data1["timestamp"]
        timestamp2 = data2["timestamp"]

        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        assert re.match(timestamp_pattern, timestamp1)
        assert re.match(timestamp_pattern, timestamp2)

    def test_health_endpoints_application_info_consistency(self, client: TestClient):
        """測試健康檢查端點應用程式資訊的一致性。"""
        response1 = client.get("/healthz")
        response2 = client.get("/readyz")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # 檢查應用程式資訊一致性
        assert data1["app_name"] == data2["app_name"]
        assert data1["version"] == data2["version"]
        assert data1["app_name"] == settings.app_name
        assert data1["version"] == get_project_version()

    def test_health_endpoints_error_handling(self, client: TestClient):
        """測試健康檢查端點的錯誤處理。"""
        # 測試存活探測錯誤
        response = client.get("/healthz?fail=true")
        assert response.status_code == 500

        # 測試準備就緒探測錯誤
        response = client.get("/readyz?fail=true")
        assert response.status_code == 503

        # 測試資料庫失敗
        response = client.get("/readyz?db_fail=true")
        assert response.status_code == 503

    def test_health_endpoints_with_multiple_parameters(self, client: TestClient):
        """測試健康檢查端點的多個參數組合。"""
        # 測試準備就緒探測的多個參數
        response = client.get("/readyz?fail=true&db_fail=true")

        # 應該優先處理 fail 參數
        assert response.status_code == 503
        response_data = response.json()
        assert "準備就緒探測檢查錯誤" in response_data["error"]["message"]

    def test_health_endpoints_cors_headers(self, client: TestClient):
        """測試健康檢查端點的 CORS 標頭。"""
        endpoints = ["/healthz", "/readyz"]

        for endpoint in endpoints:
            response = client.get(endpoint, headers={"Origin": "http://localhost:3000"})

            assert response.status_code == 200

            # 檢查 CORS 標頭
            headers = response.headers
            assert "access-control-allow-origin" in headers
            assert headers["access-control-allow-origin"] == "http://localhost:3000"
            assert headers["access-control-allow-credentials"] == "true"

    def test_health_endpoints_content_type(self, client: TestClient):
        """測試健康檢查端點的內容類型。"""
        endpoints = ["/healthz", "/readyz"]

        for endpoint in endpoints:
            response = client.get(endpoint)

            assert response.status_code == 200
            assert "application/json" in response.headers.get("content-type", "")

    def test_health_endpoints_method_not_allowed(self, client: TestClient):
        """測試健康檢查端點不允許的 HTTP 方法。"""
        endpoints = ["/healthz", "/readyz"]

        for endpoint in endpoints:
            # 測試 POST 方法（應該不被允許）
            response = client.post(endpoint)
            assert response.status_code == 405

            # 測試 PUT 方法（應該不被允許）
            response = client.put(endpoint)
            assert response.status_code == 405

            # 測試 DELETE 方法（應該不被允許）
            response = client.delete(endpoint)
            assert response.status_code == 405
