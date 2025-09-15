"""資料驗證模式模組。

提供所有 Pydantic 資料模型的統一導入點，用於：
- API 請求資料驗證
- 回應資料序列化
- 資料型別安全保證

包含：
- 時段相關模式（ScheduleBase, ScheduleResponse 等）
"""

# ===== 本地模組 =====
from .health import (
    HealthCheckBaseResponse,
    HealthCheckLivenessResponse,
    HealthCheckReadinessResponse,
)
from .schedule import (
    ScheduleBase,
    ScheduleCreateRequest,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleResponse,
    ScheduleUpdateBase,
    ScheduleUpdateRequest,
)

__all__ = [
    # 健康檢查相關模式
    "HealthCheckBaseResponse",
    "HealthCheckLivenessResponse",
    "HealthCheckReadinessResponse",
    # 時段相關模式
    "ScheduleBase",
    "ScheduleCreateRequest",
    "ScheduleUpdateBase",
    "ScheduleUpdateRequest",
    "SchedulePartialUpdateRequest",
    "ScheduleDeleteRequest",
    "ScheduleResponse",
]
