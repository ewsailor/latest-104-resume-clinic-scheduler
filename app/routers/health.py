"""
健康檢查路由模組。

包含健康檢查和連線測試等端點。
"""

# ===== 標準函式庫 =====
import logging
from typing import Any

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status

# ===== 本地模組 =====
# 絕對路徑導入（跨模組）
from app.core import get_project_version, settings
from app.models.database import get_healthy_db
from app.utils.timezone import get_utc_timestamp

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=dict[str, Any])
async def liveness_probe() -> dict[str, Any]:
    """
    存活探測：檢查應用程式是否正在運行。

    這個端點用於 Kubernetes 的 liveness probe，檢查應用程式是否存活。
    不應該包含外部依賴檢查，只檢查應用程式本身狀態。

    Returns:
        dict[str, Any]: 應用程式狀態資訊，包含狀態、時間戳、版本等資訊。
    """
    logger.info("liveness_probe() called: 執行存活探測檢查")

    try:
        response_data = {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": get_project_version(),
            "uptime": "running",
            "timestamp": get_utc_timestamp(),
        }

        logger.info("liveness_probe() success: 應用程式狀態健康")
        return response_data

    except Exception as e:
        logger.error(f"liveness_probe() error: 存活探測檢查失敗 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unhealthy",
                "error": "Application health check failed",
                "timestamp": get_utc_timestamp(),
            },
        )


@router.get("/readyz", response_model=dict[str, Any])
async def readiness_probe(db_healthy: bool = Depends(get_healthy_db)) -> dict[str, Any]:
    """
    準備就緒探測：檢查應用程式所有外部依賴（資料庫、快取等），是否已經準備好處理請求。

    這個端點用於 Kubernetes 的 readiness probe，檢查所有依賴是否就緒。
    使用依賴注入方式檢查資料庫連線，如果連線失敗會自動拋出 503 錯誤。

    Args:
        db_healthy: 資料庫連線狀態依賴，由 get_healthy_db() 提供

    Returns:
        dict[str, Any]: 應用程式就緒狀態資訊。
    """
    logger.info("readiness_probe() called: 執行準備就緒探測檢查")

    # 可以在此加入其他依賴檢查，例如：
    # - Redis 連線檢查
    # - 外部 API 連線檢查
    # - 檔案系統權限檢查

    response_data = {
        "status": "healthy",
        "database": "connected",
        "message": "Application and database are ready to serve traffic.",
        "timestamp": get_utc_timestamp(),
        "checks": {
            "database": "healthy",
            # "redis": "healthy",  # 未來可加入
            # "external_api": "healthy"  # 未來可加入
        },
    }
    logger.info("readiness_probe() success: 應用程式準備就緒，所有依賴檢查通過")
    return response_data
