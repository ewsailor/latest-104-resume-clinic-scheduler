"""
健康檢查路由測試。

測試健康檢查路由模組的功能。
"""

import inspect
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

# ===== 標準函式庫 =====
import pytest

# ===== 本地模組 =====
from app.routers.health import liveness_probe, readiness_probe, router

# ===== 測試設定 =====


class TestHealthRouter:
    """健康檢查路由測試類別。"""

    @pytest.fixture
    def app(self):
        """建立測試用的 FastAPI 應用程式。"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """建立測試客戶端。"""
        return TestClient(app)

    @pytest.fixture
    def mock_settings(self):
        """模擬設定。"""
        mock_settings = Mock()
        mock_settings.app_name = "test-app"
        return mock_settings

    @pytest.fixture
    def mock_get_project_version(self):
        """模擬專案版本函數。"""
        return Mock(return_value="1.0.0")

    @pytest.fixture
    def mock_get_utc_timestamp(self):
        """模擬 UTC 時間戳函數。"""
        return Mock(return_value="2024-01-01T00:00:00Z")

    def test_liveness_probe_success(
        self, client, mock_settings, mock_get_project_version, mock_get_utc_timestamp
    ):
        """測試存活探測成功情況。"""
        with (
            patch("app.routers.health.settings", mock_settings),
            patch("app.routers.health.get_project_version", mock_get_project_version),
            patch("app.routers.health.get_utc_timestamp", mock_get_utc_timestamp),
        ):

            # 發送請求
            response = client.get("/healthz")

            # 驗證回應
            assert response.status_code == 200
            data = response.json()

            assert data["message"] == "應用程式存活"
            assert data["status"] == "healthy"
            assert data["app_name"] == "test-app"
            assert data["version"] == "1.0.0"
            assert data["timestamp"] == "2024-01-01T00:00:00Z"
            assert data["checks"]["application"] == "healthy"

    def test_liveness_probe_with_fail_parameter(self, client):
        """測試存活探測失敗參數。"""
        # 發送帶有 fail=true 的請求，應該會拋出異常
        with pytest.raises(Exception):
            client.get("/healthz?fail=true")

    def test_readiness_probe_success(
        self, client, mock_settings, mock_get_project_version, mock_get_utc_timestamp
    ):
        """測試準備就緒探測成功情況。"""
        with (
            patch("app.routers.health.settings", mock_settings),
            patch("app.routers.health.get_project_version", mock_get_project_version),
            patch("app.routers.health.get_utc_timestamp", mock_get_utc_timestamp),
            patch("app.routers.health.check_db_connection") as mock_check_db,
        ):

            # 發送請求
            response = client.get("/readyz")

            # 驗證回應
            assert response.status_code == 200
            data = response.json()

            assert data["message"] == "應用程式準備就緒"
            assert data["status"] == "healthy"
            assert data["app_name"] == "test-app"
            assert data["version"] == "1.0.0"
            assert data["timestamp"] == "2024-01-01T00:00:00Z"
            assert data["checks"]["application"] == "healthy"
            assert data["checks"]["database"] == "healthy"

            # 驗證資料庫檢查被調用
            mock_check_db.assert_called_once()

    def test_readiness_probe_with_fail_parameter(self, client):
        """測試準備就緒探測失敗參數。"""
        # 發送帶有 fail=true 的請求，應該會拋出異常
        with pytest.raises(Exception):
            client.get("/readyz?fail=true")

    def test_readiness_probe_with_db_fail_parameter(self, client):
        """測試準備就緒探測資料庫失敗參數。"""
        # 發送帶有 db_fail=true 的請求，應該會拋出異常
        with pytest.raises(Exception):
            client.get("/readyz?db_fail=true")

    def test_readiness_probe_database_connection_failure(
        self, client, mock_settings, mock_get_project_version, mock_get_utc_timestamp
    ):
        """測試準備就緒探測資料庫連線失敗。"""
        with (
            patch("app.routers.health.settings", mock_settings),
            patch("app.routers.health.get_project_version", mock_get_project_version),
            patch("app.routers.health.get_utc_timestamp", mock_get_utc_timestamp),
            patch("app.routers.health.check_db_connection") as mock_check_db,
        ):

            # 模擬資料庫連線失敗
            mock_check_db.side_effect = Exception("資料庫連線失敗")

            # 發送請求
            response = client.get("/readyz")

            # 驗證回應
            assert response.status_code == 500
            data = response.json()

            # 檢查錯誤格式（可能是自定義格式或 FastAPI 預設格式）
            assert "error" in data or "detail" in data
            if "error" in data:
                assert "資料庫連線失敗" in data["error"]
            else:
                assert "內部伺服器錯誤" in data["detail"]

    def test_liveness_probe_route_metadata(self):
        """測試存活探測路由元資料。"""
        # 找到存活探測路由
        liveness_route = None
        for route in router.routes:
            if route.path == "/healthz":
                liveness_route = route
                break

        assert liveness_route is not None
        assert liveness_route.methods == {"GET"}
        assert liveness_route.tags == ["Health Check"]

    def test_readiness_probe_route_metadata(self):
        """測試準備就緒探測路由元資料。"""
        # 找到準備就緒探測路由
        readiness_route = None
        for route in router.routes:
            if route.path == "/readyz":
                readiness_route = route
                break

        assert readiness_route is not None
        assert readiness_route.methods == {"GET"}
        assert readiness_route.tags == ["Health Check"]

    def test_router_configuration(self):
        """測試路由器配置。"""
        # 驗證路由器基本配置
        assert router.prefix == ""
        assert router.tags == ["Health Check"]
        assert len(router.routes) == 2

    def test_liveness_probe_function_signature(self):
        """測試存活探測函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(liveness_probe)
        params = list(sig.parameters.keys())

        assert params == ["fail"]
        assert sig.parameters["fail"].default is False

    def test_readiness_probe_function_signature(self):
        """測試準備就緒探測函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(readiness_probe)
        params = list(sig.parameters.keys())

        assert params == ["fail", "db_fail"]
        assert sig.parameters["fail"].default is False
        assert sig.parameters["db_fail"].default is False

    def test_liveness_probe_async_function(self):
        """測試存活探測函數是否為非同步函數。"""
        # 驗證函數是否為協程函數
        assert inspect.iscoroutinefunction(liveness_probe)

    def test_readiness_probe_async_function(self):
        """測試準備就緒探測函數是否為非同步函數。"""
        # 驗證函數是否為協程函數
        assert inspect.iscoroutinefunction(readiness_probe)

    def test_liveness_probe_response_structure(
        self, client, mock_settings, mock_get_project_version, mock_get_utc_timestamp
    ):
        """測試存活探測回應結構。"""
        with (
            patch("app.routers.health.settings", mock_settings),
            patch("app.routers.health.get_project_version", mock_get_project_version),
            patch("app.routers.health.get_utc_timestamp", mock_get_utc_timestamp),
        ):

            # 發送請求
            response = client.get("/healthz")

            # 驗證回應結構
            assert response.status_code == 200
            data = response.json()

            # 驗證必要欄位
            required_fields = [
                "message",
                "status",
                "app_name",
                "version",
                "timestamp",
                "checks",
            ]
            for field in required_fields:
                assert field in data

            # 驗證 checks 結構
            assert "application" in data["checks"]

    def test_readiness_probe_response_structure(
        self, client, mock_settings, mock_get_project_version, mock_get_utc_timestamp
    ):
        """測試準備就緒探測回應結構。"""
        with (
            patch("app.routers.health.settings", mock_settings),
            patch("app.routers.health.get_project_version", mock_get_project_version),
            patch("app.routers.health.get_utc_timestamp", mock_get_utc_timestamp),
            patch("app.routers.health.check_db_connection"),
        ):

            # 發送請求
            response = client.get("/readyz")

            # 驗證回應結構
            assert response.status_code == 200
            data = response.json()

            # 驗證必要欄位
            required_fields = [
                "message",
                "status",
                "app_name",
                "version",
                "timestamp",
                "checks",
            ]
            for field in required_fields:
                assert field in data

            # 驗證 checks 結構
            assert "application" in data["checks"]
            assert "database" in data["checks"]

    def test_liveness_probe_with_different_fail_values(self, client):
        """測試存活探測不同失敗值。"""
        # 測試 fail=false（預設值）
        response = client.get("/healthz?fail=false")
        assert response.status_code == 200

        # 測試 fail=true，應該會拋出異常
        with pytest.raises(Exception):
            client.get("/healthz?fail=true")

        # 測試 fail=1（布林值轉換），應該會拋出異常
        with pytest.raises(Exception):
            client.get("/healthz?fail=1")

    def test_readiness_probe_with_different_fail_values(
        self, client, mock_settings, mock_get_project_version, mock_get_utc_timestamp
    ):
        """測試準備就緒探測不同失敗值。"""
        with (
            patch("app.routers.health.settings", mock_settings),
            patch("app.routers.health.get_project_version", mock_get_project_version),
            patch("app.routers.health.get_utc_timestamp", mock_get_utc_timestamp),
            patch("app.routers.health.check_db_connection"),
        ):

            # 測試 fail=false, db_fail=false（預設值）
            response = client.get("/readyz?fail=false&db_fail=false")
            assert response.status_code == 200

            # 測試 fail=true，應該會拋出異常
            with pytest.raises(Exception):
                client.get("/readyz?fail=true")

            # 測試 db_fail=true，應該會拋出異常
            with pytest.raises(Exception):
                client.get("/readyz?db_fail=true")

            # 測試兩者都為 true，應該會拋出異常
            with pytest.raises(Exception):
                client.get("/readyz?fail=true&db_fail=true")
