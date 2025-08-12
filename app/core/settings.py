"""
應用程式配置管理模組。

使用 Pydantic BaseSettings 集中管理所有應用程式配置，包括路徑、應用程式資訊、API 設定等。
提供型別安全、自動驗證和環境變數整合功能。
"""

# ===== 標準函式庫 =====
import tomllib  # Python 3.11+ 內建，解析 TOML 格式檔案
from pathlib import Path  # 現代化的路徑處理
from typing import Any  # 保留 Any，因為它沒有內建替代

# ===== 第三方套件 =====
from pydantic import Field, SecretStr, field_validator  # Pydantic v2 驗證和欄位定義
from pydantic_settings import BaseSettings, SettingsConfigDict  # Pydantic v2 設定管理


def get_project_version() -> str:
    """
    從 pyproject.toml 檔案中讀取專案版本號。

    Returns:
        str: 專案版本號，如果讀取失敗則返回預設版本號
    """
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return str(pyproject_data["tool"]["poetry"]["version"])
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError) as e:
        # 使用 logging 而不是 print，避免在生產環境中輸出
        import logging

        logging.warning(f"無法從 pyproject.toml 讀取專案版本號。錯誤: {e}")
        return "0.1.0"  # 預設版本號


class Settings(BaseSettings):
    """
    應用程式設定管理類別。

    使用 Pydantic BaseSettings 提供：
    - 自動環境變數載入
    - 型別安全驗證
    - 預設值管理
    - 配置驗證
    """

    # Pydantic 設定配置
    model_config = SettingsConfigDict(
        env_file=".env",  # 自動載入 .env 檔案
        env_file_encoding="utf-8",  # 檔案編碼
        case_sensitive=False,  # 環境變數名稱不區分大小寫
        extra="ignore",  # 忽略未定義的環境變數
        env_parse_none_str=None,  # 禁用複雜值解析：環境變數的值是字串 "None" 時，不自動轉換成 Python 的 None 物件
    )

    # ===== 基礎路徑配置 =====
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="專案的根目錄，用來定位 pyproject.toml 等檔案",
    )
    app_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="應用程式目錄，用來定位 templates 等檔案",
    )

    # ===== 應用程式基本配置 =====
    app_name: str = Field(
        default="104 Resume Clinic Scheduler", description="應用程式名稱"
    )
    app_description: str = Field(
        default="【MVP】104 履歷診療室 - 站內諮詢時間媒合系統",
        description="應用程式描述",
    )
    app_version: str = Field(
        default_factory=get_project_version, description="應用程式版本號"
    )

    # ===== 環境設定 =====
    app_env: str = Field(
        default="development",
        description="應用程式環境 (development, staging, production)",
    )
    # ⚠️ 正式環境記得將 .env 設定成 DEBUG=false
    # 如果 .env 或系統中結果是小寫字串 "true"，就回傳 True，開啟「除錯模式（debug mode）」
    # 如果 .env 或系統中沒有 DEBUG，預設回傳 False（布林值）
    debug: bool = Field(default=False, description="是否啟用除錯模式")
    secret_key: SecretStr | None = Field(default=None, description="應用程式密鑰")

    # ===== API 文件配置 =====
    docs_url: str = Field(default="/docs", description="API 文件 URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc 文件 URL")

    # ===== 靜態檔案配置 =====
    static_url: str = Field(default="/static", description="靜態檔案 URL 路徑")
    static_name: str = Field(default="static", description="靜態檔案掛載名稱")

    # ===== 日誌配置 =====
    log_level: str = Field(
        default="INFO",
        description="日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_api_requests: bool = Field(default=True, description="是否記錄 API 請求日誌")
    log_static_requests: bool = Field(
        default=False, description="是否記錄靜態資源請求日誌"
    )
    log_file: str = Field(default="logs/app.log", description="日誌檔案路徑")

    # ===== 資料庫配置 =====
    # MySQL 配置
    mysql_host: str = Field(default="localhost", description="MySQL 主機地址")
    mysql_port: int = Field(default=3306, description="MySQL 連接埠")
    mysql_user: str | None = Field(
        default=None,
        description="MySQL 使用者名稱（建議使用專用應用程式帳號，不要使用 root）",
    )
    mysql_password: SecretStr | None = Field(
        default=None,  # 使用 None 作為預設值，強制從環境變數設定
        description="MySQL 密碼",
    )
    mysql_database: str = Field(default="scheduler_db", description="MySQL 資料庫名稱")
    mysql_charset: str = Field(default="utf8mb4", description="MySQL 字符集")

    # MongoDB 配置
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 連接 URI"
    )
    mongodb_database: str = Field(
        default="scheduler_db", description="MongoDB 資料庫名稱"
    )

    # Redis 配置
    redis_host: str = Field(default="localhost", description="Redis 主機地址")
    redis_port: int = Field(default=6379, description="Redis 連接埠")
    redis_db: int = Field(default=0, description="Redis 資料庫編號")
    redis_password: SecretStr | None = Field(default=None, description="Redis 密碼")

    # ===== AWS 配置 =====
    aws_access_key_id: str | None = Field(default=None, description="AWS 存取金鑰 ID")
    aws_secret_access_key: SecretStr | None = Field(
        default=None, description="AWS 秘密存取金鑰"
    )
    aws_region: str = Field(default="ap-northeast-1", description="AWS 區域")
    aws_s3_bucket: str | None = Field(default=None, description="AWS S3 儲存桶名稱")

    # ===== 104 API 配置 =====
    api_104_base_url: str | None = Field(default=None, description="104 API 基礎 URL")
    api_104_client_id: str | None = Field(default=None, description="104 API 客戶端 ID")
    api_104_client_secret: SecretStr | None = Field(
        default=None, description="104 API 客戶端密鑰"
    )

    # ===== API 超時配置 =====
    api_timeout: int = Field(default=10, description="API 請求總超時時間（秒）")
    api_connect_timeout: int = Field(default=5, description="API 連接超時時間（秒）")
    api_read_timeout: int = Field(default=10, description="API 讀取超時時間（秒）")

    # ===== 安全配置 =====
    cors_origins: str = Field(
        default="http://localhost:8000", description="CORS 允許的來源（逗號分隔）"
    )
    session_secret: SecretStr | None = Field(default=None, description="會話密鑰")

    # ===== 郵件配置 =====
    smtp_host: str | None = Field(default=None, description="SMTP 主機地址")
    smtp_port: int = Field(default=587, description="SMTP 連接埠")
    smtp_user: str | None = Field(default=None, description="SMTP 使用者名稱")
    smtp_password: SecretStr | None = Field(default=None, description="SMTP 密碼")

    # ===== 驗證器 =====
    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """驗證應用程式環境設定"""
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"app_env 必須是以下其中之一: {allowed_envs}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """驗證日誌等級設定"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"log_level 必須是以下其中之一: {allowed_levels}")
        return v.upper()

    @field_validator("mysql_port", "redis_port", "smtp_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """驗證連接埠設定"""
        if not (1 <= v <= 65535):
            raise ValueError("連接埠必須在 1-65535 範圍內")
        return v

    @field_validator("secret_key", "session_secret")
    @classmethod
    def validate_secret_key(cls, v: SecretStr | None, info: Any) -> SecretStr | None:
        if v is None or len(v.get_secret_value()) < 32:
            raise ValueError(f"{info.field_name} 必須設定且長度至少 32 個字元")
        return v

    @field_validator("mysql_user")
    @classmethod
    def validate_mysql_user(cls, v: str | None) -> str | None:
        """驗證 MySQL 使用者設定"""
        if v is None or not v:  # 檢查 None 或空字串
            raise ValueError("❌ MYSQL_USER 未設定，請檢查 .env 檔案")
        if v.lower() == "root":
            raise ValueError("❌ 不建議使用 root 帳號，請建立專用的應用程式帳號")
        return v

    @field_validator("mysql_password")
    @classmethod
    def validate_mysql_password(cls, v: SecretStr | None) -> SecretStr | None:
        """驗證 MySQL 密碼設定"""
        if v is None or not v.get_secret_value():
            raise ValueError("❌ MYSQL_PASSWORD 未設定，請檢查 .env 檔案")
        return v

    @field_validator("api_timeout", "api_connect_timeout", "api_read_timeout")
    @classmethod
    def validate_api_timeout(cls, v: int) -> int:
        """驗證 API 超時設定"""
        if v <= 0:
            raise ValueError("API 超時時間必須大於 0 秒")
        if v > 300:  # 最大 5 分鐘
            raise ValueError("API 超時時間不能超過 300 秒")
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """驗證 CORS 來源設定"""
        if not v or not v.strip():
            raise ValueError("CORS 來源不能為空")

        # 檢查基本格式
        origins = [origin.strip() for origin in v.split(",") if origin.strip()]
        if not origins:
            raise ValueError("至少需要一個有效的 CORS 來源")

        # 檢查每個來源的格式
        import re

        for origin in origins:
            if not re.match(r"^https?://[a-zA-Z0-9.-]+(:\d+)?$", origin):
                raise ValueError(f"無效的 CORS 來源格式：{origin}")

        return v

    @field_validator("mongodb_uri")
    @classmethod
    def validate_mongodb_uri(cls, v: str) -> str:
        """驗證 MongoDB URI 格式"""
        if not v or not v.strip():
            raise ValueError("MongoDB URI 不能為空")

        # 檢查基本格式
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MongoDB URI 必須以 mongodb:// 或 mongodb+srv:// 開頭")

        return v

    @field_validator("aws_region")
    @classmethod
    def validate_aws_region(cls, v: str) -> str:
        """驗證 AWS 區域格式"""
        if not v or not v.strip():
            raise ValueError("AWS 區域不能為空")

        # 檢查 AWS 區域格式 (例如: us-east-1, ap-northeast-1)
        import re

        if not re.match(r"^[a-z]{2}-[a-z]+-\d+$", v):
            raise ValueError(f"無效的 AWS 區域格式：{v}")

        return v

    @field_validator("redis_db")
    @classmethod
    def validate_redis_db(cls, v: int) -> int:
        """驗證 Redis 資料庫編號"""
        if not isinstance(v, int) or v < 0 or v > 15:
            raise ValueError("Redis 資料庫編號必須在 0-15 範圍內")
        return v

    @field_validator("mysql_charset")
    @classmethod
    def validate_mysql_charset(cls, v: str) -> str:
        """驗證 MySQL 字符集"""
        if not v or not v.strip():
            raise ValueError("MySQL 字符集不能為空")

        # 檢查常見的 MySQL 字符集
        valid_charsets = [
            "utf8",
            "utf8mb4",
            "utf8mb3",
            "latin1",
            "ascii",
            "binary",
            "gbk",
            "big5",
        ]
        if v.lower() not in valid_charsets:
            raise ValueError(f"不支援的 MySQL 字符集：{v}")

        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """取得 CORS 來源列表"""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    # ===== 計算屬性 =====
    @property
    def static_dir(self) -> Path:
        """靜態檔案目錄"""
        return self.project_root / "static"

    @property
    def templates_dir(self) -> Path:
        """模板目錄"""
        return self.app_dir / "templates"

    @property
    def is_development(self) -> bool:
        """是否為開發環境"""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """是否為生產環境"""
        return self.app_env == "production"

    @property
    def is_staging(self) -> bool:
        """是否為測試環境"""
        return self.app_env == "staging"

    @property
    def mysql_connection_string(self) -> str:
        """MySQL 連接字串"""
        password = (
            self.mysql_password.get_secret_value()
            if self.mysql_password is not None
            else ""
        )
        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset={self.mysql_charset}"
        )

    @property
    def redis_connection_string(self) -> str:
        """Redis 連接字串"""
        if self.redis_password:
            password = self.redis_password.get_secret_value()
            return (
                f"redis://:{password}@{self.redis_host}:"
                f"{self.redis_port}/{self.redis_db}"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_smtp_config(self) -> dict[str, Any]:
        """取得 SMTP 配置"""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            return {}

        return {
            "host": self.smtp_host,
            "port": self.smtp_port,
            "username": self.smtp_user,
            "password": (
                self.smtp_password.get_secret_value() if self.smtp_password else ""
            ),
            "use_tls": True,
        }

    @property
    def has_smtp_config(self) -> bool:
        """檢查是否有完整的 SMTP 配置"""
        return all([self.smtp_host, self.smtp_user, self.smtp_password])

    @property
    def has_aws_config(self) -> bool:
        """檢查是否有完整的 AWS 配置"""
        return all(
            [self.aws_access_key_id, self.aws_secret_access_key, self.aws_region]
        )

    @property
    def has_104_api_config(self) -> bool:
        """檢查是否有完整的 104 API 配置"""
        return all(
            [self.api_104_base_url, self.api_104_client_id, self.api_104_client_secret]
        )

    # ===== 安全相關的便利方法 =====
    def get_secret_key(self) -> str:
        """安全地取得應用程式密鑰"""
        return self.secret_key.get_secret_value() if self.secret_key else ""

    def get_session_secret(self) -> str:
        """安全地取得會話密鑰"""
        return self.session_secret.get_secret_value() if self.session_secret else ""

    def get_aws_secret_key(self) -> str:
        """安全地取得 AWS 秘密金鑰"""
        return (
            self.aws_secret_access_key.get_secret_value()
            if self.aws_secret_access_key
            else ""
        )

    def get_104_api_secret(self) -> str:
        """安全地取得 104 API 密鑰"""
        return (
            self.api_104_client_secret.get_secret_value()
            if self.api_104_client_secret
            else ""
        )


# 全域設定實例
settings = Settings()
