"""健康檢查相關的 Pydantic 資料模型。

定義健康檢查 API 的回應模型。
"""

# ===== 標準函式庫 =====
from typing import Any, Dict

# ===== 第三方套件 =====
from pydantic import BaseModel, Field

# ===== 本地模組 =====
# 不需要導入 APIError，因為我們會使用字典來表示錯誤結構


# ===== 健康檢查回應模型 =====
class HealthCheckBaseResponse(BaseModel):
    """健康檢查回應基礎模型。"""

    status: str = Field(
        ..., description="健康狀態", json_schema_extra={"example": "healthy"}
    )
    app_name: str = Field(
        ...,
        description="應用程式名稱",
        json_schema_extra={"example": "【MVP】104 Resume Clinic Scheduler"},
    )
    version: str = Field(
        ..., description="應用程式版本", json_schema_extra={"example": "0.1.0"}
    )
    timestamp: str = Field(
        ...,
        description="檢查時間戳（UTC）",
        json_schema_extra={"example": "2024-01-01T00:00:00Z"},
    )
    checks: Dict[str, str] = Field(
        ...,
        description="各項檢查結果",
        json_schema_extra={"example": {"application": "healthy"}},
    )

    model_config = {"from_attributes": True}


class HealthCheckLivenessResponse(HealthCheckBaseResponse):
    """健康檢查存活探測成功回應模型。"""

    message: str = Field(..., description="存活探測訊息")


class HealthCheckReadinessResponse(HealthCheckBaseResponse):
    """健康檢查就緒探測成功回應模型。"""

    message: str = Field(
        ...,
        description="就緒探測訊息",
        json_schema_extra={"example": "應用程式準備就緒"},
    )

    # 覆寫 checks 欄位的範例，因為就緒探測包含更多檢查項目
    checks: Dict[str, str] = Field(
        ...,
        description="各項檢查結果",
        json_schema_extra={
            "example": {"application": "healthy", "database": "healthy"}
        },
    )


class HealthCheckErrorResponse(BaseModel):
    """健康檢查錯誤回應模型。"""

    error: Dict[str, Any] = Field(
        ...,
        description="錯誤資訊",
        json_schema_extra={
            "example": {
                "message": "準備就緒探測檢查錯誤：應用程式未準備就緒",
                "status_code": 503,
                "code": "READINESS_CHECK_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {},
            }
        },
    )

    model_config = {"from_attributes": True}


class ValidationErrorResponse(BaseModel):
    """參數驗證錯誤回應模型。"""

    error: Dict[str, Any] = Field(
        ...,
        description="驗證錯誤資訊",
        json_schema_extra={
            "example": {
                "message": "參數驗證錯誤",
                "status_code": 422,
                "code": "VALIDATION_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {
                    "fail": "參數類型錯誤，應為布林值",
                    "db_fail": "參數類型錯誤，應為布林值",
                },
            }
        },
    )

    model_config = {"from_attributes": True}
