"""時段服務層測試。"""

from datetime import date, time
from unittest.mock import Mock, patch

import pytest

from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.enums.operations import DeletionResult
from app.schemas import ScheduleBase
from app.services.schedule import ScheduleService


@pytest.fixture
def service():
    """建立服務實例。"""
    return ScheduleService()


@pytest.fixture
def mock_db():
    """建立模擬資料庫會話。"""
    return Mock()


@pytest.fixture
def sample_schedule_data():
    """建立範例時段資料。"""
    return ScheduleBase(
        giver_id=1,
        date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )


def test_service_initialization(service):
    """測試服務初始化。"""
    # GIVEN：服務實例已建立

    # WHEN：檢查服務屬性
    has_crud = hasattr(service, 'schedule_crud')
    crud_not_none = service.schedule_crud is not None

    # THEN：確認服務具有必要的屬性
    assert has_crud
    assert crud_not_none


def test_check_schedule_overlap_no_overlap(service, mock_db):
    """測試檢查時段重疊 - 無重疊。"""
    # GIVEN：設定模擬資料庫查詢，返回空結果（無重疊）
    mock_query = Mock()
    mock_query.filter.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.options.return_value = mock_query

    # WHEN：檢查時段重疊
    result = service.check_schedule_overlap(
        db=mock_db,
        giver_id=1,
        schedule_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    # THEN：確認沒有重疊的時段
    assert result == []


def test_determine_schedule_status_taker_role(service, sample_schedule_data):
    """測試決定時段狀態 - Taker 角色。"""
    # GIVEN：Taker 角色和範例時段資料

    # WHEN：決定時段狀態
    status = service.determine_schedule_status(UserRoleEnum.TAKER, sample_schedule_data)

    # THEN：確認狀態為 PENDING
    assert status == ScheduleStatusEnum.PENDING


def test_determine_schedule_status_giver_role(service, sample_schedule_data):
    """測試決定時段狀態 - Giver 角色。"""
    # GIVEN：Giver 角色和範例時段資料

    # WHEN：決定時段狀態
    status = service.determine_schedule_status(UserRoleEnum.GIVER, sample_schedule_data)

    # THEN：確認狀態為 AVAILABLE
    assert status == ScheduleStatusEnum.AVAILABLE


@patch('app.services.schedule.logger')
def test_create_schedules_success(mock_logger, service, mock_db, sample_schedule_data):
    """測試建立時段 - 成功。"""
    # GIVEN：設定模擬的重疊檢查和建立方法
    with patch.object(service, 'check_multiple_schedules_overlap') as mock_check:
        mock_check.return_value = []

        with patch.object(service.schedule_crud, 'create_schedules') as mock_create:
            mock_create.return_value = [Mock()]

            # WHEN：建立時段
            result = service.create_schedules(
                mock_db, [sample_schedule_data], 1, UserRoleEnum.GIVER
            )

            # THEN：確認建立成功
            assert result is not None


@patch('app.services.schedule.logger')
def test_delete_schedule_success(mock_logger, service, mock_db):
    """測試刪除時段 - 成功。"""
    # GIVEN：設定模擬的刪除方法返回成功結果
    with patch.object(service.schedule_crud, 'delete_schedule') as mock_delete:
        mock_delete.return_value = DeletionResult.SUCCESS

        # WHEN：刪除時段
        result = service.delete_schedule(mock_db, 1, 1, UserRoleEnum.GIVER)

        # THEN：確認刪除成功
        assert result is True
