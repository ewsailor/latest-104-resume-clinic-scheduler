"""
中間件整合測試模組。

測試多個中間件同時運作的情況，確保它們能正確協同工作。
"""

# ===== 標準函式庫 =====
import re

# ===== 第三方套件 =====
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.errors import AuthenticationError, ValidationError
from app.middleware.cors import setup_cors_middleware
from app.middleware.error_handler import setup_error_handlers


class TestMiddlewareIntegration:
    """中間件整合測試類別。"""

    @pytest.fixture
    def app_with_all_middleware(self):
        """建立包含所有中間件的測試應用程式。"""
        app = FastAPI()

        # 設定所有中間件
        setup_cors_middleware(app)
        setup_error_handlers(app)

        # 添加測試路由
        @app.get("/test/success")
        async def test_success():
            return {"message": "success"}

        @app.post("/test/success")
        async def test_post_success():
            return {"message": "post success"}

        @app.get("/test/error")
        async def test_error():
            raise ValidationError("Test validation error")

        @app.post("/test/error")
        async def test_post_error():
            raise AuthenticationError("Test authentication error")

        @app.get("/test/http-exception")
        async def test_http_exception():
            raise HTTPException(status_code=400, detail="HTTP exception")

        return app

    @pytest.fixture
    def client(self, app_with_all_middleware):
        """建立測試客戶端。"""
        return TestClient(app_with_all_middleware)

    def test_cors_and_success_response(self, client):
        """測試 CORS 中間件與成功回應的整合。"""
        response = client.get(
            "/test/success", headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200

        # 檢查 CORS 標頭
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert headers["access-control-allow-origin"] == "http://localhost:3000"
        assert headers["access-control-allow-credentials"] == "true"

        # 檢查回應內容
        response_data = response.json()
        assert response_data["message"] == "success"

    def test_cors_and_error_response(self, client):
        """測試 CORS 中間件與錯誤回應的整合。"""
        response = client.get(
            "/test/error", headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 422

        # 檢查 CORS 標頭仍然存在
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert headers["access-control-allow-origin"] == "http://localhost:3000"
        assert headers["access-control-allow-credentials"] == "true"

        # 檢查錯誤回應結構
        response_data = response.json()
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]
        assert response_data["error"]["status_code"] == 422

    def test_cors_preflight_with_error_endpoint(self, client):
        """測試 CORS 預檢請求與錯誤端點的整合。"""
        response = client.options(
            "/test/error",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        assert response.status_code == 200

        # 檢查 CORS 標頭
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert headers["access-control-allow-origin"] == "http://localhost:3000"
        assert headers["access-control-allow-credentials"] == "true"
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers

    def test_post_request_with_cors_and_error(self, client):
        """測試 POST 請求的 CORS 和錯誤處理整合。"""
        response = client.post(
            "/test/error",
            headers={
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json",
            },
            json={"test": "data"},
        )

        assert response.status_code == 401

        # 檢查 CORS 標頭
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert headers["access-control-allow-origin"] == "http://localhost:3000"
        assert headers["access-control-allow-credentials"] == "true"

        # 檢查錯誤回應結構
        response_data = response.json()
        assert "error" in response_data
        assert response_data["error"]["status_code"] == 401
        assert "Test authentication error" in response_data["error"]["message"]

    def test_http_exception_with_cors(self, client):
        """測試 HTTP 異常與 CORS 的整合。"""
        response = client.get(
            "/test/http-exception", headers={"Origin": "http://127.0.0.1:8000"}
        )

        assert response.status_code == 400

        # 檢查 CORS 標頭
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert headers["access-control-allow-origin"] == "http://127.0.0.1:8000"
        assert headers["access-control-allow-credentials"] == "true"

        # 檢查錯誤回應結構（FastAPI 的 HTTPException 使用標準格式）
        response_data = response.json()
        assert "detail" in response_data
        assert response_data["detail"] == "HTTP exception"

    def test_multiple_origins_with_errors(self, client):
        """測試多個來源與錯誤處理的整合。"""
        origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

        for origin in origins:
            response = client.get("/test/error", headers={"Origin": origin})

            assert response.status_code == 422

            # 檢查 CORS 標頭
            headers = response.headers
            assert "access-control-allow-origin" in headers
            assert headers["access-control-allow-origin"] == origin
            assert headers["access-control-allow-credentials"] == "true"

            # 檢查錯誤回應結構
            response_data = response.json()
            assert "error" in response_data
            assert response_data["error"]["status_code"] == 422

    def test_cors_headers_preserved_in_error_responses(self, client):
        """測試錯誤回應中 CORS 標頭的保留。"""
        # 測試自定義錯誤（會被我們的錯誤處理中間件處理）
        response1 = client.get(
            "/test/error", headers={"Origin": "http://localhost:3000"}
        )

        assert response1.status_code == 422
        headers1 = response1.headers
        assert "access-control-allow-origin" in headers1
        assert headers1["access-control-allow-origin"] == "http://localhost:3000"
        assert headers1["access-control-allow-credentials"] == "true"
        assert "access-control-allow-methods" in headers1
        assert "access-control-allow-headers" in headers1

        # 測試 HTTP 異常（被 FastAPI 內建處理器處理）
        response2 = client.get(
            "/test/http-exception", headers={"Origin": "http://localhost:3000"}
        )

        assert response2.status_code == 400
        headers2 = response2.headers
        assert "access-control-allow-origin" in headers2
        assert headers2["access-control-allow-origin"] == "http://localhost:3000"
        assert headers2["access-control-allow-credentials"] == "true"

    def test_middleware_order_consistency(self, client):
        """測試中間件執行順序的一致性。"""
        # 測試成功請求
        success_response = client.get(
            "/test/success", headers={"Origin": "http://localhost:3000"}
        )
        assert success_response.status_code == 200
        assert "access-control-allow-origin" in success_response.headers

        # 測試錯誤請求
        error_response = client.get(
            "/test/error", headers={"Origin": "http://localhost:3000"}
        )
        assert error_response.status_code == 422
        assert "access-control-allow-origin" in error_response.headers

        # 確保兩種情況下 CORS 標頭都存在
        success_cors_headers = {
            k: v
            for k, v in success_response.headers.items()
            if k.startswith("access-control-")
        }
        error_cors_headers = {
            k: v
            for k, v in error_response.headers.items()
            if k.startswith("access-control-")
        }

        # 基本 CORS 標頭應該存在
        assert "access-control-allow-origin" in success_cors_headers
        assert "access-control-allow-origin" in error_cors_headers
        assert "access-control-allow-credentials" in success_cors_headers
        assert "access-control-allow-credentials" in error_cors_headers

        # 錯誤回應中會有額外的 CORS 標頭（由錯誤處理中間件添加）
        assert "access-control-allow-methods" in error_cors_headers
        assert "access-control-allow-headers" in error_cors_headers

    def test_error_timestamp_consistency(self, client):
        """測試錯誤回應中時間戳的一致性。"""
        response1 = client.get("/test/error")
        response2 = client.get("/test/error")

        # 兩個錯誤回應都應該有時間戳
        assert response1.status_code == 422
        assert response2.status_code == 422

        data1 = response1.json()
        data2 = response2.json()

        assert "timestamp" in data1["error"]
        assert "timestamp" in data2["error"]

        # 時間戳格式應該一致
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'

        assert re.match(timestamp_pattern, data1["error"]["timestamp"])
        assert re.match(timestamp_pattern, data2["error"]["timestamp"])

    def test_cors_with_different_http_methods_and_errors(self, client):
        """測試不同 HTTP 方法與錯誤處理的 CORS 整合。"""
        methods_and_endpoints = [
            ("GET", "/test/error"),
            ("POST", "/test/error"),
        ]

        for method, endpoint in methods_and_endpoints:
            if method == "GET":
                response = client.get(
                    endpoint, headers={"Origin": "http://localhost:3000"}
                )
            elif method == "POST":
                response = client.post(
                    endpoint,
                    headers={
                        "Origin": "http://localhost:3000",
                        "Content-Type": "application/json",
                    },
                    json={"test": "data"},
                )

            # 確保是錯誤回應
            assert response.status_code >= 400

            # 檢查 CORS 標頭
            headers = response.headers
            assert "access-control-allow-origin" in headers
            assert headers["access-control-allow-origin"] == "http://localhost:3000"
            assert headers["access-control-allow-credentials"] == "true"
            assert "access-control-allow-methods" in headers
            assert "access-control-allow-headers" in headers

            # 檢查錯誤回應結構
            response_data = response.json()
            assert "error" in response_data
            assert "message" in response_data["error"]
            assert "status_code" in response_data["error"]
            assert "timestamp" in response_data["error"]
