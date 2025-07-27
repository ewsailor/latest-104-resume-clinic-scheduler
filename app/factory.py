"""
應用程式工廠模組。

負責建立和配置 FastAPI 應用程式的各個組件，包括靜態檔案服務、模板引擎等。
"""

# ===== 第三方套件 =====
from fastapi import FastAPI  # Web 框架核心
from fastapi.staticfiles import StaticFiles  # 靜態檔案服務
from fastapi.templating import Jinja2Templates  # HTML 模板引擎


def create_static_files(config) -> StaticFiles:
    """
    建立並配置靜態檔案服務。
    
    Args:
        config: 應用程式配置物件。
        
    Returns:
        StaticFiles: 配置完成的靜態檔案服務實例。
    """
    return StaticFiles(directory=str(config.static_dir))


def create_templates(config) -> Jinja2Templates:
    """
    建立並配置 Jinja2 模板引擎。
    
    Args:
        config: 應用程式配置物件。
        
    Returns:
        Jinja2Templates: 配置完成的模板引擎實例。
    """
    return Jinja2Templates(directory=str(config.templates_dir))


def create_app(config) -> FastAPI:
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