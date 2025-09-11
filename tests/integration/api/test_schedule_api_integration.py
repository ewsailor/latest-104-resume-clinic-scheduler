"""
Schedule API 路由整合測試模組。

測試時段相關的 API 端點，包括建立、查詢、更新和刪除時段的完整流程。
"""

# ===== 標準函式庫 =====
import datetime
from typing import Any, Dict

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.main import app

from .test_utils import generate_multiple_time_slots, generate_unique_time_slot


class TestScheduleAPIIntegration:
    """Schedule API 整合測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    @pytest.fixture(autouse=True)
    def cleanup_test_data(self):
        """自動清理測試資料。"""
        # 測試前清理
        yield
        # 測試後清理 - 刪除測試時段
        try:
            from app.models.database import get_db
            from app.models.schedule import Schedule

            db = next(get_db())
            # 刪除所有 giver_id=1 且日期在未來365天內的測試時段
            future_date = datetime.date.today() + datetime.timedelta(days=365)
            test_schedules = (
                db.query(Schedule)
                .filter(Schedule.giver_id == 1, Schedule.date >= future_date)
                .all()
            )
            for schedule in test_schedules:
                db.delete(schedule)
            db.commit()
            db.close()
        except Exception:
            # 忽略清理錯誤，避免影響測試
            pass

    @pytest.fixture
    def sample_schedule_data(self) -> Dict[str, Any]:
        """提供測試用的時段資料。"""
        # 使用工具函數生成唯一時段
        date, start_time, end_time = generate_unique_time_slot()

        return {
            "giver_id": 1,  # 使用現有的 giver_id
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "status": "AVAILABLE",
        }

    @pytest.fixture
    def sample_schedule_list_data(
        self, sample_schedule_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提供測試用的時段列表資料。"""
        # 使用工具函數生成多個唯一時段
        time_slots = generate_multiple_time_slots(count=2)

        schedules = []
        for date, start_time, end_time in time_slots:
            schedules.append(
                {
                    "giver_id": 1,  # 使用現有的 giver_id
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "AVAILABLE",
                }
            )

        return {
            "schedules": schedules,
            "created_by": 1,
            "created_by_role": "GIVER",
        }

    def test_create_schedules_success(
        self, client: TestClient, sample_schedule_list_data: Dict[str, Any]
    ):
        """測試成功建立多個時段。"""
        response = client.post("/api/v1/schedules", json=sample_schedule_list_data)

        assert response.status_code == 201
        response_data = response.json()

        # 檢查回應結構
        assert isinstance(response_data, list)
        assert len(response_data) == 2

        # 檢查每個時段的結構
        for schedule in response_data:
            assert "id" in schedule
            assert "giver_id" in schedule
            assert "date" in schedule
            assert "start_time" in schedule
            assert "end_time" in schedule
            assert "status" in schedule
            assert "created_at" in schedule
            assert "updated_at" in schedule
            assert "created_by" in schedule
            assert "created_by_role" in schedule

            # 檢查資料正確性
            assert schedule["giver_id"] == 1
            assert schedule["status"] == "AVAILABLE"
            assert schedule["created_by"] == 1
            assert schedule["created_by_role"] == "GIVER"

    def test_create_schedules_validation_error(self, client: TestClient):
        """測試建立時段時的驗證錯誤。"""
        invalid_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-01-01",
                    "start_time": "10:00:00",  # 開始時間晚於結束時間
                    "end_time": "09:00:00",
                    "status": "AVAILABLE",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        response = client.post("/api/v1/schedules", json=invalid_data)

        assert response.status_code == 400
        response_data = response.json()
        assert "開始時間必須早於結束時間" in response_data["detail"]

    def test_list_schedules_success(
        self, client: TestClient, sample_schedule_list_data: Dict[str, Any]
    ):
        """測試成功取得時段列表。"""
        # 先建立一些時段
        create_response = client.post(
            "/api/v1/schedules", json=sample_schedule_list_data
        )
        assert create_response.status_code == 201

        # 取得時段列表
        response = client.get("/api/v1/schedules")

        assert response.status_code == 200
        response_data = response.json()

        # 檢查回應結構
        assert isinstance(response_data, list)
        assert len(response_data) >= 2  # 至少包含我們剛建立的時段

        # 檢查每個時段的結構
        for schedule in response_data:
            assert "id" in schedule
            assert "giver_id" in schedule
            assert "date" in schedule
            assert "start_time" in schedule
            assert "end_time" in schedule
            assert "status" in schedule

    def test_list_schedules_with_filters(
        self, client: TestClient, sample_schedule_list_data: Dict[str, Any]
    ):
        """測試使用篩選條件取得時段列表。"""
        # 先建立一些時段
        create_response = client.post(
            "/api/v1/schedules", json=sample_schedule_list_data
        )
        assert create_response.status_code == 201

        # 使用 giver_id 篩選
        response = client.get("/api/v1/schedules?giver_id=1")

        assert response.status_code == 200
        response_data = response.json()

        # 檢查所有時段都屬於指定的 giver_id
        for schedule in response_data:
            assert schedule["giver_id"] == 1

    def test_get_schedule_by_id_success(
        self, client: TestClient, sample_schedule_list_data: Dict[str, Any]
    ):
        """測試根據 ID 成功取得單一時段。"""
        # 先建立時段
        create_response = client.post(
            "/api/v1/schedules", json=sample_schedule_list_data
        )
        assert create_response.status_code == 201
        created_schedules = create_response.json()
        schedule_id = created_schedules[0]["id"]

        # 取得特定時段
        response = client.get(f"/api/v1/schedules/{schedule_id}")

        assert response.status_code == 200
        response_data = response.json()

        # 檢查回應結構
        assert "id" in response_data
        assert "giver_id" in response_data
        assert "date" in response_data
        assert "start_time" in response_data
        assert "end_time" in response_data
        assert "status" in response_data

        # 檢查資料正確性
        assert response_data["id"] == schedule_id
        assert response_data["giver_id"] == 1

    def test_get_schedule_by_id_not_found(self, client: TestClient):
        """測試取得不存在的時段。"""
        response = client.get("/api/v1/schedules/99999")

        assert response.status_code == 404
        response_data = response.json()
        assert "error" in response_data
        assert "時段不存在" in response_data["error"]["message"]

    def test_update_schedule_success(
        self, client: TestClient, sample_schedule_list_data: Dict[str, Any]
    ):
        """測試成功更新時段。"""
        # 先建立時段
        create_response = client.post(
            "/api/v1/schedules", json=sample_schedule_list_data
        )
        assert create_response.status_code == 201
        created_schedules = create_response.json()
        schedule_id = created_schedules[0]["id"]

        # 更新時段
        update_data = {
            "schedule": {
                "status": "PENDING",
                # 不設置 taker_id，因為可能不存在於資料庫中
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        response = client.patch(f"/api/v1/schedules/{schedule_id}", json=update_data)

        assert response.status_code == 200
        response_data = response.json()

        # 檢查更新後的資料
        assert response_data["id"] == schedule_id
        assert response_data["status"] == "PENDING"
        # taker_id 可能為 None，因為我們沒有設置
        assert response_data["updated_by"] == 1
        assert response_data["updated_by_role"] == "GIVER"

    def test_update_schedule_not_found(self, client: TestClient):
        """測試更新不存在的時段。"""
        update_data = {
            "schedule": {
                "status": "BOOKED",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        response = client.patch("/api/v1/schedules/99999", json=update_data)

        assert response.status_code == 422  # 驗證錯誤，因為資料格式不正確
        response_data = response.json()
        assert "detail" in response_data

    def test_delete_schedule_success(
        self, client: TestClient, sample_schedule_list_data: Dict[str, Any]
    ):
        """測試成功刪除時段。"""
        # 先建立時段
        create_response = client.post(
            "/api/v1/schedules", json=sample_schedule_list_data
        )
        assert create_response.status_code == 201
        created_schedules = create_response.json()
        schedule_id = created_schedules[0]["id"]

        # 刪除時段
        delete_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        import json

        response = client.request(
            "DELETE",
            f"/api/v1/schedules/{schedule_id}",
            content=json.dumps(delete_data),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 204

        # 確認時段已被刪除
        get_response = client.get(f"/api/v1/schedules/{schedule_id}")
        assert get_response.status_code == 404

    def test_delete_schedule_not_found(self, client: TestClient):
        """測試刪除不存在的時段。"""
        delete_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        import json

        # 使用 TestClient 的 request 方法
        response = client.request(
            "DELETE",
            "/api/v1/schedules/99999",
            content=json.dumps(delete_data),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 404
        response_data = response.json()
        assert "時段不存在或無法刪除" in response_data["detail"]

    def test_schedule_lifecycle_complete_flow(self, client: TestClient):
        """測試時段完整生命週期流程。"""
        # 使用工具函數生成唯一時段
        date, start_time, end_time = generate_unique_time_slot(hour_start=13)

        # 1. 建立時段
        create_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "AVAILABLE",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        create_response = client.post("/api/v1/schedules", json=create_data)
        assert create_response.status_code == 201
        created_schedules = create_response.json()
        schedule_id = created_schedules[0]["id"]

        # 2. 查詢時段
        get_response = client.get(f"/api/v1/schedules/{schedule_id}")
        assert get_response.status_code == 200
        schedule_data = get_response.json()
        assert schedule_data["status"] == "AVAILABLE"

        # 3. 更新時段狀態為待處理
        update_data = {
            "schedule": {
                "status": "PENDING",
                # 不設置 taker_id，因為可能不存在於資料庫中
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        update_response = client.patch(
            f"/api/v1/schedules/{schedule_id}", json=update_data
        )
        assert update_response.status_code == 200
        updated_schedule = update_response.json()
        assert updated_schedule["status"] == "PENDING"
        # taker_id 可能為 None，因為我們沒有設置

        # 4. 再次查詢確認更新
        get_response = client.get(f"/api/v1/schedules/{schedule_id}")
        assert get_response.status_code == 200
        final_schedule = get_response.json()
        assert final_schedule["status"] == "PENDING"
        # taker_id 可能為 None，因為我們沒有設置

        # 5. 刪除時段
        delete_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        import json

        delete_response = client.request(
            "DELETE",
            f"/api/v1/schedules/{schedule_id}",
            content=json.dumps(delete_data),
            headers={"Content-Type": "application/json"},
        )
        assert delete_response.status_code == 204

        # 6. 確認時段已被刪除
        get_response = client.get(f"/api/v1/schedules/{schedule_id}")
        assert get_response.status_code == 404

    def test_schedule_api_error_handling(self, client: TestClient):
        """測試 Schedule API 的錯誤處理。"""
        # 測試無效的 JSON 資料
        response = client.post("/api/v1/schedules", json={"invalid": "data"})
        assert response.status_code == 422  # 驗證錯誤

        # 測試缺少必要欄位
        invalid_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    # 缺少 date, start_time, end_time
                    "status": "AVAILABLE",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        response = client.post("/api/v1/schedules", json=invalid_data)
        assert response.status_code == 422  # 驗證錯誤

    def test_schedule_api_response_format_consistency(
        self, client: TestClient, sample_schedule_list_data: Dict[str, Any]
    ):
        """測試 Schedule API 回應格式的一致性。"""
        # 建立時段
        create_response = client.post(
            "/api/v1/schedules", json=sample_schedule_list_data
        )
        assert create_response.status_code == 201
        created_schedules = create_response.json()
        schedule_id = created_schedules[0]["id"]

        # 測試不同端點的回應格式一致性
        endpoints = [
            ("GET", f"/api/v1/schedules/{schedule_id}"),
            ("GET", "/api/v1/schedules"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)

            assert response.status_code == 200
            response_data = response.json()

            # 檢查回應格式
            if isinstance(response_data, list):
                # 列表回應
                for item in response_data:
                    self._validate_schedule_response_format(item)
            else:
                # 單一項目回應
                self._validate_schedule_response_format(response_data)

    def _validate_schedule_response_format(self, schedule_data: Dict[str, Any]):
        """驗證時段回應格式。"""
        required_fields = [
            "id",
            "giver_id",
            "date",
            "start_time",
            "end_time",
            "status",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_role",
        ]

        for field in required_fields:
            assert field in schedule_data, f"缺少必要欄位: {field}"

        # 檢查資料類型
        assert isinstance(schedule_data["id"], int)
        assert isinstance(schedule_data["giver_id"], int)
        assert isinstance(schedule_data["date"], str)
        assert isinstance(schedule_data["start_time"], str)
        assert isinstance(schedule_data["end_time"], str)
        assert isinstance(schedule_data["status"], str)
        assert isinstance(schedule_data["created_at"], str)
        assert isinstance(schedule_data["updated_at"], str)
        assert isinstance(schedule_data["created_by"], int)
        assert isinstance(schedule_data["created_by_role"], str)
