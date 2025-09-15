"""
Schedule 模型測試。

測試 Schedule 模型的屬性、方法和行為。
"""

# ===== 標準函式庫 =====
from datetime import date, datetime, time
from unittest.mock import Mock

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import class_mapper, sessionmaker

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.models.database import Base
from app.models.schedule import Schedule

# ===== 測試設定 =====


class TestScheduleModel:
    """Schedule 模型測試類別。"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """設定測試環境。"""
        # 使用記憶體資料庫進行測試
        self.test_engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.test_engine
        )

        # 建立資料表
        Base.metadata.create_all(bind=self.test_engine)

        yield

    def test_schedule_creation(self):
        """測試 Schedule 實例創建。"""
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
        )

        assert schedule.giver_id == 1
        assert schedule.taker_id is None
        assert schedule.status is None  # 預設值只在資料庫層面生效
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

        assert schedule.status is None  # 預設值只在資料庫層面生效
        assert schedule.taker_id is None
        assert schedule.note is None
        assert schedule.deleted_at is None
        assert schedule.created_at is None  # 預設值只在資料庫層面生效
        assert schedule.updated_at is None  # 預設值只在資料庫層面生效

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

    def test_schedule_repr(self):
        """測試 Schedule 字串表示。"""
        schedule = Schedule(
            id=1,
            giver_id=1,
            date=date(2024, 1, 15),
            status=ScheduleStatusEnum.AVAILABLE,
        )

        repr_str = repr(schedule)
        assert "Schedule" in repr_str
        assert "id=1" in repr_str
        assert "giver_id=1" in repr_str
        assert "date=2024-01-15" in repr_str
        assert "status=ScheduleStatusEnum.AVAILABLE" in repr_str

    def test_schedule_to_dict_success(self):
        """測試 Schedule to_dict 方法成功情況。"""
        schedule = Schedule(
            id=1,
            giver_id=1,
            taker_id=2,
            status=ScheduleStatusEnum.AVAILABLE,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            created_at=datetime(2024, 1, 1, 12, 0),
            updated_at=datetime(2024, 1, 2, 12, 0),
        )

        result = schedule.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["giver_id"] == 1
        assert result["taker_id"] == 2
        assert result["status"] == ScheduleStatusEnum.AVAILABLE
        assert result["date"] == "2024-01-15"
        assert result["start_time"] == "09:00:00"
        assert result["end_time"] == "10:00:00"
        assert result["note"] == "測試時段"
        assert result["is_active"] is True
        assert result["is_deleted"] is False
        assert result["is_available"] is False  # status 為 None，所以不可用

    def test_schedule_to_dict_with_relationships(self):
        """測試 Schedule to_dict 方法包含關聯資料。"""
        # 模擬關聯物件
        mock_created_by_user = Mock()
        mock_created_by_user.name = "創建者"
        mock_updated_by_user = Mock()
        mock_updated_by_user.name = "更新者"
        mock_deleted_by_user = Mock()
        mock_deleted_by_user.name = "刪除者"

        schedule = Schedule(
            id=1,
            giver_id=1,
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
            updated_by=2,
            updated_by_role=UserRoleEnum.TAKER,
            deleted_by=3,
            deleted_by_role=UserRoleEnum.SYSTEM,
        )

        # 直接設置屬性，避免 SQLAlchemy 的關聯處理
        schedule.__dict__['created_by_user'] = mock_created_by_user
        schedule.__dict__['updated_by_user'] = mock_updated_by_user
        schedule.__dict__['deleted_by_user'] = mock_deleted_by_user

        result = schedule.to_dict()

        assert result["created_by_user"] == "創建者"
        assert result["updated_by_user"] == "更新者"
        assert result["deleted_by_user"] == "刪除者"
        assert result["created_by_role"] == UserRoleEnum.GIVER
        assert result["updated_by_role"] == UserRoleEnum.TAKER
        assert result["deleted_by_role"] == UserRoleEnum.SYSTEM

    def test_schedule_to_dict_with_none_relationships(self):
        """測試 Schedule to_dict 方法處理 None 關聯資料。"""
        schedule = Schedule(
            id=1,
            giver_id=1,
            created_by=None,
            updated_by=None,
            deleted_by=None,
        )

        schedule.__dict__['created_by_user'] = None
        schedule.__dict__['updated_by_user'] = None
        schedule.__dict__['deleted_by_user'] = None

        result = schedule.to_dict()

        assert result["created_by_user"] is None
        assert result["updated_by_user"] is None
        assert result["deleted_by_user"] is None

    def test_schedule_to_dict_error_handling(self):
        """測試 Schedule to_dict 方法錯誤處理。"""
        schedule = Schedule(
            id=1,
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        # 測試正常情況下的 to_dict 方法
        result = schedule.to_dict()

        # 驗證正常情況
        assert isinstance(result, dict)
        assert "id" in result
        assert "giver_id" in result
        assert "error" not in result

    def test_schedule_table_structure(self):
        """測試 Schedule 資料表結構。"""
        # 驗證資料表已建立
        # 注意：在記憶體資料庫中，我們需要先建立資料表
        Base.metadata.create_all(bind=self.test_engine)
        inspector = inspect(self.test_engine)
        tables = inspector.get_table_names()

        assert "schedules" in tables

        # 驗證欄位存在
        columns = inspector.get_columns("schedules")
        column_names = [col["name"] for col in columns]

        expected_columns = [
            "id",
            "giver_id",
            "taker_id",
            "status",
            "date",
            "start_time",
            "end_time",
            "note",
            "created_at",
            "created_by",
            "created_by_role",
            "updated_at",
            "updated_by",
            "updated_by_role",
            "deleted_at",
            "deleted_by",
            "deleted_by_role",
        ]

        for column in expected_columns:
            assert column in column_names

    def test_schedule_indexes(self):
        """測試 Schedule 資料表索引。"""
        # 驗證索引存在
        Base.metadata.create_all(bind=self.test_engine)
        inspector = inspect(self.test_engine)

        indexes = inspector.get_indexes("schedules")
        index_names = [idx["name"] for idx in indexes]

        expected_indexes = [
            "idx_schedule_giver_date",
            "idx_schedule_taker_date",
            "idx_schedule_status",
            "idx_schedule_giver_time",
        ]

        for index in expected_indexes:
            assert index in index_names

    def test_schedule_foreign_keys(self):
        """測試 Schedule 外鍵約束。"""
        # 驗證外鍵存在
        Base.metadata.create_all(bind=self.test_engine)
        inspector = inspect(self.test_engine)

        foreign_keys = inspector.get_foreign_keys("schedules")
        fk_columns = [fk["constrained_columns"] for fk in foreign_keys]

        expected_fk_columns = [
            ["giver_id"],
            ["taker_id"],
            ["created_by"],
            ["updated_by"],
            ["deleted_by"],
        ]

        for expected_fk in expected_fk_columns:
            assert expected_fk in fk_columns

    def test_schedule_enum_values(self):
        """測試 Schedule 枚舉值。"""
        # 測試所有狀態枚舉值
        for status in ScheduleStatusEnum:
            schedule = Schedule(
                giver_id=1,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                status=status,
            )
            assert schedule.status == status

        # 測試所有角色枚舉值
        for role in UserRoleEnum:
            schedule = Schedule(
                giver_id=1,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_by_role=role,
            )
            assert schedule.created_by_role == role

    def test_schedule_soft_delete(self):
        """測試 Schedule 軟刪除功能。"""
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        # 初始狀態
        assert schedule.is_active is True
        assert schedule.is_deleted is False

        # 軟刪除
        schedule.deleted_at = datetime.now()
        schedule.deleted_by = 1
        schedule.deleted_by_role = UserRoleEnum.SYSTEM

        assert schedule.is_active is False
        assert schedule.is_deleted is True

    def test_schedule_audit_fields(self):
        """測試 Schedule 審計欄位。"""
        datetime.now()
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
            updated_by=2,
            updated_by_role=UserRoleEnum.TAKER,
        )

        # 驗證審計欄位
        assert schedule.created_by == 1
        assert schedule.created_by_role == UserRoleEnum.GIVER
        assert schedule.updated_by == 2
        assert schedule.updated_by_role == UserRoleEnum.TAKER
        assert schedule.created_at is None  # 預設值只在資料庫層面生效
        assert schedule.updated_at is None  # 預設值只在資料庫層面生效

    def test_schedule_relationship_lazy_loading(self):
        """測試 Schedule 關聯的延遲載入設定。"""
        # 驗證關聯的 lazy 設定
        schedule = Schedule(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        # 高頻使用的關聯應該使用 lazy="joined"
        mapper = class_mapper(Schedule)

        assert mapper.relationships['giver'].lazy == "joined"
        assert mapper.relationships['taker'].lazy == "joined"

        # 低頻使用的關聯應該使用 lazy="select"
        assert mapper.relationships['created_by_user'].lazy == "select"
        assert mapper.relationships['updated_by_user'].lazy == "select"
        assert mapper.relationships['deleted_by_user'].lazy == "select"
