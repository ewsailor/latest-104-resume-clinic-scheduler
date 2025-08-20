"""
錯誤代碼常數模組。

定義系統中使用的所有錯誤代碼。
"""


class ErrorCode:
    """錯誤代碼常數類別"""

    # 驗證錯誤
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 422 - 資料驗證失敗

    # 業務邏輯錯誤
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"  # 400 - 業務邏輯錯誤
    SCHEDULE_OVERLAP = "SCHEDULE_OVERLAP"  # 400 - 時段重疊
    USER_NOT_FOUND = "USER_NOT_FOUND"  # 404 - 使用者不存在
    SCHEDULE_NOT_FOUND = "SCHEDULE_NOT_FOUND"  # 404 - 時段不存在

    # 資料庫錯誤
    DATABASE_ERROR = "DATABASE_ERROR"  # 500 - 資料庫操作失敗

    # 系統錯誤
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 500 - 內部伺服器錯誤
