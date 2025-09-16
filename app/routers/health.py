"""健康檢查路由模組。

包含存活探測和準備就緒探測等端點。
"""

# ===== 第三方套件 =====
from fastapi import APIRouter, status

# ===== 本地模組 =====
from app.core import get_project_version, settings
from app.database import check_db_connection
from app.decorators import handle_api_errors_async, log_operation
from app.errors import create_liveness_check_error, create_readiness_check_error
from app.schemas import HealthCheckLivenessResponse, HealthCheckReadinessResponse
from app.utils.timezone import get_utc_timestamp

router = APIRouter(tags=["Health Check"])


@router.get(
    "/healthz",
    response_model=HealthCheckLivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="存活探測檢查",
    description="""
## 功能簡介
- 檢查應用程式是否存活、正在運行，用於 Kubernetes 的 liveness probe
- 不包含外部依資料庫、快取等檢查
- 僅檢查應用程式進程狀態

### 使用場景
- Kubernetes 容器健康檢查
- 負載平衡器健康檢查
- 應用程式監控系統

### 測試參數
- `fail=true`: 模擬存活探測檢查錯誤

### 回應狀態
- **200 OK**: 應用程式存活、正常運行
- **422 Unprocessable Entity**: 參數驗證錯誤
- **500 Internal Server Error**: 存活探測檢查錯誤：應用程式異常、未正常運行
    """,
    responses={
        200: {
            "description": "應用程式存活、正常運行",
            "content": {
                "application/json": {
                    "example": {
                        "message": "應用程式存活、正常運行",
                        "status": "healthy",
                        "app_name": "104 Resume Clinic Scheduler",
                        "version": "0.1.0",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "checks": {"application": "healthy"},
                    }
                }
            },
        },
        422: {
            "description": "參數驗證錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "參數驗證錯誤",
                            "status_code": 422,
                            "code": "VALIDATION_ERROR",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "details": {"fail": "參數類型錯誤，應為布林值"},
                        }
                    }
                }
            },
        },
        500: {
            "description": "存活探測檢查錯誤：應用程式異常、未正常運行",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "存活探測檢查錯誤：應用程式異常、未正常運行",
                            "status_code": 500,
                            "code": "LIVENESS_CHECK_ERROR",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "details": {},
                        }
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
) -> HealthCheckLivenessResponse:
    """存活探測：用於 Kubernetes 的 liveness probe，檢查應用程式是否存活、正在運行。
    不包含外部依資料庫、快取等檢查，只檢查應用程式進程狀態。

    Args:
        fail: 存活探測檢查錯誤，應用程式異常、未正常運行。

    Returns:
        HealthCheckLivenessResponse: 應用程式狀態資訊，包含狀態、時間戳、版本等資訊。
    """
    if fail:
        raise create_liveness_check_error("存活探測檢查錯誤：應用程式異常、未正常運行")

    return HealthCheckLivenessResponse(
        message="應用程式存活、正常運行",
        status="healthy",
        app_name=settings.app_name,
        version=get_project_version(),
        timestamp=get_utc_timestamp(),
        checks={
            "application": "healthy",
        },
    )


@router.get(
    "/readyz",
    response_model=HealthCheckReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="準備就緒探測檢查",
    description="""
## 功能簡介
- 檢查應用程式所有外部依賴，是否已準備好處理請求，用於 Kubernetes 的 readiness probe
- 外部依賴如資料庫、快取、外部 API 等
- 檢查應用程式進程狀態、資料庫連線、基本查詢，如連線失敗會拋出異常

### 使用場景
- Kubernetes 容器就緒檢查
- 藍綠部署時的流量切換
- 負載平衡器流量分配

### 檢查項目
- **應用程式**: 檢查應用程式進程狀態
- **資料庫**: 檢查資料庫連線和基本查詢
- **快取** (未來): 檢查 Redis 連線狀態
- **外部 API** (未來): 檢查關鍵外部服務連線

### 測試參數
- `fail=true`: 準備就緒探測檢查錯誤
- `db_fail=true`: 資料庫連線失敗錯誤

### 回應狀態
- **200 OK**: 應用程式準備就緒
- **422 Unprocessable Entity**: 參數驗證錯誤
- **503 Service Unavailable**: 準備就緒探測檢查錯誤：應用程式未準備就緒
    """,
    responses={
        200: {
            "description": "應用程式準備就緒",
            "content": {
                "application/json": {
                    "example": {
                        "message": "應用程式準備就緒",
                        "status": "healthy",
                        "app_name": "104 Resume Clinic Scheduler",
                        "version": "0.1.0",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "checks": {
                            "application": "healthy",
                            "database": "healthy",
                        },
                    }
                }
            },
        },
        422: {
            "description": "參數驗證錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "參數驗證錯誤",
                            "status_code": 422,
                            "code": "VALIDATION_ERROR",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "details": {
                                "fail": "參數類型錯誤，應為布林值",
                                "db_fail": "參數類型錯誤，應為布林值",
                            },
                        }
                    }
                }
            },
        },
        503: {
            "description": "準備就緒探測檢查錯誤：應用程式未準備就緒",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "準備就緒探測檢查錯誤：應用程式未準備就緒",
                            "status_code": 503,
                            "code": "READINESS_CHECK_ERROR",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "details": {},
                        }
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
) -> HealthCheckReadinessResponse:
    """準備就緒探測：用於 Kubernetes 的 readiness probe，檢查應用程式所有外部依賴如資料庫、快取、外部 API 等，是否已經準備好處理請求。

    Args:
        fail: 準備就緒探測檢查錯誤。
        db_fail: 資料庫連線失敗錯誤。

    Returns:
        HealthCheckReadinessResponse: 應用程式就緒狀態資訊，包含狀態、時間戳、版本等資訊。
    """
    if fail:
        raise create_readiness_check_error("準備就緒探測檢查錯誤")

    if db_fail:
        raise create_readiness_check_error("資料庫連線失敗錯誤")

    # 檢查真實資料庫連線（如果連線失敗會拋出異常）
    try:
        check_db_connection()
    except Exception as e:
        raise create_readiness_check_error(f"資料庫連線失敗: {str(e)}")

    return HealthCheckReadinessResponse(
        message="應用程式準備就緒",
        status="healthy",
        app_name=settings.app_name,
        version=get_project_version(),
        timestamp=get_utc_timestamp(),
        checks={
            "application": "healthy",
            "database": "healthy",
            # "redis": "healthy",  # 未來可加入
            # "external_api": "healthy"  # 未來可加入
        },
    )
