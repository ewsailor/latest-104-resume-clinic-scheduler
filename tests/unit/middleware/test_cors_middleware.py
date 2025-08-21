#!/usr/bin/env python3
"""
CORS 中間件測試模組。

測試 CORS 中間件的各種功能和安全性。
"""

from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.core.settings import Settings
from app.middleware.cors import (
    get_cors_config_summary,
    get_cors_headers,
    get_cors_methods,
    get_cors_origins_by_environment,
    setup_cors_middleware,
    validate_cors_origins,
)


class TestCorsMiddleware:
    """CORS 中間件測試類別。"""

    def setup_method(self):
        """每個測試方法前的設定。"""
        self.settings = Mock(spec=Settings)
        # 設定必要的屬性以避免 AttributeError
        self.settings.app_env = "development"
        self.settings.cors_origins_list = ["http://localhost:8000"]

    def test_get_cors_origins_development(self):
        """測試開發環境的 CORS 來源設定。"""
        self.settings.is_development = True
        self.settings.is_staging = False
        self.settings.is_production = False
        self.settings.cors_origins = "http://localhost:8000"

        origins = get_cors_origins_by_environment(self.settings)

        expected_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

        assert origins == expected_origins

    def test_get_cors_origins_production(self):
        """測試生產環境的 CORS 來源設定。"""
        self.settings.is_development = False
        self.settings.is_staging = False
        self.settings.is_production = True
        self.settings.cors_origins = "http://localhost:8000"
        self.settings.app_env = "production"

        origins = get_cors_origins_by_environment(self.settings)

        expected_origins = ["https://www.104.com.tw", "https://api.104.com.tw"]

        assert origins == expected_origins

    def test_get_cors_origins_custom(self):
        """測試自定義 CORS 來源設定。"""
        self.settings.is_development = True
        self.settings.is_staging = False
        self.settings.is_production = False
        self.settings.cors_origins = "https://custom.com,https://api.custom.com"
        self.settings.cors_origins_list = [
            "https://custom.com",
            "https://api.custom.com",
        ]
        self.settings.app_env = "development"

        origins = get_cors_origins_by_environment(self.settings)

        expected_origins = ["https://custom.com", "https://api.custom.com"]
        assert origins == expected_origins

    def test_validate_cors_origins_valid(self):
        """測試有效的 CORS 來源驗證。"""
        origins = [
            "http://localhost:3000",
            "https://api.example.com",
            "http://127.0.0.1:8000",
        ]

        validated = validate_cors_origins(origins)

        assert validated == origins
        assert len(validated) == 3

    def test_validate_cors_origins_invalid(self):
        """測試無效的 CORS 來源驗證。"""
        origins = [
            "http://localhost:3000",
            "",  # 空字串
            "invalid-url",  # 無效格式
            "http://localhost:3000",  # 重複
            "https://api.example.com",
        ]

        validated = validate_cors_origins(origins)

        expected = ["http://localhost:3000", "https://api.example.com"]
        assert validated == expected
        assert len(validated) == 2

    def test_get_cors_methods(self):
        """測試取得 CORS 方法列表。"""
        methods = get_cors_methods()

        expected_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        assert methods == expected_methods
        assert len(methods) == 6

    def test_get_cors_headers(self):
        """測試取得 CORS 標頭列表。"""
        headers = get_cors_headers()

        expected_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
        ]
        assert headers == expected_headers
        assert len(headers) == 7

    def test_setup_cors_middleware_success(self):
        """測試成功設定 CORS 中間件。"""
        app = FastAPI()
        self.settings.is_development = True
        self.settings.is_staging = False
        self.settings.is_production = False
        self.settings.cors_origins = "http://localhost:8000"
        self.settings.app_env = "development"

        # 測試設定成功
        setup_cors_middleware(app, self.settings)

        # 驗證中間件已添加
        assert len(app.user_middleware) > 0

        # 檢查是否有 CORS 中間件
        cors_middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware_found = True
                break

        assert cors_middleware_found

    def test_setup_cors_middleware_no_valid_origins(self):
        """測試沒有有效來源時的 CORS 中間件設定。"""
        app = FastAPI()
        self.settings.is_development = False
        self.settings.is_staging = False
        self.settings.is_production = False
        self.settings.cors_origins = ""
        self.settings.cors_origins_list = []
        self.settings.app_env = "unknown"

        # 測試設定（即使沒有自定義來源，也會使用預設來源）
        setup_cors_middleware(app, self.settings)

        # 驗證中間件已添加（因為有預設來源）
        assert len(app.user_middleware) > 0

        # 檢查是否有 CORS 中間件
        cors_middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware_found = True
                break

        assert cors_middleware_found

    def test_get_cors_config_summary(self):
        """測試取得 CORS 配置摘要。"""
        self.settings.is_development = True
        self.settings.is_staging = False
        self.settings.is_production = False
        self.settings.cors_origins = "http://localhost:8000"
        self.settings.app_env = "development"

        summary = get_cors_config_summary(self.settings)

        assert summary["environment"] == "development"
        assert summary["total_origins"] == 4
        assert "http://localhost:3000" in summary["origins"]
        assert len(summary["methods"]) == 6
        assert len(summary["headers"]) == 7
        assert summary["max_age"] == 3600
        assert summary["allow_credentials"] is True


class TestCorsMiddlewareIntegration:
    """CORS 中間件整合測試類別。"""

    def test_cors_headers_in_response(self):
        """測試 CORS 標頭是否正確出現在回應中。"""
        app = FastAPI()

        # 模擬設定
        settings = Mock(spec=Settings)
        settings.is_development = True
        settings.is_staging = False
        settings.is_production = False
        settings.cors_origins = "http://localhost:8000"
        settings.app_env = "development"
        settings.cors_origins_list = ["http://localhost:8000"]

        # 設定 CORS 中間件
        setup_cors_middleware(app, settings)

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


if __name__ == "__main__":
    pytest.main([__file__])
