"""
CORS 中間件整合測試模組。

測試 CORS 中間件的功能，包括跨域請求處理、預檢請求等。
"""

# ===== 第三方套件 =====
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.middleware.cors import setup_cors_middleware


class TestCORSMiddleware:
    """CORS 中間件整合測試類別。"""

    @pytest.fixture
    def app_with_cors(self):
        """建立包含 CORS 中間件的測試應用程式。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加測試路由
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        @app.post("/test")
        async def test_post_endpoint():
            return {"message": "test post"}

        return app

    @pytest.fixture
    def client(self, app_with_cors):
        """建立測試客戶端。"""
        return TestClient(app_with_cors)

    def test_cors_preflight_request_success(self, client):
        """測試 CORS 預檢請求成功。"""
        # 發送 OPTIONS 預檢請求
        response = client.options(
            "/test",
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
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers
        assert "access-control-allow-credentials" in headers

        # 檢查允許的來源
        assert headers["access-control-allow-origin"] == "http://localhost:3000"
        assert headers["access-control-allow-credentials"] == "true"

    def test_cors_allowed_origins(self, client):
        """測試允許的來源列表。"""
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

        for origin in allowed_origins:
            response = client.get("/test", headers={"Origin": origin})

            assert response.status_code == 200
            assert response.headers["access-control-allow-origin"] == origin

    def test_cors_allowed_methods(self, client):
        """測試允許的 HTTP 方法。"""
        allowed_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

        for method in allowed_methods:
            if method == "GET":
                response = client.get(
                    "/test", headers={"Origin": "http://localhost:3000"}
                )
            elif method == "POST":
                response = client.post(
                    "/test", headers={"Origin": "http://localhost:3000"}
                )
            elif method == "PUT":
                response = client.put(
                    "/test", headers={"Origin": "http://localhost:3000"}
                )
            elif method == "PATCH":
                response = client.patch(
                    "/test", headers={"Origin": "http://localhost:3000"}
                )
            elif method == "DELETE":
                response = client.delete(
                    "/test", headers={"Origin": "http://localhost:3000"}
                )
            elif method == "OPTIONS":
                response = client.options(
                    "/test", headers={"Origin": "http://localhost:3000"}
                )

            assert response.status_code in [
                200,
                405,
            ]  # 405 表示方法不允許，但 CORS 仍應處理
            assert "access-control-allow-origin" in response.headers

    def test_cors_credentials_allowed(self, client):
        """測試憑證允許設定。"""
        response = client.get("/test", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_cors_headers_in_response(self, client):
        """測試回應中包含的 CORS 標頭。"""
        response = client.get("/test", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200

        # 檢查必要的 CORS 標頭
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-credentials" in headers
        # 注意：access-control-allow-methods 和 access-control-allow-headers
        # 只在預檢請求中出現，不在實際請求的回應中

    def test_cors_without_origin_header(self, client):
        """測試沒有 Origin 標頭的請求。"""
        response = client.get("/test")

        assert response.status_code == 200
        # 沒有 Origin 標頭時，不應該有 CORS 相關標頭
        assert "access-control-allow-origin" not in response.headers

    def test_cors_preflight_with_custom_headers(self, client):
        """測試包含自定義標頭的預檢請求。"""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type, X-Custom-Header",
            },
        )

        assert response.status_code == 200
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )
        assert response.headers["access-control-allow-credentials"] == "true"

        # 檢查允許的標頭（應該包含 * 表示允許所有標頭）
        allowed_headers = response.headers["access-control-allow-headers"]
        assert "*" in allowed_headers or "Authorization" in allowed_headers

    def test_cors_multiple_origins_handling(self, client):
        """測試多個來源的處理。"""
        # 測試第一個允許的來源
        response1 = client.get("/test", headers={"Origin": "http://localhost:3000"})
        assert response1.status_code == 200
        assert (
            response1.headers["access-control-allow-origin"] == "http://localhost:3000"
        )

        # 測試第二個允許的來源
        response2 = client.get("/test", headers={"Origin": "http://127.0.0.1:8000"})
        assert response2.status_code == 200
        assert (
            response2.headers["access-control-allow-origin"] == "http://127.0.0.1:8000"
        )
