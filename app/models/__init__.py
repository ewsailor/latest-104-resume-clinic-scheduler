"""
模型模組。

提供所有資料庫模型和相關的資料結構定義。
"""

# 絕對路徑導入（跨模組）
from app.enums.models import UserRoleEnum  # 避免循環導入

# 相對路徑導入（同模組）
from .database import engine, get_db
from .schedule import Schedule
from .user import User

__all__ = [
    "get_db",
    "engine",
    "UserRoleEnum",
    "Schedule",
    "User",
]
