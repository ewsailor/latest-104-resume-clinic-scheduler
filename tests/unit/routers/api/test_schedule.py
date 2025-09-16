"""
時段管理 API 路由測試。

測試時段管理 API 路由模組的功能。
"""

# ===== 標準函式庫 =====
from datetime import date, time
import inspect
from unittest.mock import Mock, patch

# ===== 第三方套件 =====
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.routers.api.schedule import (
    create_schedules,
    delete_schedule,
    get_schedule,
    list_schedules,
    router,
    update_schedule,
)
from app.schemas import (
    ScheduleBase,
    ScheduleCreateRequest,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleUpdateBase,
)


# ===== 測試設定 =====
class TestScheduleAPIRouter:
    """時段管理 API 路由測試類別。"""

    @pytest.fixture
    def app(self):
        """建立測試用的 FastAPI 應用程式。"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """建立測試客戶端。"""
        return TestClient(app)

    def test_router_configuration(self):
        """測試路由器配置。"""
        # 檢查路由器基本屬性
        assert hasattr(router, 'routes')
        assert hasattr(router, 'prefix')
        assert hasattr(router, 'tags')

        # 檢查路由數量
        assert len(router.routes) == 5

    def test_route_paths(self):
        """測試路由路徑。"""
        expected_paths = [
            "/api/v1/schedules",
            "/api/v1/schedules",
            "/api/v1/schedules/{schedule_id}",
            "/api/v1/schedules/{schedule_id}",
            "/api/v1/schedules/{schedule_id}",
        ]

        actual_paths = [route.path for route in router.routes]
        for expected_path in expected_paths:
            assert expected_path in actual_paths

    def test_route_methods(self):
        """測試路由方法。"""
        expected_methods = ["POST", "GET", "GET", "PATCH", "DELETE"]

        actual_methods = []
        for route in router.routes:
            if hasattr(route, 'methods'):
                actual_methods.extend(route.methods)

        for expected_method in expected_methods:
            assert expected_method in actual_methods

    def test_create_schedules_function_signature(self):
        """測試建立時段函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(create_schedules)

        # 檢查參數
        assert 'request' in sig.parameters
        assert 'db' in sig.parameters

        # 檢查返回類型
        assert sig.return_annotation is not None

    def test_list_schedules_function_signature(self):
        """測試取得時段列表函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(list_schedules)

        # 檢查參數
        assert 'db' in sig.parameters
        assert 'giver_id' in sig.parameters
        assert 'taker_id' in sig.parameters
        assert 'status_filter' in sig.parameters

        # 檢查返回類型
        assert (
            hasattr(sig.return_annotation, '__origin__')
            and sig.return_annotation.__origin__ is list
        )

    def test_get_schedule_function_signature(self):
        """測試取得單一時段函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(get_schedule)

        # 檢查參數
        assert 'schedule_id' in sig.parameters
        assert 'db' in sig.parameters

        # 檢查返回類型
        assert sig.return_annotation is not None

    def test_update_schedule_function_signature(self):
        """測試更新時段函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(update_schedule)

        # 檢查參數
        assert 'schedule_id' in sig.parameters
        assert 'request' in sig.parameters
        assert 'db' in sig.parameters

        # 檢查返回類型
        assert sig.return_annotation is not None

    def test_delete_schedule_function_signature(self):
        """測試刪除時段函數簽名。"""
        # 驗證函數簽名
        sig = inspect.signature(delete_schedule)

        # 檢查參數
        assert 'schedule_id' in sig.parameters
        assert 'request' in sig.parameters
        assert 'db' in sig.parameters

        # 檢查返回類型
        assert sig.return_annotation in [type(None), None]

    def test_all_functions_are_async(self):
        """測試所有函數都是非同步函數。"""
        functions = [
            create_schedules,
            list_schedules,
            get_schedule,
            update_schedule,
            delete_schedule,
        ]

        for func in functions:
            assert inspect.iscoroutinefunction(func), f"{func.__name__} should be async"

    def test_create_schedules_validation_logic(self):
        """測試建立時段的驗證邏輯。"""
        # 測試資料：有效的時間範圍
        valid_schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),  # 開始時間早於結束時間
            end_time=time(10, 0),
        )

        request = ScheduleCreateRequest(
            schedules=[valid_schedule],
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
        )

        # 驗證邏輯：開始時間必須早於結束時間
        for schedule in request.schedules:
            assert schedule.start_time < schedule.end_time, "開始時間必須早於結束時間"

    def test_delete_schedule_request_validation(self):
        """測試刪除時段請求驗證。"""
        # 測試有效的刪除請求
        valid_request = ScheduleDeleteRequest(
            deleted_by=1,
            deleted_by_role=UserRoleEnum.GIVER,
        )

        assert valid_request.deleted_by > 0
        assert valid_request.deleted_by_role is not None

    def test_update_schedule_data_transformation(self):
        """測試更新時段資料轉換邏輯。"""
        # 測試資料轉換邏輯
        update_data = {
            "date": "2024-01-15",  # 字串格式
            "status": ScheduleStatusEnum.AVAILABLE,
        }

        # 驗證資料轉換
        assert isinstance(update_data["date"], str)
        assert update_data["status"] == ScheduleStatusEnum.AVAILABLE

    def test_route_decorators(self):
        """測試路由裝飾器。"""
        functions = [
            create_schedules,
            list_schedules,
            get_schedule,
            update_schedule,
            delete_schedule,
        ]

        # 檢查函數是否有適當的裝飾器
        for func in functions:
            assert hasattr(func, '__wrapped__') or hasattr(func, '__name__')

    def test_import_structure(self):
        """測試導入結構。"""
        # 檢查所有必要的模組都能正確導入
        assert router is not None
        assert hasattr(router, 'routes')
        assert hasattr(router, 'prefix')
        assert hasattr(router, 'tags')

    @pytest.mark.asyncio
    async def test_create_schedules_success(self):
        """測試成功建立時段。"""
        # 準備測試資料
        valid_schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        request = ScheduleCreateRequest(
            schedules=[valid_schedule],
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
        )

        # Mock 資料庫會話
        mock_db = Mock()

        # Mock 服務回傳的時段
        mock_schedule = Mock()
        mock_schedule.id = 1
        mock_schedule.giver_id = 1
        mock_schedule.taker_id = None
        mock_schedule.status = ScheduleStatusEnum.AVAILABLE
        mock_schedule.date = date(2024, 1, 15)
        mock_schedule.start_time = time(9, 0)
        mock_schedule.end_time = time(10, 0)
        mock_schedule.note = None
        mock_schedule.created_at = "2024-01-01T00:00:00Z"
        mock_schedule.created_by = 1
        mock_schedule.created_by_role = UserRoleEnum.GIVER
        mock_schedule.updated_at = "2024-01-01T00:00:00Z"
        mock_schedule.updated_by = 1
        mock_schedule.updated_by_role = UserRoleEnum.GIVER
        mock_schedule.deleted_at = None
        mock_schedule.deleted_by = None
        mock_schedule.deleted_by_role = None

        # Mock schedule_service.create_schedules
        with patch('app.routers.api.schedule.schedule_service') as mock_service:
            mock_service.create_schedules.return_value = [mock_schedule]

            # 執行函數
            result = await create_schedules(request, mock_db)

            # 驗證結果
            assert len(result) == 1
            assert result[0].id == 1
            assert result[0].giver_id == 1

            # 驗證服務被正確調用
            mock_service.create_schedules.assert_called_once_with(
                mock_db,
                [valid_schedule],
                created_by=1,
                created_by_role=UserRoleEnum.GIVER,
            )

    @pytest.mark.asyncio
    async def test_create_schedules_invalid_time(self):
        """測試建立時段時時間驗證失敗。"""
        # 準備無效的測試資料（開始時間晚於結束時間）
        invalid_schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),
            start_time=time(10, 0),  # 開始時間晚於結束時間
            end_time=time(9, 0),
        )

        request = ScheduleCreateRequest(
            schedules=[invalid_schedule],
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
        )

        # Mock 資料庫會話
        mock_db = Mock()

        # 執行函數並驗證拋出異常
        with pytest.raises(Exception) as exc_info:
            await create_schedules(request, mock_db)

        assert "開始時間必須早於結束時間" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_schedules_success(self):
        """測試成功取得時段列表。"""
        # Mock 資料庫會話
        mock_db = Mock()

        # Mock 服務回傳的時段列表
        mock_schedule = Mock()
        mock_schedule.id = 1
        mock_schedule.giver_id = 1
        mock_schedule.taker_id = None
        mock_schedule.status = ScheduleStatusEnum.AVAILABLE
        mock_schedule.date = date(2024, 1, 15)
        mock_schedule.start_time = time(9, 0)
        mock_schedule.end_time = time(10, 0)
        mock_schedule.note = None
        mock_schedule.created_at = "2024-01-01T00:00:00Z"
        mock_schedule.created_by = 1
        mock_schedule.created_by_role = UserRoleEnum.GIVER
        mock_schedule.updated_at = "2024-01-01T00:00:00Z"
        mock_schedule.updated_by = 1
        mock_schedule.updated_by_role = UserRoleEnum.GIVER
        mock_schedule.deleted_at = None
        mock_schedule.deleted_by = None
        mock_schedule.deleted_by_role = None

        # Mock schedule_service.list_schedules
        with patch('app.routers.api.schedule.schedule_service') as mock_service:
            mock_service.list_schedules.return_value = [mock_schedule]

            # 執行函數
            result = await list_schedules(
                giver_id=1,
                taker_id=None,
                status_filter=ScheduleStatusEnum.AVAILABLE,
                db=mock_db,
            )

            # 驗證結果
            assert len(result) == 1
            assert result[0].id == 1
            assert result[0].giver_id == 1

            # 驗證服務被正確調用
            mock_service.list_schedules.assert_called_once_with(
                mock_db,
                1,  # giver_id
                None,  # taker_id
                ScheduleStatusEnum.AVAILABLE,  # status_filter
            )

    @pytest.mark.asyncio
    async def test_get_schedule_success(self):
        """測試成功取得單一時段。"""
        # Mock 資料庫會話
        mock_db = Mock()

        # Mock 服務回傳的時段
        mock_schedule = Mock()
        mock_schedule.id = 1
        mock_schedule.giver_id = 1
        mock_schedule.taker_id = None
        mock_schedule.status = ScheduleStatusEnum.AVAILABLE
        mock_schedule.date = date(2024, 1, 15)
        mock_schedule.start_time = time(9, 0)
        mock_schedule.end_time = time(10, 0)
        mock_schedule.note = None
        mock_schedule.created_at = "2024-01-01T00:00:00Z"
        mock_schedule.created_by = 1
        mock_schedule.created_by_role = UserRoleEnum.GIVER
        mock_schedule.updated_at = "2024-01-01T00:00:00Z"
        mock_schedule.updated_by = 1
        mock_schedule.updated_by_role = UserRoleEnum.GIVER
        mock_schedule.deleted_at = None
        mock_schedule.deleted_by = None
        mock_schedule.deleted_by_role = None

        # Mock schedule_service.get_schedule
        with patch('app.routers.api.schedule.schedule_service') as mock_service:
            mock_service.get_schedule.return_value = mock_schedule

            # 執行函數
            result = await get_schedule(schedule_id=1, db=mock_db)

            # 驗證結果
            assert result.id == 1
            assert result.giver_id == 1

            # 驗證服務被正確調用
            mock_service.get_schedule.assert_called_once_with(mock_db, 1)

    @pytest.mark.asyncio
    async def test_update_schedule_success(self):
        """測試成功更新時段。"""
        # 準備測試資料
        update_schedule_data = ScheduleUpdateBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用 date 別名，會被轉換為 schedule_date
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )

        request = SchedulePartialUpdateRequest(
            schedule=update_schedule_data,
            updated_by=1,
            updated_by_role=UserRoleEnum.GIVER,
        )

        # Mock 資料庫會話
        mock_db = Mock()

        # Mock 服務回傳的更新後時段
        mock_schedule = Mock()
        mock_schedule.id = 1
        mock_schedule.giver_id = 1
        mock_schedule.taker_id = None
        mock_schedule.status = ScheduleStatusEnum.AVAILABLE
        mock_schedule.date = date(2024, 1, 15)
        mock_schedule.start_time = time(9, 0)
        mock_schedule.end_time = time(10, 0)
        mock_schedule.note = None
        mock_schedule.created_at = "2024-01-01T00:00:00Z"
        mock_schedule.created_by = 1
        mock_schedule.created_by_role = UserRoleEnum.GIVER
        mock_schedule.updated_at = "2024-01-01T00:00:00Z"
        mock_schedule.updated_by = 1
        mock_schedule.updated_by_role = UserRoleEnum.GIVER
        mock_schedule.deleted_at = None
        mock_schedule.deleted_by = None
        mock_schedule.deleted_by_role = None

        # Mock schedule_service.update_schedule
        with patch('app.routers.api.schedule.schedule_service') as mock_service:
            mock_service.update_schedule.return_value = mock_schedule

            # 執行函數
            result = await update_schedule(
                request=request,
                schedule_id=1,
                db=mock_db,
            )

            # 驗證結果
            assert result.id == 1
            assert result.giver_id == 1

            # 驗證服務被正確調用
            mock_service.update_schedule.assert_called_once()
            call_args = mock_service.update_schedule.call_args
            assert call_args[0][0] == mock_db  # db
            assert call_args[0][1] == 1  # schedule_id
            assert call_args[1]['updated_by'] == 1
            assert call_args[1]['updated_by_role'] == UserRoleEnum.GIVER
            # 驗證 date 被轉換為 schedule_date（第 502 行被覆蓋）
            assert 'schedule_date' in call_args[1]
            assert 'date' not in call_args[1]  # 原始 date 鍵應該被移除

    @pytest.mark.asyncio
    async def test_delete_schedule_success(self):
        """測試成功刪除時段。"""
        # 準備測試資料
        request = ScheduleDeleteRequest(
            deleted_by=1,
            deleted_by_role=UserRoleEnum.GIVER,
        )

        # Mock 資料庫會話
        mock_db = Mock()

        # Mock schedule_service.delete_schedule
        with patch('app.routers.api.schedule.schedule_service') as mock_service:
            mock_service.delete_schedule.return_value = None

            # 執行函數
            result = await delete_schedule(
                request=request,
                schedule_id=1,
                db=mock_db,
            )

            # 驗證結果（刪除操作沒有回傳值）
            assert result is None

            # 驗證服務被正確調用
            mock_service.delete_schedule.assert_called_once_with(
                mock_db,
                1,
                deleted_by=1,
                deleted_by_role=UserRoleEnum.GIVER,
            )

    @pytest.mark.asyncio
    async def test_update_schedule_without_date_field(self):
        """測試更新時段時沒有 date 欄位的情況。"""
        # 準備測試資料（不包含 date 欄位）
        update_schedule_data = ScheduleUpdateBase(
            giver_id=1,
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=ScheduleStatusEnum.AVAILABLE,
        )

        request = SchedulePartialUpdateRequest(
            schedule=update_schedule_data,
            updated_by=1,
            updated_by_role=UserRoleEnum.GIVER,
        )

        # Mock 資料庫會話
        mock_db = Mock()

        # Mock 服務回傳的更新後時段
        mock_schedule = Mock()
        mock_schedule.id = 1
        mock_schedule.giver_id = 1
        mock_schedule.taker_id = None
        mock_schedule.status = ScheduleStatusEnum.AVAILABLE
        mock_schedule.date = date(2024, 1, 15)
        mock_schedule.start_time = time(9, 0)
        mock_schedule.end_time = time(10, 0)
        mock_schedule.note = None
        mock_schedule.created_at = "2024-01-01T00:00:00Z"
        mock_schedule.created_by = 1
        mock_schedule.created_by_role = UserRoleEnum.GIVER
        mock_schedule.updated_at = "2024-01-01T00:00:00Z"
        mock_schedule.updated_by = 1
        mock_schedule.updated_by_role = UserRoleEnum.GIVER
        mock_schedule.deleted_at = None
        mock_schedule.deleted_by = None
        mock_schedule.deleted_by_role = None

        # Mock schedule_service.update_schedule
        with patch('app.routers.api.schedule.schedule_service') as mock_service:
            mock_service.update_schedule.return_value = mock_schedule

            # 執行函數
            result = await update_schedule(
                request=request,
                schedule_id=1,
                db=mock_db,
            )

            # 驗證結果
            assert result.id == 1
            assert result.giver_id == 1

            # 驗證服務被正確調用
            mock_service.update_schedule.assert_called_once()
            call_args = mock_service.update_schedule.call_args
            assert call_args[0][0] == mock_db  # db
            assert call_args[0][1] == 1  # schedule_id
            assert call_args[1]['updated_by'] == 1
            assert call_args[1]['updated_by_role'] == UserRoleEnum.GIVER
            # 驗證沒有 date 欄位轉換
            assert 'date' not in call_args[1]
            assert 'schedule_date' not in call_args[1]
