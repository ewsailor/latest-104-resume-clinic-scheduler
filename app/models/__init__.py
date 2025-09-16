"""模型模組。

提供所有資料庫模型和相關的資料結構定義。
"""

# ===== 標準函式庫 =====
from typing import Tuple

# ===== 本地模組 =====
# 絕對路徑導入（跨模組）
from app.enums.models import UserRoleEnum

from .database import engine, get_db

# 相對路徑導入（同模組）
# 注意：這裡只導入模型類別，不導入 database 模組以避免循環導入
from .schedule import Schedule
from .user import User

# 延遲導入資料庫組件的函數


def get_database_components() -> Tuple[object, object]:
    """延遲導入資料庫組件以避免循環導入。"""
    return engine, get_db


__all__ = [
    # 模型類別
    "Schedule",
    "User",
    # 相關 ENUM
    "UserRoleEnum",
    # 延遲導入函數
    "get_database_components",
]
