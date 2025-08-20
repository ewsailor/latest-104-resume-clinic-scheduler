"""
統一 Enum 定義模組。

集中管理系統中所有的 Enum 定義，包括：
- 資料庫模型相關的 Enum
- 操作相關的 Enum
- API 相關的 Enum
- 驗證相關的 Enum
"""

# 資料庫模型相關的 Enum
from .models import ScheduleStatusEnum, UserRoleEnum

# 操作相關的 Enum
from .operations import AuditAction, OperationContext, ValidationContext

# 匯出所有 Enum
__all__ = [
    # 模型相關
    "UserRoleEnum",
    "ScheduleStatusEnum",
    # 操作相關
    "OperationContext",
    "ValidationContext",
    "AuditAction",
]
