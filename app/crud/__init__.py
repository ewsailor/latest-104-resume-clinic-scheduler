"""
CRUD 操作模組。

提供資料庫操作的抽象層，將業務邏輯與資料庫操作分離。

包含：
- 時段 CRUD 操作（schedule_crud）
- 使用者 CRUD 操作（user_crud）
"""

# 絕對路徑導入（跨模組）
from app.enums.operations import (  # 避免循環導入
    AuditAction,
    OperationContext,
    ValidationContext,
)

# 相對路徑導入（同模組）
from .schedule import schedule_crud
from .user import user_crud

# 匯出所有 CRUD 實例和 ENUM
__all__ = [
    "schedule_crud",
    "user_crud",
    "OperationContext",
    "ValidationContext",
    "AuditAction",
]
