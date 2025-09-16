"""
服務層效能整合測試模組。

測試服務層的效能、批量操作、查詢最佳化和記憶體使用。
"""

# ===== 標準函式庫 =====
import datetime
import os
import time

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 嘗試導入 psutil，如果不可用則跳過相關測試
try:
    import psutil
except ImportError:
    psutil = None

from app.database import Base

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.models.user import User
from app.schemas import ScheduleBase
from app.services.schedule import ScheduleService


class TestServicePerformanceIntegration:
    """服務層效能整合測試類別。"""

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

    def test_bulk_schedule_creation_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試批量時段建立效能。"""
        # 建立大量時段資料
        bulk_schedules_data = []
        for i in range(100):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),  # 9-16 點
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"批量時段 {i + 1}",
            )
            bulk_schedules_data.append(schedule_data)

        # 測試批量建立效能
        start_time = time.time()

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        end_time = time.time()
        processing_time = end_time - start_time

        # 驗證結果
        assert len(created_schedules) == 100
        assert processing_time < 5.0  # 應該在 5 秒內完成

        # 驗證每個時段都正確建立
        for i, schedule in enumerate(created_schedules):
            assert schedule.id is not None
            assert schedule.giver_id == sample_users["giver"].id
            assert schedule.note == f"批量時段 {i + 1}"

    def test_bulk_schedule_query_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試批量時段查詢效能。"""
        # 建立大量時段
        bulk_schedules_data = []
        for i in range(200):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"查詢測試時段 {i + 1}",
            )
            bulk_schedules_data.append(schedule_data)

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 測試查詢所有時段效能
        start_time = time.time()

        all_schedules = schedule_service.list_schedules(db=db_session)

        end_time = time.time()
        query_time = end_time - start_time

        # 驗證結果
        assert len(all_schedules) == 200
        assert query_time < 2.0  # 應該在 2 秒內完成

    def test_schedule_filtering_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段篩選效能。"""
        # 建立大量時段，包含不同狀態
        bulk_schedules_data = []
        statuses = [
            ScheduleStatusEnum.AVAILABLE,
            ScheduleStatusEnum.PENDING,
            ScheduleStatusEnum.ACCEPTED,
        ]

        for i in range(300):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"篩選測試時段 {i + 1}",
                status=statuses[i % len(statuses)],
            )
            bulk_schedules_data.append(schedule_data)

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 測試按狀態篩選效能
        start_time = time.time()

        available_schedules = schedule_service.list_schedules(
            db=db_session, status_filter="AVAILABLE"
        )
        pending_schedules = schedule_service.list_schedules(
            db=db_session, status_filter="PENDING"
        )
        accepted_schedules = schedule_service.list_schedules(
            db=db_session, status_filter="ACCEPTED"
        )

        end_time = time.time()
        filtering_time = end_time - start_time

        # 驗證結果
        assert len(available_schedules) == 100  # 300 / 3
        assert len(pending_schedules) == 100
        assert len(accepted_schedules) == 100
        assert filtering_time < 3.0  # 應該在 3 秒內完成

    def test_schedule_overlap_check_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段重疊檢查效能。"""
        # 建立大量現有時段
        existing_schedules_data = []
        for i in range(50):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"現有時段 {i + 1}",
            )
            existing_schedules_data.append(schedule_data)

        existing_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=existing_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 測試重疊檢查效能
        start_time = time.time()

        # 檢查多個時段的重疊情況
        test_schedules_data = []
        for i in range(20):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9 + (i % 8), 30),  # 重疊時間
                end_time=datetime.time(10 + (i % 8), 30),
                note=f"測試重疊時段 {i + 1}",
            )
            test_schedules_data.append(schedule_data)

        overlapping_schedules = schedule_service.check_multiple_schedules_overlap(
            db=db_session, schedules=test_schedules_data
        )

        end_time = time.time()
        overlap_check_time = end_time - start_time

        # 驗證結果
        assert len(overlapping_schedules) > 0  # 應該找到重疊時段
        assert overlap_check_time < 2.0  # 應該在 2 秒內完成

    def test_schedule_update_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段更新效能。"""
        # 建立大量時段
        bulk_schedules_data = []
        for i in range(100):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"更新測試時段 {i + 1}",
            )
            bulk_schedules_data.append(schedule_data)

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 測試批量更新效能
        start_time = time.time()

        for i, schedule in enumerate(created_schedules):
            updated_schedule = schedule_service.update_schedule(
                db=db_session,
                schedule_id=schedule.id,
                updated_by=sample_users["giver"].id,
                updated_by_role=UserRoleEnum.GIVER,
                status=ScheduleStatusEnum.AVAILABLE,
                note=f"更新後的時段 {i + 1}",
            )
            assert updated_schedule.status == ScheduleStatusEnum.AVAILABLE

        end_time = time.time()
        update_time = end_time - start_time

        # 驗證結果
        assert update_time < 10.0  # 應該在 10 秒內完成 100 次更新

    def test_schedule_deletion_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試時段刪除效能。"""
        # 建立大量時段
        bulk_schedules_data = []
        for i in range(100):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"刪除測試時段 {i + 1}",
            )
            bulk_schedules_data.append(schedule_data)

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 測試批量刪除效能
        start_time = time.time()

        deletion_count = 0
        for schedule in created_schedules:
            deletion_success = schedule_service.delete_schedule(
                db=db_session,
                schedule_id=schedule.id,
                deleted_by=sample_users["admin"].id,
                deleted_by_role=UserRoleEnum.SYSTEM,
            )
            if deletion_success:
                deletion_count += 1

        end_time = time.time()
        deletion_time = end_time - start_time

        # 驗證結果
        assert deletion_count == 100
        assert deletion_time < 5.0  # 應該在 5 秒內完成

    def test_schedule_service_memory_usage(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層記憶體使用。"""
        if psutil is None:
            pytest.skip("psutil not available")

        # 記錄初始記憶體使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 建立大量時段
        bulk_schedules_data = []
        for i in range(500):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"記憶體測試時段 {i + 1}",
            )
            bulk_schedules_data.append(schedule_data)

        # 建立時段
        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 查詢所有時段
        all_schedules = schedule_service.list_schedules(db=db_session)

        # 記錄最終記憶體使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # 驗證結果
        assert len(created_schedules) == 500
        assert len(all_schedules) == 500
        assert memory_increase < 100  # 記憶體增加應該小於 100MB

    def test_schedule_service_concurrent_operations_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層連續操作效能。"""
        # 建立現有時段
        existing_schedules_data = []
        for i in range(10):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"連續測試現有時段 {i + 1}",
            )
            existing_schedules_data.append(schedule_data)

        existing_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=existing_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        # 連續操作測試
        start_time = time.time()
        results = []

        for i in range(10):
            # 查詢時段
            schedules = schedule_service.list_schedules(db=db_session)
            results.append(len(schedules))

        end_time = time.time()
        operation_time = end_time - start_time

        # 驗證結果
        assert len(results) == 10  # 所有操作都應該成功
        assert operation_time < 5.0  # 應該在 5 秒內完成

        # 驗證所有查詢都返回相同的結果
        for schedule_count in results:
            assert schedule_count == 10

    def test_schedule_service_large_dataset_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層大資料集效能。"""
        # 建立大量時段（1000 個）
        large_schedules_data = []
        for i in range(1000):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"大資料集時段 {i + 1}",
            )
            large_schedules_data.append(schedule_data)

        # 測試建立大量時段效能
        start_time = time.time()

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=large_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        creation_time = time.time() - start_time

        # 測試查詢大量時段效能
        start_time = time.time()

        all_schedules = schedule_service.list_schedules(db=db_session)

        query_time = time.time() - start_time

        # 測試篩選大量時段效能
        start_time = time.time()

        giver_schedules = schedule_service.list_schedules(
            db=db_session, giver_id=sample_users["giver"].id
        )

        filtering_time = time.time() - start_time

        # 驗證結果
        assert len(created_schedules) == 1000
        assert len(all_schedules) == 1000
        assert len(giver_schedules) == 1000
        assert creation_time < 30.0  # 建立應該在 30 秒內完成
        assert query_time < 5.0  # 查詢應該在 5 秒內完成
        assert filtering_time < 3.0  # 篩選應該在 3 秒內完成

    def test_schedule_service_orm_object_creation_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層 ORM 物件建立效能。"""
        # 建立大量時段資料
        bulk_schedules_data = []
        for i in range(200):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"ORM 測試時段 {i + 1}",
            )
            bulk_schedules_data.append(schedule_data)

        # 測試 ORM 物件建立效能
        start_time = time.time()

        schedule_orm_objects = schedule_service.create_schedule_orm_objects(
            schedules=bulk_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        orm_creation_time = time.time() - start_time

        # 驗證結果
        assert len(schedule_orm_objects) == 200
        assert orm_creation_time < 2.0  # 應該在 2 秒內完成

        # 驗證每個 ORM 物件都正確建立
        for i, schedule_orm in enumerate(schedule_orm_objects):
            assert schedule_orm.giver_id == sample_users["giver"].id
            assert schedule_orm.note == f"ORM 測試時段 {i + 1}"
            assert schedule_orm.created_by == sample_users["admin"].id
            assert schedule_orm.created_by_role == UserRoleEnum.SYSTEM

    def test_schedule_service_status_determination_performance(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層狀態決定效能。"""
        # 建立大量時段資料
        bulk_schedules_data = []
        for i in range(300):
            schedule_data = ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=i + 1),
                start_time=datetime.time(9 + (i % 8), 0),
                end_time=datetime.time(10 + (i % 8), 0),
                note=f"狀態測試時段 {i + 1}",
            )
            bulk_schedules_data.append(schedule_data)

        # 測試狀態決定效能
        start_time = time.time()

        roles = [UserRoleEnum.SYSTEM, UserRoleEnum.GIVER, UserRoleEnum.TAKER]
        for i, schedule_data in enumerate(bulk_schedules_data):
            role = roles[i % len(roles)]
            status = schedule_service.determine_schedule_status(
                created_by_role=role, schedule_data=schedule_data
            )

            # 驗證狀態決定正確性
            if role == UserRoleEnum.TAKER:
                assert status == ScheduleStatusEnum.PENDING
            elif role == UserRoleEnum.GIVER:
                assert status == ScheduleStatusEnum.AVAILABLE
            else:  # SYSTEM
                assert status == ScheduleStatusEnum.DRAFT

        status_determination_time = time.time() - start_time

        # 驗證結果
        assert status_determination_time < 1.0  # 應該在 1 秒內完成
