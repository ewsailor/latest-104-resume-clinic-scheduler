"""
CRUD 操作模組。

提供資料庫操作的抽象層，將業務邏輯與資料庫操作分離。
"""

# 匯入所有 CRUD 模組
from app.crud.crud_schedule import schedule_crud

# 匯出所有 CRUD 實例
__all__ = ["schedule_crud"]
