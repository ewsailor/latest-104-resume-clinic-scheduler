"""
模型關聯整合測試模組。

測試 User 和 Schedule 模型之間的關聯、反向關聯查詢和關聯資料完整性。
"""

# ===== 標準函式庫 =====
import datetime

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


class TestModelRelationshipsIntegration:
    """模型關聯整合測試類別。"""

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
        users_data = [
            {"name": "Giver 1", "email": "giver1@example.com"},
            {"name": "Giver 2", "email": "giver2@example.com"},
            {"name": "Taker 1", "email": "taker1@example.com"},
            {"name": "Taker 2", "email": "taker2@example.com"},
            {"name": "系統管理員", "email": "admin@example.com"},
        ]

        users = [User(**data) for data in users_data]
        db_session.add_all(users)
        db_session.commit()

        for user in users:
            db_session.refresh(user)

        return {
            "giver1": users[0],
            "giver2": users[1],
            "taker1": users[2],
            "taker2": users[3],
            "admin": users[4],
        }

    def test_user_giver_schedules_relationship(self, db_session, sample_users):
        """測試使用者作為 Giver 的時段關聯。"""
        # 建立多個時段，giver1 作為 Giver
        schedules_data = [
            {
                "giver_id": sample_users["giver1"].id,
                "taker_id": sample_users["taker1"].id,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "時段 1",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver1"].id,
                "taker_id": sample_users["taker2"].id,
                "status": ScheduleStatusEnum.PENDING,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "時段 2",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 測試 giver1 的 giver_schedules 關聯
        giver1_schedules = sample_users["giver1"].giver_schedules.all()
        assert len(giver1_schedules) == 2

        # 驗證關聯的時段
        schedule_ids = [s.id for s in giver1_schedules]
        assert schedules[0].id in schedule_ids
        assert schedules[1].id in schedule_ids

        # 測試 giver2 沒有時段
        giver2_schedules = sample_users["giver2"].giver_schedules.all()
        assert len(giver2_schedules) == 0

    def test_user_taker_schedules_relationship(self, db_session, sample_users):
        """測試使用者作為 Taker 的時段關聯。"""
        # 建立多個時段，taker1 作為 Taker
        schedules_data = [
            {
                "giver_id": sample_users["giver1"].id,
                "taker_id": sample_users["taker1"].id,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "時段 1",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver2"].id,
                "taker_id": sample_users["taker1"].id,
                "status": ScheduleStatusEnum.PENDING,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "時段 2",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 測試 taker1 的 taker_schedules 關聯
        taker1_schedules = sample_users["taker1"].taker_schedules.all()
        assert len(taker1_schedules) == 2

        # 驗證關聯的時段
        schedule_ids = [s.id for s in taker1_schedules]
        assert schedules[0].id in schedule_ids
        assert schedules[1].id in schedule_ids

        # 測試 taker2 沒有時段
        taker2_schedules = sample_users["taker2"].taker_schedules.all()
        assert len(taker2_schedules) == 0

    def test_user_created_schedules_relationship(self, db_session, sample_users):
        """測試使用者建立的時段關聯。"""
        # 建立多個時段，admin 作為建立者
        schedules_data = [
            {
                "giver_id": sample_users["giver1"].id,
                "taker_id": sample_users["taker1"].id,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "時段 1",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver2"].id,
                "taker_id": sample_users["taker2"].id,
                "status": ScheduleStatusEnum.PENDING,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "時段 2",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 測試 admin 的 created_schedules 關聯
        admin_created_schedules = sample_users["admin"].created_schedules.all()
        assert len(admin_created_schedules) == 2

        # 驗證關聯的時段
        schedule_ids = [s.id for s in admin_created_schedules]
        assert schedules[0].id in schedule_ids
        assert schedules[1].id in schedule_ids

        # 測試其他使用者沒有建立的時段
        giver1_created_schedules = sample_users["giver1"].created_schedules.all()
        assert len(giver1_created_schedules) == 0

    def test_schedule_giver_relationship(self, db_session, sample_users):
        """測試時段的 Giver 關聯。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試時段的 giver 關聯
        assert schedule.giver is not None
        assert schedule.giver.id == sample_users["giver1"].id
        assert schedule.giver.name == "Giver 1"
        assert schedule.giver.email == "giver1@example.com"

    def test_schedule_taker_relationship(self, db_session, sample_users):
        """測試時段的 Taker 關聯。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試時段的 taker 關聯
        assert schedule.taker is not None
        assert schedule.taker.id == sample_users["taker1"].id
        assert schedule.taker.name == "Taker 1"
        assert schedule.taker.email == "taker1@example.com"

    def test_schedule_created_by_user_relationship(self, db_session, sample_users):
        """測試時段的建立者關聯。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試時段的 created_by_user 關聯
        assert schedule.created_by_user is not None
        assert schedule.created_by_user.id == sample_users["admin"].id
        assert schedule.created_by_user.name == "系統管理員"
        assert schedule.created_by_user.email == "admin@example.com"

    def test_schedule_updated_by_user_relationship(self, db_session, sample_users):
        """測試時段的更新者關聯。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 更新時段
        schedule.status = ScheduleStatusEnum.PENDING
        schedule.updated_by = sample_users["giver1"].id
        schedule.updated_by_role = UserRoleEnum.GIVER
        db_session.commit()
        db_session.refresh(schedule)

        # 測試時段的 updated_by_user 關聯
        assert schedule.updated_by_user is not None
        assert schedule.updated_by_user.id == sample_users["giver1"].id
        assert schedule.updated_by_user.name == "Giver 1"
        assert schedule.updated_by_user.email == "giver1@example.com"

    def test_schedule_deleted_by_user_relationship(self, db_session, sample_users):
        """測試時段的刪除者關聯。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 軟刪除時段
        schedule.deleted_at = datetime.datetime.now()
        schedule.deleted_by = sample_users["admin"].id
        schedule.deleted_by_role = UserRoleEnum.SYSTEM
        db_session.commit()
        db_session.refresh(schedule)

        # 測試時段的 deleted_by_user 關聯
        assert schedule.deleted_by_user is not None
        assert schedule.deleted_by_user.id == sample_users["admin"].id
        assert schedule.deleted_by_user.name == "系統管理員"
        assert schedule.deleted_by_user.email == "admin@example.com"

    def test_relationship_lazy_loading(self, db_session, sample_users):
        """測試關聯的延遲載入。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試 giver 和 taker 關聯使用 joined 載入（應該立即載入）
        assert schedule.giver is not None
        assert schedule.taker is not None

        # 測試審計關聯使用 select 載入（延遲載入）
        # 這些關聯應該在需要時才載入
        assert schedule.created_by_user is not None
        assert schedule.updated_by_user is None  # 尚未更新
        assert schedule.deleted_by_user is None  # 尚未刪除

    def test_relationship_cascade_behavior(self, db_session, sample_users):
        """測試關聯的級聯行為。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試刪除 Giver 時的行為（RESTRICT）
        # 應該不能刪除有時段的 Giver
        with pytest.raises(IntegrityError):
            db_session.delete(sample_users["giver1"])
            db_session.commit()

        db_session.rollback()

        # 測試刪除 Taker 時的行為（SET NULL）
        # 應該可以刪除，時段的 taker_id 設為 NULL
        db_session.delete(sample_users["taker1"])
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.taker_id is None
        assert schedule.taker is None

    def test_relationship_data_integrity(self, db_session, sample_users):
        """測試關聯資料完整性。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 驗證關聯資料的一致性
        assert schedule.giver_id == schedule.giver.id
        assert schedule.taker_id == schedule.taker.id
        assert schedule.created_by == schedule.created_by_user.id

        # 驗證反向關聯的一致性
        giver_schedules = sample_users["giver1"].giver_schedules.all()
        assert len(giver_schedules) == 1
        assert giver_schedules[0].id == schedule.id

        taker_schedules = sample_users["taker1"].taker_schedules.all()
        assert len(taker_schedules) == 1
        assert taker_schedules[0].id == schedule.id

        admin_created_schedules = sample_users["admin"].created_schedules.all()
        assert len(admin_created_schedules) == 1
        assert admin_created_schedules[0].id == schedule.id

    def test_relationship_query_optimization(self, db_session, sample_users):
        """測試關聯查詢最佳化。"""
        # 建立多個時段
        schedules_data = []
        for i in range(5):
            schedule_data = {
                "giver_id": sample_users["giver1"].id,
                "taker_id": sample_users["taker1"].id,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=i + 1),
                "start_time": datetime.time(9 + i, 0),
                "end_time": datetime.time(10 + i, 0),
                "note": f"時段 {i+1}",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            }
            schedules_data.append(schedule_data)

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 測試查詢時段的 Giver 和 Taker（應該使用 JOIN 載入）
        all_schedules = db_session.query(Schedule).all()

        for schedule in all_schedules:
            # 這些關聯應該已經載入，不需要額外查詢
            assert schedule.giver is not None
            assert schedule.taker is not None
            assert schedule.giver.name == "Giver 1"
            assert schedule.taker.name == "Taker 1"

    def test_relationship_filtering(self, db_session, sample_users):
        """測試關聯篩選。"""
        # 建立多個時段
        schedules_data = [
            {
                "giver_id": sample_users["giver1"].id,
                "taker_id": sample_users["taker1"].id,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "時段 1",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver2"].id,
                "taker_id": sample_users["taker2"].id,
                "status": ScheduleStatusEnum.PENDING,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "時段 2",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 測試按 Giver 篩選時段
        giver1_schedules = (
            db_session.query(Schedule)
            .filter(Schedule.giver_id == sample_users["giver1"].id)
            .all()
        )
        assert len(giver1_schedules) == 1
        assert giver1_schedules[0].note == "時段 1"

        # 測試按 Taker 篩選時段
        taker1_schedules = (
            db_session.query(Schedule)
            .filter(Schedule.taker_id == sample_users["taker1"].id)
            .all()
        )
        assert len(taker1_schedules) == 1
        assert taker1_schedules[0].note == "時段 1"

        # 測試按建立者篩選時段
        admin_created_schedules = (
            db_session.query(Schedule)
            .filter(Schedule.created_by == sample_users["admin"].id)
            .all()
        )
        assert len(admin_created_schedules) == 2
