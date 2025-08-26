"""
錯誤處理輔助函式模組。

提供建立特定錯誤實例的輔助函式。
"""

# ===== 本地模組 =====
from app.errors.exceptions import (
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    LivenessCheckError,
    ReadinessCheckError,
    ScheduleNotFoundError,
    ServiceUnavailableError,
    UserNotFoundError,
)

# ===== Router 層級錯誤 =====
# 目前沒有 Router 層級的錯誤處理函式


# ===== Service 層級錯誤 =====
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


# ===== CRUD 層級錯誤 =====
def create_database_error(message: str) -> DatabaseError:
    """建立資料庫錯誤"""
    return DatabaseError(message)


# ===== System 層級錯誤 =====
def create_liveness_check_error(message: str) -> LivenessCheckError:
    """建立存活檢查錯誤"""
    return LivenessCheckError(message)


def create_readiness_check_error(message: str) -> ReadinessCheckError:
    """建立準備就緒檢查錯誤"""
    return ReadinessCheckError(message)


def create_service_unavailable_error(message: str) -> ServiceUnavailableError:
    """建立服務不可用錯誤"""
    return ServiceUnavailableError(message)
