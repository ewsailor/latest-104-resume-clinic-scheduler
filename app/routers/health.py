"""健康檢查路由模組。

包含存活探測和準備就緒探測等端點。
"""

# ===== 標準函式庫 =====
from typing import Any

# ===== 第三方套件 =====
from fastapi import APIRouter, status

# ===== 本地模組 =====
from app.core import get_project_version, settings
from app.decorators import handle_api_errors_async, log_operation
from app.errors import create_liveness_check_error, create_readiness_check_error
from app.models.database import check_db_connection
from app.utils.timezone import get_utc_timestamp

router = APIRouter(tags=["health"])


@router.get(
    "/healthz",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="存活探測檢查",
    description="""
    ## 存活探測端點

    檢查應用程式是否正在運行，用於 Kubernetes 的 liveness probe。

    ### 功能說明
    - 檢查應用程式本身是否存活
    - 不包含外部依賴檢查（如資料庫、快取等）
    - 僅檢查應用程式進程狀態

    ### 使用場景
    - Kubernetes 容器健康檢查
    - 負載平衡器健康檢查
    - 應用程式監控系統

    ### 回應狀態
    - **200 OK**: 應用程式正常運行
    - **500 Internal Server Error**: 應用程式異常

    ### 測試參數
    - `fail=true`: 故意觸發錯誤以測試錯誤處理機制
    """,
    responses={
        200: {
            "description": "應用程式存活",
            "content": {
                "application/json": {
                    "example": {
                        "message": "應用程式存活",
                        "status": "healthy",
                        "app_name": "resume-clinic-scheduler",
                        "version": "1.0.0",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "checks": {"application": "healthy"},
                    }
                }
            },
        },
        500: {
            "description": "應用程式異常",
            "content": {
                "application/json": {
                    "example": {
                        "error": "存活探測檢查失敗",
                        "detail": "應用程式內部錯誤",
                        "timestamp": "2024-01-01T00:00:00Z",
                    }
                }
            },
        },
    },
)
@handle_api_errors_async()
@log_operation("存活探測檢查")
async def liveness_probe(
    fail: bool = False,
) -> dict[str, Any]:
    """
    存活探測：檢查應用程式是否正在運行。

    這個端點用於 Kubernetes 的 liveness probe，檢查應用程式是否存活。
    不應該包含外部依賴檢查，只檢查應用程式本身狀態。

    Args:
        fail: 故意觸發錯誤測試。

    Returns:
        dict[str, Any]: 應用程式狀態資訊，包含狀態、時間戳、版本等資訊。
    """
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

    return response_data


@router.get(
    "/readyz",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="準備就緒探測檢查",
    description="""
    ## 準備就緒探測端點

    檢查應用程式所有外部依賴是否已經準備好處理請求，用於 Kubernetes 的 readiness probe。

    ### 功能說明
    - 檢查應用程式本身狀態
    - 檢查資料庫連線狀態
    - 檢查其他外部依賴（如快取、外部API等）
    - 確保應用程式可以正常處理業務請求

    ### 使用場景
    - Kubernetes 容器就緒檢查
    - 藍綠部署時的流量切換
    - 應用程式啟動完成確認
    - 負載平衡器流量分配

    ### 檢查項目
    - **應用程式**: 檢查應用程式進程狀態
    - **資料庫**: 檢查資料庫連線和基本查詢
    - **快取** (未來): 檢查 Redis 連線狀態
    - **外部API** (未來): 檢查關鍵外部服務連線

    ### 回應狀態
    - **200 OK**: 所有依賴正常，應用程式準備就緒
    - **500 Internal Server Error**: 依賴檢查失敗，應用程式未準備就緒

    ### 測試參數
    - `fail=true`: 故意觸發一般錯誤
    - `db_fail=true`: 模擬資料庫連線失敗
    """,
    responses={
        200: {
            "description": "應用程式準備就緒",
            "content": {
                "application/json": {
                    "example": {
                        "message": "應用程式準備就緒",
                        "status": "healthy",
                        "app_name": "resume-clinic-scheduler",
                        "version": "1.0.0",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "checks": {"application": "healthy", "database": "healthy"},
                    }
                }
            },
        },
        500: {
            "description": "依賴檢查失敗",
            "content": {
                "application/json": {
                    "example": {
                        "error": "準備就緒探測檢查失敗",
                        "detail": "資料庫連線失敗，應用程式未準備就緒",
                        "timestamp": "2024-01-01T00:00:00Z",
                    }
                }
            },
        },
    },
)
@handle_api_errors_async()
@log_operation("準備就緒探測檢查")
async def readiness_probe(
    fail: bool = False,
    db_fail: bool = False,
) -> dict[str, Any]:
    """
    準備就緒探測：檢查應用程式所有外部依賴（資料庫、快取等），是否已經準備好處理請求。

    這個端點用於 Kubernetes 的 readiness probe，檢查所有依賴是否就緒。

    Returns:
        dict[str, Any]: 應用程式就緒狀態資訊。
    """
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

    return response_data
