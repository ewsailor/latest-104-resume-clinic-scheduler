"""錯誤處理輔助函式模組。

提供建立特定錯誤實例的輔助函式。
"""

# ===== 本地模組 =====
from app.errors.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    LivenessCheckError,
    ReadinessCheckError,
    ScheduleNotFoundError,
    ServiceUnavailableError,
    UserNotFoundError,
    ValidationError,
)


# ===== Router 層級錯誤 =====
def create_validation_error(
    message: str,
) -> ValidationError:
    """建立資料驗證錯誤。"""
    return ValidationError(message)


def create_authentication_error(
    message: str,
) -> AuthenticationError:
    """建立認證錯誤。"""
    return AuthenticationError(message)


def create_authorization_error(
    message: str,
) -> AuthorizationError:
    """建立權限錯誤。"""
    return AuthorizationError(message)


# ===== Service 層級錯誤 =====
def create_business_logic_error(
    message: str,
) -> BusinessLogicError:
    """建立業務邏輯錯誤。"""
    return BusinessLogicError(message)


def create_schedule_not_found_error(
    schedule_id: int | str,
) -> ScheduleNotFoundError:
    """建立時段不存在錯誤。"""
    return ScheduleNotFoundError(schedule_id)


def create_user_not_found_error(
    user_id: int | str,
) -> UserNotFoundError:
    """建立使用者不存在錯誤。"""
    return UserNotFoundError(user_id)


def create_schedule_overlap_error(
    schedule_id: int | str,
) -> ConflictError:
    """建立時段重疊錯誤。"""
    return ConflictError(f"時段重疊: ID={schedule_id}")


# ===== CRUD 層級錯誤 =====
def create_database_error(
    message: str,
) -> DatabaseError:
    """建立資料庫錯誤。"""
    return DatabaseError(message)


# ===== System 層級錯誤 =====
def create_service_unavailable_error(
    message: str,
) -> ServiceUnavailableError:
    """建立服務不可用錯誤。"""
    return ServiceUnavailableError(message)


def create_liveness_check_error(
    message: str,
) -> LivenessCheckError:
    """建立存活檢查錯誤。"""
    return LivenessCheckError(message)


def create_readiness_check_error(
    message: str,
) -> ReadinessCheckError:
    """建立準備就緒檢查錯誤。"""
    return ReadinessCheckError(message)
