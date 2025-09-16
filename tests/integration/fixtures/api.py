"""
API 相關的整合測試 Fixtures。

提供整合測試用的 API 客戶端和相關工具。
"""

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest  # 測試框架

from app.core.settings import Settings

# ===== 本地模組 =====
from app.factory import create_app


@pytest.fixture
def integration_app():
    """
    提供整合測試用的 FastAPI 應用程式。

    創建一個使用測試資料庫的應用程式實例，並確保資料庫表已創建。

    Returns:
        FastAPI: 整合測試用的應用程式實例
    """
    # 創建測試設定
    test_settings = Settings(
        testing=True,
        app_env="testing",
        sqlite_database=":memory:",
    )

    # 創建測試應用程式
    test_app = create_app(test_settings)

    # 建立模板引擎實例
    from app.factory import create_templates

    templates = create_templates(test_settings)
    test_app.state.templates = templates

    # 設定錯誤處理器
    from app.middleware.error_handler import setup_error_handlers

    setup_error_handlers(test_app)

    # 註冊路由
    from app.routers import api_router, health_router, main_router

    test_app.include_router(main_router)
    test_app.include_router(health_router)
    test_app.include_router(api_router)

    # 確保資料庫表已創建
    from app.models.database import Base, create_database_engine

    engine, _ = create_database_engine()
    Base.metadata.create_all(bind=engine)

    return test_app


@pytest.fixture
def integration_client(integration_app):
    """
    提供整合測試用的 API 客戶端。

    Args:
        integration_app: 整合測試用的 FastAPI 應用程式

    Returns:
        TestClient: 整合測試用的 API 客戶端
    """
    return TestClient(integration_app)


@pytest.fixture
def integration_client_with_cleanup(integration_app):
    """
    提供帶有自動清理功能的整合測試 API 客戶端。

    Args:
        integration_app: 整合測試用的 FastAPI 應用程式

    Yields:
        TestClient: 整合測試用的 API 客戶端
    """
    client = TestClient(integration_app)

    try:
        yield client
    finally:
        # 這裡可以添加清理邏輯，例如清理測試資料
        pass
