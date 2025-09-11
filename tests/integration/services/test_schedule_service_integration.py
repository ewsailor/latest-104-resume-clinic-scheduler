"""
ScheduleService 整合測試模組。

測試 ScheduleService 的業務邏輯、時段重疊檢查、CRUD 操作等整合功能。
"""

# ===== 標準函式庫 =====
import datetime

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.enums.operations import OperationContext
from app.errors import ConflictError
from app.models.database import Base
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas import ScheduleBase
from app.services.schedule import ScheduleService


class TestScheduleServiceIntegration:
    """ScheduleService 整合測試類別。"""

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
    def schedule_service(self):
        """提供 ScheduleService 實例。"""
        return ScheduleService()

    @pytest.fixture
    def sample_users(self, db_session):
        """建立範例使用者。"""
        users_data = [
            {"name": "Giver 使用者", "email": "giver@example.com"},
            {"name": "Taker 使用者", "email": "taker@example.com"},
            {"name": "系統管理員", "email": "admin@example.com"},
        ]

        users = [User(**data) for data in users_data]
        db_session.add_all(users)
        db_session.commit()

        for user in users:
            db_session.refresh(user)

        return {
            "giver": users[0],
            "taker": users[1],
            "admin": users[2],
        }

    @pytest.fixture
    def sample_schedule_data(self, sample_users):
        """提供範例時段資料。"""
        return ScheduleBase(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            schedule_date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="測試時段",
            status=None,  # 明確設定為 None，讓 determine_schedule_status 方法決定
        )

    def test_check_schedule_overlap_no_overlap(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段重疊檢查 - 無重疊。"""
        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="現有時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 檢查不重疊的時段
        overlapping_schedules = schedule_service.check_schedule_overlap(
            db=db_session,
            giver_id=sample_users["giver"].id,
            schedule_date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(11, 0),  # 不重疊的時間
            end_time=datetime.time(12, 0),
        )

        assert len(overlapping_schedules) == 0

    def test_check_schedule_overlap_with_overlap(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段重疊檢查 - 有重疊。"""
        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="現有時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 檢查重疊的時段
        overlapping_schedules = schedule_service.check_schedule_overlap(
            db=db_session,
            giver_id=sample_users["giver"].id,
            schedule_date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),  # 重疊的時間
            end_time=datetime.time(10, 30),
        )

        assert len(overlapping_schedules) == 1
        assert overlapping_schedules[0].id == existing_schedule.id

    def test_check_schedule_overlap_exclude_schedule_id(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段重疊檢查 - 排除指定時段 ID。"""
        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="現有時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 檢查重疊但排除自己
        overlapping_schedules = schedule_service.check_schedule_overlap(
            db=db_session,
            giver_id=sample_users["giver"].id,
            schedule_date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),  # 重疊的時間
            end_time=datetime.time(10, 30),
            exclude_schedule_id=existing_schedule.id,  # 排除自己
        )

        assert len(overlapping_schedules) == 0

    def test_check_multiple_schedules_overlap(
        self, db_session, schedule_service, sample_users
    ):
        """測試多個時段重疊檢查。"""
        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="現有時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 建立多個時段資料
        schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                schedule_date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 30),  # 重疊
                end_time=datetime.time(10, 30),
                note="重疊時段 1",
            ),
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                schedule_date=datetime.date.today() + datetime.timedelta(days=2),
                start_time=datetime.time(11, 0),  # 不重疊
                end_time=datetime.time(12, 0),
                note="不重疊時段",
            ),
        ]

        overlapping_schedules = schedule_service.check_multiple_schedules_overlap(
            db=db_session, schedules=schedules_data
        )

        assert len(overlapping_schedules) == 1
        assert overlapping_schedules[0].id == existing_schedule.id

    def test_determine_schedule_status_taker(
        self, schedule_service, sample_schedule_data
    ):
        """測試根據 Taker 角色決定時段狀態。"""
        status = schedule_service.determine_schedule_status(
            created_by_role=UserRoleEnum.TAKER,
            schedule_data=sample_schedule_data,
        )

        assert status == ScheduleStatusEnum.PENDING

    def test_determine_schedule_status_giver(
        self, schedule_service, sample_schedule_data
    ):
        """測試根據 Giver 角色決定時段狀態。"""
        status = schedule_service.determine_schedule_status(
            created_by_role=UserRoleEnum.GIVER,
            schedule_data=sample_schedule_data,
        )

        assert status == ScheduleStatusEnum.AVAILABLE

    def test_determine_schedule_status_system(
        self, schedule_service, sample_schedule_data
    ):
        """測試根據 System 角色決定時段狀態。"""
        status = schedule_service.determine_schedule_status(
            created_by_role=UserRoleEnum.SYSTEM,
            schedule_data=sample_schedule_data,
        )

        assert status == ScheduleStatusEnum.DRAFT

    def test_log_schedule_details(self, schedule_service, sample_schedule_data):
        """測試記錄時段詳情。"""
        schedules = [sample_schedule_data]

        # 測試不應該拋出異常
        schedule_service.log_schedule_details(schedules, OperationContext.CREATE)

    def test_log_schedule_details_empty_list(self, schedule_service):
        """測試記錄空時段列表詳情。"""
        # 測試不應該拋出異常
        schedule_service.log_schedule_details([], OperationContext.CREATE)

    def test_create_schedule_orm_objects(
        self, schedule_service, sample_users, sample_schedule_data
    ):
        """測試建立時段 ORM 物件。"""
        schedules_data = [sample_schedule_data]

        schedule_orm_objects = schedule_service.create_schedule_orm_objects(
            schedules=schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(schedule_orm_objects) == 1
        schedule_orm = schedule_orm_objects[0]

        assert schedule_orm.giver_id == sample_schedule_data.giver_id
        assert schedule_orm.taker_id == sample_schedule_data.taker_id
        assert schedule_orm.date == sample_schedule_data.schedule_date
        assert schedule_orm.start_time == sample_schedule_data.start_time
        assert schedule_orm.end_time == sample_schedule_data.end_time
        assert schedule_orm.note == sample_schedule_data.note
        assert (
            schedule_orm.status == ScheduleStatusEnum.DRAFT
        )  # System 角色預設為 DRAFT
        assert schedule_orm.created_by == sample_users["admin"].id
        assert schedule_orm.created_by_role == UserRoleEnum.SYSTEM
        assert schedule_orm.updated_by == sample_users["admin"].id
        assert schedule_orm.updated_by_role == UserRoleEnum.SYSTEM
        assert schedule_orm.deleted_by is None
        assert schedule_orm.deleted_by_role is None

    def test_create_schedules_success(
        self, db_session, schedule_service, sample_users, sample_schedule_data
    ):
        """測試成功建立時段。"""
        schedules_data = [sample_schedule_data]

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(created_schedules) == 1
        created_schedule = created_schedules[0]

        assert created_schedule.id is not None
        assert created_schedule.giver_id == sample_schedule_data.giver_id
        assert created_schedule.taker_id == sample_schedule_data.taker_id
        assert created_schedule.date == sample_schedule_data.schedule_date
        assert created_schedule.start_time == sample_schedule_data.start_time
        assert created_schedule.end_time == sample_schedule_data.end_time
        assert created_schedule.note == sample_schedule_data.note
        assert created_schedule.status == ScheduleStatusEnum.DRAFT

    def test_create_schedules_with_overlap_conflict(
        self, db_session, schedule_service, sample_users
    ):
        """測試建立時段時的重疊衝突。"""
        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="現有時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 嘗試建立重疊的時段
        overlapping_schedule_data = ScheduleBase(
            giver_id=sample_users["giver"].id,
            schedule_date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),  # 重疊的時間
            end_time=datetime.time(10, 30),
            note="重疊時段",
        )

        with pytest.raises(ConflictError) as exc_info:
            schedule_service.create_schedules(
                db=db_session,
                schedules=[overlapping_schedule_data],
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )

        assert "重疊時段" in str(exc_info.value)

    def test_list_schedules_all(self, db_session, schedule_service, sample_users):
        """測試查詢所有時段。"""
        # 建立多個時段
        schedules_data = [
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": sample_users["taker"].id,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "時段 1",
                "status": ScheduleStatusEnum.AVAILABLE,
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": None,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "時段 2",
                "status": ScheduleStatusEnum.PENDING,
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 查詢所有時段
        all_schedules = schedule_service.list_schedules(db=db_session)

        assert len(all_schedules) == 2

    def test_list_schedules_with_filters(
        self, db_session, schedule_service, sample_users
    ):
        """測試使用篩選條件查詢時段。"""
        # 建立多個時段
        schedules_data = [
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": sample_users["taker"].id,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "時段 1",
                "status": ScheduleStatusEnum.AVAILABLE,
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": None,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "時段 2",
                "status": ScheduleStatusEnum.PENDING,
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        # 按 giver_id 篩選
        giver_schedules = schedule_service.list_schedules(
            db=db_session, giver_id=sample_users["giver"].id
        )
        assert len(giver_schedules) == 2

        # 按 taker_id 篩選
        taker_schedules = schedule_service.list_schedules(
            db=db_session, taker_id=sample_users["taker"].id
        )
        assert len(taker_schedules) == 1

        # 按狀態篩選
        available_schedules = schedule_service.list_schedules(
            db=db_session, status_filter="AVAILABLE"
        )
        assert len(available_schedules) == 1

    def test_get_schedule_success(self, db_session, schedule_service, sample_users):
        """測試成功查詢單一時段。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 查詢時段
        retrieved_schedule = schedule_service.get_schedule(
            db=db_session, schedule_id=schedule.id
        )

        assert retrieved_schedule.id == schedule.id
        assert retrieved_schedule.giver_id == schedule.giver_id
        assert retrieved_schedule.taker_id == schedule.taker_id
        assert retrieved_schedule.note == schedule.note

    def test_new_updated_time_values(self, db_session, schedule_service, sample_users):
        """測試更新後的時間值。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試部分更新
        new_date, new_start_time, new_end_time = (
            schedule_service.new_updated_time_values(
                db=db_session,
                schedule_id=schedule.id,
                schedule_date=datetime.date.today() + datetime.timedelta(days=2),
                start_time=datetime.time(11, 0),
            )
        )

        assert new_date == datetime.date.today() + datetime.timedelta(days=2)
        assert new_start_time == datetime.time(11, 0)
        assert new_end_time == datetime.time(10, 0)  # 未更新，保持原值

    def test_check_update_overlap_no_time_change(
        self, db_session, schedule_service, sample_users
    ):
        """測試更新時段時無時間變更的重疊檢查。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 只更新 note，不更新時間
        overlapping_schedules = schedule_service.check_update_overlap(
            db=db_session, schedule_id=schedule.id, note="更新後的備註"
        )

        assert len(overlapping_schedules) == 0

    def test_check_update_overlap_with_time_change(
        self, db_session, schedule_service, sample_users
    ):
        """測試更新時段時有時間變更的重疊檢查。"""
        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="現有時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 建立要更新的時段
        schedule_to_update = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=2),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(12, 0),
            note="要更新的時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(schedule_to_update)
        db_session.commit()
        db_session.refresh(schedule_to_update)

        # 更新時段時間，使其與現有時段重疊
        overlapping_schedules = schedule_service.check_update_overlap(
            db=db_session,
            schedule_id=schedule_to_update.id,
            schedule_date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),  # 重疊的時間
            end_time=datetime.time(10, 30),
        )

        assert len(overlapping_schedules) == 1
        assert overlapping_schedules[0].id == existing_schedule.id

    def test_update_schedule_success(self, db_session, schedule_service, sample_users):
        """測試成功更新時段。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "原始備註",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 更新時段
        updated_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["giver"].id,
            updated_by_role=UserRoleEnum.GIVER,
            note="更新後的備註",
            status=ScheduleStatusEnum.PENDING,
        )

        assert updated_schedule.note == "更新後的備註"
        assert updated_schedule.status == ScheduleStatusEnum.PENDING
        assert updated_schedule.updated_by == sample_users["giver"].id
        assert updated_schedule.updated_by_role == UserRoleEnum.GIVER

    def test_update_schedule_with_overlap_conflict(
        self, db_session, schedule_service, sample_users
    ):
        """測試更新時段時的重疊衝突。"""
        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="現有時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 建立要更新的時段
        schedule_to_update = Schedule(
            giver_id=sample_users["giver"].id,
            taker_id=sample_users["taker"].id,
            date=datetime.date.today() + datetime.timedelta(days=2),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(12, 0),
            note="要更新的時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )
        db_session.add(schedule_to_update)
        db_session.commit()
        db_session.refresh(schedule_to_update)

        # 嘗試更新時段時間，使其與現有時段重疊
        with pytest.raises(ConflictError) as exc_info:
            schedule_service.update_schedule(
                db=db_session,
                schedule_id=schedule_to_update.id,
                updated_by=sample_users["giver"].id,
                updated_by_role=UserRoleEnum.GIVER,
                schedule_date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 30),  # 重疊的時間
                end_time=datetime.time(10, 30),
            )

        assert "重疊時段" in str(exc_info.value)

    def test_delete_schedule_success(self, db_session, schedule_service, sample_users):
        """測試成功軟刪除時段。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 軟刪除時段
        deletion_success = schedule_service.delete_schedule(
            db=db_session,
            schedule_id=schedule.id,
            deleted_by=sample_users["admin"].id,
            deleted_by_role=UserRoleEnum.SYSTEM,
        )

        assert deletion_success is True

        # 驗證時段已被軟刪除
        db_session.refresh(schedule)
        assert schedule.deleted_at is not None
        assert schedule.deleted_by == sample_users["admin"].id
        assert schedule.deleted_by_role == UserRoleEnum.SYSTEM

    def test_delete_schedule_not_found(
        self, db_session, schedule_service, sample_users
    ):
        """測試刪除不存在的時段。"""
        # 嘗試刪除不存在的時段
        deletion_success = schedule_service.delete_schedule(
            db=db_session,
            schedule_id=99999,  # 不存在的 ID
            deleted_by=sample_users["admin"].id,
            deleted_by_role=UserRoleEnum.SYSTEM,
        )

        assert deletion_success is False
