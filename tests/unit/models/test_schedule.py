"""
Schedule 模型單元測試。

測試 Schedule 模型的基本屬性、方法和業務邏輯。
專注於單一模型的功能，不涉及資料庫關係。
"""

# ===== 標準函式庫 =====
from datetime import date, datetime, time

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum
from app.models.schedule import Schedule

# ===== 第三方套件 =====


class TestScheduleModel:
    """Schedule 模型單元測試類別。"""

    def test_schedule_creation(self):
        """測試 Schedule 實例創建。"""
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
        )

        # 測試基本屬性
        assert schedule.giver_id == 1
        assert schedule.taker_id is None
        assert schedule.date == date(2024, 1, 15)
        assert schedule.start_time == time(9, 0)
        assert schedule.end_time == time(10, 0)
        assert schedule.note == "測試時段"
        assert schedule.deleted_at is None

    def test_schedule_default_values(self):
        """測試 Schedule 預設值。"""
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        # 測試預設值
        assert schedule.taker_id is None
        assert schedule.note is None
        assert schedule.deleted_at is None

    def test_schedule_properties(self):
        """測試 Schedule 屬性方法。"""
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        # 測試 is_active
        assert schedule.is_active is True
        schedule.deleted_at = datetime.now()
        assert schedule.is_active is False

        # 測試 is_deleted
        assert schedule.is_deleted is True
        schedule.deleted_at = None
        assert schedule.is_deleted is False

        # 測試 is_available
        schedule.status = ScheduleStatusEnum.AVAILABLE
        schedule.taker_id = None
        assert schedule.is_available is True

        schedule.taker_id = 2
        assert schedule.is_available is False

        schedule.status = ScheduleStatusEnum.DRAFT
        assert schedule.is_available is False

    def test_schedule_status_logic(self):
        """測試時段狀態邏輯。"""
        schedule = Schedule(giver_id=1, taker_id=None)

        # 測試 AVAILABLE 狀態
        schedule.status = ScheduleStatusEnum.AVAILABLE
        assert schedule.is_available is True

        # 測試 PENDING 狀態
        schedule.status = ScheduleStatusEnum.PENDING
        assert schedule.is_available is False

        # 測試 ACCEPTED 狀態
        schedule.status = ScheduleStatusEnum.ACCEPTED
        assert schedule.is_available is False

    def test_schedule_taker_logic(self):
        """測試時段 Taker 邏輯。"""
        schedule = Schedule(giver_id=1, taker_id=None)
        schedule.status = ScheduleStatusEnum.AVAILABLE

        # 沒有 Taker 時可預約
        assert schedule.is_available is True

        # 有 Taker 時不可預約
        schedule.taker_id = 2
        assert schedule.is_available is False

    def test_schedule_repr(self):
        """測試 Schedule 字串表示。"""
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        repr_str = repr(schedule)
        assert "Schedule" in repr_str
        assert "giver_id=1" in repr_str
        assert "date=2024-01-15" in repr_str

    def test_schedule_to_dict(self):
        """測試 Schedule to_dict 方法。"""
        schedule = Schedule(
            giver_id=1,
            taker_id=2,
            status=ScheduleStatusEnum.AVAILABLE,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
        )

        result = schedule.to_dict()

        assert isinstance(result, dict)
        assert result["giver_id"] == 1
        assert result["taker_id"] == 2
        assert result["status"] == ScheduleStatusEnum.AVAILABLE
        assert result["date"] == "2024-01-15"
        assert result["start_time"] == "09:00:00"
        assert result["end_time"] == "10:00:00"
        assert result["note"] == "測試時段"
        assert result["is_active"] is True
        assert result["is_deleted"] is False
        assert result["is_available"] is False  # 有 taker_id 所以不可用
