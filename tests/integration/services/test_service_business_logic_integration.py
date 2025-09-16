"""
服務層業務邏輯整合測試模組。

測試服務層的複雜業務流程、多步驟操作、資料一致性和業務規則驗證。
"""

# ===== 標準函式庫 =====
import datetime
import time

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.errors import ScheduleOverlapError
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas import ScheduleBase
from app.services.schedule import ScheduleService


class TestServiceBusinessLogicIntegration:
    """服務層業務邏輯整合測試類別。"""

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

    def test_complex_schedule_creation_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試複雜的時段建立工作流程。"""
        # 建立多個時段，模擬真實的業務場景
        schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver1"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0),
                note="上午時段 1",
            ),
            ScheduleBase(
                giver_id=sample_users["giver1"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(10, 0),
                end_time=datetime.time(11, 0),
                note="上午時段 2",
            ),
            ScheduleBase(
                giver_id=sample_users["giver1"].id,
                date=datetime.date.today() + datetime.timedelta(days=2),
                start_time=datetime.time(14, 0),
                end_time=datetime.time(15, 0),
                note="下午時段",
            ),
        ]

        # 建立時段
        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(created_schedules) == 3

        # 驗證所有時段都已正確建立
        for i, schedule in enumerate(created_schedules):
            assert schedule.id is not None
            assert schedule.giver_id == sample_users["giver1"].id
            assert schedule.date == schedules_data[i].schedule_date
            assert schedule.start_time == schedules_data[i].start_time
            assert schedule.end_time == schedules_data[i].end_time
            assert schedule.note == schedules_data[i].note
            assert (
                schedule.status == ScheduleStatusEnum.DRAFT
            )  # System 角色預設為 DRAFT

    def test_schedule_booking_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段預約工作流程。"""
        # 1. 系統管理員建立可預約時段
        available_schedule_data = ScheduleBase(
            giver_id=sample_users["giver1"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="可預約時段",
        )

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=[available_schedule_data],
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        schedule = created_schedules[0]

        # 2. 將時段狀態設為 AVAILABLE（模擬系統管理員設定）
        schedule.status = ScheduleStatusEnum.AVAILABLE
        db_session.commit()
        db_session.refresh(schedule)

        # 3. Taker 預約時段（更新 taker_id 和狀態）
        updated_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["taker1"].id,
            updated_by_role=UserRoleEnum.TAKER,
            taker_id=sample_users["taker1"].id,
            status=ScheduleStatusEnum.PENDING,
        )

        assert updated_schedule.taker_id == sample_users["taker1"].id
        assert updated_schedule.status == ScheduleStatusEnum.PENDING
        assert updated_schedule.updated_by == sample_users["taker1"].id
        assert updated_schedule.updated_by_role == UserRoleEnum.TAKER

        # 4. Giver 接受預約
        accepted_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["giver1"].id,
            updated_by_role=UserRoleEnum.GIVER,
            status=ScheduleStatusEnum.ACCEPTED,
        )

        assert accepted_schedule.status == ScheduleStatusEnum.ACCEPTED
        assert accepted_schedule.updated_by == sample_users["giver1"].id
        assert accepted_schedule.updated_by_role == UserRoleEnum.GIVER

    def test_schedule_cancellation_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段取消工作流程。"""
        # 1. 建立已預約的時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "已預約時段",
            "status": ScheduleStatusEnum.ACCEPTED,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 2. Taker 取消預約
        cancelled_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["taker1"].id,
            updated_by_role=UserRoleEnum.TAKER,
            taker_id=None,  # 移除 taker_id
            status=ScheduleStatusEnum.AVAILABLE,  # 設為可預約
        )

        assert cancelled_schedule.taker_id is None
        assert cancelled_schedule.status == ScheduleStatusEnum.AVAILABLE
        assert cancelled_schedule.updated_by == sample_users["taker1"].id
        assert cancelled_schedule.updated_by_role == UserRoleEnum.TAKER

    def test_schedule_rescheduling_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段重新安排工作流程。"""
        # 1. 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker1"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "原始時段",
            "status": ScheduleStatusEnum.ACCEPTED,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        existing_schedule = Schedule(**existing_schedule_data)
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 2. 建立要重新安排的時段
        schedule_to_reschedule_data = {
            "giver_id": sample_users["giver1"].id,
            "taker_id": sample_users["taker2"].id,
            "date": datetime.date.today() + datetime.timedelta(days=2),
            "start_time": datetime.time(11, 0),
            "end_time": datetime.time(12, 0),
            "note": "要重新安排的時段",
            "status": ScheduleStatusEnum.ACCEPTED,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule_to_reschedule = Schedule(**schedule_to_reschedule_data)
        db_session.add(schedule_to_reschedule)
        db_session.commit()
        db_session.refresh(schedule_to_reschedule)

        # 3. 重新安排時段到不衝突的時間
        rescheduled_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule_to_reschedule.id,
            updated_by=sample_users["giver1"].id,
            updated_by_role=UserRoleEnum.GIVER,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(11, 0),  # 不與現有時段重疊
            end_time=datetime.time(12, 0),
            note="重新安排的時段",
        )

        assert rescheduled_schedule.date == datetime.date.today() + datetime.timedelta(
            days=1
        )
        assert rescheduled_schedule.start_time == datetime.time(11, 0)
        assert rescheduled_schedule.end_time == datetime.time(12, 0)
        assert rescheduled_schedule.note == "重新安排的時段"
        assert rescheduled_schedule.updated_by == sample_users["giver1"].id
        assert rescheduled_schedule.updated_by_role == UserRoleEnum.GIVER

    def test_multi_giver_schedule_management(
        self, db_session, schedule_service, sample_users
    ):
        """測試多個 Giver 的時段管理。"""
        # 為兩個 Giver 建立時段
        giver1_schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver1"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0),
                note="Giver 1 時段 1",
            ),
            ScheduleBase(
                giver_id=sample_users["giver1"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(10, 0),
                end_time=datetime.time(11, 0),
                note="Giver 1 時段 2",
            ),
        ]

        giver2_schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver2"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(14, 0),
                end_time=datetime.time(15, 0),
                note="Giver 2 時段 1",
            ),
        ]

        # 建立 Giver 1 的時段
        giver1_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=giver1_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 建立 Giver 2 的時段
        giver2_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=giver2_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(giver1_schedules) == 2
        assert len(giver2_schedules) == 1

        # 查詢各 Giver 的時段
        giver1_schedule_list = schedule_service.list_schedules(
            db=db_session, giver_id=sample_users["giver1"].id
        )
        giver2_schedule_list = schedule_service.list_schedules(
            db=db_session, giver_id=sample_users["giver2"].id
        )

        assert len(giver1_schedule_list) == 2
        assert len(giver2_schedule_list) == 1

        # 驗證時段歸屬正確
        for schedule in giver1_schedule_list:
            assert schedule.giver_id == sample_users["giver1"].id

        for schedule in giver2_schedule_list:
            assert schedule.giver_id == sample_users["giver2"].id

    def test_schedule_status_transition_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段狀態轉換工作流程。"""
        # 1. 建立 DRAFT 時段
        schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "測試時段",
            "status": ScheduleStatusEnum.DRAFT,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 2. DRAFT -> AVAILABLE
        available_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["giver1"].id,
            updated_by_role=UserRoleEnum.GIVER,
            status=ScheduleStatusEnum.AVAILABLE,
        )
        assert available_schedule.status == ScheduleStatusEnum.AVAILABLE

        # 3. AVAILABLE -> PENDING (Taker 預約)
        pending_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["taker1"].id,
            updated_by_role=UserRoleEnum.TAKER,
            taker_id=sample_users["taker1"].id,
            status=ScheduleStatusEnum.PENDING,
        )
        assert pending_schedule.status == ScheduleStatusEnum.PENDING
        assert pending_schedule.taker_id == sample_users["taker1"].id

        # 4. PENDING -> ACCEPTED (Giver 接受)
        accepted_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["giver1"].id,
            updated_by_role=UserRoleEnum.GIVER,
            status=ScheduleStatusEnum.ACCEPTED,
        )
        assert accepted_schedule.status == ScheduleStatusEnum.ACCEPTED

        # 5. ACCEPTED -> COMPLETED (完成)
        completed_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["giver1"].id,
            updated_by_role=UserRoleEnum.GIVER,
            status=ScheduleStatusEnum.COMPLETED,
        )
        assert completed_schedule.status == ScheduleStatusEnum.COMPLETED

    def test_schedule_bulk_operations_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段批量操作工作流程。"""
        # 1. 批量建立時段
        bulk_schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver1"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + i, 0),
                end_time=datetime.time(10 + i, 0),
                note=f"批量時段 {i + 1}",
            )
            for i in range(5)
        ]

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(created_schedules) == 5

        # 2. 批量查詢和篩選
        all_schedules = schedule_service.list_schedules(db=db_session)
        assert len(all_schedules) == 5

        giver_schedules = schedule_service.list_schedules(
            db=db_session, giver_id=sample_users["giver1"].id
        )
        assert len(giver_schedules) == 5

        # 3. 批量更新狀態
        for i, schedule in enumerate(created_schedules):
            updated_schedule = schedule_service.update_schedule(
                db=db_session,
                schedule_id=schedule.id,
                updated_by=sample_users["giver1"].id,
                updated_by_role=UserRoleEnum.GIVER,
                status=ScheduleStatusEnum.AVAILABLE,
            )
            assert updated_schedule.status == ScheduleStatusEnum.AVAILABLE

        # 4. 驗證批量更新結果
        available_schedules = schedule_service.list_schedules(
            db=db_session, status_filter="AVAILABLE"
        )
        assert len(available_schedules) == 5

    def test_schedule_data_consistency_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段資料一致性工作流程。"""
        # 1. 建立時段
        schedule_data = ScheduleBase(
            giver_id=sample_users["giver1"].id,
            taker_id=sample_users["taker1"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="一致性測試時段",
        )

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=[schedule_data],
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        schedule = created_schedules[0]

        # 2. 驗證建立時的資料一致性
        assert schedule.giver_id == schedule_data.giver_id
        assert schedule.taker_id == schedule_data.taker_id
        assert schedule.date == schedule_data.schedule_date
        assert schedule.start_time == schedule_data.start_time
        assert schedule.end_time == schedule_data.end_time
        assert schedule.note == schedule_data.note
        assert schedule.created_by == sample_users["admin"].id
        assert schedule.created_by_role == UserRoleEnum.SYSTEM
        assert schedule.updated_by == sample_users["admin"].id
        assert schedule.updated_by_role == UserRoleEnum.SYSTEM

        # 3. 更新時段
        updated_schedule = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["giver1"].id,
            updated_by_role=UserRoleEnum.GIVER,
            note="更新後的備註",
            status=ScheduleStatusEnum.AVAILABLE,
        )

        # 4. 驗證更新後的資料一致性
        assert updated_schedule.note == "更新後的備註"
        assert updated_schedule.status == ScheduleStatusEnum.AVAILABLE
        assert updated_schedule.updated_by == sample_users["giver1"].id
        assert updated_schedule.updated_by_role == UserRoleEnum.GIVER
        # 建立者資訊不應該改變
        assert updated_schedule.created_by == sample_users["admin"].id
        assert updated_schedule.created_by_role == UserRoleEnum.SYSTEM

        # 5. 查詢驗證資料一致性
        retrieved_schedule = schedule_service.get_schedule(
            db=db_session, schedule_id=schedule.id
        )
        assert retrieved_schedule.note == "更新後的備註"
        assert retrieved_schedule.status == ScheduleStatusEnum.AVAILABLE
        assert retrieved_schedule.updated_by == sample_users["giver1"].id
        assert retrieved_schedule.updated_by_role == UserRoleEnum.GIVER

    def test_schedule_business_rules_validation(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段業務規則驗證。"""
        # 1. 測試時間重疊規則
        # 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver1"].id,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "現有時段",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        existing_schedule = Schedule(**existing_schedule_data)
        db_session.add(existing_schedule)
        db_session.commit()
        db_session.refresh(existing_schedule)

        # 嘗試建立重疊時段
        overlapping_schedule_data = ScheduleBase(
            giver_id=sample_users["giver1"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),  # 重疊時間
            end_time=datetime.time(10, 30),
            note="重疊時段",
        )

        with pytest.raises(ScheduleOverlapError):
            schedule_service.create_schedules(
                db=db_session,
                schedules=[overlapping_schedule_data],
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )

        # 2. 測試不同 Giver 可以同時段
        different_giver_schedule_data = ScheduleBase(
            giver_id=sample_users["giver2"].id,  # 不同的 Giver
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),  # 相同時間
            end_time=datetime.time(10, 0),
            note="不同 Giver 時段",
        )

        # 應該成功，因為是不同的 Giver
        different_giver_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=[different_giver_schedule_data],
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(different_giver_schedules) == 1
        assert different_giver_schedules[0].giver_id == sample_users["giver2"].id

    def test_schedule_audit_trail_workflow(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段審計追蹤工作流程。"""
        # 1. 建立時段
        schedule_data = ScheduleBase(
            giver_id=sample_users["giver1"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            note="審計測試時段",
        )

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=[schedule_data],
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        schedule = created_schedules[0]
        original_created_at = schedule.created_at
        original_updated_at = schedule.updated_at

        # 2. 第一次更新
        time.sleep(0.01)  # 確保時間差異

        updated_schedule_1 = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["giver1"].id,
            updated_by_role=UserRoleEnum.GIVER,
            status=ScheduleStatusEnum.AVAILABLE,
        )

        # 3. 第二次更新
        time.sleep(0.01)  # 確保時間差異

        updated_schedule_2 = schedule_service.update_schedule(
            db=db_session,
            schedule_id=schedule.id,
            updated_by=sample_users["taker1"].id,
            updated_by_role=UserRoleEnum.TAKER,
            taker_id=sample_users["taker1"].id,
            status=ScheduleStatusEnum.PENDING,
        )

        # 4. 驗證審計追蹤
        assert updated_schedule_2.created_at == original_created_at  # 建立時間不變
        assert (
            updated_schedule_2.updated_at >= original_updated_at
        )  # 更新時間改變或相等
        assert (
            updated_schedule_2.updated_at >= updated_schedule_1.updated_at
        )  # 第二次更新時間更晚或相等

        # 5. 軟刪除
        deletion_success = schedule_service.delete_schedule(
            db=db_session,
            schedule_id=schedule.id,
            deleted_by=sample_users["admin"].id,
            deleted_by_role=UserRoleEnum.SYSTEM,
        )

        assert deletion_success is True

        # 6. 驗證軟刪除審計
        db_session.refresh(updated_schedule_2)
        assert updated_schedule_2.deleted_at is not None
        assert updated_schedule_2.deleted_by == sample_users["admin"].id
        assert updated_schedule_2.deleted_by_role == UserRoleEnum.SYSTEM
