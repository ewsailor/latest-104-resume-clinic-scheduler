"""
服務層相關的整合測試 Fixtures。

提供整合測試用的服務實例和相關工具。
"""

# ===== 第三方套件 =====
import pytest  # 測試框架

# ===== 本地模組 =====
from app.services.schedule import ScheduleService


@pytest.fixture
def schedule_service():
    """
    提供 ScheduleService 實例。

    Returns:
        ScheduleService: 整合測試用的時段服務實例
    """
    return ScheduleService()


@pytest.fixture
def schedule_service_with_session(integration_db_session):
    """
    提供帶有資料庫會話的 ScheduleService 實例。

    Args:
        integration_db_session: 整合測試用的資料庫會話

    Returns:
        ScheduleService: 帶有資料庫會話的時段服務實例
    """
    service = ScheduleService()
    # 可以在這裡設定服務的資料庫會話，如果需要的话
    return service
