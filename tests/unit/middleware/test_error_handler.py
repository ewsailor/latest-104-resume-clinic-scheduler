"""
錯誤處理中間件測試模組。

測試錯誤處理中間件的功能。
"""

# ===== 標準函式庫 =====
from unittest.mock import AsyncMock, MagicMock, patch

# ===== 第三方套件 =====
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
import pytest
from starlette.responses import JSONResponse

# ===== 本地模組 =====
from app.errors.exceptions import (
    APIError,
    AuthenticationError,
    BusinessLogicError,
    ValidationError,
)
from app.middleware.error_handler import ErrorHandlerMiddleware, setup_error_handlers


class TestErrorHandlerMiddleware:
    """ErrorHandlerMiddleware 測試。"""

    def test_error_handler_middleware_initialization(self):
        """測試錯誤處理中間件初始化。"""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        assert middleware.app == app

    @patch('app.middleware.error_handler.format_error_response')
    @patch('app.middleware.error_handler.logger')
    @pytest.mark.asyncio
    async def test_dispatch_success(self, mock_logger, mock_format_error):
        """測試正常請求處理。"""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        # 模擬正常回應
        expected_response = Response(content="success", status_code=200)
        mock_call_next = AsyncMock(return_value=expected_response)

        # 模擬請求
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        # 執行 dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # 驗證結果
        assert result == expected_response
        mock_call_next.assert_called_once_with(mock_request)
        mock_format_error.assert_not_called()
        mock_logger.error.assert_not_called()

    @patch('app.middleware.error_handler.format_error_response')
    @patch('app.middleware.error_handler.logger')
    @pytest.mark.asyncio
    async def test_dispatch_with_api_error(self, mock_logger, mock_format_error):
        """測試處理 APIError。"""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        # 模擬 APIError
        api_error = ValidationError("驗證失敗", {"field": "email"})
        mock_call_next = AsyncMock(side_effect=api_error)

        # 模擬格式化錯誤回應
        mock_format_error.return_value = {
            "error": {
                "message": "驗證失敗",
                "status_code": 422,
                "code": "ROUTER_VALIDATION_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"field": "email"},
            }
        }

        # 模擬請求
        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"

        # 執行 dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # 驗證結果
        assert isinstance(result, JSONResponse)
        assert result.status_code == 422
        assert (
            result.body.decode()
            == '{"error":{"message":"驗證失敗","status_code":422,"code":"ROUTER_VALIDATION_ERROR","timestamp":"2024-01-01T00:00:00Z","details":{"field":"email"}}}'
        )

        # 驗證日誌記錄
        mock_logger.error.assert_called_once_with("錯誤: POST /api/test - 驗證失敗")
        mock_format_error.assert_called_once_with(api_error)

    @patch('app.middleware.error_handler.format_error_response')
    @patch('app.middleware.error_handler.logger')
    @pytest.mark.asyncio
    async def test_dispatch_with_http_exception(self, mock_logger, mock_format_error):
        """測試處理 HTTPException。"""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        # 模擬 HTTPException
        http_error = HTTPException(status_code=404, detail="Not Found")
        mock_call_next = AsyncMock(side_effect=http_error)

        # 模擬格式化錯誤回應
        mock_format_error.return_value = {
            "error": {
                "message": "Not Found",
                "status_code": 404,
                "code": "HTTP_404",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"detail": "Not Found"},
            }
        }

        # 模擬請求
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/api/missing"

        # 執行 dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # 驗證結果
        assert isinstance(result, JSONResponse)
        assert result.status_code == 404
        assert (
            result.body.decode()
            == '{"error":{"message":"Not Found","status_code":404,"code":"HTTP_404","timestamp":"2024-01-01T00:00:00Z","details":{"detail":"Not Found"}}}'
        )

        # 驗證日誌記錄（HTTPException 的 str() 包含狀態碼）
        mock_logger.error.assert_called_once_with(
            "錯誤: GET /api/missing - 404: Not Found"
        )

    @patch('app.middleware.error_handler.format_error_response')
    @patch('app.middleware.error_handler.logger')
    @pytest.mark.asyncio
    async def test_dispatch_with_generic_exception(
        self, mock_logger, mock_format_error
    ):
        """測試處理一般異常。"""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        # 模擬一般異常
        generic_error = ValueError("一般錯誤")
        mock_call_next = AsyncMock(side_effect=generic_error)

        # 模擬格式化錯誤回應
        mock_format_error.return_value = {
            "error": {
                "message": "一般錯誤",
                "status_code": 500,
                "code": "INTERNAL_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"error": "一般錯誤"},
            }
        }

        # 模擬請求
        mock_request = MagicMock(spec=Request)
        mock_request.method = "PUT"
        mock_request.url.path = "/api/update"

        # 執行 dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # 驗證結果
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        assert (
            result.body.decode()
            == '{"error":{"message":"一般錯誤","status_code":500,"code":"INTERNAL_ERROR","timestamp":"2024-01-01T00:00:00Z","details":{"error":"一般錯誤"}}}'
        )

        # 驗證日誌記錄
        mock_logger.error.assert_called_once_with("錯誤: PUT /api/update - 一般錯誤")

    @patch('app.middleware.error_handler.format_error_response')
    @patch('app.middleware.error_handler.logger')
    @pytest.mark.asyncio
    async def test_handle_exception_different_error_types(
        self, mock_logger, mock_format_error
    ):
        """測試處理不同類型的錯誤。"""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        # 測試不同類型的錯誤
        test_cases = [
            (AuthenticationError("認證失敗"), 401, "認證失敗"),
            (BusinessLogicError("業務邏輯錯誤"), 400, "業務邏輯錯誤"),
            (HTTPException(status_code=403, detail="Forbidden"), 403, "403: Forbidden"),
            (RuntimeError("運行時錯誤"), 500, "運行時錯誤"),
        ]

        for error, expected_status, expected_message in test_cases:
            # 重置 mock
            mock_format_error.reset_mock()
            mock_logger.reset_mock()

            # 模擬格式化錯誤回應
            mock_format_error.return_value = {
                "error": {
                    "message": expected_message,
                    "status_code": expected_status,
                    "code": f"TEST_{expected_status}",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "details": {},
                }
            }

            # 模擬請求
            mock_request = MagicMock(spec=Request)
            mock_request.method = "POST"
            mock_request.url.path = "/test"

            # 執行 _handle_exception
            result = await middleware._handle_exception(mock_request, error)

            # 驗證結果
            assert isinstance(result, JSONResponse)
            assert result.status_code == expected_status
            mock_format_error.assert_called_once_with(error)
            mock_logger.error.assert_called_once_with(
                f"錯誤: POST /test - {expected_message}"
            )

    @patch('app.middleware.error_handler.format_error_response')
    @patch('app.middleware.error_handler.logger')
    @pytest.mark.asyncio
    async def test_handle_exception_with_complex_error(
        self, mock_logger, mock_format_error
    ):
        """測試處理複雜錯誤。"""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        # 模擬複雜錯誤
        complex_error = APIError(
            "複雜錯誤",
            "COMPLEX_ERROR",
            422,
            {"field": "email", "errors": ["格式不正確", "長度不足"]},
        )

        # 模擬格式化錯誤回應
        mock_format_error.return_value = {
            "error": {
                "message": "複雜錯誤",
                "status_code": 422,
                "code": "COMPLEX_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"field": "email", "errors": ["格式不正確", "長度不足"]},
            }
        }

        # 模擬請求
        mock_request = MagicMock(spec=Request)
        mock_request.method = "PATCH"
        mock_request.url.path = "/api/complex"

        # 執行 _handle_exception
        result = await middleware._handle_exception(mock_request, complex_error)

        # 驗證結果
        assert isinstance(result, JSONResponse)
        assert result.status_code == 422

        # 驗證回應內容
        response_data = result.body.decode()
        assert "複雜錯誤" in response_data
        assert "COMPLEX_ERROR" in response_data
        assert "格式不正確" in response_data
        assert "長度不足" in response_data

        # 驗證日誌記錄
        mock_logger.error.assert_called_once_with("錯誤: PATCH /api/complex - 複雜錯誤")


class TestSetupErrorHandlers:
    """setup_error_handlers 函數測試。"""

    def test_setup_error_handlers_success(self):
        """測試成功設定錯誤處理器。"""
        app = FastAPI()

        # 記錄初始中間件數量
        initial_middleware_count = len(app.user_middleware)

        # 設定錯誤處理器
        setup_error_handlers(app)

        # 驗證中間件已添加
        assert len(app.user_middleware) == initial_middleware_count + 1

        # 檢查是否有 ErrorHandlerMiddleware
        error_middleware_found = False
        for middleware in app.user_middleware:
            if "ErrorHandlerMiddleware" in str(middleware.cls):
                error_middleware_found = True
                break

        assert error_middleware_found

    def test_setup_error_handlers_multiple_calls(self):
        """測試多次調用 setup_error_handlers。"""
        app = FastAPI()

        # 第一次設定
        setup_error_handlers(app)
        first_middleware_count = len(app.user_middleware)

        # 第二次設定
        setup_error_handlers(app)
        second_middleware_count = len(app.user_middleware)

        # 驗證中間件數量增加
        assert second_middleware_count == first_middleware_count + 1

    def test_setup_error_handlers_with_existing_middleware(self):
        """測試在已有中間件的應用程式上設定錯誤處理器。"""
        app = FastAPI()

        # 添加其他中間件
        app.add_middleware(CORSMiddleware, allow_origins=["*"])

        initial_middleware_count = len(app.user_middleware)

        # 設定錯誤處理器
        setup_error_handlers(app)

        # 驗證中間件已添加
        assert len(app.user_middleware) == initial_middleware_count + 1


class TestErrorHandlerMiddlewareIntegration:
    """錯誤處理中間件整合測試。"""

    def test_error_handler_integration_with_fastapi(self):
        """測試錯誤處理中間件與 FastAPI 的整合。"""
        app = FastAPI()

        # 設定錯誤處理器
        setup_error_handlers(app)

        # 添加會拋出錯誤的端點
        @app.get("/test-error")
        def test_error_endpoint():
            raise ValidationError("測試驗證錯誤", {"field": "test"})

        @app.get("/test-http-error")
        def test_http_error_endpoint():
            raise HTTPException(status_code=404, detail="測試 HTTP 錯誤")

        @app.get("/test-generic-error")
        def test_generic_error_endpoint():
            raise RuntimeError("測試一般錯誤")

        # 建立測試客戶端
        client = TestClient(app)

        # 測試 ValidationError
        response = client.get("/test-error")
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["message"] == "測試驗證錯誤"
        assert data["error"]["code"] == "ROUTER_VALIDATION_ERROR"

        # 測試 HTTPException（可能被 FastAPI 內建處理器處理）
        response = client.get("/test-http-error")
        assert response.status_code == 404
        data = response.json()
        # HTTPException 可能被 FastAPI 內建處理器處理，所以格式可能不同
        if "error" in data:
            assert data["error"]["message"] == "測試 HTTP 錯誤"
        else:
            # FastAPI 內建處理器的格式
            assert "detail" in data
            assert data["detail"] == "測試 HTTP 錯誤"

        # 測試一般錯誤
        response = client.get("/test-generic-error")
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["message"] == "測試一般錯誤"

    def test_error_handler_preserves_successful_responses(self):
        """測試錯誤處理器不影響正常回應。"""
        app = FastAPI()

        # 設定錯誤處理器
        setup_error_handlers(app)

        # 添加正常端點
        @app.get("/test-success")
        def test_success_endpoint():
            return {"message": "成功", "status": "ok"}

        # 建立測試客戶端
        client = TestClient(app)

        # 測試正常回應
        response = client.get("/test-success")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "成功"
        assert data["status"] == "ok"

    def test_error_handler_with_different_http_methods(self):
        """測試錯誤處理器處理不同 HTTP 方法。"""
        app = FastAPI()

        # 設定錯誤處理器
        setup_error_handlers(app)

        # 添加會拋出錯誤的端點
        @app.post("/test-post")
        def test_post_error():
            raise BusinessLogicError("POST 錯誤")

        @app.get("/test-get")
        def test_get_error():
            raise BusinessLogicError("GET 錯誤")

        @app.patch("/test-patch")
        def test_patch_error():
            raise BusinessLogicError("PATCH 錯誤")

        @app.delete("/test-delete")
        def test_delete_error():
            raise BusinessLogicError("DELETE 錯誤")

        # 建立測試客戶端
        client = TestClient(app)

        # 測試不同方法的錯誤處理
        methods_and_endpoints = [
            ("POST", "/test-post"),
            ("GET", "/test-get"),
            ("PATCH", "/test-patch"),
            ("DELETE", "/test-delete"),
        ]

        for method, endpoint in methods_and_endpoints:
            match method:
                case "POST":
                    response = client.post(endpoint)
                case "GET":
                    response = client.get(endpoint)
                case "PATCH":
                    response = client.patch(endpoint)
                case "DELETE":
                    response = client.delete(endpoint)

            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert data["error"]["message"] == f"{method} 錯誤"
