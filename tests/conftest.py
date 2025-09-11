"""
測試配置檔案。

設定 pytest 的共用配置和 fixture。
"""

# ===== 標準函式庫 =====
import pytest  # 測試框架

# 確保 pytest-mock 可用
pytest_plugins = ["pytest_mock"]

# 導入單元測試的 fixtures
from tests.unit.fixtures.database import db_session  # noqa: F401
