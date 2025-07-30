"""
核心模組

包含應用程式的核心功能，如設定管理、資料庫連接等。
"""

from .settings import Settings, settings, get_project_version 

__all__ = [
    "Settings", "settings", "get_project_version"
] 