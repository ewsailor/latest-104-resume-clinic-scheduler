"""
簡化的 CORS 中間件。

提供基本的跨來源資源共用設定，適合投履歷展示。
"""

# ===== 標準函式庫 =====
import logging

# ===== 第三方套件 =====
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


def setup_cors_middleware(app: FastAPI) -> None:
    """設定 CORS 中間件"""

    # 允許的來源
    origins = [
        "http://localhost:3000",  # React 開發伺服器
        "http://localhost:8000",  # FastAPI 開發伺服器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # 允許的方法
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    # 允許的標頭
    headers = ["*"]

    # 添加 CORS 中間件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=methods,
        allow_headers=headers,
    )

    logger.info("CORS 中間件設定完成")
