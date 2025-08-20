"""
時段 CRUD 操作測試模組。

測試時段相關的資料庫操作，包括建立、查詢、更新和刪除時段。
"""

# ===== 標準函式庫 =====
from datetime import date, time  # 日期和時間處理

# ===== 第三方套件 =====
import pytest  # 測試框架
from sqlalchemy.orm import Session  # 資料庫會話

# ===== 本地模組 =====
from app.crud.crud_schedule import ScheduleCRUD  # CRUD 操作
from app.models.enums import ScheduleStatusEnum, UserRoleEnum  # 角色枚舉
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型
from app.schemas import ScheduleData, UserCreate  # 資料模型
from app.utils.error_handler import BusinessLogicError, NotFoundError  # 錯誤處理
from tests.logger import log_test_info


class TestScheduleCRUD:
    """時段 CRUD 操作測試類別。"""

    def test_create_user_success(self, db_session: Session):
        """測試成功建立使用者。"""
        # 直接使用 User 模型建立使用者
        user = User(name="測試使用者", email="test@example.com")
        db_session.add(user)
        db_session.commit()

        assert user.name == "測試使用者"
        assert user.email == "test@example.com"
        assert user.id is not None

    def test_create_user_duplicate_email(self, db_session: Session):
        """測試建立重複 email 的使用者。"""
        # 建立第一個使用者
        user1 = User(name="測試使用者1", email="test@example.com")
        db_session.add(user1)
        db_session.commit()

        # 嘗試建立第二個相同 email 的使用者
        user2 = User(name="測試使用者2", email="test@example.com")
        db_session.add(user2)

        # 這會在提交時拋出資料庫約束錯誤，這是預期的行為
        with pytest.raises(Exception):  # 可以是 IntegrityError 或其他資料庫錯誤
            db_session.commit()

    def test_create_schedules_success(self, db_session: Session):
        """測試成功建立多個時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        schedules_data = [
            ScheduleData(
                giver_id=user.id,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="測試時段1",
                status=ScheduleStatusEnum.AVAILABLE,
            ),
            ScheduleData(
                giver_id=user.id,
                date=date(2024, 1, 16),
                start_time=time(14, 0),
                end_time=time(15, 0),
                note="測試時段2",
                status=ScheduleStatusEnum.AVAILABLE,
            ),
        ]

        schedules = crud.create_schedules(
            db_session,
            schedules_data,
            created_by=user.id,
            created_by_role=UserRoleEnum.GIVER,
        )

        assert len(schedules) == 2
        assert schedules[0].giver_id == user.id
        assert schedules[0].date == date(2024, 1, 15)
        assert schedules[1].giver_id == user.id
        assert schedules[1].date == date(2024, 1, 16)

    def test_check_schedule_overlap_no_overlap(self, db_session: Session):
        """測試檢查時段重疊 - 無重疊。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(existing_schedule)
        db_session.commit()

        # 檢查新時段（不重疊）
        overlapping = crud.check_schedule_overlap(
            db_session, user.id, date(2024, 1, 15), time(10, 0), time(11, 0)
        )

        assert len(overlapping) == 0

    def test_check_schedule_overlap_with_overlap(self, db_session: Session):
        """測試檢查時段重疊 - 有重疊。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(existing_schedule)
        db_session.commit()

        # 檢查新時段（重疊）
        overlapping = crud.check_schedule_overlap(
            db_session, user.id, date(2024, 1, 15), time(9, 30), time(10, 30)
        )

        assert len(overlapping) == 1
        assert overlapping[0].id == existing_schedule.id

    def test_create_schedules_with_overlap(self, db_session: Session):
        """測試建立重疊時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立現有時段
        existing_schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(existing_schedule)
        db_session.commit()

        # 嘗試建立重疊時段
        schedules_data = [
            ScheduleData(
                giver_id=user.id,
                date=date(2024, 1, 15),
                start_time=time(9, 30),
                end_time=time(10, 30),
                note="重疊時段",
                status=ScheduleStatusEnum.AVAILABLE,
            )
        ]

        with pytest.raises(BusinessLogicError, match="時段重複或重疊"):
            crud.create_schedules(
                db_session,
                schedules_data,
                created_by=user.id,
                created_by_role=UserRoleEnum.GIVER,
            )

    def test_get_schedules_all(self, db_session: Session):
        """測試查詢所有時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule1 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status=ScheduleStatusEnum.PENDING,
        )
        db_session.add_all([schedule1, schedule2])
        db_session.commit()

        schedules = crud.get_schedules(db_session)

        assert len(schedules) == 2

    def test_get_schedules_filter_by_giver_id(self, db_session: Session):
        """測試根據 giver_id 篩選時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user1 = User(name="測試 Giver 1", email="giver1@example.com")
        user2 = User(name="測試 Giver 2", email="giver2@example.com")
        db_session.add_all([user1, user2])
        db_session.commit()

        # 建立測試時段
        schedule1 = Schedule(
            giver_id=user1.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        schedule2 = Schedule(
            giver_id=user2.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add_all([schedule1, schedule2])
        db_session.commit()

        schedules = crud.get_schedules(db_session, giver_id=user1.id)

        assert len(schedules) == 1
        assert schedules[0].giver_id == user1.id

    def test_get_schedules_filter_by_status(self, db_session: Session):
        """測試根據狀態篩選時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule1 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status=ScheduleStatusEnum.PENDING,
        )
        db_session.add_all([schedule1, schedule2])
        db_session.commit()

        schedules = crud.get_schedules(
            db_session, status_filter=ScheduleStatusEnum.AVAILABLE
        )

        assert len(schedules) == 1
        assert schedules[0].status == ScheduleStatusEnum.AVAILABLE

    def test_get_schedules_filter_by_both(self, db_session: Session):
        """測試同時根據 giver_id 和狀態篩選時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user1 = User(name="測試 Giver 1", email="giver1@example.com")
        user2 = User(name="測試 Giver 2", email="giver2@example.com")
        db_session.add_all([user1, user2])
        db_session.commit()

        # 建立測試時段
        schedule1 = Schedule(
            giver_id=user1.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        schedule2 = Schedule(
            giver_id=user1.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status=ScheduleStatusEnum.ACCEPTED,
        )
        schedule3 = Schedule(
            giver_id=user2.id,
            date=date(2024, 1, 17),
            start_time=time(16, 0),
            end_time=time(17, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add_all([schedule1, schedule2, schedule3])
        db_session.commit()

        schedules = crud.get_schedules(
            db_session, giver_id=user1.id, status_filter=ScheduleStatusEnum.AVAILABLE
        )

        assert len(schedules) == 1
        assert schedules[0].giver_id == user1.id
        assert schedules[0].status == ScheduleStatusEnum.AVAILABLE

    def test_get_schedules_exclude_deleted(self, db_session: Session):
        """測試查詢時段時排除已軟刪除的記錄。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule1 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add_all([schedule1, schedule2])
        db_session.commit()

        # 軟刪除其中一個時段
        crud.delete_schedule(db_session, schedule1.id)

        # 查詢時段，應該只返回未刪除的時段
        schedules = crud.get_schedules(db_session, giver_id=user.id)

        assert len(schedules) == 1
        assert schedules[0].id == schedule2.id
        assert schedules[0].deleted_at is None

    def test_get_schedule_by_id_success(self, db_session: Session):
        """測試成功根據 ID 查詢時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule)
        db_session.commit()

        found_schedule = crud.get_schedule_by_id(db_session, schedule.id)

        assert found_schedule is not None
        assert found_schedule.id == schedule.id
        assert found_schedule.giver_id == user.id

    def test_get_schedule_by_id_not_found(self, db_session: Session):
        """測試根據不存在的 ID 查詢時段。"""
        crud = ScheduleCRUD()

        with pytest.raises(NotFoundError, match="時段不存在: ID=999"):
            crud.get_schedule_by_id(db_session, 999)

    def test_update_schedule_success(self, db_session: Session):
        """測試成功更新時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule)
        db_session.commit()

        # 更新時段
        updated_schedule = crud.update_schedule(
            db_session,
            schedule.id,
            updated_by=user.id,
            updated_by_role=UserRoleEnum.GIVER,
            schedule_date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            note="更新後的備註",
        )

        assert updated_schedule is not None
        assert updated_schedule.date == date(2024, 1, 16)
        assert updated_schedule.start_time == time(14, 0)
        assert updated_schedule.end_time == time(15, 0)
        assert updated_schedule.note == "更新後的備註"

    def test_update_schedule_not_found(self, db_session: Session):
        """測試更新不存在的時段。"""
        crud = ScheduleCRUD()

        # 先建立一個使用者
        user = User(name="測試使用者", email="test@example.com")
        db_session.add(user)
        db_session.commit()

        with pytest.raises(NotFoundError, match="時段不存在: ID=999"):
            crud.update_schedule(
                db_session,
                999,
                updated_by=user.id,
                updated_by_role=UserRoleEnum.SYSTEM,
                note="測試備註",
            )

    def test_update_schedule_with_overlap(self, db_session: Session):
        """測試更新時段時的重疊檢查。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立第一個時段
        schedule1 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule1)

        # 建立第二個時段（與第一個重疊）
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 30),
            end_time=time(10, 30),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule2)
        db_session.commit()

        # 嘗試更新第一個時段，使其與第二個時段重疊
        with pytest.raises(BusinessLogicError, match="時段重疊"):
            crud.update_schedule(
                db_session,
                schedule1.id,
                updated_by=user.id,
                updated_by_role=UserRoleEnum.GIVER,
                start_time=time(9, 15),
                end_time=time(10, 15),
            )

    def test_update_schedule_without_overlap(self, db_session: Session):
        """測試更新時段時無重疊的情況。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立第一個時段
        schedule1 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule1)

        # 建立第二個時段（不重疊）
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(11, 0),
            end_time=time(12, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule2)
        db_session.commit()

        # 更新第一個時段，不與第二個時段重疊
        updated_schedule = crud.update_schedule(
            db_session,
            schedule1.id,
            updated_by=user.id,
            updated_by_role=UserRoleEnum.GIVER,
            start_time=time(8, 0),
            end_time=time(9, 0),
        )

        assert updated_schedule is not None
        assert updated_schedule.start_time == time(8, 0)
        assert updated_schedule.end_time == time(9, 0)

    def test_update_schedule_non_time_fields_no_overlap_check(
        self, db_session: Session
    ):
        """測試更新非時間欄位時不進行重疊檢查。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule)
        db_session.commit()

        # 更新非時間欄位（應該不會觸發重疊檢查）
        updated_schedule = crud.update_schedule(
            db_session,
            schedule.id,
            updated_by=user.id,
            updated_by_role=UserRoleEnum.GIVER,
            note="更新備註",
            status=ScheduleStatusEnum.PENDING,
        )

        assert updated_schedule is not None
        assert updated_schedule.note == "更新備註"
        assert updated_schedule.status == ScheduleStatusEnum.PENDING

    def test_delete_schedule_success(self, db_session: Session):
        """測試成功軟刪除時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule)
        db_session.commit()

        # 軟刪除時段
        result = crud.delete_schedule(db_session, schedule.id)

        assert result is True

        # 確認時段已被軟刪除（在正常查詢中不可見）
        with pytest.raises(NotFoundError, match="時段不存在: ID=1"):
            crud.get_schedule_by_id(db_session, schedule.id)

        # 確認時段仍然存在但已被軟刪除
        found_schedule_with_deleted = crud.get_schedule_by_id_including_deleted(
            db_session, schedule.id
        )
        assert found_schedule_with_deleted is not None
        assert found_schedule_with_deleted.deleted_at is not None

    def test_delete_schedule_not_found(self, db_session: Session):
        """測試刪除不存在的時段。"""
        crud = ScheduleCRUD()

        result = crud.delete_schedule(db_session, 999)

        assert result is False

    def test_delete_schedule_already_deleted(self, db_session: Session):
        """測試重複軟刪除時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule)
        db_session.commit()

        # 第一次軟刪除
        result1 = crud.delete_schedule(db_session, schedule.id)
        assert result1 is True

        # 第二次軟刪除（應該成功，因為已經被軟刪除）
        result2 = crud.delete_schedule(db_session, schedule.id)
        assert result2 is True

        # 確認時段仍然存在但已被軟刪除
        found_schedule_with_deleted = crud.get_schedule_by_id_including_deleted(
            db_session, schedule.id
        )
        assert found_schedule_with_deleted is not None
        assert found_schedule_with_deleted.deleted_at is not None

    def test_create_schedules_with_invalid_operator(self, db_session: Session):
        """測試使用不存在的操作者建立時段。"""
        crud = ScheduleCRUD()
        schedule_data = [
            ScheduleData(
                giver_id=1,
                date="2024-01-15",
                start_time="09:00:00",
                end_time="10:00:00",
                note="測試時段",
                status=ScheduleStatusEnum.AVAILABLE,
            )
        ]

        # 嘗試使用不存在的操作者ID
        with pytest.raises(NotFoundError, match="使用者不存在: ID=999"):
            crud.create_schedules(
                db_session,
                schedule_data,
                created_by=999,
                created_by_role=UserRoleEnum.GIVER,
            )

    def test_update_schedule_with_invalid_operator(self, db_session: Session):
        """測試使用不存在的操作者更新時段。"""
        crud = ScheduleCRUD()

        # 先建立一個使用者和時段
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        schedule_data = [
            ScheduleData(
                giver_id=user.id,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="原始時段",
                status=ScheduleStatusEnum.AVAILABLE,
            )
        ]

        schedules = crud.create_schedules(
            db_session, schedule_data, user.id, UserRoleEnum.GIVER
        )
        schedule = schedules[0]

        # 嘗試使用不存在的操作者ID更新時段
        with pytest.raises(NotFoundError, match="使用者不存在: ID=999"):
            crud.update_schedule(
                db_session,
                schedule.id,
                updated_by=999,
                updated_by_role=UserRoleEnum.GIVER,
                note="更新的時段",
            )

    def test_delete_schedule_with_invalid_operator(self, db_session: Session):
        """測試使用無效操作者刪除時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule)
        db_session.commit()

        # 嘗試使用不存在的操作者刪除時段
        with pytest.raises(NotFoundError, match="使用者不存在: ID=999"):
            crud.delete_schedule(
                db_session,
                schedule.id,
                deleted_by=999,  # 不存在的使用者 ID
                deleted_by_role=UserRoleEnum.GIVER,
            )

    def test_format_overlap_error_message(self, db_session: Session):
        """測試格式化重疊時段錯誤訊息。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        # 建立測試時段
        schedule = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),  # 週一
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule)
        db_session.commit()

        # 測試建立上下文的錯誤訊息
        create_error_msg = crud._format_overlap_error_message(
            [schedule], date(2024, 1, 15), "建立"
        )
        expected_create_msg = "您正輸入的時段，和您之前曾輸入的「2024/01/15（週一） 09:00~10:00」時段重複或重疊，請重新輸入"
        assert create_error_msg == expected_create_msg

        # 測試更新上下文的錯誤訊息
        update_error_msg = crud._format_overlap_error_message(
            [schedule], date(2024, 1, 15), "更新"
        )
        expected_update_msg = (
            "時段重疊：與以下時段衝突 - 2024/01/15（週一） 09:00-10:00"
        )
        assert update_error_msg == expected_update_msg

        # 測試多個重疊時段
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 15),  # 週一
            start_time=time(14, 0),
            end_time=time(15, 0),
            note="測試時段2",
            status=ScheduleStatusEnum.AVAILABLE,
        )
        db_session.add(schedule2)
        db_session.commit()

        multi_error_msg = crud._format_overlap_error_message(
            [schedule, schedule2], date(2024, 1, 15), "建立"
        )
        expected_multi_msg = "您正輸入的時段，和您之前曾輸入的「2024/01/15（週一） 09:00~10:00, 2024/01/15（週一） 14:00~15:00」時段重複或重疊，請重新輸入"
        assert multi_error_msg == expected_multi_msg

    def test_validate_user_exists(self, db_session: Session):
        """測試使用者驗證輔助函數。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試使用者", email="test@example.com")
        db_session.add(user)
        db_session.commit()

        # 測試成功驗證
        validated_user = crud._validate_user_exists(db_session, user.id, "操作者")
        assert validated_user.id == user.id
        assert validated_user.name == "測試使用者"

        # 測試不存在的使用者
        with pytest.raises(NotFoundError, match="使用者不存在: ID=999"):
            crud._validate_user_exists(db_session, 999, "操作者")

        # 測試不同的上下文
        with pytest.raises(NotFoundError, match="使用者不存在: ID=999"):
            crud._validate_user_exists(db_session, 999, "更新者")
