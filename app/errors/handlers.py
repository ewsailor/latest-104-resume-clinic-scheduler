"""
錯誤處理輔助函式模組。

提供建立特定錯誤實例的輔助函式。
"""

# ===== 本地模組 =====
from app.errors.exceptions import (
    BusinessLogicError,
    ConflictError,
    ScheduleNotFoundError,
    UserNotFoundError,
)


def create_schedule_not_found_error(schedule_id: int | str) -> ScheduleNotFoundError:
    """建立時段不存在錯誤"""
    return ScheduleNotFoundError(schedule_id)


def create_user_not_found_error(user_id: int | str) -> UserNotFoundError:
    """建立使用者不存在錯誤"""
    return UserNotFoundError(user_id)


def create_schedule_overlap_error() -> ConflictError:
    """建立時段重疊錯誤"""
    return ConflictError("時段重疊")


def create_business_logic_error(message: str) -> BusinessLogicError:
    """建立業務邏輯錯誤"""
    return BusinessLogicError(message)
