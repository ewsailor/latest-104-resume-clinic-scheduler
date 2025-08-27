"""核心模組。

提供應用程式的核心功能，包括：
- 應用程式設定管理
- 專案版本資訊
- 環境配置處理

匯入說明：
- 外部模組使用：from app.core import settings
- 內部模組使用：from .settings import Settings
"""

# ===== 本地模組 =====
from .settings import Settings, get_project_version, settings

__all__ = [
    # 設定管理
    "Settings",
    "settings",
    "get_project_version",
]
