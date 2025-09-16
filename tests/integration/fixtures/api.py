"""
API 相關的整合測試 Fixtures。

提供整合測試用的 API 客戶端和相關工具。
"""

import os
import stat
import tempfile

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest  # 測試框架
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core.settings import Settings
from app.database import Base
import app.database.connection as db_module

# ===== 本地模組 =====
from app.factory import create_templates
from app.middleware.cors import setup_cors_middleware
from app.middleware.error_handler import setup_error_handlers
from app.routers import api_router, health_router, main_router


@pytest.fixture
def integration_app():
    """
    提供整合測試用的 FastAPI 應用程式。

    創建一個使用測試資料庫的應用程式實例，並確保資料庫表已創建。

    Returns:
        FastAPI: 整合測試用的應用程式實例
    """
    # 設定環境變數以確保使用測試設定（在創建應用程式之前）
    original_testing = os.environ.get("TESTING")
    original_app_env = os.environ.get("APP_ENV")
    original_sqlite_db = os.environ.get("SQLITE_DATABASE")

    try:
        # 創建測試設定（使用檔案資料庫而不是記憶體資料庫）
        # 在 CI 環境中使用 /tmp 目錄確保寫入權限
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(
            temp_dir, f"test_db_{os.getpid()}_{id(tempfile)}.db"
        )

        # 創建空檔案
        with open(temp_db_path, 'w') as f:
            pass

        # 確保檔案有寫入權限（在 Linux 環境下很重要）
        os.chmod(
            temp_db_path,
            stat.S_IRUSR
            | stat.S_IWUSR
            | stat.S_IRGRP
            | stat.S_IWGRP
            | stat.S_IROTH
            | stat.S_IWOTH,
        )

        os.environ["TESTING"] = "true"
        os.environ["APP_ENV"] = "testing"
        os.environ["SQLITE_DATABASE"] = temp_db_path

        test_settings = Settings(
            testing=True,
            app_env="testing",
            sqlite_database=temp_db_path,
        )

        # 創建測試應用程式（不調用 initialize_database）
        # 根據環境決定是否顯示 API 文件
        docs_url = test_settings.docs_url if test_settings.debug else None
        redoc_url = test_settings.redoc_url if test_settings.debug else None
        openapi_url = test_settings.openapi_url if test_settings.debug else None

        # 建立 FastAPI 應用程式
        test_app = FastAPI(
            title=test_settings.app_name,
            description=test_settings.app_description,
            version=test_settings.app_version,
            debug=test_settings.debug,
            docs_url=docs_url,
            redoc_url=redoc_url,
            openapi_url=openapi_url,
            contact={
                "name": "鍾郡荃 Oscar",
                "email": "ew12136@gmail.com",
            },
            license_info={
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT",
            },
        )

        # 設定 CORS 中間件
        setup_cors_middleware(test_app)

        # 掛載靜態檔案服務
        static_files = StaticFiles(directory=str(test_settings.static_dir))
        test_app.mount(
            test_settings.static_url, static_files, name=test_settings.static_name
        )

        # 建立模板引擎實例
        templates = create_templates(test_settings)
        test_app.state.templates = templates

        # 設定錯誤處理器
        setup_error_handlers(test_app)

        # 註冊路由
        test_app.include_router(main_router)
        test_app.include_router(health_router)
        test_app.include_router(api_router)

        # 手動初始化資料庫（使用測試設定）
        # 創建測試資料庫引擎
        test_engine = create_engine(
            test_settings.sqlite_connection_string,
            echo=False,
            pool_pre_ping=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
            },
        )

        # 創建會話工廠
        test_session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=test_engine
        )

        # 導入所有模型以確保 Base.metadata 包含所有表
        # 創建資料庫表
        Base.metadata.create_all(bind=test_engine)

        # 驗證表是否被創建
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()
        assert "users" in tables, f"users table not found in {tables}"
        assert "schedules" in tables, f"schedules table not found in {tables}"

        # 設定全域變數（用於 get_db 函數）
        db_module.engine = test_engine
        db_module.SessionLocal = test_session_local

        # 驗證全域變數是否正確設定
        assert db_module.engine is test_engine, "Global engine not set correctly"

        return test_app

    finally:
        # 清理臨時資料庫檔案
        try:
            if 'temp_db_path' in locals():
                os.unlink(temp_db_path)
        except Exception:
            pass

        # 恢復原始環境變數
        if original_testing is not None:
            os.environ["TESTING"] = original_testing
        elif "TESTING" in os.environ:
            del os.environ["TESTING"]

        if original_app_env is not None:
            os.environ["APP_ENV"] = original_app_env
        elif "APP_ENV" in os.environ:
            del os.environ["APP_ENV"]

        if original_sqlite_db is not None:
            os.environ["SQLITE_DATABASE"] = original_sqlite_db
        elif "SQLITE_DATABASE" in os.environ:
            del os.environ["SQLITE_DATABASE"]


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
