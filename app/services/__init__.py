"""
服務層模組。

提供業務邏輯處理服務，包括時段管理、使用者管理等。
"""

# ===== 本地模組 =====
from .schedule import ScheduleService, schedule_service
from .user import UserService, user_service

__all__ = [
    # 時段管理服務
    "ScheduleService",
    "schedule_service",
    # 使用者管理服務
    "UserService",
    "user_service",
]
