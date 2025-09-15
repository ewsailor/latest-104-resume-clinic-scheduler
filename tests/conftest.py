"""
測試配置檔案。

設定 pytest 的共用配置和 fixture。
"""

# ===== 第三方套件 =====
import pytest  # 測試框架

# ===== 本地模組 =====
# 導入單元測試的 fixtures
from tests.unit.fixtures.database import db_session  # noqa: F401

# 確保 pytest-mock 可用
pytest_plugins = ["pytest_mock"]
