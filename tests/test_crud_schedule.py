"""
CRUD 時段模組測試。

測試時段相關的資料庫操作，包括建立、查詢、更新和刪除時段。
"""

from datetime import date, time

# ===== 標準函式庫 =====
import pytest

# ===== 第三方套件 =====
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ===== 本地模組 =====
from app.crud.crud_schedule import ScheduleCRUD
from app.models.user import User
from app.schemas import ScheduleCreate, UserCreate


# ===== 測試設定 =====
class TestScheduleCRUD:
    """時段 CRUD 測試類別。"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """設定測試環境。"""
        # 使用記憶體資料庫進行測試
        self.engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # 建立資料表
        from app.models.database import Base

        Base.metadata.create_all(bind=self.engine)

        # 建立 CRUD 實例
        self.crud = ScheduleCRUD()

        # 建立測試會話
        self.db = self.TestingSessionLocal()

        yield

        # 清理測試資料
        self.db.close()

    def test_create_user_success(self):
        """測試成功建立使用者。"""
        # 準備測試資料
        user_data = UserCreate(name="測試使用者", email="test@example.com")

        # 執行測試
        result = self.crud.create_user(self.db, user_data)

        # 驗證結果
        assert result is not None
        assert result.name == "測試使用者"
        assert result.email == "test@example.com"
        assert result.id is not None

        # 驗證資料庫中確實存在
        db_user = self.db.query(User).filter(User.email == "test@example.com").first()
        assert db_user is not None
        assert db_user.name == "測試使用者"

    def test_create_user_duplicate_email(self):
        """測試建立重複 email 的使用者。"""
        # 準備測試資料
        user_data = UserCreate(name="測試使用者", email="test@example.com")

        # 先建立一個使用者
        self.crud.create_user(self.db, user_data)

        # 嘗試建立相同 email 的使用者
        with pytest.raises(ValueError, match="此電子信箱已被使用"):
            self.crud.create_user(self.db, user_data)

    def test_create_schedules_success(self):
        """測試成功建立多個時段。"""
        # 準備測試資料
        schedules_data = [
            ScheduleCreate(
                giver_id=1,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="測試時段1",
                status="available",
                role="giver",
            ),
            ScheduleCreate(
                giver_id=1,
                date=date(2024, 1, 16),
                start_time=time(14, 0),
                end_time=time(15, 0),
                note="測試時段2",
                status="available",
                role="giver",
            ),
        ]

        # 執行測試
        result = self.crud.create_schedules(self.db, schedules_data)

        # 驗證結果
        assert len(result) == 2
        assert result[0].giver_id == 1
        assert result[0].date == date(2024, 1, 15)
        assert result[0].start_time == time(9, 0)
        assert result[0].end_time == time(10, 0)
        assert result[0].note == "測試時段1"
        assert result[0].status == "available"
        assert result[0].role == "giver"

        assert result[1].giver_id == 1
        assert result[1].date == date(2024, 1, 16)
        assert result[1].start_time == time(14, 0)
        assert result[1].end_time == time(15, 0)
        assert result[1].note == "測試時段2"
        assert result[1].status == "available"
        assert result[1].role == "giver"

        # 驗證所有時段都有 ID
        assert result[0].id is not None
        assert result[1].id is not None

    def test_get_schedules_all(self):
        """測試查詢所有時段。"""
        # 準備測試資料
        schedules_data = [
            ScheduleCreate(
                giver_id=1,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="測試時段1",
                status="available",
                role="giver",
            ),
            ScheduleCreate(
                giver_id=2,
                date=date(2024, 1, 16),
                start_time=time(14, 0),
                end_time=time(15, 0),
                note="測試時段2",
                status="booked",
                role="giver",
            ),
        ]

        # 建立時段
        self.crud.create_schedules(self.db, schedules_data)

        # 執行測試 - 查詢所有時段
        result = self.crud.get_schedules(self.db)

        # 驗證結果
        assert len(result) == 2

    def test_get_schedules_filter_by_giver_id(self):
        """測試根據 giver_id 篩選時段。"""
        # 準備測試資料
        schedules_data = [
            ScheduleCreate(
                giver_id=1,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="測試時段1",
                status="available",
                role="giver",
            ),
            ScheduleCreate(
                giver_id=2,
                date=date(2024, 1, 16),
                start_time=time(14, 0),
                end_time=time(15, 0),
                note="測試時段2",
                status="available",
                role="giver",
            ),
        ]

        # 建立時段
        self.crud.create_schedules(self.db, schedules_data)

        # 執行測試 - 篩選 giver_id = 1
        result = self.crud.get_schedules(self.db, giver_id=1)

        # 驗證結果
        assert len(result) == 1
        assert result[0].giver_id == 1

    def test_get_schedules_filter_by_status(self):
        """測試根據狀態篩選時段。"""
        # 準備測試資料
        schedules_data = [
            ScheduleCreate(
                giver_id=1,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="測試時段1",
                status="available",
                role="giver",
            ),
            ScheduleCreate(
                giver_id=2,
                date=date(2024, 1, 16),
                start_time=time(14, 0),
                end_time=time(15, 0),
                note="測試時段2",
                status="booked",
                role="giver",
            ),
        ]

        # 建立時段
        self.crud.create_schedules(self.db, schedules_data)

        # 執行測試 - 篩選 status = "booked"
        result = self.crud.get_schedules(self.db, status_filter="booked")

        # 驗證結果
        assert len(result) == 1
        assert result[0].status == "booked"

    def test_get_schedules_filter_by_both(self):
        """測試同時根據 giver_id 和狀態篩選時段。"""
        # 準備測試資料
        schedules_data = [
            ScheduleCreate(
                giver_id=1,
                date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                note="測試時段1",
                status="available",
                role="giver",
            ),
            ScheduleCreate(
                giver_id=1,
                date=date(2024, 1, 16),
                start_time=time(14, 0),
                end_time=time(15, 0),
                note="測試時段2",
                status="booked",
                role="giver",
            ),
            ScheduleCreate(
                giver_id=2,
                date=date(2024, 1, 17),
                start_time=time(16, 0),
                end_time=time(17, 0),
                note="測試時段3",
                status="available",
                role="giver",
            ),
        ]

        # 建立時段
        self.crud.create_schedules(self.db, schedules_data)

        # 執行測試 - 篩選 giver_id = 1 且 status = "available"
        result = self.crud.get_schedules(self.db, giver_id=1, status_filter="available")

        # 驗證結果
        assert len(result) == 1
        assert result[0].giver_id == 1
        assert result[0].status == "available"

    def test_get_schedule_by_id_success(self):
        """測試成功根據 ID 查詢時段。"""
        # 準備測試資料
        schedule_data = ScheduleCreate(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            status="available",
            role="giver",
        )

        # 建立時段
        created_schedules = self.crud.create_schedules(self.db, [schedule_data])
        schedule_id = created_schedules[0].id

        # 執行測試
        result = self.crud.get_schedule_by_id(self.db, schedule_id)

        # 驗證結果
        assert result is not None
        assert result.id == schedule_id
        assert result.giver_id == 1
        assert result.note == "測試時段"

    def test_get_schedule_by_id_not_found(self):
        """測試查詢不存在的時段 ID。"""
        # 執行測試
        result = self.crud.get_schedule_by_id(self.db, 999)

        # 驗證結果
        assert result is None

    def test_update_schedule_success(self):
        """測試成功更新時段。"""
        # 準備測試資料
        schedule_data = ScheduleCreate(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="原始備註",
            status="available",
            role="giver",
        )

        # 建立時段
        created_schedules = self.crud.create_schedules(self.db, [schedule_data])
        schedule_id = created_schedules[0].id

        # 執行測試 - 更新備註和狀態
        result = self.crud.update_schedule(
            self.db, schedule_id, note="更新後的備註", status="booked"
        )

        # 驗證結果
        assert result is not None
        assert result.id == schedule_id
        assert result.note == "更新後的備註"
        assert result.status == "booked"
        assert result.giver_id == 1  # 其他欄位保持不變

    def test_update_schedule_not_found(self):
        """測試更新不存在的時段。"""
        # 執行測試
        result = self.crud.update_schedule(self.db, 999, note="新備註")

        # 驗證結果
        assert result is None

    def test_delete_schedule_success(self):
        """測試成功刪除時段。"""
        # 準備測試資料
        schedule_data = ScheduleCreate(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            status="available",
            role="giver",
        )

        # 建立時段
        created_schedules = self.crud.create_schedules(self.db, [schedule_data])
        schedule_id = created_schedules[0].id

        # 執行測試
        result = self.crud.delete_schedule(self.db, schedule_id)

        # 驗證結果
        assert result is True

        # 驗證時段確實被刪除
        deleted_schedule = self.crud.get_schedule_by_id(self.db, schedule_id)
        assert deleted_schedule is None

    def test_delete_schedule_not_found(self):
        """測試刪除不存在的時段。"""
        # 執行測試
        result = self.crud.delete_schedule(self.db, 999)

        # 驗證結果
        assert result is False
