"""
模型方法整合測試模組。

測試模型屬性方法、序列化方法和業務邏輯方法的整合功能。
"""

# ===== 標準函式庫 =====
import datetime

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.models.schedule import Schedule
from app.models.user import User


class TestModelMethodsIntegration:
    """模型方法整合測試類別。"""

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

    def test_user_properties_integration(self, db_session, sample_users):
        """測試使用者屬性方法整合。"""
        user = sample_users["giver"]

        # 測試活躍狀態
        assert user.is_active is True
        assert user.is_deleted is False

        # 軟刪除使用者
        user.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(user)

        # 測試刪除狀態
        assert user.is_active is False
        assert user.is_deleted is True

    def test_user_to_dict_integration(self, db_session, sample_users):
        """測試使用者 to_dict 方法整合。"""
        user = sample_users["giver"]

        # 測試活躍使用者的序列化
        user_dict = user.to_dict()

        assert isinstance(user_dict, dict)
        assert user_dict["id"] == user.id
        assert user_dict["name"] == user.name
        assert user_dict["email"] == user.email
        assert user_dict["is_active"] is True
        assert user_dict["is_deleted"] is False
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
        assert user_dict["deleted_at"] is None

        # 軟刪除使用者
        user.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(user)

        # 測試已刪除使用者的序列化
        deleted_user_dict = user.to_dict()

        assert deleted_user_dict["is_active"] is False
        assert deleted_user_dict["is_deleted"] is True
        assert deleted_user_dict["deleted_at"] is not None

    def test_user_repr_integration(self, db_session, sample_users):
        """測試使用者 __repr__ 方法整合。"""
        user = sample_users["giver"]

        # 測試字串表示
        user_repr = repr(user)

        assert isinstance(user_repr, str)
        assert f"User(id={user.id}" in user_repr
        assert f"name='{user.name}'" in user_repr
        assert f"email='{user.email}'" in user_repr

    def test_schedule_properties_integration(self, db_session, sample_users):
        """測試時段屬性方法整合。"""
        # 建立可預約時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": None,  # 可預約
            "status": ScheduleStatusEnum.AVAILABLE,
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "start_time": datetime.time(9, 0),
            "end_time": datetime.time(10, 0),
            "note": "可預約時段",
            "created_by": sample_users["admin"].id,
            "created_by_role": UserRoleEnum.SYSTEM,
        }

        schedule = Schedule(**schedule_data)
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        # 測試可預約狀態
        assert schedule.is_active is True
        assert schedule.is_deleted is False
        assert schedule.is_available is True

        # 預約時段
        schedule.taker_id = sample_users["taker"].id
        schedule.status = ScheduleStatusEnum.PENDING
        db_session.commit()
        db_session.refresh(schedule)

        # 測試預約後狀態
        assert schedule.is_active is True
        assert schedule.is_deleted is False
        assert schedule.is_available is False

        # 軟刪除時段
        schedule.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(schedule)

        # 測試刪除狀態
        assert schedule.is_active is False
        assert schedule.is_deleted is True
        assert schedule.is_available is False

    def test_schedule_to_dict_integration(self, db_session, sample_users):
        """測試時段 to_dict 方法整合。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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
        assert "created_by_user" in schedule_dict
        assert "updated_by_user" in schedule_dict
        assert "deleted_by_user" in schedule_dict

    def test_schedule_repr_integration(self, db_session, sample_users):
        """測試時段 __repr__ 方法整合。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 測試字串表示
        schedule_repr = repr(schedule)

        assert isinstance(schedule_repr, str)
        assert f"Schedule(id={schedule.id}" in schedule_repr
        assert f"giver_id={schedule.giver_id}" in schedule_repr
        assert f"date={schedule.date}" in schedule_repr
        assert f"status={schedule.status}" in schedule_repr

    def test_model_methods_with_relationships(self, db_session, sample_users):
        """測試模型方法與關聯的整合。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 測試時段的 to_dict 包含關聯資料
        schedule_dict = schedule.to_dict()

        # 驗證關聯使用者名稱
        assert schedule_dict["created_by_user"] == "系統管理員"
        assert schedule_dict["updated_by_user"] is None  # 尚未更新
        assert schedule_dict["deleted_by_user"] is None  # 尚未刪除

        # 更新時段
        schedule.status = ScheduleStatusEnum.PENDING
        schedule.updated_by = sample_users["giver"].id
        schedule.updated_by_role = UserRoleEnum.GIVER
        db_session.commit()
        db_session.refresh(schedule)

        # 測試更新後的序列化
        updated_schedule_dict = schedule.to_dict()
        assert updated_schedule_dict["updated_by_user"] == "Giver 使用者"

        # 軟刪除時段
        schedule.deleted_at = datetime.datetime.now()
        schedule.deleted_by = sample_users["admin"].id
        schedule.deleted_by_role = UserRoleEnum.SYSTEM
        db_session.commit()
        db_session.refresh(schedule)

        # 測試刪除後的序列化
        deleted_schedule_dict = schedule.to_dict()
        assert deleted_schedule_dict["deleted_by_user"] == "系統管理員"
        assert deleted_schedule_dict["is_active"] is False
        assert deleted_schedule_dict["is_deleted"] is True

    def test_model_methods_error_handling(self, db_session, sample_users):
        """測試模型方法錯誤處理。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 測試 to_dict 方法的錯誤處理
        # 模擬關聯物件為 None 的情況
        original_created_by_user = schedule.created_by_user
        schedule.created_by_user = None

        # 測試序列化不會因為關聯物件為 None 而失敗
        schedule_dict = schedule.to_dict()
        assert schedule_dict["created_by_user"] is None

        # 恢復原始狀態
        schedule.created_by_user = original_created_by_user

    def test_model_methods_performance(self, db_session, sample_users):
        """測試模型方法效能。"""
        # 建立多個時段
        schedules_data = []
        for i in range(10):
            schedule_data = {
                "giver_id": sample_users["giver"].id,
                "taker_id": sample_users["taker"].id if i % 2 == 0 else None,
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

        for schedule in schedules:
            db_session.refresh(schedule)

        # 測試批量序列化效能
        start_time = datetime.datetime.now()

        schedule_dicts = []
        for schedule in schedules:
            schedule_dict = schedule.to_dict()
            schedule_dicts.append(schedule_dict)

        end_time = datetime.datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # 驗證序列化成功且效能合理
        assert len(schedule_dicts) == 10
        assert processing_time < 1.0  # 應該在 1 秒內完成

        # 驗證每個序列化結果都正確
        for i, schedule_dict in enumerate(schedule_dicts):
            assert schedule_dict["id"] == schedules[i].id
            assert schedule_dict["note"] == f"時段 {i+1}"
            assert schedule_dict["is_active"] is True
            assert schedule_dict["is_deleted"] is False

    def test_model_methods_consistency(self, db_session, sample_users):
        """測試模型方法一致性。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 測試屬性方法與序列化方法的一致性
        assert schedule.is_active == schedule.to_dict()["is_active"]
        assert schedule.is_deleted == schedule.to_dict()["is_deleted"]
        assert schedule.is_available == schedule.to_dict()["is_available"]

        # 測試字串表示與實際資料的一致性
        schedule_repr = repr(schedule)
        assert str(schedule.id) in schedule_repr
        assert str(schedule.giver_id) in schedule_repr
        assert str(schedule.date) in schedule_repr
        assert str(schedule.status) in schedule_repr

    def test_model_methods_with_different_states(self, db_session, sample_users):
        """測試不同狀態下的模型方法。"""
        # 建立多個不同狀態的時段
        schedules_data = [
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": None,
                "status": ScheduleStatusEnum.AVAILABLE,
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "start_time": datetime.time(9, 0),
                "end_time": datetime.time(10, 0),
                "note": "可預約時段",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": sample_users["taker"].id,
                "status": ScheduleStatusEnum.PENDING,
                "date": datetime.date.today() + datetime.timedelta(days=2),
                "start_time": datetime.time(10, 0),
                "end_time": datetime.time(11, 0),
                "note": "待確認時段",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
            {
                "giver_id": sample_users["giver"].id,
                "taker_id": sample_users["taker"].id,
                "status": ScheduleStatusEnum.ACCEPTED,
                "date": datetime.date.today() + datetime.timedelta(days=3),
                "start_time": datetime.time(11, 0),
                "end_time": datetime.time(12, 0),
                "note": "已接受時段",
                "created_by": sample_users["admin"].id,
                "created_by_role": UserRoleEnum.SYSTEM,
            },
        ]

        schedules = [Schedule(**data) for data in schedules_data]
        db_session.add_all(schedules)
        db_session.commit()

        for schedule in schedules:
            db_session.refresh(schedule)

        # 測試不同狀態的屬性方法
        available_schedule = schedules[0]
        assert available_schedule.is_available is True
        assert available_schedule.is_active is True
        assert available_schedule.is_deleted is False

        pending_schedule = schedules[1]
        assert pending_schedule.is_available is False  # 有 taker_id
        assert pending_schedule.is_active is True
        assert pending_schedule.is_deleted is False

        accepted_schedule = schedules[2]
        assert accepted_schedule.is_available is False  # 有 taker_id
        assert accepted_schedule.is_active is True
        assert accepted_schedule.is_deleted is False

        # 軟刪除第一個時段
        available_schedule.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(available_schedule)

        # 測試刪除後的狀態
        assert available_schedule.is_available is False  # 已刪除
        assert available_schedule.is_active is False
        assert available_schedule.is_deleted is True

        # 測試序列化結果的一致性
        for schedule in schedules:
            schedule_dict = schedule.to_dict()
            assert schedule_dict["is_active"] == schedule.is_active
            assert schedule_dict["is_deleted"] == schedule.is_deleted
            assert schedule_dict["is_available"] == schedule.is_available

    def test_model_methods_edge_cases(self, db_session, sample_users):
        """測試模型方法邊界情況。"""
        # 建立時段
        schedule_data = {
            "giver_id": sample_users["giver"].id,
            "taker_id": sample_users["taker"].id,
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

        # 測試 taker_id 為 None 的情況
        schedule.taker_id = None
        schedule.status = ScheduleStatusEnum.AVAILABLE
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.is_available is True

        # 測試狀態不是 AVAILABLE 的情況
        schedule.status = ScheduleStatusEnum.DRAFT
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.is_available is False

        # 測試同時滿足多個條件的情況
        schedule.taker_id = None
        schedule.status = ScheduleStatusEnum.AVAILABLE
        schedule.deleted_at = None
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.is_available is True
        assert schedule.is_active is True
        assert schedule.is_deleted is False
