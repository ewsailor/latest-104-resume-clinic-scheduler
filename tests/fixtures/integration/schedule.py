"""整合測試時段 fixtures。

提供整合測試用的時段資料和實例。
"""

# ===== 第三方套件 =====
import pytest


@pytest.fixture
def schedule_create_payload():
    """時段建立請求資料。"""
    return {
        "schedules": [
            {
                "giver_id": 1,
                "date": "2024-12-25",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "note": "測試時段",
            }
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def schedule_update_payload():
    """時段更新請求資料。"""
    return {
        "schedule": {
            "start_time": "14:00:00",
            "end_time": "15:00:00",
            "note": "更新後的時段",
        },
        "updated_by": 1,
        "updated_by_role": "GIVER",
    }


@pytest.fixture
def schedule_delete_payload():
    """時段刪除請求資料。"""
    return {"deleted_by": 1, "deleted_by_role": "GIVER"}
