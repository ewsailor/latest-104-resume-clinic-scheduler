"""
測試資料相關的整合測試 Fixtures。

提供整合測試用的測試資料和範例物件。
"""

# ===== 標準函式庫 =====
from datetime import date, time, timedelta

# ===== 第三方套件 =====
import pytest  # 測試框架

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.models.schedule import Schedule
from app.models.user import User


@pytest.fixture
def sample_users_data():
    """
    提供範例使用者資料。

    Returns:
        List[Dict[str, Any]]: 範例使用者資料列表
    """
    return [
        {
            "name": "Giver 使用者",
            "email": "giver@example.com",
            "role": UserRoleEnum.GIVER,
        },
        {
            "name": "Taker 使用者",
            "email": "taker@example.com",
            "role": UserRoleEnum.TAKER,
        },
        {
            "name": "系統管理員",
            "email": "admin@example.com",
            "role": UserRoleEnum.ADMIN,
        },
    ]


@pytest.fixture
def sample_schedule_data():
    """
    提供範例時段資料。

    Returns:
        Dict[str, Any]: 範例時段資料
    """
    today = date.today()
    return {
        "giver_id": 1,
        "date": today + timedelta(days=1),
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "status": ScheduleStatusEnum.AVAILABLE,
        "note": "測試時段",
    }


@pytest.fixture
def sample_schedules_data():
    """
    提供多個範例時段資料。

    Returns:
        List[Dict[str, Any]]: 範例時段資料列表
    """
    today = date.today()
    return [
        {
            "giver_id": 1,
            "date": today + timedelta(days=1),
            "start_time": time(9, 0),
            "end_time": time(10, 0),
            "status": ScheduleStatusEnum.AVAILABLE,
            "note": "上午時段",
        },
        {
            "giver_id": 1,
            "date": today + timedelta(days=1),
            "start_time": time(14, 0),
            "end_time": time(15, 0),
            "status": ScheduleStatusEnum.AVAILABLE,
            "note": "下午時段",
        },
        {
            "giver_id": 1,
            "date": today + timedelta(days=2),
            "start_time": time(10, 0),
            "end_time": time(11, 0),
            "status": ScheduleStatusEnum.AVAILABLE,
            "note": "隔天時段",
        },
    ]


@pytest.fixture
def sample_users(integration_db_session, sample_users_data):
    """
    建立範例使用者物件並儲存到資料庫。

    Args:
        integration_db_session: 整合測試用的資料庫會話
        sample_users_data: 範例使用者資料

    Returns:
        Dict[str, User]: 範例使用者物件字典
    """
    users = []

    for user_data in sample_users_data:
        user = User(**user_data)
        integration_db_session.add(user)
        users.append(user)

    integration_db_session.commit()

    # 重新整理物件以獲取 ID
    for user in users:
        integration_db_session.refresh(user)

    return {"giver": users[0], "taker": users[1], "admin": users[2]}


@pytest.fixture
def sample_schedules(integration_db_session, sample_users, sample_schedules_data):
    """
    建立範例時段物件並儲存到資料庫。

    Args:
        integration_db_session: 整合測試用的資料庫會話
        sample_users: 範例使用者物件
        sample_schedules_data: 範例時段資料

    Returns:
        List[Schedule]: 範例時段物件列表
    """
    schedules = []

    for schedule_data in sample_schedules_data:
        schedule = Schedule(**schedule_data)
        integration_db_session.add(schedule)
        schedules.append(schedule)

    integration_db_session.commit()

    # 重新整理物件以獲取 ID
    for schedule in schedules:
        integration_db_session.refresh(schedule)

    return schedules


@pytest.fixture
def overlapping_schedule_data():
    """
    提供重疊時段的測試資料。

    Returns:
        Dict[str, Any]: 重疊時段資料
    """
    today = date.today()
    return {
        "giver_id": 1,
        "date": today + timedelta(days=1),
        "start_time": time(9, 30),  # 與 9:00-10:00 重疊
        "end_time": time(10, 30),
        "status": ScheduleStatusEnum.AVAILABLE,
        "note": "重疊時段",
    }


@pytest.fixture
def booked_schedule_data():
    """
    提供已預約時段的測試資料。

    Returns:
        Dict[str, Any]: 已預約時段資料
    """
    today = date.today()
    return {
        "giver_id": 1,
        "taker_id": 2,
        "date": today + timedelta(days=1),
        "start_time": time(11, 0),
        "end_time": time(12, 0),
        "status": ScheduleStatusEnum.BOOKED,
        "note": "已預約時段",
    }
