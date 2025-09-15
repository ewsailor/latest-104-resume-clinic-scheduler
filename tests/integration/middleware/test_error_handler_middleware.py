"""
錯誤處理中間件整合測試模組。

測試錯誤處理中間件的功能，包括異常捕獲、錯誤格式化等。
"""

# ===== 第三方套件 =====
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.errors import (
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    LivenessCheckError,
    ReadinessCheckError,
    ScheduleNotFoundError,
    ServiceUnavailableError,
    UserNotFoundError,
    ValidationError,
)
from app.middleware.error_handler import setup_error_handlers


class TestErrorHandlerMiddleware:
    """錯誤處理中間件整合測試類別。"""

    @pytest.fixture
    def app_with_error_handler(self):
        """建立包含錯誤處理中間件的測試應用程式。"""
        app = FastAPI()

        # 設定錯誤處理中間件
        setup_error_handlers(app)

        # 添加測試路由
        @app.get("/test/success")
        async def test_success():
            return {"message": "success"}

        @app.get("/test/generic-error")
        async def test_generic_error():
            raise Exception("Generic error message")

        @app.get("/test/http-exception")
        async def test_http_exception():
            raise HTTPException(status_code=400, detail="HTTP exception")

        @app.get("/test/validation-error")
        async def test_validation_error():
            raise ValidationError("Validation failed")

        @app.get("/test/authentication-error")
        async def test_authentication_error():
            raise AuthenticationError("Authentication failed")

        @app.get("/test/authorization-error")
        async def test_authorization_error():
            raise AuthorizationError("Authorization failed")

        @app.get("/test/business-logic-error")
        async def test_business_logic_error():
            raise BusinessLogicError("Business logic error")

        @app.get("/test/database-error")
        async def test_database_error():
            raise DatabaseError("Database connection failed")

        @app.get("/test/schedule-not-found-error")
        async def test_schedule_not_found_error():
            raise ScheduleNotFoundError("Schedule not found")

        @app.get("/test/user-not-found-error")
        async def test_user_not_found_error():
            raise UserNotFoundError("User not found")

        @app.get("/test/conflict-error")
        async def test_conflict_error():
            raise ConflictError("Resource conflict")

        @app.get("/test/service-unavailable-error")
        async def test_service_unavailable_error():
            raise ServiceUnavailableError("Service unavailable")

        @app.get("/test/liveness-check-error")
        async def test_liveness_check_error():
            raise LivenessCheckError("Liveness check failed")

        @app.get("/test/readiness-check-error")
        async def test_readiness_check_error():
            raise ReadinessCheckError("Readiness check failed")

        return app

    @pytest.fixture
    def client(self, app_with_error_handler):
        """建立測試客戶端。"""
        return TestClient(app_with_error_handler)

    def test_successful_request_not_affected(self, client):
        """測試成功請求不受錯誤處理中間件影響。"""
        response = client.get("/test/success")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "success"

    def test_generic_exception_handling(self, client):
        """測試通用異常處理。"""
        response = client.get("/test/generic-error")

        assert response.status_code == 500
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 500
        assert "Generic error message" in response_data["error"]["message"]

    def test_http_exception_handling(self, client):
        """測試 HTTP 異常處理。"""
        response = client.get("/test/http-exception")

        assert response.status_code == 400
        response_data = response.json()

        # FastAPI 的 HTTPException 被內建處理器處理，不會經過我們的錯誤處理中間件
        # 所以回應格式是 FastAPI 的標準格式
        assert "detail" in response_data
        assert response_data["detail"] == "HTTP exception"

    def test_validation_error_handling(self, client):
        """測試驗證錯誤處理。"""
        response = client.get("/test/validation-error")

        assert response.status_code == 422
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 422
        assert "Validation failed" in response_data["error"]["message"]

    def test_authentication_error_handling(self, client):
        """測試認證錯誤處理。"""
        response = client.get("/test/authentication-error")

        assert response.status_code == 401
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 401
        assert "Authentication failed" in response_data["error"]["message"]

    def test_authorization_error_handling(self, client):
        """測試授權錯誤處理。"""
        response = client.get("/test/authorization-error")

        assert response.status_code == 403
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 403
        assert "Authorization failed" in response_data["error"]["message"]

    def test_business_logic_error_handling(self, client):
        """測試業務邏輯錯誤處理。"""
        response = client.get("/test/business-logic-error")

        assert response.status_code == 400
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 400
        assert "Business logic error" in response_data["error"]["message"]

    def test_database_error_handling(self, client):
        """測試資料庫錯誤處理。"""
        response = client.get("/test/database-error")

        assert response.status_code == 500
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 500
        assert "Database connection failed" in response_data["error"]["message"]

    def test_schedule_not_found_error_handling(self, client):
        """測試排程未找到錯誤處理。"""
        response = client.get("/test/schedule-not-found-error")

        assert response.status_code == 404
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 404
        assert "Schedule not found" in response_data["error"]["message"]

    def test_user_not_found_error_handling(self, client):
        """測試使用者未找到錯誤處理。"""
        response = client.get("/test/user-not-found-error")

        assert response.status_code == 404
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 404
        assert "User not found" in response_data["error"]["message"]

    def test_conflict_error_handling(self, client):
        """測試衝突錯誤處理。"""
        response = client.get("/test/conflict-error")

        assert response.status_code == 409
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 409
        assert "Resource conflict" in response_data["error"]["message"]

    def test_service_unavailable_error_handling(self, client):
        """測試服務不可用錯誤處理。"""
        response = client.get("/test/service-unavailable-error")

        assert response.status_code == 503
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 503
        assert "Service unavailable" in response_data["error"]["message"]

    def test_liveness_check_error_handling(self, client):
        """測試存活檢查錯誤處理。"""
        response = client.get("/test/liveness-check-error")

        assert response.status_code == 500
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 500
        assert "Liveness check failed" in response_data["error"]["message"]

    def test_readiness_check_error_handling(self, client):
        """測試就緒檢查錯誤處理。"""
        response = client.get("/test/readiness-check-error")

        assert response.status_code == 503
        response_data = response.json()

        # 檢查錯誤回應結構
        assert "error" in response_data
        assert "message" in response_data["error"]
        assert "status_code" in response_data["error"]
        assert "timestamp" in response_data["error"]

        # 檢查錯誤內容
        assert response_data["error"]["status_code"] == 503
        assert "Readiness check failed" in response_data["error"]["message"]

    def test_error_response_timestamp_format(self, client):
        """測試錯誤回應中的時間戳格式。"""
        response = client.get("/test/generic-error")

        assert response.status_code == 500
        response_data = response.json()

        # 檢查時間戳格式
        timestamp = response_data["error"]["timestamp"]
        assert isinstance(timestamp, str)
        # 驗證時間戳格式：YYYY-MM-DDTHH:MM:SSZ
        import re

        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        assert re.match(timestamp_pattern, timestamp), f"時間戳格式不正確: {timestamp}"

    def test_error_response_consistency(self, client):
        """測試錯誤回應格式的一致性。"""
        error_endpoints = [
            "/test/validation-error",
            "/test/authentication-error",
            "/test/authorization-error",
            "/test/business-logic-error",
            "/test/database-error",
            "/test/schedule-not-found-error",
            "/test/user-not-found-error",
            "/test/conflict-error",
            "/test/service-unavailable-error",
        ]

        for endpoint in error_endpoints:
            response = client.get(endpoint)

            # 所有錯誤回應都應該有相同的結構
            assert response.status_code >= 400
            response_data = response.json()

            # 檢查錯誤回應結構
            assert "error" in response_data
            assert "message" in response_data["error"]
            assert "status_code" in response_data["error"]
            assert "timestamp" in response_data["error"]

            # 檢查狀態碼一致性
            assert response_data["error"]["status_code"] == response.status_code
