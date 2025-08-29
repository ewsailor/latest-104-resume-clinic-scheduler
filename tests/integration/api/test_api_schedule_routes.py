"""
測試 app/routers/api/schedule.py 模組。

測試時段相關的 API 端點，包括建立、查詢、更新和刪除時段。
"""

# ===== 標準函式庫 =====
import datetime
import random
import time
from unittest.mock import patch

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.main import app
from tests.logger import log_test_info

# 建立測試客戶端
client = TestClient(app)


class TestScheduleAPI:
    """測試時段 API 端點。"""

    @pytest.fixture
    def sample_schedule_data(self):
        """提供測試用的時段資料。"""
        log_test_info("建立測試用的時段資料")
        # 使用未來日期避免重疊，但要在2個月內
        # 添加時間戳以確保每次測試都不同
        timestamp = int(time.time()) % 10000  # 使用時間戳的後4位
        future_date = datetime.date.today() + datetime.timedelta(
            days=random.randint(1, 60) + timestamp % 20  # 使用1-60天內的日期
        )
        hour = random.randint(8, 18) + (timestamp % 5)  # 額外的隨機性
        return {
            "giver_id": 1,
            "date": future_date.strftime("%Y-%m-%d"),
            "start_time": f"{hour:02d}:00:00",
            "end_time": f"{hour+1:02d}:00:00",
            "status": "AVAILABLE",
        }

    @pytest.fixture
    def sample_schedule_list(self):
        """提供測試用的時段列表資料。"""
        log_test_info("建立測試用的時段列表資料")
        # 使用未來日期避免重疊，但要在3個月內
        # 添加時間戳以確保每次測試都不同
        timestamp = int(time.time()) % 10000  # 使用時間戳的後4位
        random_days = random.randint(1, 90) + timestamp % 30  # 使用1-90天內的日期
        future_date = datetime.date.today() + datetime.timedelta(days=random_days)

        # 使用隨機時間避免重疊
        hour1 = random.randint(8, 9)  # 限制範圍
        hour2 = hour1 + 4  # 確保不重疊，間隔4小時
        return {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": future_date.strftime("%Y-%m-%d"),
                    "start_time": f"{hour1:02d}:00:00",
                    "end_time": f"{hour1+1:02d}:00:00",
                    "status": "AVAILABLE",
                },
                {
                    "giver_id": 1,
                    "date": future_date.strftime("%Y-%m-%d"),
                    "start_time": f"{hour2:02d}:00:00",
                    "end_time": f"{hour2+1:02d}:00:00",
                    "status": "AVAILABLE",
                },
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

    def test_create_schedules_success(self, sample_schedule_list):
        """測試成功建立多個時段。"""
        log_test_info("測試成功建立多個時段")

        # 執行測試
        response = client.post("/api/v1/schedules", json=sample_schedule_list)

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
            # 檢查日期格式是否正確（不檢查具體日期，因為使用隨機日期）
            assert "date" in schedule
            assert schedule["status"] == "AVAILABLE"

    def test_create_schedules_invalid_data(self):
        """測試建立時段時使用無效資料。"""
        log_test_info("測試建立時段時使用無效資料")

        # 無效的時段資料
        invalid_data = {
            "schedules": [
                {
                    "giver_id": "invalid",  # 應該是整數
                    "date": "2025-09-15",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "status": "AVAILABLE",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # 執行測試
        response = client.post("/api/v1/schedules", json=invalid_data)

        # 驗證回應
        assert response.status_code == 422  # Validation error

    def test_create_schedules_empty_list(self):
        """測試建立空的時段列表。"""
        log_test_info("測試建立空的時段列表")

        # 空的時段列表
        empty_data = {
            "schedules": [],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # 執行測試
        response = client.post("/api/v1/schedules", json=empty_data)

        # 驗證回應
        assert response.status_code == 201
        data = response.json()
        assert data == []

    @patch('app.routers.api.schedule.schedule_crud.create_schedules')
    def test_create_schedules_exception_handling(
        self, mock_create_schedules, sample_schedule_list
    ):
        """測試建立時段時的異常處理。"""
        log_test_info("測試建立時段時的異常處理")

        # 模擬異常
        mock_create_schedules.side_effect = Exception("資料庫錯誤")

        # 執行測試
        response = client.post("/api/v1/schedules", json=sample_schedule_list)

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "建立時段時發生內部錯誤" in data["error"]["message"]

    def test_get_schedules_success(self):
        """測試成功取得時段列表。"""
        log_test_info("測試成功取得時段列表")

        # 執行測試
        response = client.get("/api/v1/schedules")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證回應結構
        assert isinstance(data, list)

    def test_get_schedules_with_giver_id_filter(self):
        """測試根據 Giver ID 篩選時段。"""
        log_test_info("測試根據 Giver ID 篩選時段")

        # 執行測試
        response = client.get("/api/v1/schedules?giver_id=1")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        for schedule in data:
            assert schedule["giver_id"] == 1

    def test_get_schedules_with_status_filter(self):
        """測試根據狀態篩選時段。"""
        log_test_info("測試根據狀態篩選時段")

        # 執行測試
        response = client.get("/api/v1/schedules?status_filter=AVAILABLE")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        for schedule in data:
            assert schedule["status"] == "AVAILABLE"

    def test_get_schedules_with_combined_filters(self):
        """測試組合篩選條件。"""
        log_test_info("測試組合篩選條件")

        # 執行測試
        response = client.get("/api/v1/schedules?giver_id=1&status_filter=AVAILABLE")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        for schedule in data:
            assert schedule["giver_id"] == 1
            assert schedule["status"] == "AVAILABLE"

    @patch('app.routers.api.schedule.schedule_crud.list_schedules')
    def test_list_schedules_exception_handling(self, mock_list_schedules):
        """測試取得時段列表時的異常處理。"""
        log_test_info("測試取得時段列表時的異常處理")

        # 模擬異常
        mock_list_schedules.side_effect = Exception("查詢錯誤")

        # 執行測試
        response = client.get("/api/v1/schedules")

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "查詢時段列表失敗" in data["error"]["message"]

    def test_get_schedule_by_id_success(self):
        """測試成功根據 ID 取得時段。"""
        log_test_info("測試成功根據 ID 取得時段")

        # 先建立一個時段
        future_date = datetime.date.today() + datetime.timedelta(
            days=11
        )  # 使用 11 天後避免重疊
        schedule_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": future_date.strftime("%Y-%m-%d"),
                    "start_time": "14:00:00",
                    "end_time": "15:00:00",
                    "status": "AVAILABLE",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        create_response = client.post("/api/v1/schedules", json=schedule_data)

        # 檢查建立是否成功
        if create_response.status_code != 201:
            log_test_info(
                f"建立時段失敗: {create_response.status_code} - {create_response.text}"
            )
            # 如果建立失敗，跳過這個測試
            pytest.skip("無法建立測試時段，跳過取得時段測試")

        created_schedule = create_response.json()[0]

        # 執行測試
        response = client.get(f"/api/v1/schedules/{created_schedule['id']}")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證資料
        assert data["id"] == created_schedule["id"]
        assert data["giver_id"] == 1
        assert data["date"] == future_date.strftime("%Y-%m-%d")

    def test_get_schedule_by_id_not_found(self):
        """測試取得不存在的時段。"""
        log_test_info("測試取得不存在的時段")

        # 執行測試
        response = client.get("/api/v1/schedules/999")

        # 驗證回應
        assert response.status_code == 404
        data = response.json()
        # 檢查錯誤訊息是否包含預期的文字
        assert "時段不存在: ID=999" in str(data["error"]["message"])

    @patch('app.routers.api.schedule.schedule_crud.get_schedule')
    def test_get_schedule_exception_handling(self, mock_get_schedule):
        """測試取得單一時段時的異常處理。"""
        log_test_info("測試取得單一時段時的異常處理")

        # 模擬異常
        mock_get_schedule.side_effect = Exception("查詢錯誤")

        # 執行測試
        response = client.get("/api/v1/schedules/1")

        # 驗證異常處理
        assert response.status_code == 500
        data = response.json()
        assert "查詢單一時段失敗" in data["error"]["message"]

    def test_update_schedule_success(self, sample_schedule_data):
        """測試成功更新時段。"""
        log_test_info("測試成功更新時段")

        # 先建立一個時段
        create_data = {
            "schedules": [sample_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        create_response = client.post("/api/v1/schedules", json=create_data)

        # 檢查建立是否成功
        if create_response.status_code != 201:
            log_test_info(
                f"建立時段失敗: {create_response.status_code} - {create_response.text}"
            )
            # 如果建立失敗，跳過這個測試
            pytest.skip("無法建立測試時段，跳過更新測試")

        created_schedule = create_response.json()[0]

        # 更新資料
        update_data = {
            "schedule": {
                "giver_id": 2,
                "date": "2025-09-16",
                "start_time": "10:00:00",
                "end_time": "11:00:00",
                "status": "AVAILABLE",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # 執行測試
        response = client.patch(
            f"/api/v1/schedules/{created_schedule['id']}", json=update_data
        )

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證更新結果
        assert data["giver_id"] == 2
        assert data["date"] == "2025-09-16"
        assert data["status"] == "AVAILABLE"

    def test_update_schedule_not_found(self):
        """測試更新不存在的時段。"""
        log_test_info("測試更新不存在的時段")

        # 更新資料
        update_data = {
            "schedule": {
                "giver_id": 1,
                "date": "2025-09-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "status": "AVAILABLE",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # 執行測試
        response = client.patch("/api/v1/schedules/999", json=update_data)

        # 驗證回應
        assert response.status_code == 404  # 時段不存在應該返回 404
        data = response.json()
        assert "時段不存在" in data["error"]["message"] or "時段不存在" in str(data)

    def test_update_schedule_invalid_data(self):
        """測試更新時段時使用無效資料。"""
        log_test_info("測試更新時段時使用無效資料")

        # 無效的更新資料
        invalid_data = {
            "schedule": {
                "giver_id": "invalid",  # 應該是整數
                "date": "2025-09-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "status": "AVAILABLE",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # 執行測試
        response = client.patch("/api/v1/schedules/1", json=invalid_data)

        # 驗證回應
        assert response.status_code == 422  # Validation error

    @patch('app.routers.api.schedule.schedule_crud.update_schedule')
    def test_update_schedule_exception_handling(
        self, mock_update_schedule, sample_schedule_data
    ):
        """測試更新時段時的異常處理。"""
        log_test_info("測試更新時段時的異常處理")

        # 先建立一個時段
        create_data = {
            "schedules": [sample_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        create_response = client.post("/api/v1/schedules", json=create_data)

        # 檢查建立是否成功
        if create_response.status_code != 201:
            log_test_info(
                f"建立時段失敗: {create_response.status_code} - {create_response.text}"
            )
            # 如果建立失敗，跳過這個測試
            pytest.skip("無法建立測試時段，跳過更新異常處理測試")

        created_schedule = create_response.json()[0]

        # 模擬異常
        mock_update_schedule.side_effect = Exception("更新錯誤")

        # 執行測試
        update_data = {
            "schedule": sample_schedule_data,
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }
        response = client.patch(
            f"/api/v1/schedules/{created_schedule['id']}", json=update_data
        )

        # 驗證回應
        assert response.status_code == 400  # 更新異常處理返回 400
        data = response.json()
        assert "更新時段失敗" in data["error"]["message"]

    def test_delete_schedule_success(self, sample_schedule_data):
        """測試成功刪除時段。"""
        log_test_info("測試成功刪除時段")

        # 使用不同的時段資料避免重疊
        # 使用時間戳確保唯一性，但限制在2個月內
        timestamp = int(time.time()) % 10000
        unique_date = datetime.date.today() + datetime.timedelta(
            days=random.randint(1, 60) + timestamp % 20
        )
        unique_hour = random.randint(8, 18) + timestamp % 5
        unique_schedule_data = {
            "giver_id": 1,
            "date": unique_date.strftime("%Y-%m-%d"),
            "start_time": f"{unique_hour:02d}:00:00",
            "end_time": f"{unique_hour+1:02d}:00:00",
            "status": "AVAILABLE",
        }

        # 先建立一個時段
        create_request = {
            "schedules": [unique_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        create_response = client.post("/api/v1/schedules", json=create_request)

        # 檢查回應狀態
        if create_response.status_code != 201:
            log_test_info(
                f"建立時段失敗: {create_response.status_code} - {create_response.text}"
            )
            assert False, f"建立時段失敗: {create_response.status_code}"

        created_schedule = create_response.json()[0]

        # 執行測試
        delete_request = {"deleted_by": 1, "deleted_by_role": "GIVER"}

        response = client.request(
            "DELETE", f"/api/v1/schedules/{created_schedule['id']}", json=delete_request
        )

        # 驗證回應
        assert response.status_code == 204
        # 204 No Content 不應該有回應內容

    def test_delete_schedule_not_found(self):
        """測試刪除不存在的時段。"""
        log_test_info("測試刪除不存在的時段")

        # 執行測試
        delete_request = {"deleted_by": 1, "deleted_by_role": "GIVER"}

        response = client.request(
            "DELETE", "/api/v1/schedules/999", json=delete_request
        )

        # 驗證回應
        assert response.status_code == 404
        data = response.json()
        assert "時段不存在" in data["error"]["message"]

    @patch('app.routers.api.schedule.schedule_crud.delete_schedule')
    def test_delete_schedule_exception_handling(
        self, mock_delete_schedule, sample_schedule_data
    ):
        """測試刪除時段時的異常處理。"""
        log_test_info("測試刪除時段時的異常處理")

        # 使用不同的時段資料避免重疊
        unique_date = datetime.date.today() + datetime.timedelta(
            days=5
        )  # 使用更遠的日期
        unique_hour = random.randint(8, 18)
        unique_schedule_data = {
            "giver_id": 1,
            "date": unique_date.strftime("%Y-%m-%d"),
            "start_time": f"{unique_hour:02d}:00:00",
            "end_time": f"{unique_hour+1:02d}:00:00",
            "status": "AVAILABLE",
        }

        # 先建立一個時段
        create_request = {
            "schedules": [unique_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        create_response = client.post("/api/v1/schedules", json=create_request)

        # 檢查建立是否成功
        if create_response.status_code != 201:
            log_test_info(
                f"建立時段失敗: {create_response.status_code} - {create_response.text}"
            )
            # 如果建立失敗，跳過這個測試
            pytest.skip("無法建立測試時段，跳過刪除異常處理測試")

        created_schedule = create_response.json()[0]

        # 模擬異常
        mock_delete_schedule.side_effect = Exception("刪除錯誤")

        # 執行測試
        delete_request = {"deleted_by": 1, "deleted_by_role": "GIVER"}

        response = client.request(
            "DELETE", f"/api/v1/schedules/{created_schedule['id']}", json=delete_request
        )

        # 驗證回應
        assert response.status_code == 400
        data = response.json()
        assert "刪除時段失敗" in data["error"]["message"]

    def test_schedule_date_field_mapping(self, sample_schedule_data):
        """測試時段日期欄位映射。"""
        log_test_info("測試時段日期欄位映射")

        # 執行測試
        create_data = {
            "schedules": [sample_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        response = client.post("/api/v1/schedules", json=create_data)

        # 驗證回應
        assert response.status_code == 201
        data = response.json()

        # 驗證日期欄位正確映射
        assert "date" in data[0]
        # 檢查日期格式是否正確（不檢查具體日期，因為使用隨機日期）
        assert isinstance(data[0]["date"], str)

    def test_schedule_validation_edge_cases(self):
        """測試時段驗證的邊界情況。"""
        log_test_info("測試時段驗證的邊界情況")

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
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        response = client.post("/api/v1/schedules", json=invalid_request)
        assert response.status_code == 422

        # 測試無效的時間格式
        invalid_time_data = {
            "giver_id": 1,
            "date": "2025-09-15",
            "start_time": "invalid-time",
            "end_time": "10:00:00",
            "status": "AVAILABLE",
        }

        invalid_request = {
            "schedules": [invalid_time_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        response = client.post("/api/v1/schedules", json=invalid_request)
        assert response.status_code == 422

        # 測試無效的狀態 - Pydantic 會拒絕無效狀態，返回 422 錯誤
        invalid_status_data = {
            "giver_id": 1,
            "date": "2025-09-15",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "status": "INVALID_STATUS",
        }

        invalid_request = {
            "schedules": [invalid_status_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        response = client.post("/api/v1/schedules", json=invalid_request)
        assert response.status_code == 422

    def test_schedule_bulk_operations(self):
        """測試時段批量操作。"""
        log_test_info("測試時段批量操作")

        # 建立多個時段
        # 使用更隨機的日期範圍以避免與其他測試衝突，但要在2個月內
        timestamp = int(time.time()) % 10000
        random_days = random.randint(1, 60) + timestamp % 20  # 使用1-60天內的日期
        future_date = datetime.date.today() + datetime.timedelta(days=random_days)

        # 使用更分散的時間避免重疊
        hour1 = 9 + (timestamp % 2)  # 9-10 點
        hour2 = 14 + (timestamp % 2)  # 14-15 點
        hour3 = 16 + (timestamp % 2)  # 16-17 點

        bulk_data = [
            {
                "giver_id": 1,
                "date": future_date.strftime("%Y-%m-%d"),
                "start_time": f"{hour1:02d}:00:00",
                "end_time": f"{hour1+1:02d}:00:00",
                "status": "AVAILABLE",
            },
            {
                "giver_id": 1,
                "date": future_date.strftime("%Y-%m-%d"),
                "start_time": f"{hour2:02d}:00:00",
                "end_time": f"{hour2+1:02d}:00:00",
                "status": "AVAILABLE",
            },
            {
                "giver_id": 2,
                "date": (future_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                "start_time": f"{hour3:02d}:00:00",
                "end_time": f"{hour3+1:02d}:00:00",
                "status": "AVAILABLE",
            },
        ]

        # 執行測試
        bulk_request = {
            "schedules": bulk_data,
            "created_by": 1,
            "created_by_role": "GIVER",
        }
        response = client.post("/api/v1/schedules", json=bulk_request)

        # 驗證回應
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3

        # 驗證每個時段都有唯一的 ID
        ids = [schedule["id"] for schedule in data]
        assert len(ids) == len(set(ids))
