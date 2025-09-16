"""
測試配置檔案。

設定 pytest 的共用配置和 fixture。
"""

# ===== 第三方套件 =====
import pytest  # 測試框架

from tests.integration.fixtures.api import (  # noqa: F401
    integration_app,
    integration_client,
    integration_client_with_cleanup,
)

# 導入整合測試的 fixtures
from tests.integration.fixtures.database import (  # noqa: F401
    integration_db_engine,
    integration_db_session,
    integration_db_session_with_rollback,
)
from tests.integration.fixtures.services import (  # noqa: F401
    schedule_service,
    schedule_service_with_session,
)
from tests.integration.fixtures.test_data import (  # noqa: F401
    booked_schedule_data,
    overlapping_schedule_data,
    sample_schedule_data,
    sample_schedules,
    sample_schedules_data,
    sample_users,
    sample_users_data,
)

# ===== 本地模組 =====
# 導入單元測試的 fixtures
from tests.unit.fixtures.database import db_session  # noqa: F401

# 確保 pytest-mock 可用
pytest_plugins = ["pytest_mock"]
