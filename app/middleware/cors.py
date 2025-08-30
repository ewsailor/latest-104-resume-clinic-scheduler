"""簡化的 CORS 中間件。

提供基本的跨來源資源共用設定。
"""

# ===== 標準函式庫 =====
import logging

# ===== 第三方套件 =====
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ===== 本地模組 =====
from app.core.settings import settings

logger = logging.getLogger(__name__)


def log_app_startup(app: FastAPI) -> None:
    """記錄應用程式啟動資訊。"""
    logger.info("=== 應用程式啟動 ===")
    logger.info(f"環境: {settings.app_env}")
    logger.info(f"版本: {settings.app_version}")
    logger.info(f"除錯模式: {settings.debug}")
    logger.info("=== 啟動完成 ===")


def setup_cors_middleware(app: FastAPI) -> None:
    """設定 CORS 中間件。"""
    origins = [
        "http://localhost:3000",  # React 開發伺服器
        "http://localhost:8000",  # FastAPI 開發伺服器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    logger.info(f"CORS 中間件設定完成，允許 {len(origins)} 個來源")
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    headers = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=methods,
        allow_headers=headers,
    )
