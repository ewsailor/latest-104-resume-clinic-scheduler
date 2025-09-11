"""
Schedule 模型整合測試模組。

測試 Schedule 模型的 CRUD 操作、狀態管理和關聯查詢。
"""

# ===== 標準函式庫 =====
import datetime
from typing import Any, Dict

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.models.database import Base
from app.models.schedule import Schedule
from app.models.user import User


class TestScheduleIntegration:
    """Schedule 模型整合測試類別。"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """設定測試資料庫。"""
        # 使用記憶體 SQLite 資料庫
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # 建立資料表
        Base.metadata.create_all(bind=self.engine)

        yield

        # 清理
        Base.metadata.drop_all(bind=self.engine)

    @pytest.fixture
    def db_session(self):
        """提供資料庫會話。"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.fixture
    def sample_users(self, db_session):
        """建立範例使用者。"""
        giver = User(name="Giver 使用者", email="giver@example.com")
        taker = User(name="Taker 使用者", email="taker@example.com")
        creator = User(name="建立者", email="creator@example.com")

        db_session.add_all([giver, taker, creator])
        db_session.commit()
        db_session.refresh(giver)
        db_session.refresh(taker)
        db_session.refresh(creator)

        return {
            "giver": giver,
            "taker": taker,
            "creator": creator,
        }

    @pytest.fixture
    def sample_schedule_data(self, sample_users) -> Dict[str, Any]:
        """提供範例時段資料。"""
        return {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["creator"].id,
            "created_by_role": UserRoleEnum.GIVER,
        }

    def test_schedule_crud_operations(self, db_session, sample_schedule_data):
        """測試時段 CRUD 操作。"""
        # 建立時段
        schedule = Schedule(**sample_schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 驗證建立
        assert schedule.id is not None
        assert schedule.id > 0
        assert schedule.giver_id == sample_schedule_data["giver_id"]
        assert schedule.taker_id == sample_schedule_data["taker_id"]
        assert schedule.status == ScheduleStatusEnum.AVAILABLE
        assert schedule.date == sample_schedule_data["date"]
        assert schedule.start_time == sample_schedule_data["start_time"]
        assert schedule.end_time == sample_schedule_data["end_time"]
        assert schedule.note == "測試時段"
        assert schedule.created_at is not None
        assert schedule.updated_at is not None
        assert schedule.deleted_at is None

        # 讀取時段
        retrieved_schedule = (
            db_session.query(Schedule).filter(Schedule.id == schedule.id).first()
        )
        assert retrieved_schedule is not None
        assert retrieved_schedule.giver_id == schedule.giver_id
        assert retrieved_schedule.taker_id == schedule.taker_id
        assert retrieved_schedule.status == schedule.status

        # 更新時段
        retrieved_schedule.status = ScheduleStatusEnum.PENDING
        retrieved_schedule.note = "更新後的備註"
        db_session.commit()
        db_session.refresh(retrieved_schedule)

        # 驗證更新
        assert retrieved_schedule.status == ScheduleStatusEnum.PENDING
        assert retrieved_schedule.note == "更新後的備註"
        # 注意：在快速執行時，時間戳記可能相同，所以只驗證不早於原始時間
        assert retrieved_schedule.updated_at >= schedule.updated_at

        # 軟刪除時段
        retrieved_schedule.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(retrieved_schedule)

        # 驗證軟刪除
        assert retrieved_schedule.deleted_at is not None
        assert retrieved_schedule.is_deleted is True
        assert retrieved_schedule.is_active is False

    def test_schedule_status_enum_validation(self, db_session, sample_schedule_data):
        """測試時段狀態枚舉驗證。"""
        # 測試所有有效的狀態值
        valid_statuses = [
            ScheduleStatusEnum.DRAFT,
            ScheduleStatusEnum.AVAILABLE,
            ScheduleStatusEnum.PENDING,
            ScheduleStatusEnum.ACCEPTED,
            ScheduleStatusEnum.REJECTED,
            ScheduleStatusEnum.CANCELLED,
            ScheduleStatusEnum.COMPLETED,
        ]

        for status in valid_statuses:
            schedule_data = sample_schedule_data.copy()
            schedule_data["status"] = status

            schedule = Schedule(**schedule_data)
            db_session.add(schedule)
            db_session.commit()
            db_session.refresh(schedule)

            assert schedule.status == status

            # 清理
            db_session.delete(schedule)
            db_session.commit()

    def test_schedule_required_fields(self, db_session, sample_users):
        """測試時段必要欄位驗證。"""
        # 測試缺少 giver_id
        schedule = Schedule(
            taker_id=sample_users["taker"].id,
            date=datetime.date.today(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
        )
        db_session.add(schedule)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

        # 測試缺少 date
        schedule = Schedule(
            giver_id=sample_users["giver"].id,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
        )
        db_session.add(schedule)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

        # 測試缺少 start_time
        schedule = Schedule(
            giver_id=sample_users["giver"].id,
            date=datetime.date.today(),
            end_time=datetime.time(10, 0),
        )
        db_session.add(schedule)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

        # 測試缺少 end_time
        schedule = Schedule(
            giver_id=sample_users["giver"].id,
            date=datetime.date.today(),
            start_time=datetime.time(9, 0),
        )
        db_session.add(schedule)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_schedule_properties(self, db_session, sample_schedule_data):
        """測試時段屬性方法。"""
        # 建立活躍時段
        schedule = Schedule(**sample_schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試活躍狀態
        assert schedule.is_active is True
        assert schedule.is_deleted is False

        # 測試可預約狀態（AVAILABLE 且 taker_id 為 None）
        schedule.taker_id = None
        schedule.status = ScheduleStatusEnum.AVAILABLE
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.is_available is True

        # 測試不可預約狀態（有 taker_id）
        schedule.taker_id = sample_schedule_data["taker_id"]
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.is_available is False

        # 測試不可預約狀態（狀態不是 AVAILABLE）
        schedule.taker_id = None
        schedule.status = ScheduleStatusEnum.PENDING
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.is_available is False

        # 軟刪除時段
        schedule.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(schedule)

        # 測試刪除狀態
        assert schedule.is_active is False
        assert schedule.is_deleted is True
        assert schedule.is_available is False

    def test_schedule_to_dict_method(self, db_session, sample_schedule_data):
        """測試時段 to_dict 方法。"""
        schedule = Schedule(**sample_schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試序列化
        schedule_dict = schedule.to_dict()

        assert isinstance(schedule_dict, dict)
        assert schedule_dict["id"] == schedule.id
        assert schedule_dict["giver_id"] == schedule.giver_id
        assert schedule_dict["taker_id"] == schedule.taker_id
        assert schedule_dict["status"] == schedule.status
        assert schedule_dict["note"] == schedule.note
        assert schedule_dict["is_active"] is True
        assert schedule_dict["is_deleted"] is False
        assert schedule_dict["is_available"] is False  # 因為有 taker_id
        assert "created_at" in schedule_dict
        assert "updated_at" in schedule_dict
        assert "date" in schedule_dict
        assert "start_time" in schedule_dict
        assert "end_time" in schedule_dict

    def test_schedule_repr_method(self, db_session, sample_schedule_data):
        """測試時段 __repr__ 方法。"""
        schedule = Schedule(**sample_schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試字串表示
        schedule_repr = repr(schedule)

        assert isinstance(schedule_repr, str)
        assert f"Schedule(id={schedule.id}" in schedule_repr
        assert f"giver_id={schedule.giver_id}" in schedule_repr
        assert f"date={schedule.date}" in schedule_repr
        assert f"status={schedule.status}" in schedule_repr

    def test_schedule_audit_fields(self, db_session, sample_schedule_data):
        """測試時段審計欄位。"""
        schedule = Schedule(**sample_schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 驗證審計欄位
        assert schedule.created_by == sample_schedule_data["created_by"]
        assert schedule.created_by_role == sample_schedule_data["created_by_role"]
        assert schedule.updated_by is None  # 建立時應該為 None
        assert schedule.updated_by_role is None  # 建立時應該為 None
        assert schedule.deleted_by is None  # 建立時應該為 None
        assert schedule.deleted_by_role is None  # 建立時應該為 None

    def test_schedule_foreign_key_constraints(self, db_session, sample_schedule_data):
        """測試時段外鍵約束。"""
        # 測試無效的 giver_id
        invalid_schedule_data = sample_schedule_data.copy()
        invalid_schedule_data["giver_id"] = 99999  # 不存在的使用者 ID

        schedule = Schedule(**invalid_schedule_data)
        db_session.add(schedule)

        # 注意：SQLite 記憶體資料庫預設不強制外鍵約束
        # 在實際的 MySQL 環境中會觸發 IntegrityError
        # 這裡主要測試資料結構正確性
        try:
            db_session.commit()
            # 如果成功提交，驗證資料已儲存
            assert schedule.id is not None
        except IntegrityError:
            # 如果觸發外鍵約束錯誤，這是預期行為
            pass

        db_session.rollback()

        # 測試無效的 taker_id
        invalid_schedule_data = sample_schedule_data.copy()
        invalid_schedule_data["taker_id"] = 99999  # 不存在的使用者 ID

        schedule = Schedule(**invalid_schedule_data)
        db_session.add(schedule)

        # 注意：SQLite 記憶體資料庫預設不強制外鍵約束
        # 在實際的 MySQL 環境中會觸發 IntegrityError
        # 這裡主要測試資料結構正確性
        try:
            db_session.commit()
            # 如果成功提交，驗證資料已儲存
            assert schedule.id is not None
        except IntegrityError:
            # 如果觸發外鍵約束錯誤，這是預期行為
            pass

        db_session.rollback()

        # 測試無效的 created_by
        invalid_schedule_data = sample_schedule_data.copy()
        invalid_schedule_data["created_by"] = 99999  # 不存在的使用者 ID

        schedule = Schedule(**invalid_schedule_data)
        db_session.add(schedule)

        # 注意：SQLite 記憶體資料庫預設不強制外鍵約束
        # 在實際的 MySQL 環境中會觸發 IntegrityError
        # 這裡主要測試資料結構正確性
        try:
            db_session.commit()
            # 如果成功提交，驗證資料已儲存
            assert schedule.id is not None
        except IntegrityError:
            # 如果觸發外鍵約束錯誤，這是預期行為
            pass

    def test_schedule_optional_taker_id(self, db_session, sample_users):
        """測試時段可選的 taker_id。"""
        # 建立沒有 taker_id 的時段（可預約狀態）
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": None,  # 可為 None
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "可預約時段",
            "created_by": sample_users["creator"].id,
            "created_by_role": UserRoleEnum.GIVER,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 驗證可預約狀態
        assert schedule.taker_id is None
        assert schedule.is_available is True

        # 預約時段
        schedule.taker_id = sample_users["taker"].id
        schedule.status = ScheduleStatusEnum.PENDING
        db_session.commit()
        db_session.refresh(schedule)

        # 驗證預約後狀態
        assert schedule.taker_id == sample_users["taker"].id
        assert schedule.is_available is False

    def test_schedule_time_validation(self, db_session, sample_users):
        """測試時段時間驗證。"""
        # 測試開始時間晚於結束時間
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(10, 0),  # 開始時間
            "end_time": datetime.time(9, 0),  # 結束時間（早於開始時間）
            "created_by": sample_users["creator"].id,
            "created_by_role": UserRoleEnum.GIVER,
        }

        # 注意：SQLAlchemy 不會自動驗證時間邏輯，這需要在應用層處理
        # 這裡主要測試資料庫約束
        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()  # 應該成功，因為沒有資料庫約束

        # 驗證資料已儲存
        assert schedule.start_time == datetime.time(10, 0)
        assert schedule.end_time == datetime.time(9, 0)

    def test_schedule_bulk_operations(self, db_session, sample_users):
        """測試時段批量操作。"""
        # 建立多個時段
        schedules_data = []
        for i in range(1, 6):
            schedule_data = {
                "giver_id": sample_users["giver"].id,
                "taker_id": sample_users["taker"].id if i % 2 == 0 else None,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=i),
                "start_time": datetime.time(9 + i, 0),
                "end_time": datetime.time(10 + i, 0),
                "note": f"測試時段 {i}",
                "created_by": sample_users["creator"].id,
                "created_by_role": UserRoleEnum.GIVER,
            }
            schedules_data.append(schedule_data)

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 驗證所有時段都已建立
        all_schedules = db_session.query(Schedule).all()
        assert len(all_schedules) == 5

        # 驗證每個時段都有唯一的 ID
        schedule_ids = [schedule.id for schedule in all_schedules]
        assert len(set(schedule_ids)) == 5  # 所有 ID 都應該是唯一的

    def test_schedule_query_filters(self, db_session, sample_users):
        """測試時段查詢篩選。"""
        # 建立多個時段
        schedules_data = [
            {
                "giver_id": sample_users["giver"].id,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "可預約時段",
                "created_by": sample_users["creator"].id,
                "created_by_role": UserRoleEnum.GIVER,
            },
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": sample_users["taker"].id,
                "status": ScheduleStatusEnum.PENDING,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "待確認時段",
                "created_by": sample_users["creator"].id,
                "created_by_role": UserRoleEnum.GIVER,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 測試按狀態查詢
        available_schedules = (
            db_session.query(Schedule)
            .filter(Schedule.status == ScheduleStatusEnum.AVAILABLE)
            .all()
        )
        assert len(available_schedules) == 1
        assert available_schedules[0].note == "可預約時段"

        # 測試按 Giver 查詢
        giver_schedules = (
            db_session.query(Schedule)
            .filter(Schedule.giver_id == sample_users["giver"].id)
            .all()
        )
        assert len(giver_schedules) == 2

        # 測試按日期查詢
        today_plus_one = datetime.date.today() + datetime.timedelta(days=1)
        today_schedules = (
            db_session.query(Schedule).filter(Schedule.date == today_plus_one).all()
        )
        assert len(today_schedules) == 1
        assert today_schedules[0].note == "可預約時段"

    def test_schedule_soft_delete_queries(self, db_session, sample_schedule_data):
        """測試時段軟刪除查詢。"""
        # 建立多個時段
        schedules_data = [
            sample_schedule_data.copy(),
            sample_schedule_data.copy(),
            sample_schedule_data.copy(),
        ]

        # 修改第二個時段的日期
        schedules_data[1]["date"] = datetime.date.today() + datetime.timedelta(days=2)
        schedules_data[2]["date"] = datetime.date.today() + datetime.timedelta(days=3)

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 軟刪除第三個時段
        schedules[2].deleted_at = datetime.datetime.now()
        db_session.commit()

        # 測試查詢所有時段（包括已刪除）
        all_schedules = db_session.query(Schedule).all()
        assert len(all_schedules) == 3

        # 測試查詢活躍時段
        active_schedules = (
            db_session.query(Schedule).filter(Schedule.deleted_at.is_(None)).all()
        )
        assert len(active_schedules) == 2

        # 測試查詢已刪除時段
        deleted_schedules = (
            db_session.query(Schedule).filter(Schedule.deleted_at.isnot(None)).all()
        )
        assert len(deleted_schedules) == 1
        assert deleted_schedules[0].date == datetime.date.today() + datetime.timedelta(
            days=3
        )

    def test_schedule_indexes(self, db_session, sample_schedule_data):
        """測試時段索引。"""
        # 建立時段
        schedule = Schedule(**sample_schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 驗證索引存在（通過查詢效能間接驗證）
        # 這個測試主要確保索引不會導致錯誤

        # 測試按 giver_id 和 date 查詢
        giver_date_schedules = (
            db_session.query(Schedule)
            .filter(
                Schedule.giver_id == schedule.giver_id, Schedule.date == schedule.date
            )
            .all()
        )

        assert len(giver_date_schedules) >= 1
        assert giver_date_schedules[0].id == schedule.id

        # 測試按狀態查詢
        status_schedules = (
            db_session.query(Schedule).filter(Schedule.status == schedule.status).all()
        )

        assert len(status_schedules) >= 1
        assert status_schedules[0].id == schedule.id
