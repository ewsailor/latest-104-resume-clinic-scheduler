"""
應用程式工廠模組。

負責建立和配置 FastAPI 應用程式的各個組件，包括靜態檔案服務、模板引擎等。
"""

# ===== 第三方套件 =====
from fastapi import FastAPI  # Web 框架核心
from fastapi.staticfiles import StaticFiles  # 靜態檔案服務
from fastapi.templating import Jinja2Templates  # HTML 模板引擎

# ===== 本地模組 =====
from app.middleware.cors import setup_cors_middleware  # CORS 中間件設定


def create_static_files(settings) -> StaticFiles:
    """
    建立並配置靜態檔案服務。

    Args:
        settings: 應用程式設定物件。

    Returns:
        StaticFiles: 配置完成的靜態檔案服務實例。
    """
    return StaticFiles(directory=str(settings.static_dir))


def create_templates(settings) -> Jinja2Templates:
    """
    建立並配置 Jinja2 模板引擎。

    Args:
        settings: 應用程式設定物件。

    Returns:
        Jinja2Templates: 配置完成的模板引擎實例。
    """
    return Jinja2Templates(directory=str(settings.templates_dir))


def create_app(settings) -> FastAPI:
    """
    建立並配置 FastAPI 應用程式。

    Args:
        settings: 應用程式設定物件。

    Returns:
        FastAPI: 配置完成的 FastAPI 應用程式實例。
    """
    # 根據環境決定是否顯示 API 文件
    docs_url = settings.docs_url if settings.debug else None
    redoc_url = settings.redoc_url if settings.debug else None

    # 建立 FastAPI 應用程式
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug,  # 根據設定決定是否開啟 debug 模式
        docs_url=docs_url,  # 生產環境隱藏 API 文件
        redoc_url=redoc_url,  # 生產環境隱藏 API 文件
    )

    # ===== CORS 中間件設定 =====
    setup_cors_middleware(app, settings)

    # 掛載靜態檔案服務
    app.mount(
        settings.static_url, create_static_files(settings), name=settings.static_name
    )

    return app
