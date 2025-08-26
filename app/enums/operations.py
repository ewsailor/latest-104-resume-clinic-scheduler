"""
操作相關的 ENUM 定義模組。

定義各種操作使用的 ENUM 型別，包括操作上下文、驗證上下文、審計操作等。
"""

# ===== 標準函式庫 =====
from enum import Enum


class OperationContext(str, Enum):
    """操作上下文枚舉"""

    CREATE = "建立"
    UPDATE = "更新"
    DELETE = "刪除"
    DUPLICATE = "複製"  # 未來可能的新操作
    ARCHIVE = "封存"  # 未來可能的新操作


class ValidationContext(str, Enum):
    """驗證上下文枚舉"""

    PRE_SAVE = "儲存前"
    POST_SAVE = "儲存後"
    PRE_DELETE = "刪除前"
    PRE_UPDATE = "更新前"


class AuditAction(str, Enum):
    """審計操作枚舉"""

    CREATE = "建立"
    UPDATE = "更新"
    DELETE = "刪除"
    VIEW = "查看"
    EXPORT = "匯出"
