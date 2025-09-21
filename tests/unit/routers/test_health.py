"""
健康檢查路由測試。

測試健康檢查路由模組的功能。
"""

# ===== 標準函式庫 =====
import inspect
from unittest.mock import patch

# ===== 第三方套件 =====
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.middleware.error_handler import setup_error_handlers
from app.routers.health import liveness_probe, readiness_probe, router

# ===== 測試設定 =====


class TestHealthRouter:
    """健康檢查路由測試類別。"""

    @pytest.fixture
    def app(self):
        """建立測試用的 FastAPI 應用程式。"""
        app = FastAPI()
        app.include_router(router)
        setup_error_handlers(app)
        return app

    @pytest.fixture
    def client(self, app):
        """建立測試客戶端。"""
        return TestClient(app)

    # 簡化後不再需要這些 mock fixture

    def test_liveness_probe_success(self, client):
        """測試存活探測成功情況。"""
        # 發送請求
        response = client.get("/healthz")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 簡化後只返回基本狀態
        assert data["status"] == "healthy"

    def test_liveness_probe_with_fail_parameter(self, client):
        """測試存活探測失敗參數（已移除，參數不再有效）。"""
        # 簡化後不再支援 fail 參數，應該正常返回
        response = client.get("/healthz?fail=true")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_readiness_probe_success(self, client):
        """測試準備就緒探測成功情況。"""
        with patch("app.routers.health.check_db_connection") as mock_check_db:
            # 發送請求
            response = client.get("/readyz")

            # 驗證回應
            assert response.status_code == 200
            data = response.json()

            # 簡化後只返回基本狀態
            assert data["status"] == "healthy"

            # 驗證資料庫檢查被調用
            mock_check_db.assert_called_once()

    def test_readiness_probe_with_fail_parameter(self, client):
        """測試準備就緒探測失敗參數（已移除，參數不再有效）。"""
        with patch("app.routers.health.check_db_connection"):
            # 簡化後不再支援 fail 參數，應該正常返回
            response = client.get("/readyz?fail=true")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_readiness_probe_with_db_fail_parameter(self, client):
        """測試準備就緒探測資料庫失敗參數（已移除，參數不再有效）。"""
        with patch("app.routers.health.check_db_connection"):
            # 簡化後不再支援 db_fail 參數，應該正常返回
            response = client.get("/readyz?db_fail=true")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_readiness_probe_database_connection_failure(self, client):
        """測試準備就緒探測資料庫連線失敗。"""
        with patch("app.routers.health.check_db_connection") as mock_check_db:
            # 模擬資料庫連線失敗
            mock_check_db.side_effect = Exception("資料庫連線失敗")

            # 發送請求
            response = client.get("/readyz")

            # 驗證回應
            assert response.status_code == 503
            data = response.json()

            # 簡化後的錯誤格式
            assert data["detail"] == "Service Unavailable"

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
        # 驗證函數簽名（簡化後無參數）
        sig = inspect.signature(liveness_probe)
        params = list(sig.parameters.keys())

        assert params == []

    def test_readiness_probe_function_signature(self):
        """測試準備就緒探測函數簽名。"""
        # 驗證函數簽名（簡化後無參數）
        sig = inspect.signature(readiness_probe)
        params = list(sig.parameters.keys())

        assert params == []

    def test_liveness_probe_async_function(self):
        """測試存活探測函數是否為非同步函數。"""
        # 驗證函數是否為協程函數
        assert inspect.iscoroutinefunction(liveness_probe)

    def test_readiness_probe_async_function(self):
        """測試準備就緒探測函數是否為非同步函數。"""
        # 驗證函數是否為協程函數
        assert inspect.iscoroutinefunction(readiness_probe)

    def test_liveness_probe_response_structure(self, client):
        """測試存活探測回應結構。"""
        # 發送請求
        response = client.get("/healthz")

        # 驗證回應結構
        assert response.status_code == 200
        data = response.json()

        # 簡化後只驗證必要欄位
        assert "status" in data
        assert data["status"] == "healthy"

    def test_readiness_probe_response_structure(self, client):
        """測試準備就緒探測回應結構。"""
        with patch("app.routers.health.check_db_connection"):
            # 發送請求
            response = client.get("/readyz")

            # 驗證回應結構
            assert response.status_code == 200
            data = response.json()

            # 簡化後只驗證必要欄位
            assert "status" in data
            assert data["status"] == "healthy"

    def test_liveness_probe_with_different_fail_values(self, client):
        """測試存活探測不同失敗值（已移除，參數不再有效）。"""
        # 簡化後不再支援 fail 參數，所有請求都應該正常返回
        response = client.get("/healthz?fail=false")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        response = client.get("/healthz?fail=true")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        response = client.get("/healthz?fail=1")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_readiness_probe_with_different_fail_values(self, client):
        """測試準備就緒探測不同失敗值（已移除，參數不再有效）。"""
        with patch("app.routers.health.check_db_connection"):
            # 簡化後不再支援 fail 和 db_fail 參數，所有請求都應該正常返回
            response = client.get("/readyz?fail=false&db_fail=false")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

            response = client.get("/readyz?fail=true")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

            response = client.get("/readyz?db_fail=true")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

            response = client.get("/readyz?fail=true&db_fail=true")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
