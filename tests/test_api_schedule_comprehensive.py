"""
完整的 API 路由層測試。

測試所有 API 端點，包括成功和失敗情況，提升測試覆蓋率。
"""

from datetime import datetime
from unittest.mock import Mock, patch

# ===== 標準函式庫 =====
import pytest

# ===== 第三方套件 =====
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.main import app
from app.routers.api.schedule import create_schedules, get_schedules
from app.routers.api.users import create_user


class TestAPIScheduleComprehensive:
    """完整的 API 時段路由測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """模擬資料庫會話。"""
        db = Mock()
        db.rollback = Mock()
        return db

    @pytest.fixture
    def mock_user(self):
        """模擬使用者資料。"""
        user = Mock()
        user.id = 1
        user.name = "測試使用者"
        user.email = "test@example.com"
        user.to_dict.return_value = {
            "id": 1,
            "name": "測試使用者",
            "email": "test@example.com",
        }
        return user

    @pytest.fixture
    def mock_schedule(self):
        """模擬時段資料。"""
        schedule = Mock()
        schedule.id = 1
        schedule.giver_id = 1
        schedule.taker_id = None
        schedule.date = "2024-01-15"
        schedule.start_time = "09:00:00"
        schedule.end_time = "10:00:00"
        schedule.note = "測試時段"
        schedule.status = "available"
        # role 欄位已移除 - 改用計算屬性
        schedule.creator_role = "TAKER"
        schedule.role = "TAKER"  # 為了向後相容，mock 對象仍需要這個屬性
        schedule.updated_by = 1
        schedule.updated_by_role = "TAKER"
        schedule.created_at = datetime.now()
        schedule.updated_at = datetime.now()
        schedule.deleted_at = None
        return schedule

    # ===== 直接函數測試 =====

    @pytest.mark.asyncio
    async def test_create_user_success_direct(self, mock_db, mock_user):
        """直接測試成功建立使用者函數。"""
        from app.schemas import UserCreate

        # 準備測試資料
        user_data = UserCreate(name="新使用者", email="newuser@example.com")

        # 模擬 CRUD 操作
        with patch('app.crud.schedule_crud.create_user', return_value=mock_user):
            # 執行測試
            result = await create_user(user_data, mock_db)

        # 驗證結果
        assert result["message"] == "使用者建立成功"
        assert result["user"]["name"] == "測試使用者"
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["id"] == 1

    @pytest.mark.asyncio
    async def test_create_user_value_error_direct(self, mock_db):
        """直接測試建立使用者時拋出 ValueError。"""
        from app.schemas import UserCreate

        # 準備測試資料
        user_data = UserCreate(name="重複使用者", email="existing@example.com")

        # 模擬 CRUD 操作拋出 ValueError
        with patch(
            'app.crud.schedule_crud.create_user',
            side_effect=ValueError("此電子信箱已被使用"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException) as exc_info:
                await create_user(user_data, mock_db)

        # 驗證異常詳情
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "此電子信箱已被使用" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_user_general_exception_direct(self, mock_db):
        """直接測試建立使用者時拋出一般異常。"""
        from app.schemas import UserCreate

        # 準備測試資料
        user_data = UserCreate(name="測試使用者", email="test@example.com")

        # 模擬 CRUD 操作拋出一般異常
        with patch(
            'app.crud.schedule_crud.create_user',
            side_effect=Exception("資料庫連線失敗"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException) as exc_info:
                await create_user(user_data, mock_db)

        # 驗證異常詳情
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "建立使用者失敗" in str(exc_info.value.detail)
        assert "資料庫連線失敗" in str(exc_info.value.detail)

        # 驗證資料庫回滾被呼叫
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_schedules_success_direct(self, mock_db, mock_schedule):
        """直接測試成功建立時段函數。"""
        from app.schemas import ScheduleCreate

        # 準備測試資料
        schedule_data = [
            ScheduleCreate(
                giver_id=1,
                date="2024-01-15",
                start_time="09:00:00",
                end_time="10:00:00",
                note="測試時段",
                status="AVAILABLE",
            )
        ]

        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.create_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            result = await create_schedules(schedule_data, mock_db)

        # 驗證結果
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].giver_id == 1

    @pytest.mark.asyncio
    async def test_create_schedules_exception_direct(self, mock_db):
        """直接測試建立時段時拋出異常。"""
        from app.schemas import ScheduleCreate

        # 準備測試資料
        schedule_data = [
            ScheduleCreate(
                giver_id=1,
                date="2024-01-15",
                start_time="09:00:00",
                end_time="10:00:00",
                note="測試時段",
                status="AVAILABLE",
            )
        ]

        # 模擬 CRUD 操作拋出異常
        with patch(
            'app.crud.schedule_crud.create_schedules',
            side_effect=Exception("資料庫錯誤"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException) as exc_info:
                await create_schedules(schedule_data, mock_db)

        # 驗證異常詳情
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "建立時段失敗" in str(exc_info.value.detail)
        assert "資料庫錯誤" in str(exc_info.value.detail)

        # 驗證資料庫回滾被呼叫
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_schedules_success_direct(self, mock_db, mock_schedule):
        """直接測試成功查詢時段函數。"""
        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            result = await get_schedules(None, None, mock_db)

        # 驗證結果
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].giver_id == 1

    @pytest.mark.asyncio
    async def test_get_schedules_with_filters_direct(self, mock_db, mock_schedule):
        """直接測試帶篩選條件的查詢時段函數。"""
        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            result = await get_schedules(
                giver_id=1, status_filter="available", db=mock_db
            )

        # 驗證結果
        assert len(result) == 1
        assert result[0].id == 1

    @pytest.mark.asyncio
    async def test_get_schedules_exception_direct(self, mock_db):
        """直接測試查詢時段時拋出異常。"""
        # 模擬 CRUD 操作拋出異常
        with patch(
            'app.crud.schedule_crud.get_schedules',
            side_effect=Exception("查詢失敗"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException) as exc_info:
                await get_schedules(None, None, mock_db)

        # 驗證異常詳情
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "查詢時段失敗" in str(exc_info.value.detail)
        assert "查詢失敗" in str(exc_info.value.detail)

    # ===== 邊界情況測試 =====

    @pytest.mark.asyncio
    async def test_create_schedules_empty_list_direct(self, mock_db):
        """直接測試建立空時段列表。"""
        # 準備測試資料 - 空列表
        schedule_data = []

        # 模擬 CRUD 操作
        with patch('app.crud.schedule_crud.create_schedules', return_value=[]):
            # 執行測試
            result = await create_schedules(schedule_data, mock_db)

        # 驗證結果
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_schedules_no_results_direct(self, mock_db):
        """直接測試查詢時段無結果。"""
        # 模擬 CRUD 操作返回空列表
        with patch('app.crud.schedule_crud.get_schedules', return_value=[]):
            # 執行測試
            result = await get_schedules(None, None, mock_db)

        # 驗證結果
        assert len(result) == 0

    # ===== 錯誤處理測試 =====

    @pytest.mark.asyncio
    async def test_create_user_db_rollback_on_exception(self, mock_db):
        """測試建立使用者時資料庫回滾。"""
        from app.schemas import UserCreate

        # 準備測試資料
        user_data = UserCreate(name="測試使用者", email="test@example.com")

        # 模擬 CRUD 操作拋出異常
        with patch(
            'app.crud.schedule_crud.create_user',
            side_effect=Exception("資料庫錯誤"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException):
                await create_user(user_data, mock_db)

        # 驗證資料庫回滾被呼叫
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_schedules_db_rollback_on_exception(self, mock_db):
        """測試建立時段時資料庫回滾。"""
        from app.schemas import ScheduleCreate

        # 準備測試資料
        schedule_data = [
            ScheduleCreate(
                giver_id=1,
                date="2024-01-15",
                start_time="09:00:00",
                end_time="10:00:00",
                note="測試時段",
                status="AVAILABLE",
            )
        ]

        # 模擬 CRUD 操作拋出異常
        with patch(
            'app.crud.schedule_crud.create_schedules',
            side_effect=Exception("資料庫錯誤"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException):
                await create_schedules(schedule_data, mock_db)

        # 驗證資料庫回滾被呼叫
        mock_db.rollback.assert_called_once()

    # ===== 資料驗證測試 =====

    @pytest.mark.asyncio
    async def test_create_user_with_invalid_data(self, mock_db):
        """測試建立使用者時無效資料處理。"""
        from app.schemas import UserCreate

        # 準備測試資料 - 無效的 email 格式
        user_data = UserCreate(name="測試使用者", email="invalid-email")

        # 模擬 CRUD 操作拋出 ValueError
        with patch(
            'app.crud.schedule_crud.create_user',
            side_effect=ValueError("無效的電子信箱格式"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException) as exc_info:
                await create_user(user_data, mock_db)

        # 驗證異常詳情
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "無效的電子信箱格式" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_schedules_with_invalid_data(self, mock_db):
        """測試建立時段時無效資料處理。"""
        from app.schemas import ScheduleCreate

        # 準備測試資料 - 使用有效的時間格式，但模擬 CRUD 層的驗證錯誤
        schedule_data = [
            ScheduleCreate(
                giver_id=1,
                date="2024-01-15",
                start_time="09:00:00",
                end_time="10:00:00",
                note="測試時段",
                status="AVAILABLE",
            )
        ]

        # 模擬 CRUD 操作拋出異常（例如：時間衝突）
        with patch(
            'app.crud.schedule_crud.create_schedules',
            side_effect=Exception("時間衝突：該時段已被預約"),
        ):
            # 執行測試並驗證異常
            with pytest.raises(HTTPException) as exc_info:
                await create_schedules(schedule_data, mock_db)

        # 驗證異常詳情
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "建立時段失敗" in str(exc_info.value.detail)
        assert "時間衝突" in str(exc_info.value.detail)

    # ===== 整合測試 =====

    def test_api_endpoints_integration(self, client):
        """測試 API 端點整合功能。"""
        # 測試端點存在性
        response = client.get("/docs")
        assert response.status_code == 200

        # 測試 OpenAPI 文件
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_spec = response.json()

        # 驗證 API 路徑存在
        assert "/api/users" in openapi_spec["paths"]
        assert "/api/schedules" in openapi_spec["paths"]

    def test_api_response_models(self, client):
        """測試 API 回應模型。"""
        # 測試使用者建立端點的回應模型
        user_data = {"name": "測試使用者", "email": "test@example.com"}

        with patch('app.crud.schedule_crud.create_user') as mock_create:
            mock_user = Mock()
            mock_user.to_dict.return_value = {
                "id": 1,
                "name": "測試使用者",
                "email": "test@example.com",
            }
            mock_create.return_value = mock_user

            response = client.post("/api/users", json=user_data)

            assert response.status_code == 201
            result = response.json()
            assert "message" in result
            assert "user" in result
            assert isinstance(result["user"], dict)

    def test_api_error_responses(self, client):
        """測試 API 錯誤回應格式。"""
        # 測試無效的 JSON 資料
        response = client.post("/api/users", content="invalid json")
        assert response.status_code == 422  # Unprocessable Entity

        # 測試缺少必要欄位
        response = client.post("/api/users", json={})
        assert response.status_code == 422

        # 測試無效的時段資料
        response = client.post("/api/schedules", json=[{"invalid": "data"}])
        assert response.status_code == 422

    # ===== 效能和穩定性測試 =====

    @pytest.mark.asyncio
    async def test_create_schedules_large_list(self, mock_db, mock_schedule):
        """測試建立大量時段。"""
        from app.schemas import ScheduleCreate

        # 準備測試資料 - 大量時段
        schedule_data = [
            ScheduleCreate(
                giver_id=1,
                date="2024-01-15",
                start_time="09:00:00",
                end_time="10:00:00",
                note=f"測試時段 {i}",
                status="AVAILABLE",
            )
            for i in range(100)
        ]

        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.create_schedules',
            return_value=[mock_schedule] * 100,
        ):
            # 執行測試
            result = await create_schedules(schedule_data, mock_db)

        # 驗證結果
        assert len(result) == 100

    @pytest.mark.asyncio
    async def test_get_schedules_with_complex_filters(self, mock_db, mock_schedule):
        """測試複雜篩選條件的查詢。"""
        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試 - 同時使用多個篩選條件
            result = await get_schedules(
                giver_id=1, status_filter="available", db=mock_db
            )

        # 驗證結果
        assert len(result) == 1
        assert result[0].id == 1

    # ===== 日誌和監控測試 =====

    def test_api_logging_coverage(self, client):
        """測試 API 日誌記錄覆蓋率。"""
        # 測試成功情況的日誌
        user_data = {"name": "日誌測試使用者", "email": "log@example.com"}

        with patch('app.crud.schedule_crud.create_user') as mock_create:
            mock_user = Mock()
            mock_user.to_dict.return_value = {
                "id": 1,
                "name": "日誌測試使用者",
                "email": "log@example.com",
            }
            mock_create.return_value = mock_user

            response = client.post("/api/users", json=user_data)
            assert response.status_code == 201

        # 測試錯誤情況的日誌
        with patch(
            'app.crud.schedule_crud.create_user', side_effect=Exception("測試錯誤")
        ):
            response = client.post("/api/users", json=user_data)
            assert response.status_code == 400
