"""
資料驗證模式模組。

提供所有 Pydantic 資料模型的統一導入點，用於：
- API 請求資料驗證
- 回應資料序列化
- 資料型別安全保證

包含：
- 時段相關模式（ScheduleData, ScheduleResponse 等）
- 使用者相關模式（UserCreate, UserResponse 等）
"""

from .schedule import (
    ScheduleCreateRequest,
    ScheduleData,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleResponse,
    ScheduleUpdateData,
    ScheduleUpdateRequest,
)
from .user import UserCreate, UserResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "ScheduleData",
    "ScheduleCreateRequest",
    "ScheduleUpdateData",
    "ScheduleUpdateRequest",
    "SchedulePartialUpdateRequest",
    "ScheduleDeleteRequest",
    "ScheduleResponse",
]
