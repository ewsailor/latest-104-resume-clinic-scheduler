"""
應用程式工廠測試模組。

測試應用程式工廠模組的功能。
"""

# ===== 標準函式庫 =====
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.core.settings import Settings
from app.factory import create_app, create_static_files, create_templates


class TestCreateStaticFiles:
    """測試 create_static_files 函數。"""

    def test_create_static_files_success(self):
        """測試成功建立靜態檔案服務。"""
        # 準備測試資料
        mock_settings = Mock(spec=Settings)
        mock_settings.static_dir = Path("static")

        # 執行函數
        result = create_static_files(mock_settings)

        # 驗證結果
        assert isinstance(result, StaticFiles)
        assert result.directory == "static"

    def test_create_static_files_with_string_path(self):
        """測試使用字串路徑建立靜態檔案服務。"""
        # 準備測試資料
        mock_settings = Mock(spec=Settings)
        mock_settings.static_dir = "static"

        # 執行函數
        result = create_static_files(mock_settings)

        # 驗證結果
        assert isinstance(result, StaticFiles)
        assert result.directory == "static"


class TestCreateTemplates:
    """測試 create_templates 函數。"""

    def test_create_templates_success(self):
        """測試成功建立模板引擎。"""
        # 準備測試資料
        mock_settings = Mock(spec=Settings)
        mock_settings.templates_dir = Path("templates")

        # 執行函數
        result = create_templates(mock_settings)

        # 驗證結果
        assert isinstance(result, Jinja2Templates)
        assert hasattr(result, 'env')

    def test_create_templates_with_string_path(self):
        """測試使用字串路徑建立模板引擎。"""
        # 準備測試資料
        mock_settings = Mock(spec=Settings)
        mock_settings.templates_dir = "templates"

        # 執行函數
        result = create_templates(mock_settings)

        # 驗證結果
        assert isinstance(result, Jinja2Templates)
        assert hasattr(result, 'env')


class TestCreateApp:
    """測試 create_app 函數。"""

    @pytest.fixture
    def mock_settings_debug(self):
        """建立除錯模式的設定 mock。"""
        mock_settings = Mock(spec=Settings)
        mock_settings.debug = True
        mock_settings.app_name = "Test App"
        mock_settings.app_description = "Test Description"
        mock_settings.app_version = "1.0.0"
        mock_settings.docs_url = "/docs"
        mock_settings.redoc_url = "/redoc"
        mock_settings.openapi_url = "/openapi.json"
        mock_settings.server_url = "http://localhost:8000"
        mock_settings.server_description = "Development Server"
        mock_settings.app_env = "development"
        mock_settings.static_url = "/static"
        mock_settings.static_name = "static"
        mock_settings.static_dir = Path("static")
        return mock_settings

    @pytest.fixture
    def mock_settings_production(self):
        """建立生產模式的設定 mock。"""
        mock_settings = Mock(spec=Settings)
        mock_settings.debug = False
        mock_settings.app_name = "Test App"
        mock_settings.app_description = "Test Description"
        mock_settings.app_version = "1.0.0"
        mock_settings.docs_url = "/docs"
        mock_settings.redoc_url = "/redoc"
        mock_settings.openapi_url = "/openapi.json"
        mock_settings.server_url = "http://localhost:8000"
        mock_settings.server_description = "Development Server"
        mock_settings.app_env = "production"
        mock_settings.static_url = "/static"
        mock_settings.static_name = "static"
        mock_settings.static_dir = Path("static")
        return mock_settings

    @patch('app.factory.initialize_database')
    @patch('app.factory.setup_cors_middleware')
    @patch('app.factory.log_app_startup')
    @patch('app.factory.create_static_files')
    def test_create_app_debug_mode(
        self,
        mock_create_static_files,
        mock_log_app_startup,
        mock_setup_cors_middleware,
        mock_initialize_database,
        mock_settings_debug,
    ):
        """測試除錯模式下建立應用程式。"""
        # 準備 mock 回傳值
        mock_static_files = Mock(spec=StaticFiles)
        mock_create_static_files.return_value = mock_static_files

        # 執行函數
        result = create_app(mock_settings_debug)

        # 驗證結果
        assert isinstance(result, FastAPI)
        assert result.title == "Test App"
        assert result.description == "Test Description"
        assert result.version == "1.0.0"
        assert result.debug is True
        assert result.docs_url == "/docs"
        assert result.redoc_url == "/redoc"
        assert result.openapi_url == "/openapi.json"

        # 驗證伺服器設定
        assert len(result.servers) == 1
        assert result.servers[0]["url"] == "http://localhost:8000"
        assert result.servers[0]["description"] == "Development Server"

        # 驗證聯絡資訊
        assert result.contact["name"] == "鍾郡荃 Oscar"
        assert result.contact["email"] == "ew12136@gmail.com"

        # 驗證授權資訊
        assert result.license_info["name"] == "MIT License"
        assert result.license_info["url"] == "https://opensource.org/licenses/MIT"

        # 驗證函數被調用
        mock_log_app_startup.assert_called_once()
        mock_setup_cors_middleware.assert_called_once()
        mock_initialize_database.assert_called_once()
        mock_create_static_files.assert_called_once()

    @patch('app.factory.initialize_database')
    @patch('app.factory.setup_cors_middleware')
    @patch('app.factory.log_app_startup')
    @patch('app.factory.create_static_files')
    def test_create_app_production_mode(
        self,
        mock_create_static_files,
        mock_log_app_startup,
        mock_setup_cors_middleware,
        mock_initialize_database,
        mock_settings_production,
    ):
        """測試生產模式下建立應用程式。"""
        # 準備 mock 回傳值
        mock_static_files = Mock(spec=StaticFiles)
        mock_create_static_files.return_value = mock_static_files

        # 執行函數
        result = create_app(mock_settings_production)

        # 驗證結果
        assert isinstance(result, FastAPI)
        assert result.title == "Test App"
        assert result.description == "Test Description"
        assert result.version == "1.0.0"
        assert result.debug is False
        assert result.docs_url is None
        assert result.redoc_url is None
        assert result.openapi_url is None

        # 驗證伺服器設定（生產模式不應該有伺服器資訊）
        assert len(result.servers) == 0

        # 驗證函數被調用
        mock_log_app_startup.assert_called_once()
        mock_setup_cors_middleware.assert_called_once()
        mock_initialize_database.assert_called_once()
        mock_create_static_files.assert_called_once()

    @patch('app.factory.initialize_database')
    @patch('app.factory.setup_cors_middleware')
    @patch('app.factory.log_app_startup')
    @patch('app.factory.create_static_files')
    def test_create_app_development_environment(
        self,
        mock_create_static_files,
        mock_log_app_startup,
        mock_setup_cors_middleware,
        mock_initialize_database,
        mock_settings_debug,
    ):
        """測試開發環境下的應用程式建立。"""
        # 設定為開發環境
        mock_settings_debug.app_env = "development"

        # 準備 mock 回傳值
        mock_static_files = Mock(spec=StaticFiles)
        mock_create_static_files.return_value = mock_static_files

        # 執行函數
        result = create_app(mock_settings_debug)

        # 驗證結果
        assert isinstance(result, FastAPI)
        assert result.debug is True

        # 驗證伺服器設定
        assert len(result.servers) == 1
        assert result.servers[0]["url"] == "http://localhost:8000"
        assert result.servers[0]["description"] == "Development Server"

    @patch('app.factory.initialize_database')
    @patch('app.factory.setup_cors_middleware')
    @patch('app.factory.log_app_startup')
    @patch('app.factory.create_static_files')
    def test_create_app_error_handling(
        self,
        mock_create_static_files,
        mock_log_app_startup,
        mock_setup_cors_middleware,
        mock_initialize_database,
        mock_settings_debug,
    ):
        """測試應用程式建立時的錯誤處理。"""
        # 模擬 initialize_database 拋出異常
        mock_initialize_database.side_effect = Exception("資料庫初始化失敗")

        # 準備 mock 回傳值
        mock_static_files = Mock(spec=StaticFiles)
        mock_create_static_files.return_value = mock_static_files

        # 執行函數並驗證拋出異常
        with pytest.raises(Exception) as exc_info:
            create_app(mock_settings_debug)

        assert "資料庫初始化失敗" in str(exc_info.value)

        # 驗證其他函數仍然被調用
        mock_log_app_startup.assert_called_once()
        mock_setup_cors_middleware.assert_called_once()
        # 當 initialize_database 拋出異常時，create_static_files 不會被調用
        mock_create_static_files.assert_not_called()

    @patch('app.factory.initialize_database')
    @patch('app.factory.setup_cors_middleware')
    @patch('app.factory.log_app_startup')
    @patch('app.factory.create_static_files')
    def test_create_app_static_files_mounting(
        self,
        mock_create_static_files,
        mock_log_app_startup,
        mock_setup_cors_middleware,
        mock_initialize_database,
        mock_settings_debug,
    ):
        """測試靜態檔案掛載功能。"""
        # 準備 mock 回傳值
        mock_static_files = Mock(spec=StaticFiles)
        mock_create_static_files.return_value = mock_static_files

        # 執行函數
        result = create_app(mock_settings_debug)

        # 驗證結果
        assert isinstance(result, FastAPI)

        # 驗證 create_static_files 被正確調用
        mock_create_static_files.assert_called_once_with(mock_settings_debug)
