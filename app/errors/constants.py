"""
錯誤代碼常數模組。

定義系統中使用的所有錯誤代碼，按架構層級分類。
"""


class RouterErrorCode:
    """Routers 層級錯誤代碼 (API 路由層)"""

    # 400 Bad Request - 路由層請求錯誤
    BAD_REQUEST = "ROUTER_BAD_REQUEST"  # 400 - 路由參數格式錯誤
    INVALID_METHOD = "ROUTER_INVALID_METHOD"  # 400 - 不支援的 HTTP 方法

    # 401 Unauthorized - 路由層認證錯誤
    AUTHENTICATION_ERROR = "ROUTER_AUTHENTICATION_ERROR"  # 401 - 路由層認證失敗

    # 403 Forbidden - 路由層權限錯誤
    AUTHORIZATION_ERROR = "ROUTER_AUTHORIZATION_ERROR"  # 403 - 路由層權限不足

    # 404 Not Found - 路由層資源錯誤
    ENDPOINT_NOT_FOUND = "ROUTER_ENDPOINT_NOT_FOUND"  # 404 - API 端點不存在

    # 422 Unprocessable Entity - 路由層驗證錯誤
    VALIDATION_ERROR = "ROUTER_VALIDATION_ERROR"  # 422 - 路由層資料驗證失敗


class ServiceErrorCode:
    """Service 層級錯誤代碼 (業務邏輯層)"""

    # 400 Bad Request - 服務層業務錯誤
    BUSINESS_LOGIC_ERROR = "SERVICE_BUSINESS_LOGIC_ERROR"  # 400 - 業務邏輯錯誤
    SCHEDULE_OVERLAP = "SERVICE_SCHEDULE_OVERLAP"  # 400 - 時段重疊
    INVALID_OPERATION = "SERVICE_INVALID_OPERATION"  # 400 - 無效操作

    # 404 Not Found - 服務層資源錯誤
    USER_NOT_FOUND = "SERVICE_USER_NOT_FOUND"  # 404 - 使用者不存在
    SCHEDULE_NOT_FOUND = "SERVICE_SCHEDULE_NOT_FOUND"  # 404 - 時段不存在

    # 409 Conflict - 服務層衝突錯誤
    CONFLICT = "SERVICE_CONFLICT"  # 409 - 業務邏輯衝突（如重複 email）


class CRUDErrorCode:
    """CRUD 層級錯誤代碼 (資料存取層)"""

    # 400 Bad Request - CRUD 層請求錯誤
    BAD_REQUEST = "CRUD_BAD_REQUEST"  # 400 - CRUD 操作參數錯誤

    # 404 Not Found - CRUD 層資源錯誤
    RECORD_NOT_FOUND = "CRUD_RECORD_NOT_FOUND"  # 404 - 資料庫記錄不存在

    # 409 Conflict - CRUD 層衝突錯誤
    CONSTRAINT_VIOLATION = "CRUD_CONSTRAINT_VIOLATION"  # 409 - 資料庫約束違反

    # 500 Internal Server Error - CRUD 層資料庫錯誤
    DATABASE_ERROR = "CRUD_DATABASE_ERROR"  # 500 - 資料庫操作失敗
    CONNECTION_ERROR = "CRUD_CONNECTION_ERROR"  # 500 - 資料庫連線錯誤


class CORSErrorCode:
    """CORS 層級錯誤代碼 (跨域請求層)"""

    # 403 Forbidden - CORS 層權限錯誤
    ORIGIN_NOT_ALLOWED = "CORS_ORIGIN_NOT_ALLOWED"  # 403 - 來源網域不被允許
    METHOD_NOT_ALLOWED = "CORS_METHOD_NOT_ALLOWED"  # 403 - HTTP 方法不被允許
    HEADER_NOT_ALLOWED = "CORS_HEADER_NOT_ALLOWED"  # 403 - 請求標頭不被允許


class SystemErrorCode:
    """通用錯誤代碼 (跨層級使用)"""

    # 500 Internal Server Error - 通用系統錯誤
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 500 - 內部伺服器錯誤

    # 503 Service Unavailable - 通用服務錯誤
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"  # 503 - 服務不可用


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
