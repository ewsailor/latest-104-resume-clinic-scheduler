"""
錯誤代碼常數模組。

此模組已重構為模組化結構，現在從 error_codes 子模組匯入所有錯誤代碼。
為保持向後相容性，此檔案仍然提供相同的介面。
"""

# 從新的模組化結構匯入所有錯誤代碼
from .error_codes import (
    CORSErrorCode,
    CRUDErrorCode,
    ErrorCode,
    RouterErrorCode,
    ServiceErrorCode,
    SystemErrorCode,
)

# 向後相容性匯出
__all__ = [
    "RouterErrorCode",
    "ServiceErrorCode",
    "CRUDErrorCode",
    "CORSErrorCode",
    "SystemErrorCode",
    "ErrorCode",
]
