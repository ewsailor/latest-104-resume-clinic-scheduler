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
from app.models.enums import UserRoleEnum  # 角色枚舉
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型
from app.schemas import ScheduleCreate, UserCreate  # 資料模型


class TestScheduleCRUD:
    """時段 CRUD 操作測試類別。"""

    def test_create_user_success(self, db_session: Session):
        """測試成功建立使用者。"""
        crud = ScheduleCRUD()
        user_data = UserCreate(name="測試使用者", email="test@example.com")

        user = crud.create_user(db_session, user_data)

        assert user.name == "測試使用者"
        assert user.email == "test@example.com"
        assert user.id is not None

    def test_create_user_duplicate_email(self, db_session: Session):
        """測試建立重複 email 的使用者。"""
        crud = ScheduleCRUD()
        user_data = UserCreate(name="測試使用者", email="test@example.com")

        # 建立第一個使用者
        crud.create_user(db_session, user_data)

        # 嘗試建立第二個相同 email 的使用者
        with pytest.raises(ValueError, match="此電子信箱已被使用"):
            crud.create_user(db_session, user_data)

    def test_create_schedules_success(self, db_session: Session):
        """測試成功建立多個時段。"""
        crud = ScheduleCRUD()

        # 建立測試使用者
        user = User(name="測試 Giver", email="giver@example.com")
        db_session.add(user)
        db_session.commit()

        schedules_data = [
            ScheduleCreate(
                giver_id=user.id,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="測試時段1",
                status="AVAILABLE",
            ),
            ScheduleCreate(
                giver_id=user.id,
                date=date(2024, 1, 16),
                start_time=time(14, 0),
                end_time=time(15, 0),
                note="測試時段2",
                status="AVAILABLE",
            ),
        ]

        schedules = crud.create_schedules(
            db_session,
            schedules_data,
            operator_user_id=user.id,
            operator_role=UserRoleEnum.GIVER,
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
            status="AVAILABLE",
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
            status="AVAILABLE",
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
            status="AVAILABLE",
        )
        db_session.add(existing_schedule)
        db_session.commit()

        # 嘗試建立重疊時段
        schedules_data = [
            ScheduleCreate(
                giver_id=user.id,
                date=date(2024, 1, 15),
                start_time=time(9, 30),
                end_time=time(10, 30),
                note="重疊時段",
                status="AVAILABLE",
            )
        ]

        with pytest.raises(ValueError, match="時段重複或重疊"):
            crud.create_schedules(
                db_session,
                schedules_data,
                operator_user_id=user.id,
                operator_role=UserRoleEnum.GIVER,
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
            status="AVAILABLE",
        )
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status="BOOKED",
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
            status="AVAILABLE",
        )
        schedule2 = Schedule(
            giver_id=user2.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status="AVAILABLE",
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
            status="AVAILABLE",
        )
        schedule2 = Schedule(
            giver_id=user.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status="BOOKED",
        )
        db_session.add_all([schedule1, schedule2])
        db_session.commit()

        schedules = crud.get_schedules(db_session, status_filter="AVAILABLE")

        assert len(schedules) == 1
        assert schedules[0].status == "AVAILABLE"

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
            status="AVAILABLE",
        )
        schedule2 = Schedule(
            giver_id=user1.id,
            date=date(2024, 1, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status="BOOKED",
        )
        schedule3 = Schedule(
            giver_id=user2.id,
            date=date(2024, 1, 17),
            start_time=time(16, 0),
            end_time=time(17, 0),
            status="AVAILABLE",
        )
        db_session.add_all([schedule1, schedule2, schedule3])
        db_session.commit()

        schedules = crud.get_schedules(
            db_session, giver_id=user1.id, status_filter="AVAILABLE"
        )

        assert len(schedules) == 1
        assert schedules[0].giver_id == user1.id
        assert schedules[0].status == "AVAILABLE"

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
            status="AVAILABLE",
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

        found_schedule = crud.get_schedule_by_id(db_session, 999)

        assert found_schedule is None

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
            status="AVAILABLE",
        )
        db_session.add(schedule)
        db_session.commit()

        # 更新時段
        updated_schedule = crud.update_schedule(
            db_session,
            schedule.id,
            updated_by_user_id=user.id,
            operator_role=UserRoleEnum.GIVER,
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

        updated_schedule = crud.update_schedule(
            db_session,
            999,
            updated_by_user_id=1,
            operator_role=UserRoleEnum.SYSTEM,
            note="測試備註",
        )

        assert updated_schedule is None

    def test_delete_schedule_success(self, db_session: Session):
        """測試成功刪除時段。"""
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
            status="AVAILABLE",
        )
        db_session.add(schedule)
        db_session.commit()

        # 刪除時段
        result = crud.delete_schedule(db_session, schedule.id)

        assert result is True

        # 確認時段已被刪除
        found_schedule = crud.get_schedule_by_id(db_session, schedule.id)
        assert found_schedule is None

    def test_delete_schedule_not_found(self, db_session: Session):
        """測試刪除不存在的時段。"""
        crud = ScheduleCRUD()

        result = crud.delete_schedule(db_session, 999)

        assert result is False
