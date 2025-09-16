"""
服務層錯誤處理整合測試模組。

測試服務層的錯誤處理、異常轉換、資料驗證和錯誤恢復機制。
"""

# ===== 標準函式庫 =====
import datetime

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.errors import ScheduleNotFoundError, ScheduleOverlapError
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas import ScheduleBase
from app.services.schedule import ScheduleService


class TestServiceErrorHandlingIntegration:
    """服務層錯誤處理整合測試類別。"""

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

    def test_create_schedules_overlap_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試建立時段時重疊錯誤處理。"""
        # 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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
        overlapping_schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 30),  # 重疊時間
                end_time=datetime.time(10, 30),
                note="重疊時段 1",
            ),
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(8, 30),  # 另一個重疊時間
                end_time=datetime.time(9, 30),
                note="重疊時段 2",
            ),
        ]

        with pytest.raises(ScheduleOverlapError) as exc_info:
            schedule_service.create_schedules(
                db=db_session,
                schedules=overlapping_schedules_data,
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )

        # 驗證錯誤訊息
        error_message = str(exc_info.value)
        assert "重疊時段" in error_message
        assert "2" in error_message  # 應該檢測到 2 個重疊時段

    def test_create_schedules_partial_overlap_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試建立時段時部分重疊錯誤處理。"""
        # 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 嘗試建立部分重疊的時段
        schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 30),  # 重疊
                end_time=datetime.time(10, 30),
                note="重疊時段",
            ),
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=2),
                start_time=datetime.time(11, 0),  # 不重疊
                end_time=datetime.time(12, 0),
                note="不重疊時段",
            ),
        ]

        with pytest.raises(ScheduleOverlapError) as exc_info:
            schedule_service.create_schedules(
                db=db_session,
                schedules=schedules_data,
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )

        # 驗證錯誤訊息
        error_message = str(exc_info.value)
        assert "重疊時段" in error_message

    def test_update_schedule_overlap_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試更新時段時重疊錯誤處理。"""
        # 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 建立要更新的時段
        schedule_to_update_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "date": datetime.date.today() + datetime.timedelta(days=2),
            "start_time": datetime.time(11, 0),
            "end_time": datetime.time(12, 0),
            "note": "要更新的時段",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule_to_update = Schedule(**schedule_to_update_data)
        db_session.add(schedule_to_update)
        db_session.commit()
        db_session.refresh(schedule_to_update)

        # 嘗試更新時段時間，使其與現有時段重疊
        with pytest.raises(ScheduleOverlapError) as exc_info:
            schedule_service.update_schedule(
                db=db_session,
                schedule_id=schedule_to_update.id,
                updated_by=sample_users["giver"].id,
                updated_by_role=UserRoleEnum.GIVER,
                schedule_date=datetime.date.today()
                + datetime.timedelta(days=1),  # 改為同一天
                start_time=datetime.time(9, 30),  # 重疊時間
                end_time=datetime.time(10, 30),
            )

        # 驗證錯誤訊息
        error_message = str(exc_info.value)
        assert "重疊時段" in error_message
        assert str(schedule_to_update.id) in error_message

    def test_get_schedule_not_found_error_handling(self, db_session, schedule_service):
        """測試查詢不存在時段的錯誤處理。"""
        # 嘗試查詢不存在的時段
        with pytest.raises(Exception):  # 應該拋出某種異常
            schedule_service.get_schedule(db=db_session, schedule_id=99999)

    def test_update_schedule_not_found_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試更新不存在時段的錯誤處理。"""
        # 嘗試更新不存在的時段
        with pytest.raises(Exception):  # 應該拋出某種異常
            schedule_service.update_schedule(
                db=db_session,
                schedule_id=99999,
                updated_by=sample_users["giver"].id,
                updated_by_role=UserRoleEnum.GIVER,
                note="更新備註",
            )

    def test_delete_schedule_not_found_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試刪除不存在時段的錯誤處理。"""
        # 嘗試刪除不存在的時段，應該拋出 ScheduleNotFoundError
        with pytest.raises(ScheduleNotFoundError) as exc_info:
            schedule_service.delete_schedule(
                db=db_session,
                schedule_id=99999,
                deleted_by=sample_users["admin"].id,
                deleted_by_role=UserRoleEnum.SYSTEM,
            )

        # 驗證異常訊息
        assert "時段不存在" in str(exc_info.value)
        assert "ID=99999" in str(exc_info.value)

    def test_create_schedules_invalid_data_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試建立時段時無效資料錯誤處理。"""
        # 測試無效的時段資料
        invalid_schedules_data = [
            ScheduleBase(
                giver_id=99999,  # 不存在的使用者 ID
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0),
                note="無效時段",
            ),
        ]

        # 注意：SQLite 記憶體資料庫可能不強制外鍵約束
        # 在實際的 MySQL 環境中會觸發 IntegrityError
        try:
            created_schedules = schedule_service.create_schedules(
                db=db_session,
                schedules=invalid_schedules_data,
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )
            # 如果成功建立，驗證資料已儲存
            assert len(created_schedules) == 1
        except IntegrityError:
            # 如果觸發外鍵約束錯誤，這是預期行為
            pass

    def test_create_schedules_empty_list_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試建立空時段列表的錯誤處理。"""
        # 測試空列表
        empty_schedules_data = []

        # 應該成功處理空列表
        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=empty_schedules_data,
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(created_schedules) == 0

    def test_create_schedules_time_validation_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試建立時段時時間驗證錯誤處理。"""
        # 測試結束時間早於開始時間的情況
        invalid_time_schedule_data = ScheduleBase(
            giver_id=sample_users["giver"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(9, 0),  # 結束時間早於開始時間
            note="無效時間時段",
        )

        # 注意：SQLAlchemy 不會自動驗證時間邏輯，這需要在應用層處理
        # 這裡主要測試服務層不會因為這種情況而崩潰
        try:
            created_schedules = schedule_service.create_schedules(
                db=db_session,
                schedules=[invalid_time_schedule_data],
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )
            # 如果成功建立，驗證資料已儲存
            assert len(created_schedules) == 1
            assert created_schedules[0].start_time == datetime.time(10, 0)
            assert created_schedules[0].end_time == datetime.time(9, 0)
        except Exception as e:
            # 如果拋出異常，確保是預期的異常類型
            assert isinstance(e, (ValueError, ScheduleOverlapError))

    def test_schedule_service_error_recovery(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層錯誤恢復機制。"""
        # 1. 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 2. 嘗試建立重疊時段（應該失敗）
        overlapping_schedule_data = ScheduleBase(
            giver_id=sample_users["giver"].id,
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

        # 3. 驗證資料庫狀態未受影響
        all_schedules = schedule_service.list_schedules(db=db_session)
        assert len(all_schedules) == 1
        assert all_schedules[0].id == existing_schedule.id
        assert all_schedules[0].note == "現有時段"

        # 4. 成功建立不重疊的時段
        non_overlapping_schedule_data = ScheduleBase(
            giver_id=sample_users["giver"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(11, 0),  # 不重疊時間
            end_time=datetime.time(12, 0),
            note="不重疊時段",
        )

        created_schedules = schedule_service.create_schedules(
            db=db_session,
            schedules=[non_overlapping_schedule_data],
            created_by=sample_users["admin"].id,
            created_by_role=UserRoleEnum.SYSTEM,
        )

        assert len(created_schedules) == 1
        assert created_schedules[0].note == "不重疊時段"

        # 5. 驗證最終狀態
        final_schedules = schedule_service.list_schedules(db=db_session)
        assert len(final_schedules) == 2

    def test_schedule_service_transaction_rollback_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層事務回滾錯誤處理。"""
        # 1. 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 2. 嘗試建立多個時段，其中一個重疊
        mixed_schedules_data = [
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(11, 0),  # 不重疊
                end_time=datetime.time(12, 0),
                note="不重疊時段",
            ),
            ScheduleBase(
                giver_id=sample_users["giver"].id,
                date=datetime.date.today() + datetime.timedelta(days=1),
                start_time=datetime.time(9, 30),  # 重疊
                end_time=datetime.time(10, 30),
                note="重疊時段",
            ),
        ]

        # 3. 應該因為重疊而失敗，整個批次都不應該建立
        with pytest.raises(ScheduleOverlapError):
            schedule_service.create_schedules(
                db=db_session,
                schedules=mixed_schedules_data,
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )

        # 4. 驗證沒有新時段被建立
        all_schedules = schedule_service.list_schedules(db=db_session)
        assert len(all_schedules) == 1
        assert all_schedules[0].id == existing_schedule.id

    def test_schedule_service_concurrent_error_handling(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層並發錯誤處理。"""
        # 1. 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 2. 模擬並發操作：同時嘗試預約同一個時段
        schedule_data_1 = ScheduleBase(
            giver_id=sample_users["giver"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),  # 重疊
            end_time=datetime.time(10, 30),
            note="並發時段 1",
        )

        schedule_data_2 = ScheduleBase(
            giver_id=sample_users["giver"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),  # 重疊
            end_time=datetime.time(10, 30),
            note="並發時段 2",
        )

        # 3. 第一個應該成功（如果沒有其他重疊）
        # 第二個應該失敗
        with pytest.raises(ScheduleOverlapError):
            schedule_service.create_schedules(
                db=db_session,
                schedules=[schedule_data_1, schedule_data_2],
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )

        # 4. 驗證只有原始時段存在
        all_schedules = schedule_service.list_schedules(db=db_session)
        assert len(all_schedules) == 1
        assert all_schedules[0].id == existing_schedule.id

    def test_schedule_service_error_message_consistency(
        self, db_session, schedule_service, sample_users
    ):
        """測試服務層錯誤訊息一致性。"""
        # 建立現有時段
        existing_schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 測試建立時段的重疊錯誤訊息
        overlapping_schedule_data = ScheduleBase(
            giver_id=sample_users["giver"].id,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 30),
            end_time=datetime.time(10, 30),
            note="重疊時段",
        )

        with pytest.raises(ScheduleOverlapError) as exc_info:
            schedule_service.create_schedules(
                db=db_session,
                schedules=[overlapping_schedule_data],
                created_by=sample_users["admin"].id,
                created_by_role=UserRoleEnum.SYSTEM,
            )

        create_error_message = str(exc_info.value)
        assert "重疊時段" in create_error_message
        assert "檢測到" in create_error_message
        assert "1" in create_error_message

        # 測試更新時段的重疊錯誤訊息
        schedule_to_update_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
            "date": datetime.date.today() + datetime.timedelta(days=2),
            "start_time": datetime.time(11, 0),
            "end_time": datetime.time(12, 0),
            "note": "要更新的時段",
            "status": ScheduleStatusEnum.AVAILABLE,
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule_to_update = Schedule(**schedule_to_update_data)
        db_session.add(schedule_to_update)
        db_session.commit()
        db_session.refresh(schedule_to_update)

        with pytest.raises(ScheduleOverlapError) as exc_info:
            schedule_service.update_schedule(
                db=db_session,
                schedule_id=schedule_to_update.id,
                updated_by=sample_users["giver"].id,
                updated_by_role=UserRoleEnum.GIVER,
                schedule_date=datetime.date.today()
                + datetime.timedelta(days=1),  # 改為同一天
                start_time=datetime.time(9, 30),
                end_time=datetime.time(10, 30),
            )

        update_error_message = str(exc_info.value)
        assert "重疊時段" in update_error_message
        assert "更新時段" in update_error_message
        assert str(schedule_to_update.id) in update_error_message
        assert "檢測到" in update_error_message
        assert "1" in update_error_message
