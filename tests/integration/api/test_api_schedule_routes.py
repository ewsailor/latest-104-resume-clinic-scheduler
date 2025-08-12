"""
測試 app/routers/api/schedule.py 模組。

測試時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

# 建立測試客戶端
client = TestClient(app)


class TestScheduleAPI:
    """測試時段 API 端點。"""

    @pytest.fixture
    def sample_schedule_data(self):
        """提供測試用的時段資料。"""
        print("建立測試用的時段資料")
        return {
            "giver_id": 1,
            "date": "2024-01-15",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "status": "AVAILABLE",
        }

    @pytest.fixture
    def sample_schedule_list(self):
        """提供測試用的時段列表資料。"""
        print("建立測試用的時段列表資料")
        return {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-01-15",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "status": "AVAILABLE",
                },
                {
                    "giver_id": 1,
                    "date": "2024-01-15",
                    "start_time": "10:00:00",
                    "end_time": "11:00:00",
                    "status": "AVAILABLE",
                },
            ],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

    def test_create_schedules_success(self, sample_schedule_list):
        """測試成功建立多個時段。"""
        print("測試成功建立多個時段")

        # 執行測試
        response = client.post("/api/schedules", json=sample_schedule_list)

        # 驗證回應
        assert response.status_code == 201
        data = response.json()

        # 驗證回應結構
        assert isinstance(data, list)
        assert len(data) == 2

        # 驗證每個時段的資料
        for schedule in data:
            assert "id" in schedule
            assert schedule["giver_id"] == 1
            assert schedule["date"] == "2024-01-15"
            assert schedule["status"] == "AVAILABLE"

    def test_create_schedules_invalid_data(self):
        """測試建立時段時使用無效資料。"""
        print("測試建立時段時使用無效資料")

        # 無效的時段資料
        invalid_data = {
            "schedules": [
                {
                    "giver_id": "invalid",  # 應該是整數
                    "date": "2024-01-15",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "status": "AVAILABLE",
                }
            ],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 執行測試
        response = client.post("/api/schedules", json=invalid_data)

        # 驗證回應
        assert response.status_code == 422  # Validation error

    def test_create_schedules_empty_list(self):
        """測試建立空的時段列表。"""
        print("測試建立空的時段列表")

        # 空的時段列表
        empty_data = {
            "schedules": [],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 執行測試
        response = client.post("/api/schedules", json=empty_data)

        # 驗證回應
        assert response.status_code == 201
        data = response.json()
        assert data == []

    @patch('app.routers.api.schedule.schedule_crud.create_schedules')
    def test_create_schedules_exception_handling(
        self, mock_create_schedules, sample_schedule_list
    ):
        """測試建立時段時的異常處理。"""
        print("測試建立時段時的異常處理")

        # 模擬異常
        mock_create_schedules.side_effect = Exception("資料庫錯誤")

        # 執行測試
        response = client.post("/api/schedules", json=sample_schedule_list)

        # 驗證回應
        assert response.status_code == 400
        data = response.json()
        assert "建立時段失敗" in data["detail"]

    def test_get_schedules_success(self):
        """測試成功取得時段列表。"""
        print("測試成功取得時段列表")

        # 執行測試
        response = client.get("/api/schedules")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證回應結構
        assert isinstance(data, list)

    def test_get_schedules_with_giver_id_filter(self):
        """測試根據 Giver ID 篩選時段。"""
        print("測試根據 Giver ID 篩選時段")

        # 執行測試
        response = client.get("/api/schedules?giver_id=1")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        for schedule in data:
            assert schedule["giver_id"] == 1

    def test_get_schedules_with_status_filter(self):
        """測試根據狀態篩選時段。"""
        print("測試根據狀態篩選時段")

        # 執行測試
        response = client.get("/api/schedules?status_filter=AVAILABLE")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        for schedule in data:
            assert schedule["status"] == "AVAILABLE"

    def test_get_schedules_with_combined_filters(self):
        """測試組合篩選條件。"""
        print("測試組合篩選條件")

        # 執行測試
        response = client.get("/api/schedules?giver_id=1&status_filter=AVAILABLE")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        for schedule in data:
            assert schedule["giver_id"] == 1
            assert schedule["status"] == "AVAILABLE"

    @patch('app.routers.api.schedule.schedule_crud.get_schedules')
    def test_get_schedules_exception_handling(self, mock_get_schedules):
        """測試取得時段列表時的異常處理。"""
        print("測試取得時段列表時的異常處理")

        # 模擬異常
        mock_get_schedules.side_effect = Exception("查詢錯誤")

        # 執行測試
        response = client.get("/api/schedules")

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "查詢時段失敗" in data["detail"]

    def test_get_schedule_by_id_success(self):
        """測試成功根據 ID 取得時段。"""
        print("測試成功根據 ID 取得時段")

        # 先建立一個時段
        schedule_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-01-20",  # 使用不同的日期避免重疊
                    "start_time": "14:00:00",  # 使用不同的時間避免重疊
                    "end_time": "15:00:00",
                    "status": "AVAILABLE",
                }
            ],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        create_response = client.post("/api/schedules", json=schedule_data)
        created_schedule = create_response.json()[0]

        # 執行測試
        response = client.get(f"/api/schedules/{created_schedule['id']}")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證資料
        assert data["id"] == created_schedule["id"]
        assert data["giver_id"] == 1
        assert data["date"] == "2024-01-15"

    def test_get_schedule_by_id_not_found(self):
        """測試取得不存在的時段。"""
        print("測試取得不存在的時段")

        # 執行測試
        response = client.get("/api/schedules/999")

        # 驗證回應
        assert response.status_code == 404
        data = response.json()
        assert "時段不存在" in data["detail"]

    @patch('app.routers.api.schedule.schedule_crud.get_schedule_by_id')
    def test_get_schedule_exception_handling(self, mock_get_schedule_by_id):
        """測試取得單一時段時的異常處理。"""
        print("測試取得單一時段時的異常處理")

        # 模擬異常
        mock_get_schedule_by_id.side_effect = Exception("查詢錯誤")

        # 執行測試
        response = client.get("/api/schedules/1")

        # 驗證異常處理
        assert response.status_code == 500
        data = response.json()
        assert "查詢時段失敗" in data["detail"]

    def test_update_schedule_success(self, sample_schedule_data):
        """測試成功更新時段。"""
        print("測試成功更新時段")

        # 先建立一個時段
        create_data = {
            "schedules": [sample_schedule_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        create_response = client.post("/api/schedules", json=create_data)
        created_schedule = create_response.json()[0]

        # 更新資料
        update_data = {
            "schedule_data": {
                "giver_id": 2,
                "date": "2024-01-16",
                "start_time": "10:00:00",
                "end_time": "11:00:00",
                "status": "AVAILABLE",
            },
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 執行測試
        response = client.put(
            f"/api/schedules/{created_schedule['id']}", json=update_data
        )

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證更新結果
        assert data["giver_id"] == 2
        assert data["date"] == "2024-01-16"
        assert data["status"] == "AVAILABLE"

    def test_update_schedule_not_found(self):
        """測試更新不存在的時段。"""
        print("測試更新不存在的時段")

        # 更新資料
        update_data = {
            "schedule_data": {
                "giver_id": 1,
                "date": "2024-01-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "status": "AVAILABLE",
            },
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 執行測試
        response = client.put("/api/schedules/999", json=update_data)

        # 驗證回應
        assert response.status_code == 404
        data = response.json()
        assert "時段不存在" in data["detail"]

    def test_update_schedule_invalid_data(self):
        """測試更新時段時使用無效資料。"""
        print("測試更新時段時使用無效資料")

        # 無效的更新資料
        invalid_data = {
            "schedule_data": {
                "giver_id": "invalid",  # 應該是整數
                "date": "2024-01-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "status": "AVAILABLE",
            },
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }

        # 執行測試
        response = client.put("/api/schedules/1", json=invalid_data)

        # 驗證回應
        assert response.status_code == 422  # Validation error

    @patch('app.routers.api.schedule.schedule_crud.update_schedule')
    def test_update_schedule_exception_handling(
        self, mock_update_schedule, sample_schedule_data
    ):
        """測試更新時段時的異常處理。"""
        print("測試更新時段時的異常處理")

        # 先建立一個時段
        create_data = {
            "schedules": [sample_schedule_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        create_response = client.post("/api/schedules", json=create_data)
        created_schedule = create_response.json()[0]

        # 模擬異常
        mock_update_schedule.side_effect = Exception("更新錯誤")

        # 執行測試
        response = client.put(
            f"/api/schedules/{created_schedule['id']}", json=sample_schedule_data
        )

        # 驗證回應
        assert response.status_code == 400
        data = response.json()
        assert "更新時段失敗" in data["detail"]

    def test_delete_schedule_success(self, sample_schedule_data):
        """測試成功刪除時段。"""
        print("測試成功刪除時段")

        # 使用不同的時段資料避免重疊
        unique_schedule_data = {
            "giver_id": 1,
            "date": "2024-01-25",  # 使用更遠的日期
            "start_time": "18:00:00",  # 使用不同的時間
            "end_time": "19:00:00",
            "status": "AVAILABLE",
        }

        # 先建立一個時段
        create_request = {
            "schedules": [unique_schedule_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        create_response = client.post("/api/schedules", json=create_request)

        # 檢查回應狀態
        if create_response.status_code != 201:
            print(
                f"建立時段失敗: {create_response.status_code} - {create_response.text}"
            )
            assert False, f"建立時段失敗: {create_response.status_code}"

        created_schedule = create_response.json()[0]

        # 執行測試
        delete_request = {"operator_user_id": 1, "operator_role": "GIVER"}
        import json

        response = client.request(
            "DELETE", f"/api/schedules/{created_schedule['id']}", json=delete_request
        )

        # 驗證回應
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "時段刪除成功"

    def test_delete_schedule_not_found(self):
        """測試刪除不存在的時段。"""
        print("測試刪除不存在的時段")

        # 執行測試
        delete_request = {"operator_user_id": 1, "operator_role": "GIVER"}
        import json

        response = client.request("DELETE", "/api/schedules/999", json=delete_request)

        # 驗證回應
        assert response.status_code == 404
        data = response.json()
        assert "時段不存在" in data["detail"]

    @patch('app.routers.api.schedule.schedule_crud.delete_schedule')
    def test_delete_schedule_exception_handling(
        self, mock_delete_schedule, sample_schedule_data
    ):
        """測試刪除時段時的異常處理。"""
        print("測試刪除時段時的異常處理")

        # 使用不同的時段資料避免重疊
        unique_schedule_data = {
            "giver_id": 1,
            "date": "2024-01-21",  # 使用不同的日期
            "start_time": "16:00:00",  # 使用不同的時間
            "end_time": "17:00:00",
            "status": "AVAILABLE",
        }

        # 先建立一個時段
        create_request = {
            "schedules": [unique_schedule_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        create_response = client.post("/api/schedules", json=create_request)
        created_schedule = create_response.json()[0]

        # 模擬異常
        mock_delete_schedule.side_effect = Exception("刪除錯誤")

        # 執行測試
        delete_request = {"operator_user_id": 1, "operator_role": "GIVER"}
        import json

        response = client.request(
            "DELETE", f"/api/schedules/{created_schedule['id']}", json=delete_request
        )

        # 驗證回應
        assert response.status_code == 400
        data = response.json()
        assert "刪除時段失敗" in data["detail"]

    def test_schedule_date_field_mapping(self, sample_schedule_data):
        """測試時段日期欄位映射。"""
        print("測試時段日期欄位映射")

        # 執行測試
        create_data = {
            "schedules": [sample_schedule_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        response = client.post("/api/schedules", json=create_data)

        # 驗證回應
        assert response.status_code == 201
        data = response.json()

        # 驗證日期欄位正確映射
        assert "date" in data[0]
        assert data[0]["date"] == "2024-01-15"

    def test_schedule_validation_edge_cases(self):
        """測試時段驗證的邊界情況。"""
        print("測試時段驗證的邊界情況")

        # 測試無效的日期格式
        invalid_date_data = {
            "giver_id": 1,
            "date": "invalid-date",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "status": "AVAILABLE",
        }

        invalid_request = {
            "schedules": [invalid_date_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        response = client.post("/api/schedules", json=invalid_request)
        assert response.status_code == 422

        # 測試無效的時間格式
        invalid_time_data = {
            "giver_id": 1,
            "date": "2024-01-15",
            "start_time": "invalid-time",
            "end_time": "10:00:00",
            "status": "AVAILABLE",
        }

        invalid_request = {
            "schedules": [invalid_time_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        response = client.post("/api/schedules", json=invalid_request)
        assert response.status_code == 422

        # 測試無效的狀態 - 資料庫會拒絕無效狀態，返回 400 錯誤
        invalid_status_data = {
            "giver_id": 1,
            "date": "2024-01-15",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "status": "INVALID_STATUS",
        }

        invalid_request = {
            "schedules": [invalid_status_data],
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        response = client.post("/api/schedules", json=invalid_request)
        assert response.status_code == 400

    def test_schedule_bulk_operations(self):
        """測試時段批量操作。"""
        print("測試時段批量操作")

        # 建立多個時段
        bulk_data = [
            {
                "giver_id": 1,
                "date": "2024-01-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "status": "AVAILABLE",
            },
            {
                "giver_id": 1,
                "date": "2024-01-15",
                "start_time": "10:00:00",
                "end_time": "11:00:00",
                "status": "AVAILABLE",
            },
            {
                "giver_id": 2,
                "date": "2024-01-16",
                "start_time": "14:00:00",
                "end_time": "15:00:00",
                "status": "AVAILABLE",
            },
        ]

        # 執行測試
        bulk_request = {
            "schedules": bulk_data,
            "operator_user_id": 1,
            "operator_role": "GIVER",
        }
        response = client.post("/api/schedules", json=bulk_request)

        # 驗證回應
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3

        # 驗證每個時段都有唯一的 ID
        ids = [schedule["id"] for schedule in data]
        assert len(ids) == len(set(ids))
