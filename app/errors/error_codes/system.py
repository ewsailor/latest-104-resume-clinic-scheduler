"""
系統層級錯誤代碼。

定義通用系統錯誤代碼，跨層級使用的錯誤代碼。
"""


class SystemErrorCode:
    """通用錯誤代碼 (跨層級使用)"""

    # 500 Internal Server Error - 通用系統錯誤
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 500 - 內部伺服器錯誤

    # 503 Service Unavailable - 通用服務錯誤
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"  # 503 - 服務不可用
