"""
服務層模組初始化測試。

測試服務層模組的導入和配置。
"""

# ===== 標準函式庫 =====
import pytest

# ===== 本地模組 =====
from app.services import ScheduleService, schedule_service


# ===== 測試設定 =====
class TestServicesInit:
    """服務層模組初始化測試類別。"""

    def test_schedule_service_import(self):
        """測試 ScheduleService 類別導入。"""
        assert ScheduleService is not None
        assert hasattr(ScheduleService, '__init__')
        assert hasattr(ScheduleService, 'create_schedules')
        assert hasattr(ScheduleService, 'list_schedules')
        assert hasattr(ScheduleService, 'get_schedule')
        assert hasattr(ScheduleService, 'update_schedule')
        assert hasattr(ScheduleService, 'delete_schedule')

    def test_schedule_service_instance_import(self):
        """測試 schedule_service 實例導入。"""
        assert schedule_service is not None
        assert isinstance(schedule_service, ScheduleService)

    def test_schedule_service_instance_methods(self):
        """測試 schedule_service 實例方法。"""
        assert hasattr(schedule_service, 'schedule_crud')
        assert hasattr(schedule_service, 'check_schedule_overlap')
        assert hasattr(schedule_service, 'check_multiple_schedules_overlap')
        assert hasattr(schedule_service, 'determine_schedule_status')
        assert hasattr(schedule_service, 'log_schedule_details')
        assert hasattr(schedule_service, 'create_schedule_orm_objects')
        assert hasattr(schedule_service, 'create_schedules')
        assert hasattr(schedule_service, 'list_schedules')
        assert hasattr(schedule_service, 'get_schedule')
        assert hasattr(schedule_service, 'new_updated_time_values')
        assert hasattr(schedule_service, 'check_update_overlap')
        assert hasattr(schedule_service, 'update_schedule')
        assert hasattr(schedule_service, 'delete_schedule')

    def test_schedule_service_singleton_pattern(self):
        """測試 schedule_service 單例模式。"""
        from app.services import schedule_service as service1
        from app.services import schedule_service as service2

        assert service1 is service2
        assert id(service1) == id(service2)


if __name__ == "__main__":
    pytest.main([__file__])
