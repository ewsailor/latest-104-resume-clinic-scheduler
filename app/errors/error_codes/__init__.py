"""
錯誤代碼模組。

整合所有層級的錯誤代碼，提供統一的錯誤代碼管理。
"""

from .cors import CORSErrorCode
from .crud import CRUDErrorCode
from .router import RouterErrorCode
from .service import ServiceErrorCode
from .system import SystemErrorCode


# 整合所有錯誤代碼類別
class ErrorCode:
    """錯誤代碼常數類別 - 整合所有層級的錯誤代碼"""

    # ===== 各層級錯誤代碼類別 =====
    ROUTER = RouterErrorCode
    SERVICE = ServiceErrorCode
    CRUD = CRUDErrorCode
    CORS = CORSErrorCode
    SYSTEM = SystemErrorCode

    # ===== 向後相容性別名 (保持舊的錯誤代碼可用) =====
    VALIDATION_ERROR = RouterErrorCode.VALIDATION_ERROR  # 422 - 資料驗證失敗
    BUSINESS_LOGIC_ERROR = ServiceErrorCode.BUSINESS_LOGIC_ERROR  # 400 - 業務邏輯錯誤
    SCHEDULE_OVERLAP = ServiceErrorCode.SCHEDULE_OVERLAP  # 400 - 時段重疊
    USER_NOT_FOUND = ServiceErrorCode.USER_NOT_FOUND  # 404 - 使用者不存在
    SCHEDULE_NOT_FOUND = ServiceErrorCode.SCHEDULE_NOT_FOUND  # 404 - 時段不存在
    CONFLICT = ServiceErrorCode.CONFLICT  # 409 - 資源衝突
    BAD_REQUEST = RouterErrorCode.BAD_REQUEST  # 400 - 請求格式錯誤
    DATABASE_ERROR = CRUDErrorCode.DATABASE_ERROR  # 500 - 資料庫操作失敗
    AUTHENTICATION_ERROR = RouterErrorCode.AUTHENTICATION_ERROR  # 401 - 認證失敗
    AUTHORIZATION_ERROR = RouterErrorCode.AUTHORIZATION_ERROR  # 403 - 權限不足


# 匯出所有錯誤代碼類別
__all__ = [
    "RouterErrorCode",
    "ServiceErrorCode",
    "CRUDErrorCode",
    "CORSErrorCode",
    "SystemErrorCode",
    "ErrorCode",
]
