"""
簡化的 API 路由層測試。

使用模擬（mock）來測試 API 端點，避免資料庫執行緒問題。
"""

from unittest.mock import Mock, patch

# ===== 標準函式庫 =====
import pytest

# ===== 第三方套件 =====
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.main import app


class TestAPIScheduleSimple:
    """簡化的 API 時段路由測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """模擬資料庫會話。"""
        return Mock()

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
        from datetime import datetime

        schedule = Mock()
        schedule.id = 1
        schedule.giver_id = 1
        schedule.taker_id = None
        schedule.date = "2024-01-15"
        schedule.start_time = "09:00:00"
        schedule.end_time = "10:00:00"
        schedule.note = "測試時段"
        schedule.status = "AVAILABLE"
        schedule.updated_by_role = "TAKER"
        schedule.updated_by = 1
        schedule.created_at = datetime.now()
        schedule.updated_at = datetime.now()
        schedule.deleted_at = None
        schedule.creator_role = "TAKER"  # 添加 creator_role 屬性
        schedule.to_dict.return_value = {
            "id": 1,
            "creator_role": "TAKER",
            "giver_id": 1,
            "taker_id": None,
            "date": "2024-01-15",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "note": "測試時段",
            "status": "AVAILABLE",
            "created_at": schedule.created_at.isoformat(),
            "updated_at": schedule.updated_at.isoformat(),
            "updated_by": 1,
            "updated_by_role": "TAKER",
            "updated_by_user": None,
            "deleted_at": None,
        }
        return schedule

    def test_create_user_success(self, client, mock_db, mock_user):
        """測試成功建立使用者。"""
        # 準備測試資料
        user_data = {"name": "新使用者", "email": "newuser@example.com"}

        # 模擬 CRUD 操作
        with patch('app.crud.user_crud.create_user', return_value=mock_user):
            # 執行測試
            response = client.post("/api/users", json=user_data)

        # 驗證結果
        assert response.status_code == 201
        result = response.json()
        assert result["message"] == "使用者建立成功"
        assert result["user"]["name"] == "測試使用者"
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["id"] == 1

    def test_create_user_duplicate_email(self, client, mock_db):
        """測試建立重複 email 的使用者。"""
        # 準備測試資料
        user_data = {"name": "重複使用者", "email": "existing@example.com"}

        # 模擬 CRUD 操作拋出 ValueError
        with patch(
            'app.crud.user_crud.create_user',
            side_effect=ValueError("此電子信箱已被使用"),
        ):
            # 執行測試
            response = client.post("/api/users", json=user_data)

        # 驗證結果
        assert response.status_code == 400
        result = response.json()
        assert "此電子信箱已被使用" in result["detail"]

    def test_create_user_invalid_data(self, client):
        """測試建立使用者時提供無效資料。"""
        # 準備無效的測試資料
        invalid_user_data = {
            "name": "",  # 空名稱
            "email": "invalid-email",  # 無效的 email 格式
        }

        # 執行測試
        response = client.post("/api/users", json=invalid_user_data)

        # 驗證結果
        assert response.status_code == 400  # 實際返回 400 錯誤

    def test_create_schedules_success(self, client, mock_db, mock_schedule):
        """測試成功建立多個時段。"""
        # 準備測試資料（新格式：包含操作者資訊）
        request_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-01-20",
                    "start_time": "14:00:00",
                    "end_time": "15:00:00",
                    "note": "測試時段1",
                    "status": "AVAILABLE",
                },
                {
                    "giver_id": 1,
                    "date": "2024-01-21",
                    "start_time": "16:00:00",
                    "end_time": "17:00:00",
                    "note": "測試時段2",
                    "status": "AVAILABLE",
                },
            ],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.create_schedules',
            return_value=[mock_schedule, mock_schedule],
        ):
            # 執行測試
            response = client.post("/api/schedules", json=request_data)

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
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 執行測試
        response = client.post("/api/schedules", json=invalid_request_data)

        # 驗證結果
        assert response.status_code == 422  # Validation Error

    def test_get_schedules_success(self, client, mock_db, mock_schedule):
        """測試成功取得時段列表。"""
        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            response = client.get("/api/schedules")

        # 驗證結果
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1

    def test_get_schedules_filter_by_giver_id(self, client, mock_db, mock_schedule):
        """測試根據 giver_id 篩選時段。"""
        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            response = client.get("/api/schedules?giver_id=1")

        # 驗證結果
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1

    def test_get_schedules_filter_by_status(self, client, mock_db, mock_schedule):
        """測試根據狀態篩選時段。"""
        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.get_schedules', return_value=[mock_schedule]
        ):
            # 執行測試
            response = client.get("/api/schedules?status_filter=AVAILABLE")

        # 驗證結果
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1

    def test_get_schedules_no_results(self, client, mock_db):
        """測試篩選條件沒有結果的情況。"""
        # 模擬 CRUD 操作返回空列表
        with patch('app.crud.schedule_crud.get_schedules', return_value=[]):
            # 執行測試
            response = client.get("/api/schedules?giver_id=999")

        # 驗證結果
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

    def test_get_schedules_invalid_filter(self, client):
        """測試無效的篩選參數。"""
        # 執行測試 - 使用無效的 giver_id 格式
        response = client.get("/api/schedules?giver_id=invalid")

        # 驗證結果
        assert response.status_code == 422  # Validation Error

    def test_api_endpoints_exist(self, client):
        """測試 API 端點是否存在。"""
        # 測試使用者建立端點
        response = client.get("/api/users")
        assert response.status_code in [404, 405]  # 端點存在但不支援 GET

        # 測試時段端點
        response = client.get("/api/schedules")
        assert response.status_code == 200  # 端點存在且支援 GET

    def test_api_response_format(self, client, mock_schedule):
        """測試 API 回應格式。"""
        # 模擬 CRUD 操作
        with patch(
            'app.crud.schedule_crud.get_schedules', return_value=[mock_schedule]
        ):
            # 測試時段列表回應格式
            response = client.get("/api/schedules")
            assert response.status_code == 200

            # 驗證回應標頭
            assert "application/json" in response.headers["content-type"]

            # 驗證回應內容是有效的 JSON
            result = response.json()
            assert isinstance(result, list)

    def test_api_error_handling(self, client):
        """測試 API 錯誤處理。"""
        # 測試不存在的端點
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

        # 測試不支援的 HTTP 方法
        response = client.delete("/api/users")
        assert response.status_code in [404, 405]

    def test_create_schedules_empty_list(self, client, mock_db):
        """測試建立空時段列表。"""
        # 準備空時段列表的請求資料（新格式：包含操作者資訊）
        empty_request_data = {
            "schedules": [],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 模擬 CRUD 操作
        with patch('app.crud.schedule_crud.create_schedules', return_value=[]):
            # 執行測試
            response = client.post("/api/schedules", json=empty_request_data)

        # 驗證結果
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 0

    def test_create_schedules_missing_required_fields(self, client):
        """測試建立時段時缺少必要欄位。"""
        # 準備缺少必要欄位的測試資料（新格式：包含操作者資訊）
        incomplete_request_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    # 缺少 date, start_time, end_time 等必要欄位
                    "note": "不完整的時段",
                }
            ],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 執行測試
        response = client.post("/api/schedules", json=incomplete_request_data)

        # 驗證結果
        assert response.status_code == 422  # Validation Error

    def test_api_documentation_endpoints(self, client):
        """測試 API 文件端點。"""
        # 測試 OpenAPI 文件
        response = client.get("/docs")
        assert response.status_code == 200

        # 測試 OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_api_health_endpoints(self, client):
        """測試健康檢查端點。"""
        # 測試健康檢查
        response = client.get("/healthz")
        assert response.status_code == 200

        # 測試準備就緒檢查
        response = client.get("/readyz")
        assert response.status_code == 200

    def test_create_schedules_with_overlap(self, client, mock_db, mock_schedule):
        """測試建立重疊時段時的回應。"""
        # 準備測試資料 - 先建立一個時段，然後嘗試建立重疊的時段（新格式：包含操作者資訊）
        overlapping_request_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-01-20",
                    "start_time": "14:00:00",
                    "end_time": "15:00:00",
                    "note": "現有時段",
                    "status": "AVAILABLE",
                },
                {
                    "giver_id": 1,
                    "date": "2024-01-20",
                    "start_time": "14:30:00",
                    "end_time": "15:30:00",
                    "note": "重疊時段",
                    "status": "AVAILABLE",
                },
            ],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 模擬 CRUD 操作拋出重疊錯誤
        with patch(
            'app.crud.schedule_crud.create_schedules',
            side_effect=ValueError(
                "您正輸入的時段，和您之前曾輸入的「2024/01/20（週六）14:00~15:00」時段重複或重疊，請重新輸入"
            ),
        ):
            # 執行測試
            response = client.post("/api/schedules", json=overlapping_request_data)

        # 驗證結果
        assert response.status_code == 400
        result = response.json()
        assert "時段重複或重疊" in result["detail"]
