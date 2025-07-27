"""
應用程式配置管理模組。

集中管理所有應用程式配置，包括路徑、應用程式資訊、API 設定等。
"""

# ===== 標準函式庫 =====
import tomllib  # Python 3.11+ 內建，解析 TOML 格式檔案
from pathlib import Path  # 現代化的路徑處理

# ===== 第三方套件 =====
# 無


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
        
        # 應用程式配置
        self.app_name = "104 Resume Clinic Scheduler"
        self.app_description = "【MVP】104 履歷診療室 - 站內諮詢時間媒合系統"
        self.default_version = "0.1.0"  # 預設版本號
        self.app_version = get_project_version()
        
        # API 文件配置
        self.docs_url = "/docs"
        self.redoc_url = "/redoc"
        
        # 靜態檔案配置
        self.static_url = "/static"
        self.static_name = "static"


# 全域配置實例
config = AppConfig() 