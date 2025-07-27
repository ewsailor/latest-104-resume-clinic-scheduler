"""
FastAPI 應用程式主入口。

【MVP】104 履歷診療室 - 站內諮詢時間媒合系統：讓 Giver、Taker 在平台內，方便地設定可面談時間，並完成配對媒合。
"""

# ===== 標準函式庫 =====
import os  # 作業系統介面
import tomllib  # Python 3.11+ 內建，解析 TOML 格式檔案
from pathlib import Path  # 現代化的路徑處理
from typing import Dict, Any  # 型別註解支援

# ===== 第三方套件 =====
from fastapi import FastAPI, Request  # Web 框架核心
from fastapi.staticfiles import StaticFiles  # 靜態檔案服務
from fastapi.templating import Jinja2Templates  # HTML 模板引擎
from fastapi.responses import HTMLResponse  # HTML 回應類型

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
        return config.default_version

def create_static_files(config: AppConfig) -> StaticFiles:
    """
    建立並配置靜態檔案服務。
    
    Args:
        config: 應用程式配置物件。
        
    Returns:
        StaticFiles: 配置完成的靜態檔案服務實例。
    """
    return StaticFiles(directory=str(config.static_dir))

def create_templates(config: AppConfig) -> Jinja2Templates:
    """
    建立並配置 Jinja2 模板引擎。
    
    Args:
        config: 應用程式配置物件。
        
    Returns:
        Jinja2Templates: 配置完成的模板引擎實例。
    """
    return Jinja2Templates(directory=str(config.templates_dir))

def create_app(config: AppConfig) -> FastAPI:
    """
    建立並配置 FastAPI 應用程式。
    
    Args:
        config: 應用程式配置物件。
        
    Returns:
        FastAPI: 配置完成的 FastAPI 應用程式實例。
    """
    # 建立 FastAPI 應用程式
    app = FastAPI(
        title=config.app_name,
        description=config.app_description,
        version=config.app_version,
        docs_url=config.docs_url,
        redoc_url=config.redoc_url,
    )
    
    # 掛載靜態檔案服務
    app.mount(config.static_url, create_static_files(config), name=config.static_name)
    
    return app

# 建立配置物件
config = AppConfig()

# 建立應用程式實例
app = create_app(config)

# 建立模板引擎實例
templates = create_templates(config)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """
    首頁路由 - 顯示履歷診療室主頁面。
    
    Args:
        request: FastAPI 請求物件。
        
    Returns:
        HTMLResponse: 渲染後的 HTML 頁面。
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康檢查端點。
    
    Returns:
        Dict[str, Any]: 應用程式狀態資訊。
    """
    return {
        "status": "healthy",
        "app_name": config.app_name,
        "version": get_project_version(),
    }

