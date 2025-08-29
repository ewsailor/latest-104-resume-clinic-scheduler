"""完整的 API 時段路由整合測試模組。

測試時段管理 API 的各種功能，包括建立、查詢、更新和刪除時段。
"""

# ===== 標準函式庫 =====
from datetime import datetime
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.enums.models import UserRoleEnum
from app.main import app
from app.routers.api.schedule import create_schedules, get_schedules
from app.schemas import ScheduleCreateRequest, ScheduleData


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
    def mock_schedule(self):
        """模擬時段資料。"""
        schedule = Mock()
        schedule.id = 1
        schedule.giver_id = 1
        schedule.taker_id = None
        schedule.date = "2025-09-15"
        schedule.start_time = "09:00:00"
        schedule.end_time = "10:00:00"
        schedule.note = "測試時段"
        schedule.status = "AVAILABLE"
        schedule.created_by = 1
        schedule.created_by_role = "TAKER"
        schedule.updated_by = 1
        schedule.updated_by_role = "TAKER"
        schedule.deleted_by = None
        schedule.deleted_by_role = None
        schedule.created_at = datetime.now()
        schedule.updated_at = datetime.now()
        schedule.deleted_at = None
        schedule.to_dict.return_value = {
            "id": 1,
            "giver_id": 1,
            "taker_id": None,
            "date": "2025-09-15",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "note": "測試時段",
            "status": "AVAILABLE",
            "created_at": schedule.created_at.isoformat(),
            "created_by": 1,
            "created_by_role": "TAKER",
            "updated_at": schedule.updated_at.isoformat(),
            "created_by": 1,
            "created_by_role": "TAKER",
            "deleted_at": None,
            "deleted_by": None,
            "deleted_by_role": None,
        }
        return schedule

    # ===== 直接函數測試 =====

    @pytest.mark.asyncio
    async def test_create_schedules_success_direct(self, mock_db, mock_schedule):
        """直接測試成功建立時段函數。"""
        # 準備測試資料
        schedule_data = ScheduleData(
            giver_id=1,
            taker_id=None,
            date="2025-09-15",
            start_time="09:00:00",
            end_time="10:00:00",
            note="測試時段",
        )
        request = ScheduleCreateRequest(
            schedules=[schedule_data],
            created_by=1,
            created_by_role=UserRoleEnum.TAKER,
        )

        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.create_schedules',
            return_value=[mock_schedule],
        ):
            # 執行測試
            result = await create_schedules(request, mock_db)

        # 驗證結果
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["giver_id"] == 1
        assert result[0]["status"] == "AVAILABLE"

    @pytest.mark.asyncio
    async def test_get_schedules_success_direct(self, mock_db, mock_schedule):
        """直接測試成功查詢時段函數。"""
        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            result = await get_schedules(db=mock_db)

        # 驗證結果
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["giver_id"] == 1

    # ===== HTTP 端點測試 =====

    @pytest.mark.asyncio
    async def test_create_schedules_endpoint_success(self, client, mock_schedule):
        """測試成功建立時段的 HTTP 端點。"""
        # 準備測試資料
        request_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "taker_id": None,
                    "date": "2025-09-15",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "TAKER",
        }

        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.create_schedules',
            return_value=[mock_schedule],
        ):
            # 執行測試
            response = client.post("/api/v1/schedules", json=request_data)

        # 驗證結果
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["giver_id"] == 1

    @pytest.mark.asyncio
    async def test_get_schedules_endpoint_success(self, client, mock_schedule):
        """測試成功查詢時段的 HTTP 端點。"""
        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            response = client.get("/api/v1/schedules")

        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["giver_id"] == 1

    @pytest.mark.asyncio
    async def test_get_schedules_with_filters(self, client, mock_schedule):
        """測試帶篩選條件的時段查詢。"""
        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            response = client.get(
                "/api/v1/schedules?giver_id=1&status_filter=AVAILABLE"
            )

        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["giver_id"] == 1

    @pytest.mark.asyncio
    async def test_get_schedule_by_id_success(self, client, mock_schedule):
        """測試根據 ID 查詢單一時段。"""
        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.get_schedule_by_id',
            return_value=mock_schedule,
        ):
            # 執行測試
            response = client.get("/api/v1/schedules/1")

        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["giver_id"] == 1

    @pytest.mark.asyncio
    async def test_update_schedule_success(self, client, mock_schedule):
        """測試成功更新時段。"""
        # 準備測試資料
        update_data = {
            "schedule": {
                "status": "PENDING",
                "note": "更新後的備註",
            },
            "updated_by": 1,
            "updated_by_role": "TAKER",
        }

        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.update_schedule', return_value=mock_schedule
        ):
            # 執行測試
            response = client.patch("/api/v1/schedules/1", json=update_data)

        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    @pytest.mark.asyncio
    async def test_delete_schedule_success(self, client):
        """測試成功刪除時段。"""
        # 準備測試資料
        delete_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        # 模擬服務層操作
        with patch('app.services.schedule_service.delete_schedule', return_value=True):
            # 執行測試
            response = client.delete("/api/v1/schedules/1", json=delete_data)

        # 驗證結果
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_schedule_not_found(self, client):
        """測試刪除不存在的時段。"""
        # 準備測試資料
        delete_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        # 模擬服務層操作
        with patch('app.services.schedule_service.delete_schedule', return_value=False):
            # 執行測試
            response = client.delete("/api/v1/schedules/999", json=delete_data)

        # 驗證結果
        assert response.status_code == 404
        data = response.json()
        assert "時段不存在或無法刪除" in data["detail"]
