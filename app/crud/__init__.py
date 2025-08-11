"""
CRUD 操作模組。

提供資料庫操作的抽象層，將業務邏輯與資料庫操作分離。

包含：
- 時段 CRUD 操作（schedule_crud）
- 使用者 CRUD 操作（user_crud）
"""

# 匯入所有 CRUD 模組
from .crud_schedule import schedule_crud
from .crud_user import user_crud

# 匯出所有 CRUD 實例
__all__ = ["schedule_crud", "user_crud"]
