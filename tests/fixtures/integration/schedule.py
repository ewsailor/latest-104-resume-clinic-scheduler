"""整合測試時段 fixtures。

提供整合測試用的時段資料和實例。

注意：這些 fixtures 使用記憶體資料庫，確保測試隔離和執行速度。
使用 Set 資料型別，避免重複問題。
"""

# ===== 標準函式庫 =====
from datetime import date, time
import random

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.models.schedule import Schedule
from app.models.user import User

# 全域 Set 避免時段重複問題
_used_time_slots = set()


def _generate_unique_time_slot():
    """生成唯一的時間槽，避免與已使用的時間重複。

    Returns:
        tuple: (date_str, start_time_str, end_time_str, giver_id)
    """
    while True:
        # 生成隨機的日期和時間
        year = 2024
        month = random.randint(6, 12)  # 6-12月避免重複
        day = random.randint(1, 28)  # 避免月末問題

        hour = random.randint(8, 22)  # 8-22點
        minute = random.randint(0, 59)
        duration = random.randint(1, 3)  # 1-3小時

        date_str = f"{year}-{month:02d}-{day:02d}"
        start_time_str = f"{hour:02d}:{minute:02d}:00"

        # 計算結束時間
        end_hour = hour + duration
        if end_hour >= 24:
            end_hour = 23
        end_time_str = f"{end_hour:02d}:{minute:02d}:00"

        giver_id = random.randint(1, 10)  # 不同的 giver_id

        time_slot = (date_str, start_time_str, end_time_str, giver_id)

        if time_slot not in _used_time_slots:
            _used_time_slots.add(time_slot)
            return time_slot


@pytest.fixture
def sample_schedule_payload():
    """單一合法時段的輸入資料。

    用於測試單一時段的建立、更新等操作。
    使用唯一時間槽避免重複問題。

    Returns:
        dict: 包含單一時段資料的字典，符合 API 格式
    """
    date_str, start_time_str, end_time_str, giver_id = _generate_unique_time_slot()

    return {
        "schedules": [
            {
                "giver_id": giver_id,
                "date": date_str,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "note": "測試時段",
            }
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def multiple_schedules_payload():
    """多筆合法時段的輸入資料。

    用於測試建立多筆時段的功能。

    Returns:
        dict: 包含多筆時段資料的字典，符合 API 格式
    """
    schedules = []
    for i in range(3):
        date_str, start_time_str, end_time_str, giver_id = _generate_unique_time_slot()
        schedules.append(
            {
                "giver_id": giver_id,
                "date": date_str,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "note": f"批次時段{i+1}",
            }
        )

    return {
        "schedules": schedules,
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def schedule_data():
    """通用時段資料，用於一般測試場景。

    Returns:
        dict: 包含時段資料的字典，符合 API 格式
    """
    date_str, start_time_str, end_time_str, giver_id = _generate_unique_time_slot()

    return {
        "schedules": [
            {
                "giver_id": giver_id,
                "date": date_str,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "note": "通用測試時段",
            }
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def seed_schedules(integration_db_session):
    """事先在 DB 建立好的時段，用於查詢/刪除測試。

    這些時段會實際寫入測試資料庫，用於測試查詢、更新、刪除等操作。
    使用唯一時間槽避免重複問題。

    Args:
        integration_db_session: 測試資料庫會話

    Returns:
        list[dict]: 已建立的時段資料列表
    """
    # 首先建立測試用戶
    test_users = []
    for i in range(1, 3):  # 建立 2 個用戶
        user = User(name=f"測試用戶{i}", email=f"test{i}@example.com")
        integration_db_session.add(user)
        integration_db_session.flush()  # 取得 ID
        test_users.append(user)

    # 建立時段資料
    created_schedules = []
    for i in range(2):
        date_str, start_time_str, end_time_str, giver_id = _generate_unique_time_slot()

        # 解析日期和時間
        schedule_date = date.fromisoformat(date_str)
        start_time = time.fromisoformat(start_time_str)
        end_time = time.fromisoformat(end_time_str)

        # 建立時段記錄
        schedule = Schedule(
            giver_id=test_users[i].id,  # 使用實際的用戶 ID
            date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            note=f"已建立的時段{i+1}",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=test_users[i].id,
            created_by_role=UserRoleEnum.GIVER,
            updated_by=test_users[i].id,
            updated_by_role=UserRoleEnum.GIVER,
        )

        integration_db_session.add(schedule)
        integration_db_session.flush()  # 取得 ID

        # 返回時段資料字典
        created_schedules.append(
            {
                "id": schedule.id,
                "giver_id": schedule.giver_id,
                "date": date_str,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "note": schedule.note,
                "status": "AVAILABLE",
            }
        )

    # 提交所有變更
    integration_db_session.commit()

    return created_schedules


@pytest.fixture
def overlap_schedule_payload():
    """與 seed_schedules 衝突的時段 payload。

    用於測試時段重疊檢查功能。

    Returns:
        dict: 包含重疊時段資料的字典，符合 API 格式
    """
    return {
        "schedules": [
            {
                "giver_id": 1,
                "date": "2024-01-01",  # 與 seed_schedules 相同的日期
                "start_time": "09:30:00",  # 與 seed_schedules 時段重疊
                "end_time": "10:30:00",
                "note": "重疊時段",
            }
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def db_constraint_payload():
    """會違反 DB unique constraint 的 payload。

    用於測試資料庫約束檢查功能。

    Returns:
        dict: 包含違反約束的時段資料的字典
    """
    return {
        "schedules": [
            {
                "giver_id": 1,
                "date": "2024-01-01",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "note": "約束測試時段",
            },
            {
                "giver_id": 1,
                "date": "2024-01-01",
                "start_time": "09:00:00",  # 完全相同，違反唯一約束
                "end_time": "10:00:00",
                "note": "重複時段",
            },
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }
