#!/usr/bin/env python3
"""
CORS 中間件測試模組。

測試 CORS 中間件的各種功能和安全性。
"""

# ===== 第三方套件 =====
from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.middleware.cors import setup_cors_middleware


class TestCorsMiddleware:
    """CORS 中間件測試類別。"""

    def test_setup_cors_middleware_success(self):
        """測試成功設定 CORS 中間件。"""
        app = FastAPI()

        # 測試設定成功
        setup_cors_middleware(app)

        # 驗證中間件已添加
        assert len(app.user_middleware) > 0

        # 檢查是否有 CORS 中間件
        cors_middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware_found = True
                break

        assert cors_middleware_found

    def test_setup_cors_middleware_multiple_calls(self):
        """測試多次調用 setup_cors_middleware。"""
        app = FastAPI()

        # 第一次設定
        setup_cors_middleware(app)
        first_middleware_count = len(app.user_middleware)

        # 第二次設定
        setup_cors_middleware(app)
        second_middleware_count = len(app.user_middleware)

        # 驗證中間件數量增加
        assert second_middleware_count == first_middleware_count + 1

    def test_setup_cors_middleware_with_existing_middleware(self):
        """測試在已有中間件的應用程式上設定 CORS 中間件。"""
        app = FastAPI()

        # 添加其他中間件
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

        initial_middleware_count = len(app.user_middleware)

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 驗證中間件已添加
        assert len(app.user_middleware) == initial_middleware_count + 1

    def test_cors_middleware_configuration(self):
        """測試 CORS 中間件配置。"""
        app = FastAPI()
        setup_cors_middleware(app)

        # 找到 CORS 中間件
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware = middleware
                break

        assert cors_middleware is not None

        # 檢查中間件參數
        # 注意：這裡我們檢查中間件是否被正確添加，具體的配置參數
        # 在實際的 cors.py 文件中定義
        assert cors_middleware.kwargs is not None


class TestCorsMiddlewareIntegration:
    """CORS 中間件整合測試類別。"""

    def test_cors_headers_in_response(self):
        """測試 CORS 標頭是否正確出現在回應中。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加測試端點
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        # 建立測試客戶端
        client = TestClient(app)

        # 發送帶有 Origin 標頭的 GET 請求來測試 CORS
        response = client.get("/test", headers={"Origin": "http://localhost:3000"})

        # 檢查是否有 CORS 標頭
        assert "access-control-allow-origin" in response.headers
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )

    def test_cors_preflight_request(self):
        """測試 CORS 預檢請求。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加測試端點
        @app.post("/test")
        def test_endpoint():
            return {"message": "test"}

        # 建立測試客戶端
        client = TestClient(app)

        # 發送 OPTIONS 預檢請求
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # 檢查預檢回應
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_different_origins(self):
        """測試不同來源的 CORS 處理。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加測試端點
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        # 建立測試客戶端
        client = TestClient(app)

        # 測試允許的來源（根據 cors.py 中的配置）
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

        for origin in allowed_origins:
            response = client.get("/test", headers={"Origin": origin})
            assert "access-control-allow-origin" in response.headers
            assert response.headers["access-control-allow-origin"] == origin

        # 測試不允許的來源
        disallowed_origins = [
            "http://localhost:8080",
            "https://example.com",
            "https://app.example.com",
        ]

        for origin in disallowed_origins:
            response = client.get("/test", headers={"Origin": origin})
            # 不允許的來源不會有 access-control-allow-origin 標頭
            assert "access-control-allow-origin" not in response.headers

    def test_cors_different_methods(self):
        """測試不同 HTTP 方法的 CORS 處理。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加測試端點
        @app.get("/test")
        def test_get():
            return {"method": "GET"}

        @app.post("/test")
        def test_post():
            return {"method": "POST"}

        @app.put("/test")
        def test_put():
            return {"method": "PUT"}

        @app.delete("/test")
        def test_delete():
            return {"method": "DELETE"}

        # 建立測試客戶端
        client = TestClient(app)

        # 測試不同的 HTTP 方法
        methods = ["GET", "POST", "PUT", "DELETE"]
        for method in methods:
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
            elif method == "DELETE":
                response = client.delete(
                    "/test", headers={"Origin": "http://localhost:3000"}
                )

            assert "access-control-allow-origin" in response.headers
            assert (
                response.headers["access-control-allow-origin"]
                == "http://localhost:3000"
            )

    def test_cors_with_credentials(self):
        """測試帶有憑證的 CORS 請求。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加測試端點
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        # 建立測試客戶端
        client = TestClient(app)

        # 發送帶有憑證的請求
        response = client.get(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Cookie": "session=abc123",
            },
        )

        # 檢查 CORS 標頭
        assert "access-control-allow-origin" in response.headers
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )

    def test_cors_without_origin_header(self):
        """測試沒有 Origin 標頭的請求。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加測試端點
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        # 建立測試客戶端
        client = TestClient(app)

        # 發送沒有 Origin 標頭的請求
        response = client.get("/test")

        # 檢查回應（應該正常處理，但可能沒有 CORS 標頭）
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "test"

    def test_cors_error_handling(self):
        """測試 CORS 中間件與錯誤處理的整合。"""
        app = FastAPI()

        # 設定 CORS 中間件
        setup_cors_middleware(app)

        # 添加會拋出錯誤的端點
        @app.get("/test-error")
        def test_error_endpoint():
            raise HTTPException(status_code=400, detail="測試錯誤")

        # 建立測試客戶端
        client = TestClient(app)

        # 發送帶有 Origin 標頭的錯誤請求
        response = client.get(
            "/test-error", headers={"Origin": "http://localhost:3000"}
        )

        # 檢查錯誤回應仍然包含 CORS 標頭
        assert response.status_code == 400
        assert "access-control-allow-origin" in response.headers
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )
