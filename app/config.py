"""
應用程式配置管理模組。

集中管理所有應用程式配置，包括路徑、應用程式資訊、API 設定等。
"""

# ===== 標準函式庫 =====
import os  # 環境變數存取
import tomllib  # Python 3.11+ 內建，解析 TOML 格式檔案
from pathlib import Path  # 現代化的路徑處理

# ===== 第三方套件 =====
from dotenv import load_dotenv  # 載入環境變數檔案

# 載入環境變數（必須在最開始執行）
load_dotenv()


def get_project_version() -> str:
    """
    從 pyproject.toml 動態讀取專案版本號。
    
    Returns:
        str: 專案版本號，如果讀取失敗則返回預設版本。
    """
    try:
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"
        
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data["tool"]["poetry"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError) as e:
        print(f"警告: 無法從 pyproject.toml 讀取專案版本號。錯誤: {e}")
        return "0.1.0"  # 預設版本號


class AppConfig:
    """
    應用程式配置管理類別。
    """    
    def __init__(self):
        # 基礎路徑配置
        self.project_root = Path(__file__).parent.parent  # 專案的根目錄，用來定位 pyproject.toml 等檔案
        self.app_dir = Path(__file__).parent  # 應用程式目錄，用來定位 templates 等檔案
        
        # 靜態檔案配置
        self.static_dir = self.project_root / "static"
        
        # 模板配置
        self.templates_dir = self.app_dir / "templates"
        
        # 應用程式配置（從環境變數讀取）
        self.app_name = os.getenv("APP_NAME", "104 Resume Clinic Scheduler")
        self.app_description = "【MVP】104 履歷診療室 - 站內諮詢時間媒合系統"
        self.default_version = "0.1.0"  # 預設版本號
        self.app_version = get_project_version()
        
        # 環境設定
        self.app_env = os.getenv("APP_ENV", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        
        # API 文件配置
        self.docs_url = "/docs"
        self.redoc_url = "/redoc"
        
        # 靜態檔案配置
        self.static_url = "/static"
        self.static_name = "static"
        
        # 資料庫配置
        self.mysql_host = os.getenv("MYSQL_HOST", "localhost")
        self.mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
        self.mysql_user = os.getenv("MYSQL_USER", "root")
        self.mysql_password = os.getenv("MYSQL_PASSWORD", "")
        self.mysql_database = os.getenv("MYSQL_DATABASE", "scheduler_db")
        self.mysql_charset = os.getenv("MYSQL_CHARSET", "utf8mb4")
        
        # MongoDB 配置
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.mongodb_database = os.getenv("MONGODB_DATABASE", "scheduler_db")
        
        # Redis 配置
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        
        # AWS 配置
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "ap-northeast-1")
        self.aws_s3_bucket = os.getenv("AWS_S3_BUCKET")
        
        # 104 API 配置
        self.api_104_base_url = os.getenv("API_104_BASE_URL")
        self.api_104_client_id = os.getenv("API_104_CLIENT_ID")
        self.api_104_client_secret = os.getenv("API_104_CLIENT_SECRET")
        
        # 日誌配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "logs/app.log")
        
        # 安全配置
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",")
        self.session_secret = os.getenv("SESSION_SECRET", "dev-session-secret")
        
        # 郵件配置
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")


# 全域配置實例
config = AppConfig() 