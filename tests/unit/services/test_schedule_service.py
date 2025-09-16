"""
時段服務層測試模組。

測試時段相關的業務邏輯處理，包括時段重疊檢查、時段管理等。
"""

# ===== 標準函式庫 =====
from unittest.mock import Mock, patch

# ===== 第三方套件 =====
import pytest
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.enums.models import UserRoleEnum
from app.errors import BusinessLogicError
from app.services.schedule import ScheduleService


class TestScheduleService:
    """時段服務測試類別。"""

    @pytest.fixture
    def service(self):
        """建立服務實例。"""
        return ScheduleService()

    @pytest.fixture
    def mock_db(self):
        """建立模擬資料庫會話。"""
        return Mock(spec=Session)

    def test_delete_schedule_unknown_result(self, service, mock_db):
        """測試刪除時段時發生未知結果。"""
        # 模擬 CRUD 返回未知的刪除結果
        with patch.object(service.schedule_crud, 'delete_schedule') as mock_delete:
            mock_delete.return_value = "UNKNOWN_RESULT"

            with pytest.raises(BusinessLogicError) as exc_info:
                service.delete_schedule(
                    mock_db,
                    schedule_id=1,
                    deleted_by=1,
                    deleted_by_role=UserRoleEnum.GIVER,
                )

            assert "未知的刪除結果: UNKNOWN_RESULT" in str(exc_info.value)

    def test_delete_schedule_unknown_result_with_none(self, service, mock_db):
        """測試刪除時段時發生 None 結果。"""
        # 模擬 CRUD 返回 None
        with patch.object(service.schedule_crud, 'delete_schedule') as mock_delete:
            mock_delete.return_value = None

            with pytest.raises(BusinessLogicError) as exc_info:
                service.delete_schedule(
                    mock_db,
                    schedule_id=1,
                    deleted_by=1,
                    deleted_by_role=UserRoleEnum.GIVER,
                )

            assert "未知的刪除結果: None" in str(exc_info.value)

    def test_delete_schedule_unknown_result_with_integer(self, service, mock_db):
        """測試刪除時段時發生整數結果。"""
        # 模擬 CRUD 返回整數（不預期的結果）
        with patch.object(service.schedule_crud, 'delete_schedule') as mock_delete:
            mock_delete.return_value = 42

            with pytest.raises(BusinessLogicError) as exc_info:
                service.delete_schedule(
                    mock_db,
                    schedule_id=1,
                    deleted_by=1,
                    deleted_by_role=UserRoleEnum.GIVER,
                )

            assert "未知的刪除結果: 42" in str(exc_info.value)
