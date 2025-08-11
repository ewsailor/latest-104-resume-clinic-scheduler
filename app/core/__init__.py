"""
核心模組。

提供應用程式的核心功能，包括：
- 應用程式設定管理
- 專案版本資訊
- 環境配置處理

匯入說明：
- 外部模組使用：from app.core import settings
- 內部模組使用：from .settings import Settings
"""

# 使用相對匯入，保持模組獨立性和重構友好性
from .settings import Settings, get_project_version, settings

__all__ = [
    "Settings",  # 設定類別，用於建立自訂設定實例
    "settings",  # 全域設定實例，用於應用程式配置
    "get_project_version",  # 版本號取得函數
]
