"""
健康檢查路由模組。

包含健康檢查和連線測試等端點。
"""

# ===== 標準函式庫 =====
import logging
from typing import Any

# ===== 第三方套件 =====
from fastapi import APIRouter

# ===== 本地模組 =====
from app.core import get_project_version, settings
from app.decorators import handle_api_errors
from app.errors import create_liveness_check_error, create_readiness_check_error
from app.models.database import check_db_connection
from app.utils.timezone import get_utc_timestamp

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=dict[str, Any])
@handle_api_errors()
async def liveness_probe(fail: bool = False) -> dict[str, Any]:
    """
    存活探測：檢查應用程式是否正在運行。

    這個端點用於 Kubernetes 的 liveness probe，檢查應用程式是否存活。
    不應該包含外部依賴檢查，只檢查應用程式本身狀態。

    Args:
        fail: 故意觸發錯誤測試。

    Returns:
        dict[str, Any]: 應用程式狀態資訊，包含狀態、時間戳、版本等資訊。
    """
    logger.info("liveness_probe() called: 執行存活探測檢查")

    if fail:
        raise create_liveness_check_error("測試模式：故意觸發存活探測檢查錯誤")

    response_data = {
        "message": "應用程式存活",
        "status": "healthy",
        "app_name": settings.app_name,
        "version": get_project_version(),
        "timestamp": get_utc_timestamp(),
        "checks": {
            "application": "healthy",
        },
    }

    logger.info("liveness_probe() success: 應用程式狀態健康")
    return response_data


@router.get("/readyz", response_model=dict[str, Any])
@handle_api_errors()
async def readiness_probe(fail: bool = False, db_fail: bool = False) -> dict[str, Any]:
    """
    準備就緒探測：檢查應用程式所有外部依賴（資料庫、快取等），是否已經準備好處理請求。

    這個端點用於 Kubernetes 的 readiness probe，檢查所有依賴是否就緒。

    Returns:
        dict[str, Any]: 應用程式就緒狀態資訊。
    """
    logger.info("readiness_probe() called: 執行準備就緒探測檢查")

    # 故意觸發錯誤測試
    if fail:
        raise create_readiness_check_error("測試模式：故意觸發準備就緒探測檢查錯誤")

    # 模擬資料庫連線失敗
    if db_fail:
        raise create_readiness_check_error(
            "真實錯誤：資料庫連線失敗，應用程式未準備就緒"
        )

    # 檢查真實資料庫連線（如果連線失敗會拋出異常）
    check_db_connection()

    response_data = {
        "message": "應用程式準備就緒",
        "status": "healthy",
        "app_name": settings.app_name,
        "version": get_project_version(),
        "timestamp": get_utc_timestamp(),
        "checks": {
            "application": "healthy",
            "database": "healthy",
            # "redis": "healthy",  # 未來可加入
            # "external_api": "healthy"  # 未來可加入
        },
    }
    logger.info("readiness_probe() success: 應用程式準備就緒，所有依賴檢查通過")
    return response_data
