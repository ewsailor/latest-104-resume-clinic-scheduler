"""
主路由測試。

測試主路由模組的功能。
"""

import inspect
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient

# ===== 標準函式庫 =====
import pytest

# ===== 本地模組 =====
from app.routers.main import router, show_index

# ===== 測試設定 =====


class TestMainRouter:
    """主路由測試類別。"""

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

    def test_show_index_success(self, client, app):
        """測試首頁路由成功情況。"""
        # 模擬應用程式狀態中的模板
        mock_templates = Mock()
        mock_template_response = HTMLResponse(
            content="<html><body>測試頁面</body></html>", status_code=200
        )
        mock_templates.TemplateResponse.return_value = mock_template_response

        # 設置應用程式狀態
        app.state.templates = mock_templates

        # 發送請求
        response = client.get("/")

        # 驗證回應
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        # 驗證模板被正確調用
        mock_templates.TemplateResponse.assert_called_once()

    def test_show_index_with_templates_not_configured(self, client):
        """測試模板未配置時的情況。"""
        # 不設置模板，應該會拋出異常
        with pytest.raises(AttributeError):
            client.get("/")

    def test_show_index_template_response_error(self, client, app):
        """測試模板回應錯誤的情況。"""
        # 模擬模板回應拋出異常
        mock_templates = Mock()
        mock_templates.TemplateResponse.side_effect = Exception("模板錯誤")

        # 設置應用程式狀態
        app.state.templates = mock_templates

        # 發送請求，應該會拋出異常
        with pytest.raises(Exception, match="模板錯誤"):
            client.get("/")

    def test_show_index_route_metadata(self):
        """測試路由元資料。"""
        # 驗證路由配置
        assert len(router.routes) == 1

        # 驗證路由路徑
        route = router.routes[0]
        assert route.path == "/"
        assert "GET" in route.methods

    def test_show_index_with_different_request_objects(self, client, app):
        """測試不同請求物件的情況。"""
        # 模擬模板系統
        mock_templates = Mock()
        mock_template_response = HTMLResponse(
            content="<html><body>測試頁面</body></html>", status_code=200
        )
        mock_templates.TemplateResponse.return_value = mock_template_response

        # 設置應用程式狀態
        app.state.templates = mock_templates

        # 第一次請求
        response1 = client.get("/")
        assert response1.status_code == 200

        # 第二次請求
        response2 = client.get("/")
        assert response2.status_code == 200

        # 驗證模板被調用了兩次
        assert mock_templates.TemplateResponse.call_count == 2

    def test_show_index_template_name(self, client, app):
        """測試模板名稱。"""
        # 模擬模板系統
        mock_templates = Mock()
        mock_template_response = HTMLResponse(
            content="<html><body>測試頁面</body></html>", status_code=200
        )
        mock_templates.TemplateResponse.return_value = mock_template_response

        # 設置應用程式狀態
        app.state.templates = mock_templates

        # 發送請求
        client.get("/")

        # 驗證模板被正確調用
        mock_templates.TemplateResponse.assert_called_once()

    def test_show_index_response_type(self, client, app):
        """測試回應類型。"""
        # 模擬模板系統
        mock_templates = Mock()
        mock_template_response = HTMLResponse(
            content="<html><body>測試頁面</body></html>", status_code=200
        )
        mock_templates.TemplateResponse.return_value = mock_template_response

        # 設置應用程式狀態
        app.state.templates = mock_templates

        # 發送請求
        response = client.get("/")

        # 驗證回應類型
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

    def test_show_index_function_signature(self):
        """測試首頁函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(show_index)
        params = list(sig.parameters.keys())

        assert params == ["request"]
        assert sig.return_annotation == HTMLResponse

    def test_show_index_is_async(self):
        """測試首頁函數是非同步函數。"""
        assert inspect.iscoroutinefunction(show_index)

    def test_router_configuration(self):
        """測試路由器配置。"""
        # 驗證路由器基本配置
        assert router.prefix == ""
        assert router.tags == []
        assert len(router.routes) == 1

    def test_route_paths(self):
        """測試路由路徑。"""
        # 收集所有路由路徑
        paths = [route.path for route in router.routes]

        # 驗證所有預期的路徑都存在
        expected_paths = ["/"]

        for expected_path in expected_paths:
            assert expected_path in paths

    def test_route_methods(self):
        """測試路由方法。"""
        # 收集所有路由方法
        routes_info = [(route.path, route.methods) for route in router.routes]

        # 驗證方法配置
        expected_routes = [
            ("/", {"GET"}),
        ]

        for expected_path, expected_methods in expected_routes:
            found = False
            for path, methods in routes_info:
                if path == expected_path and expected_methods.issubset(methods):
                    found = True
                    break
            assert (
                found
            ), f"Route {expected_path} with methods {expected_methods} not found"
