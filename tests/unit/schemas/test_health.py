"""健康檢查 Schema 單元測試模組。

測試健康檢查相關的 Pydantic 資料模型。
"""

# ===== 第三方套件 =====
from pydantic import ValidationError
import pytest

# ===== 本地模組 =====
from app.schemas import (
    HealthCheckBase,
    HealthCheckLivenessResponse,
    HealthCheckReadinessResponse,
)


class TestHealthCheckBase:
    """HealthCheckBase 模型測試類別。"""

    def test_health_check_base_creation_success(self):
        """測試 HealthCheckBase 抽象類別不能直接實例化。"""
        # HealthCheckBase 現在是抽象類別，不能直接實例化
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            HealthCheckBase(
                status="healthy",
                app_name="【MVP】104 Resume Clinic Scheduler",
                version="0.1.0",
                timestamp="2024-01-01T00:00:00Z",
                checks={
                    "application": "healthy",
                },
            )


class TestHealthCheckLivenessResponse:
    """HealthCheckLivenessResponse 模型測試類別。"""

    def test_health_check_liveness_response_creation_success(self):
        """測試 HealthCheckLivenessResponse 成功建立。"""
        response = HealthCheckLivenessResponse(
            message="應用程式存活、正常運行",
            status="healthy",
            app_name="【MVP】104 Resume Clinic Scheduler",
            version="0.1.0",
            timestamp="2024-01-01T00:00:00Z",
            checks={
                "application": "healthy",
            },
        )

        assert response.message == "應用程式存活、正常運行"
        assert response.status == "healthy"
        assert response.app_name == "【MVP】104 Resume Clinic Scheduler"
        assert response.version == "0.1.0"
        assert response.timestamp == "2024-01-01T00:00:00Z"
        assert response.checks == {
            "application": "healthy",
        }

    def test_health_check_liveness_response_validation_message_required(self):
        """測試 HealthCheckLivenessResponse message 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            HealthCheckLivenessResponse(
                status="healthy",
                app_name="Test App",
                version="1.0.0",
                timestamp="2024-01-01T00:00:00Z",
                checks={"application": "healthy"},
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "message" in str(error["loc"])
            for error in errors
        )

    def test_health_check_liveness_response_model_dump(self):
        """測試 HealthCheckLivenessResponse 模型轉換為字典。"""
        response = HealthCheckLivenessResponse(
            message="應用程式存活、正常運行",
            status="healthy",
            app_name="Test App",
            version="1.0.0",
            timestamp="2024-01-01T00:00:00Z",
            checks={"application": "healthy"},
        )

        data = response.model_dump()
        assert isinstance(data, dict)
        assert data["message"] == "應用程式存活、正常運行"
        assert data["status"] == "healthy"
        assert data["app_name"] == "Test App"
        assert data["version"] == "1.0.0"
        assert data["timestamp"] == "2024-01-01T00:00:00Z"
        assert data["checks"] == {"application": "healthy"}


class TestHealthCheckReadinessResponse:
    """HealthCheckReadinessResponse 模型測試類別。"""

    def test_health_check_readiness_response_creation_success(self):
        """測試 HealthCheckReadinessResponse 成功建立。"""
        response = HealthCheckReadinessResponse(
            message="應用程式準備就緒",
            status="healthy",
            app_name="【MVP】104 Resume Clinic Scheduler",
            version="0.1.0",
            timestamp="2024-01-01T00:00:00Z",
            checks={
                "application": "healthy",
                "database": "healthy",
            },
        )

        assert response.message == "應用程式準備就緒"
        assert response.status == "healthy"
        assert response.app_name == "【MVP】104 Resume Clinic Scheduler"
        assert response.version == "0.1.0"
        assert response.timestamp == "2024-01-01T00:00:00Z"
        assert response.checks == {
            "application": "healthy",
            "database": "healthy",
        }

    def test_health_check_readiness_response_validation_message_required(self):
        """測試 HealthCheckReadinessResponse message 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            HealthCheckReadinessResponse(
                status="healthy",
                app_name="Test App",
                version="1.0.0",
                timestamp="2024-01-01T00:00:00Z",
                checks={"application": "healthy"},
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "message" in str(error["loc"])
            for error in errors
        )

    def test_health_check_readiness_response_validation_status_required(self):
        """測試 HealthCheckReadinessResponse status 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            HealthCheckReadinessResponse(
                message="Test message",
                app_name="Test App",
                version="1.0.0",
                timestamp="2024-01-01T00:00:00Z",
                checks={"application": "healthy"},
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "status" in str(error["loc"])
            for error in errors
        )

    def test_health_check_readiness_response_model_dump(self):
        """測試 HealthCheckReadinessResponse 模型轉換為字典。"""
        response = HealthCheckReadinessResponse(
            message="應用程式準備就緒",
            status="healthy",
            app_name="Test App",
            version="1.0.0",
            timestamp="2024-01-01T00:00:00Z",
            checks={"application": "healthy"},
        )

        data = response.model_dump()
        assert isinstance(data, dict)
        assert data["message"] == "應用程式準備就緒"
        assert data["status"] == "healthy"
        assert data["app_name"] == "Test App"
        assert data["version"] == "1.0.0"
        assert data["timestamp"] == "2024-01-01T00:00:00Z"
        assert data["checks"] == {"application": "healthy"}
