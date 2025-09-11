"""
時段服務層測試。

測試時段服務層模組的功能。
"""

from datetime import date, time
from unittest.mock import Mock, patch

# ===== 標準函式庫 =====
import pytest
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.enums.operations import OperationContext
from app.errors import ConflictError
from app.models.schedule import Schedule
from app.schemas import ScheduleBase
from app.services.schedule import ScheduleService


# ===== 測試設定 =====
class TestScheduleService:
    """時段服務測試類別。"""

    @pytest.fixture
    def service(self):
        """建立測試用的服務實例。"""
        return ScheduleService()

    @pytest.fixture
    def mock_db(self):
        """建立模擬資料庫會話。"""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_schedule_data(self):
        """建立範例時段資料。"""
        return ScheduleBase(
            giver_id=1,
            taker_id=None,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
        )

    @pytest.fixture
    def sample_schedule_orm(self):
        """建立範例時段 ORM 物件。"""
        return Schedule(
            id=1,
            giver_id=1,
            taker_id=None,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            status=ScheduleStatusEnum.AVAILABLE,
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
        )

    def test_service_initialization(self, service):
        """測試服務初始化。"""
        assert hasattr(service, 'schedule_crud')
        assert service.schedule_crud is not None

    def test_check_schedule_overlap_no_overlap(self, service, mock_db):
        """測試檢查時段重疊 - 無重疊。"""
        # 模擬查詢結果為空
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.options.return_value = mock_query

        overlapping_schedules = service.check_schedule_overlap(
            db=mock_db,
            giver_id=1,
            schedule_date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        assert overlapping_schedules == []

    def test_check_schedule_overlap_with_overlap(
        self, service, mock_db, sample_schedule_orm
    ):
        """測試檢查時段重疊 - 有重疊。"""
        # 模擬查詢結果有重疊時段
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.all.return_value = [
            sample_schedule_orm
        ]
        mock_db.query.return_value.options.return_value = mock_query

        overlapping_schedules = service.check_schedule_overlap(
            db=mock_db,
            giver_id=1,
            schedule_date=date(2024, 1, 15),
            start_time=time(9, 30),  # 與現有時段重疊
            end_time=time(10, 30),
        )

        assert len(overlapping_schedules) == 1
        assert overlapping_schedules[0] == sample_schedule_orm

    def test_check_schedule_overlap_exclude_schedule_id(self, service, mock_db):
        """測試檢查時段重疊 - 排除指定時段 ID。"""
        # 設置更完整的 mock 鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 讓 filter 返回自己
        mock_query.all.return_value = []  # 最終返回空列表
        mock_db.query.return_value.options.return_value = mock_query

        with patch('app.services.schedule.logger'):
            overlapping_schedules = service.check_schedule_overlap(
                db=mock_db,
                giver_id=1,
                schedule_date=date(2024, 1, 15),
                start_time=time(9, 0),
                end_time=time(10, 0),
                exclude_schedule_id=1,
            )

        # 驗證結果
        assert overlapping_schedules == []
        # 驗證查詢中排除了指定的時段 ID
        assert mock_query.filter.call_count >= 2  # 至少調用兩次 filter

    def test_check_multiple_schedules_overlap_no_overlap(
        self, service, mock_db, sample_schedule_data
    ):
        """測試檢查多個時段重疊 - 無重疊。"""
        with patch.object(service, 'check_schedule_overlap', return_value=[]):
            schedules = [sample_schedule_data]
            overlapping_schedules = service.check_multiple_schedules_overlap(
                mock_db, schedules
            )

            assert overlapping_schedules == []

    def test_check_multiple_schedules_overlap_with_overlap(
        self, service, mock_db, sample_schedule_data, sample_schedule_orm
    ):
        """測試檢查多個時段重疊 - 有重疊。"""
        with patch.object(
            service, 'check_schedule_overlap', return_value=[sample_schedule_orm]
        ):
            schedules = [sample_schedule_data]
            overlapping_schedules = service.check_multiple_schedules_overlap(
                mock_db, schedules
            )

            assert len(overlapping_schedules) == 1
            assert overlapping_schedules[0] == sample_schedule_orm

    def test_determine_schedule_status_taker_role(self, service, sample_schedule_data):
        """測試決定時段狀態 - TAKER 角色。"""
        status = service.determine_schedule_status(
            UserRoleEnum.TAKER, sample_schedule_data
        )
        assert status == ScheduleStatusEnum.PENDING

    def test_determine_schedule_status_giver_role(self, service, sample_schedule_data):
        """測試決定時段狀態 - GIVER 角色。"""
        status = service.determine_schedule_status(
            UserRoleEnum.GIVER, sample_schedule_data
        )
        assert status == ScheduleStatusEnum.AVAILABLE

    def test_determine_schedule_status_other_role(self, service, sample_schedule_data):
        """測試決定時段狀態 - 其他角色。"""
        status = service.determine_schedule_status(
            UserRoleEnum.SYSTEM, sample_schedule_data
        )
        assert status == ScheduleStatusEnum.DRAFT

    def test_determine_schedule_status_with_existing_status(self, service):
        """測試決定時段狀態 - 已有狀態。"""
        schedule_data = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.ACCEPTED,
        )
        status = service.determine_schedule_status(UserRoleEnum.SYSTEM, schedule_data)
        assert status == ScheduleStatusEnum.ACCEPTED

    def test_log_schedule_details_empty_list(self, service):
        """測試記錄時段詳情 - 空列表。"""
        with patch('app.services.schedule.logger') as mock_logger:
            service.log_schedule_details([])
            mock_logger.info.assert_called_with("建立時段: 無時段資料")

    def test_log_schedule_details_with_schedules(self, service, sample_schedule_data):
        """測試記錄時段詳情 - 有時段資料。"""
        with patch('app.services.schedule.logger') as mock_logger:
            schedules = [sample_schedule_data]
            service.log_schedule_details(schedules, OperationContext.CREATE)

            expected_message = "建立時段詳情: 時段1: 2024-01-15 09:00:00-10:00:00"
            mock_logger.info.assert_called_with(expected_message)

    def test_create_schedule_orm_objects_giver_role(
        self, service, sample_schedule_data
    ):
        """測試建立時段 ORM 物件 - GIVER 角色。"""
        schedules = [sample_schedule_data]
        orm_objects = service.create_schedule_orm_objects(
            schedules, created_by=1, created_by_role=UserRoleEnum.GIVER
        )

        assert len(orm_objects) == 1
        schedule_orm = orm_objects[0]
        assert schedule_orm.giver_id == 1
        assert schedule_orm.date == date(2024, 1, 15)
        assert schedule_orm.start_time == time(9, 0)
        assert schedule_orm.end_time == time(10, 0)
        assert schedule_orm.status == ScheduleStatusEnum.AVAILABLE
        assert schedule_orm.created_by == 1
        assert schedule_orm.created_by_role == UserRoleEnum.GIVER

    def test_create_schedule_orm_objects_taker_role(
        self, service, sample_schedule_data
    ):
        """測試建立時段 ORM 物件 - TAKER 角色。"""
        schedules = [sample_schedule_data]
        orm_objects = service.create_schedule_orm_objects(
            schedules, created_by=2, created_by_role=UserRoleEnum.TAKER
        )

        assert len(orm_objects) == 1
        schedule_orm = orm_objects[0]
        assert schedule_orm.status == ScheduleStatusEnum.PENDING
        assert schedule_orm.created_by == 2
        assert schedule_orm.created_by_role == UserRoleEnum.TAKER

    @patch('app.services.schedule.logger')
    def test_create_schedules_success(
        self, mock_logger, service, mock_db, sample_schedule_data
    ):
        """測試建立時段 - 成功。"""
        with patch.object(service, 'check_multiple_schedules_overlap', return_value=[]):
            with patch.object(service.schedule_crud, 'create_schedules') as mock_create:
                mock_schedule = Mock()
                mock_schedule.id = 1
                mock_create.return_value = [mock_schedule]

                schedules = [sample_schedule_data]
                result = service.create_schedules(
                    mock_db, schedules, created_by=1, created_by_role=UserRoleEnum.GIVER
                )

                assert len(result) == 1
                mock_create.assert_called_once()
                mock_logger.info.assert_called()

    def test_create_schedules_with_overlap(
        self, service, mock_db, sample_schedule_data, sample_schedule_orm
    ):
        """測試建立時段 - 有重疊。"""
        with patch.object(
            service,
            'check_multiple_schedules_overlap',
            return_value=[sample_schedule_orm],
        ):
            schedules = [sample_schedule_data]

            with pytest.raises(ConflictError) as exc_info:
                service.create_schedules(
                    mock_db, schedules, created_by=1, created_by_role=UserRoleEnum.GIVER
                )

            assert "檢測到 1 個重疊時段" in str(exc_info.value)

    @patch('app.services.schedule.logger')
    def test_list_schedules(self, mock_logger, service, mock_db):
        """測試查詢時段列表。"""
        with patch.object(service.schedule_crud, 'list_schedules') as mock_list:
            mock_schedules = [Mock()]
            mock_list.return_value = mock_schedules

            result = service.list_schedules(
                mock_db, giver_id=1, taker_id=None, status_filter="AVAILABLE"
            )

            assert result == mock_schedules
            mock_list.assert_called_once_with(mock_db, 1, None, "AVAILABLE")
            mock_logger.info.assert_called()

    @patch('app.services.schedule.logger')
    def test_get_schedule(self, mock_logger, service, mock_db, sample_schedule_orm):
        """測試查詢單一時段。"""
        with patch.object(
            service.schedule_crud, 'get_schedule', return_value=sample_schedule_orm
        ):
            result = service.get_schedule(mock_db, schedule_id=1)

            assert result == sample_schedule_orm
            mock_logger.info.assert_called()

    def test_new_updated_time_values(self, service, mock_db, sample_schedule_orm):
        """測試更新後的時間值。"""
        with patch.object(
            service.schedule_crud, 'get_schedule', return_value=sample_schedule_orm
        ):
            new_date, new_start_time, new_end_time = service.new_updated_time_values(
                mock_db, schedule_id=1, start_time=time(10, 0)
            )

            assert new_date == date(2024, 1, 15)  # 原始日期
            assert new_start_time == time(10, 0)  # 新的開始時間
            assert new_end_time == time(10, 0)  # 原始結束時間

    def test_check_update_overlap_no_time_change(self, service, mock_db):
        """測試檢查更新重疊 - 無時間變更。"""
        overlapping_schedules = service.check_update_overlap(
            mock_db, schedule_id=1, note="更新備註"
        )

        assert overlapping_schedules == []

    def test_check_update_overlap_with_time_change(
        self, service, mock_db, sample_schedule_orm
    ):
        """測試檢查更新重疊 - 有時間變更。"""
        with patch.object(
            service.schedule_crud, 'get_schedule', return_value=sample_schedule_orm
        ):
            with patch.object(
                service, 'check_schedule_overlap', return_value=[]
            ) as mock_check:
                overlapping_schedules = service.check_update_overlap(
                    mock_db, schedule_id=1, start_time=time(10, 0)
                )

                assert overlapping_schedules == []
                mock_check.assert_called_once()

    def test_update_schedule_success(self, service, mock_db, sample_schedule_orm):
        """測試更新時段 - 成功。"""
        with patch.object(service, 'check_update_overlap', return_value=[]):
            with patch.object(
                service.schedule_crud,
                'update_schedule',
                return_value=sample_schedule_orm,
            ) as mock_update:
                result = service.update_schedule(
                    mock_db,
                    schedule_id=1,
                    updated_by=1,
                    updated_by_role=UserRoleEnum.GIVER,
                    note="更新備註",
                )

                assert result == sample_schedule_orm
                mock_update.assert_called_once()

    def test_update_schedule_with_overlap(self, service, mock_db, sample_schedule_orm):
        """測試更新時段 - 有重疊。"""
        with patch.object(
            service, 'check_update_overlap', return_value=[sample_schedule_orm]
        ):
            with pytest.raises(ConflictError) as exc_info:
                service.update_schedule(
                    mock_db,
                    schedule_id=1,
                    updated_by=1,
                    updated_by_role=UserRoleEnum.GIVER,
                    start_time=time(10, 0),
                )

            assert "檢測到 1 個重疊時段" in str(exc_info.value)

    @patch('app.services.schedule.logger')
    def test_delete_schedule_success(self, mock_logger, service, mock_db):
        """測試軟刪除時段 - 成功。"""
        with patch.object(
            service.schedule_crud, 'delete_schedule', return_value=True
        ) as mock_delete:
            result = service.delete_schedule(
                mock_db, schedule_id=1, deleted_by=1, deleted_by_role=UserRoleEnum.GIVER
            )

            assert result is True
            mock_delete.assert_called_once_with(mock_db, 1, 1, UserRoleEnum.GIVER)
            mock_logger.info.assert_called()

    @patch('app.services.schedule.logger')
    def test_delete_schedule_failure(self, mock_logger, service, mock_db):
        """測試軟刪除時段 - 失敗。"""
        with patch.object(
            service.schedule_crud, 'delete_schedule', return_value=False
        ) as mock_delete:
            result = service.delete_schedule(
                mock_db, schedule_id=1, deleted_by=1, deleted_by_role=UserRoleEnum.GIVER
            )

            assert result is False
            mock_delete.assert_called_once_with(mock_db, 1, 1, UserRoleEnum.GIVER)
            mock_logger.warning.assert_called()

    def test_delete_schedule_without_deleted_by(self, service, mock_db):
        """測試軟刪除時段 - 無刪除者資訊。"""
        with patch.object(
            service.schedule_crud, 'delete_schedule', return_value=True
        ) as mock_delete:
            result = service.delete_schedule(mock_db, schedule_id=1)

            assert result is True
            mock_delete.assert_called_once_with(mock_db, 1, None, None)


if __name__ == "__main__":
    pytest.main([__file__])
