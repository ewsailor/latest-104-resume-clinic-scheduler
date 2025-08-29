"""簡單的 API 時段路由整合測試模組。

測試時段管理 API 的基本功能。
"""

# ===== 標準函式庫 =====
from datetime import datetime
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.main import app


class TestAPIScheduleSimple:
    """簡單的 API 時段路由測試類別。"""

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
        schedule.created_by_role = "GIVER"
        schedule.updated_by = 1
        schedule.updated_by_role = "GIVER"
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
            "created_by_role": "GIVER",
            "updated_at": schedule.updated_at.isoformat(),
            "updated_by": 1,
            "updated_by_role": "GIVER",
            "deleted_at": None,
            "deleted_by": None,
            "deleted_by_role": None,
        }
        return schedule

    def test_create_schedules_success(self, client, mock_db, mock_schedule):
        """測試成功建立多個時段。"""
        # 準備測試資料（新格式：包含操作者資訊）
        request_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2025-09-20",
                    "start_time": "14:00:00",
                    "end_time": "15:00:00",
                    "note": "測試時段1",
                    "status": "AVAILABLE",
                },
                {
                    "giver_id": 1,
                    "date": "2025-09-21",
                    "start_time": "16:00:00",
                    "end_time": "17:00:00",
                    "note": "測試時段2",
                    "status": "AVAILABLE",
                },
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.create_schedules',
            return_value=[mock_schedule, mock_schedule],
        ):
            # 執行測試
            response = client.post("/api/v1/schedules", json=request_data)

        # 驗證結果
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 2

    def test_create_schedules_invalid_data(self, client):
        """測試建立時段時提供無效資料。"""
        # 準備無效的測試資料（新格式：包含操作者資訊）
        invalid_request_data = {
            "schedules": [
                {
                    "giver_id": 999,  # 不存在的使用者 ID
                    "date": "invalid-date",
                    "start_time": "invalid-time",
                    "end_time": "invalid-time",
                    "note": "無效時段",
                    "status": "invalid-status",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # 執行測試
        response = client.post("/api/v1/schedules", json=invalid_request_data)

        # 驗證結果 - FastAPI 的驗證錯誤返回 422
        assert response.status_code == 422  # Validation Error

    def test_get_schedules_success(self, client, mock_schedule):
        """測試成功查詢時段列表。"""
        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.get_schedules',
            return_value=[mock_schedule],
        ):
            # 執行測試
            response = client.get("/api/v1/schedules")

        # 驗證結果
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["giver_id"] == 1

    def test_get_schedules_with_filters(self, client, mock_schedule):
        """測試帶篩選條件的時段查詢。"""
        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.get_schedules',
            return_value=[mock_schedule],
        ):
            # 執行測試
            response = client.get(
                "/api/v1/schedules?giver_id=1&status_filter=AVAILABLE"
            )

        # 驗證結果
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["giver_id"] == 1

    def test_get_schedule_by_id_success(self, client, mock_schedule):
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
        result = response.json()
        assert result["id"] == 1
        assert result["giver_id"] == 1

    def test_get_schedule_by_id_not_found(self, client):
        """測試查詢不存在的時段。"""
        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.get_schedule_by_id',
            return_value=None,
        ):
            # 執行測試
            response = client.get("/api/v1/schedules/999")

        # 驗證結果
        assert response.status_code == 404

    def test_update_schedule_success(self, client, mock_schedule):
        """測試成功更新時段。"""
        # 準備測試資料
        update_data = {
            "schedule": {
                "status": "PENDING",
                "note": "更新後的備註",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.update_schedule',
            return_value=mock_schedule,
        ):
            # 執行測試
            response = client.patch("/api/v1/schedules/1", json=update_data)

        # 驗證結果
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == 1

    def test_delete_schedule_success(self, client):
        """測試成功刪除時段。"""
        # 準備測試資料
        delete_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.delete_schedule',
            return_value=True,
        ):
            # 執行測試
            response = client.delete("/api/v1/schedules/1", json=delete_data)

        # 驗證結果
        assert response.status_code == 204

    def test_delete_schedule_not_found(self, client):
        """測試刪除不存在的時段。"""
        # 準備測試資料
        delete_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        # 模擬服務層操作
        with patch(
            'app.services.schedule_service.delete_schedule',
            return_value=False,
        ):
            # 執行測試
            response = client.delete("/api/v1/schedules/999", json=delete_data)

        # 驗證結果
        assert response.status_code == 404
        result = response.json()
        assert "時段不存在或無法刪除" in result["detail"]

    def test_api_documentation_accessible(self, client):
        """測試 API 文檔是否可以訪問。"""
        # 測試 Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200

        # 測試 OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_health_check_endpoints(self, client):
        """測試健康檢查端點。"""
        # 測試基本健康檢查
        response = client.get("/healthz")
        assert response.status_code == 200

        # 測試就緒檢查
        response = client.get("/readyz")
        assert response.status_code == 200
