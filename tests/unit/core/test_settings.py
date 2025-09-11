"""
設定管理模組測試。

測試 Settings 類別和 get_project_version 函數的功能。
"""

# ===== 標準函式庫 =====
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from pydantic import ValidationError

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.core.settings import Settings, get_project_version


class TestGetProjectVersion:
    """get_project_version 函數測試類別。"""

    def test_get_project_version_success(self):
        """測試成功讀取專案版本號。"""
        # 創建臨時 pyproject.toml 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(
                """
[tool.poetry]
name = "test-project"
version = "1.2.3"
"""
            )
            temp_path = f.name

        try:
            # Mock pyproject.toml 路徑
            with patch('app.core.settings.Path') as mock_path:
                mock_path.return_value.parent.parent.parent.__truediv__.return_value = (
                    Path(temp_path)
                )

                version = get_project_version()
                assert version == "1.2.3"
        finally:
            os.unlink(temp_path)

    def test_get_project_version_file_not_found(self):
        """測試 pyproject.toml 文件不存在的情況。"""
        with patch('app.core.settings.Path') as mock_path:
            mock_path.return_value.parent.parent.parent.__truediv__.return_value = Path(
                "/nonexistent/pyproject.toml"
            )

            version = get_project_version()
            assert version == "0.1.0"

    def test_get_project_version_key_error(self):
        """測試 pyproject.toml 文件缺少版本資訊的情況。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(
                """
[tool.poetry]
name = "test-project"
"""
            )
            temp_path = f.name

        try:
            with patch('app.core.settings.Path') as mock_path:
                mock_path.return_value.parent.parent.parent.__truediv__.return_value = (
                    Path(temp_path)
                )

                version = get_project_version()
                assert version == "0.1.0"
        finally:
            os.unlink(temp_path)

    def test_get_project_version_toml_decode_error(self):
        """測試 pyproject.toml 文件格式錯誤的情況。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("invalid toml content")
            temp_path = f.name

        try:
            with patch('app.core.settings.Path') as mock_path:
                mock_path.return_value.parent.parent.parent.__truediv__.return_value = (
                    Path(temp_path)
                )

                version = get_project_version()
                assert version == "0.1.0"
        finally:
            os.unlink(temp_path)


class TestSettings:
    """Settings 類別測試類別。"""

    def test_settings_default_values(self):
        """測試 Settings 類別的預設值。"""
        settings = Settings()

        # 測試基本配置
        assert settings.app_name == "104 Resume Clinic Scheduler"
        assert settings.app_env == "development"
        # debug 的預設值可能是 True（從環境變數或 .env 文件讀取）
        assert isinstance(settings.debug, bool)
        assert settings.testing is False
        assert settings.log_level == "INFO"

        # 測試資料庫配置
        assert settings.mysql_host == "localhost"
        assert settings.mysql_port == 3306
        assert settings.mysql_database == "scheduler_db"
        assert settings.mysql_charset == "utf8mb4"

        # 測試 Redis 配置
        assert settings.redis_host == "localhost"
        assert settings.redis_port == 6379
        assert settings.redis_db == 0

        # 測試 API 配置
        assert settings.api_timeout == 10
        assert settings.api_connect_timeout == 5
        assert settings.api_read_timeout == 10

    def test_settings_environment_override(self):
        """測試環境變數覆蓋設定值。"""
        with patch.dict(
            os.environ,
            {
                'APP_NAME': 'Test App',
                'APP_ENV': 'production',
                'DEBUG': 'true',
                'MYSQL_HOST': 'test-host',
                'MYSQL_PORT': '5432',
                'LOG_LEVEL': 'DEBUG',
            },
        ):
            settings = Settings()

            assert settings.app_name == "Test App"
            assert settings.app_env == "production"
            assert settings.debug is True
            assert settings.mysql_host == "test-host"
            assert settings.mysql_port == 5432
            assert settings.log_level == "DEBUG"

    def test_settings_path_properties(self):
        """測試路徑相關屬性。"""
        settings = Settings()

        # 測試路徑屬性
        assert isinstance(settings.project_root, Path)
        assert isinstance(settings.app_dir, Path)
        assert isinstance(settings.static_dir, Path)
        assert isinstance(settings.templates_dir, Path)

        # 測試路徑關係
        assert settings.static_dir == settings.project_root / "static"
        assert settings.templates_dir == settings.app_dir / "templates"

    def test_settings_environment_properties(self):
        """測試環境判斷屬性。"""
        # 測試開發環境
        with patch.dict(os.environ, {'APP_ENV': 'development'}):
            settings = Settings()
            assert settings.is_development is True
            assert settings.is_production is False
            assert settings.is_staging is False

        # 測試生產環境
        with patch.dict(os.environ, {'APP_ENV': 'production'}):
            settings = Settings()
            assert settings.is_development is False
            assert settings.is_production is True
            assert settings.is_staging is False

        # 測試測試環境
        with patch.dict(os.environ, {'APP_ENV': 'staging'}):
            settings = Settings()
            assert settings.is_development is False
            assert settings.is_production is False
            assert settings.is_staging is True

    def test_cors_origins_list_property(self):
        """測試 CORS 來源列表屬性。"""
        # 測試單一來源
        with patch.dict(os.environ, {'CORS_ORIGINS': 'http://localhost:3000'}):
            settings = Settings()
            assert settings.cors_origins_list == ["http://localhost:3000"]

        # 測試多個來源
        with patch.dict(
            os.environ,
            {
                'CORS_ORIGINS': 'http://localhost:3000,http://localhost:8000,https://example.com'
            },
        ):
            settings = Settings()
            expected = [
                "http://localhost:3000",
                "http://localhost:8000",
                "https://example.com",
            ]
            assert settings.cors_origins_list == expected

        # 測試包含空格的來源
        with patch.dict(
            os.environ,
            {'CORS_ORIGINS': ' http://localhost:3000 , http://localhost:8000 '},
        ):
            settings = Settings()
            expected = ["http://localhost:3000", "http://localhost:8000"]
            assert settings.cors_origins_list == expected

        # 測試空來源
        with patch.dict(os.environ, {'CORS_ORIGINS': ''}):
            settings = Settings()
            assert settings.cors_origins_list == []

    def test_mysql_connection_string(self):
        """測試 MySQL 連接字串生成。"""
        with patch.dict(
            os.environ,
            {
                'MYSQL_USER': 'testuser',
                'MYSQL_PASSWORD': 'testpass',
                'MYSQL_HOST': 'testhost',
                'MYSQL_PORT': '3306',
                'MYSQL_DATABASE': 'testdb',
                'MYSQL_CHARSET': 'utf8mb4',
            },
        ):
            settings = Settings()
            connection_string = settings.mysql_connection_string
            expected = (
                "mysql+pymysql://testuser:testpass@testhost:3306/testdb?charset=utf8mb4"
            )
            assert connection_string == expected

    def test_mysql_connection_string_no_password(self):
        """測試沒有密碼的 MySQL 連接字串。"""
        with patch.dict(
            os.environ,
            {
                'MYSQL_USER': 'testuser',
                'MYSQL_HOST': 'testhost',
                'MYSQL_PORT': '3306',
                'MYSQL_DATABASE': 'testdb',
                'MYSQL_PASSWORD': '',  # 明確設定為空字串
            },
        ):
            settings = Settings()
            connection_string = settings.mysql_connection_string
            expected = "mysql+pymysql://testuser:@testhost:3306/testdb?charset=utf8mb4"
            assert connection_string == expected

    def test_redis_connection_string(self):
        """測試 Redis 連接字串生成。"""
        with patch.dict(
            os.environ,
            {
                'REDIS_HOST': 'testhost',
                'REDIS_PORT': '6379',
                'REDIS_DB': '1',
                'REDIS_PASSWORD': '',  # 明確設定為空字串
            },
        ):
            settings = Settings()
            connection_string = settings.redis_connection_string
            expected = "redis://testhost:6379/1"
            assert connection_string == expected

    def test_redis_connection_string_with_password(self):
        """測試帶密碼的 Redis 連接字串。"""
        with patch.dict(
            os.environ,
            {
                'REDIS_HOST': 'testhost',
                'REDIS_PORT': '6379',
                'REDIS_DB': '1',
                'REDIS_PASSWORD': 'testpass',
            },
        ):
            settings = Settings()
            connection_string = settings.redis_connection_string
            expected = "redis://:testpass@testhost:6379/1"
            assert connection_string == expected

    def test_smtp_config(self):
        """測試 SMTP 配置生成。"""
        with patch.dict(
            os.environ,
            {
                'SMTP_HOST': 'smtp.example.com',
                'SMTP_PORT': '587',
                'SMTP_USER': 'test@example.com',
                'SMTP_PASSWORD': 'testpass',
            },
        ):
            settings = Settings()
            smtp_config = settings.get_smtp_config()
            expected = {
                'host': 'smtp.example.com',
                'port': 587,
                'username': 'test@example.com',
                'password': 'testpass',
                'use_tls': True,
            }
            assert smtp_config == expected

    def test_smtp_config_incomplete(self):
        """測試不完整的 SMTP 配置。"""
        with patch.dict(
            os.environ,
            {
                'SMTP_HOST': 'smtp.example.com',
                'SMTP_PORT': '587',
                'SMTP_USER': '',  # 明確設定為空字串
                'SMTP_PASSWORD': '',  # 明確設定為空字串
            },
        ):
            settings = Settings()
            smtp_config = settings.get_smtp_config()
            assert smtp_config == {}

    def test_has_smtp_config(self):
        """測試 SMTP 配置完整性檢查。"""
        # 完整配置
        with patch.dict(
            os.environ,
            {
                'SMTP_HOST': 'smtp.example.com',
                'SMTP_USER': 'test@example.com',
                'SMTP_PASSWORD': 'testpass',
            },
        ):
            settings = Settings()
            assert settings.has_smtp_config is True

        # 不完整配置
        with patch.dict(
            os.environ,
            {
                'SMTP_HOST': 'smtp.example.com',
                'SMTP_USER': 'test@example.com',
                'SMTP_PASSWORD': '',  # 明確設定為空字串
            },
        ):
            settings = Settings()
            assert settings.has_smtp_config is False

    def test_has_aws_config(self):
        """測試 AWS 配置完整性檢查。"""
        # 完整配置
        with patch.dict(
            os.environ,
            {
                'AWS_ACCESS_KEY_ID': 'test-key',
                'AWS_SECRET_ACCESS_KEY': 'test-secret',
                'AWS_REGION': 'us-east-1',
            },
        ):
            settings = Settings()
            assert settings.has_aws_config is True

        # 不完整配置
        with patch.dict(
            os.environ,
            {
                'AWS_ACCESS_KEY_ID': 'test-key',
                'AWS_SECRET_ACCESS_KEY': 'test-secret',
                'AWS_REGION': '',  # 明確設定為空字串
            },
        ):
            settings = Settings()
            assert settings.has_aws_config is False

    def test_has_104_api_config(self):
        """測試 104 API 配置完整性檢查。"""
        # 完整配置
        with patch.dict(
            os.environ,
            {
                'API_104_BASE_URL': 'https://api.104.com.tw',
                'API_104_CLIENT_ID': 'test-client-id',
                'API_104_CLIENT_SECRET': 'test-client-secret',
            },
        ):
            settings = Settings()
            assert settings.has_104_api_config is True

        # 不完整配置
        with patch.dict(
            os.environ,
            {
                'API_104_BASE_URL': 'https://api.104.com.tw',
                'API_104_CLIENT_ID': 'test-client-id',
                'API_104_CLIENT_SECRET': '',  # 明確設定為空字串
            },
        ):
            settings = Settings()
            assert settings.has_104_api_config is False

    def test_secret_key_methods(self):
        """測試密鑰相關方法。"""
        with patch.dict(
            os.environ,
            {
                'SECRET_KEY': 'test-secret-key',
                'SESSION_SECRET': 'test-session-secret',
                'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
                'API_104_CLIENT_SECRET': 'test-104-secret',
            },
        ):
            settings = Settings()

            assert settings.get_secret_key() == "test-secret-key"
            assert settings.get_session_secret() == "test-session-secret"
            assert settings.get_aws_secret_key() == "test-aws-secret"
            assert settings.get_104_api_secret() == "test-104-secret"

    def test_secret_key_methods_no_secrets(self):
        """測試沒有密鑰時的方法。"""
        with patch.dict(
            os.environ,
            {
                'SECRET_KEY': '',
                'SESSION_SECRET': '',
                'AWS_SECRET_ACCESS_KEY': '',
                'API_104_CLIENT_SECRET': '',
            },
        ):
            settings = Settings()

            assert settings.get_secret_key() == ""
            assert settings.get_session_secret() == ""
            assert settings.get_aws_secret_key() == ""
            assert settings.get_104_api_secret() == ""

    def test_settings_validation(self):
        """測試設定驗證。"""
        # 測試有效的設定
        with patch.dict(
            os.environ,
            {'MYSQL_PORT': '3306', 'REDIS_PORT': '6379', 'API_TIMEOUT': '10'},
        ):
            settings = Settings()
            assert settings.mysql_port == 3306
            assert settings.redis_port == 6379
            assert settings.api_timeout == 10

    def test_settings_validation_invalid_types(self):
        """測試無效類型的設定驗證。"""
        # 測試無效的整數類型
        with patch.dict(os.environ, {'MYSQL_PORT': 'invalid'}):
            with pytest.raises(ValidationError):
                Settings()

        # 測試無效的布林類型
        with patch.dict(os.environ, {'DEBUG': 'maybe'}):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_case_insensitive(self):
        """測試環境變數大小寫不敏感。"""
        with patch.dict(
            os.environ,
            {
                'app_name': 'Test App',
                'APP_ENV': 'production',
                'mysql_host': 'test-host',
            },
        ):
            settings = Settings()

            assert settings.app_name == "Test App"
            assert settings.app_env == "production"
            assert settings.mysql_host == "test-host"

    def test_settings_extra_fields_ignored(self):
        """測試額外的環境變數被忽略。"""
        with patch.dict(
            os.environ,
            {'UNKNOWN_SETTING': 'test-value', 'ANOTHER_UNKNOWN': 'another-value'},
        ):
            # 不應該拋出異常
            settings = Settings()
            assert hasattr(settings, 'UNKNOWN_SETTING') is False
            assert hasattr(settings, 'ANOTHER_UNKNOWN') is False

    def test_settings_default_factory_functions(self):
        """測試使用 default_factory 的欄位。"""
        settings = Settings()

        # 測試路徑欄位使用 default_factory
        assert isinstance(settings.project_root, Path)
        assert isinstance(settings.app_dir, Path)

        # 測試版本號使用 default_factory
        assert isinstance(settings.app_version, str)
        assert len(settings.app_version) > 0

    def test_settings_field_descriptions(self):
        """測試欄位描述。"""
        # 檢查一些重要欄位是否有描述
        field_info = Settings.model_fields

        assert field_info['app_name'].description == "應用程式名稱"
        assert (
            field_info['app_env'].description
            == "應用程式環境 (development, staging, production)"
        )
        assert field_info['mysql_host'].description == "MySQL 主機地址"
        assert (
            field_info['log_level'].description
            == "日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        )

    def test_settings_model_config(self):
        """測試 Pydantic 模型配置。"""
        config = Settings.model_config

        assert config['env_file'] == ".env"
        assert config['env_file_encoding'] == "utf-8"
        assert config['case_sensitive'] is False
        assert config['extra'] == "ignore"
