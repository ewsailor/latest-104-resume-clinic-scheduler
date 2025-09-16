"""健康檢查相關的 Pydantic 資料模型。

定義健康檢查 API 的回應模型。
"""

# ===== 標準函式庫 =====
from abc import ABC, abstractmethod
from typing import Any, Dict

# ===== 第三方套件 =====
from pydantic import BaseModel, Field, model_serializer


class HealthCheckBase(BaseModel, ABC):
    """健康檢查基礎模型。"""

    status: str = Field(
        ..., description="健康狀態", json_schema_extra={"example": "healthy"}
    )
    app_name: str = Field(
        ...,
        description="應用程式名稱",
        json_schema_extra={"example": "104 Resume Clinic Scheduler"},
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

    @abstractmethod
    def get_message(self) -> str:
        """取得訊息內容，由子類別實作。"""

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定義序列化方法，確保 message 欄位在最前面。"""
        return {
            "message": self.get_message(),
            "status": self.status,
            "app_name": self.app_name,
            "version": self.version,
            "timestamp": self.timestamp,
            "checks": self.checks,
        }


class HealthCheckLivenessResponse(HealthCheckBase):
    """健康檢查存活探測成功回應模型。"""

    message: str = Field(
        ...,
        description="存活探測訊息",
        json_schema_extra={"example": "應用程式存活、正常運行"},
    )

    def get_message(self) -> str:
        """取得存活探測訊息。"""
        return self.message


class HealthCheckReadinessResponse(HealthCheckBase):
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
            "example": {
                "application": "healthy",
                "database": "healthy",
            }
        },
    )

    def get_message(self) -> str:
        """取得就緒探測訊息。"""
        return self.message
