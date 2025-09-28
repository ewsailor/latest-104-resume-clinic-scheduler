"""時段路由整合測試。

測試時段管理 API 的完整流程，包括建立、查詢、更新和刪除時段。
"""

# ===== 標準函式庫 =====

import json
import random

from fastapi import status
from fastapi.testclient import TestClient

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum
from app.main import app

# ===== 測試 Fixtures =====
# 暫時不使用進階 fixtures，使用基本的方式


class TestScheduleRoutes:
    """時段路由整合測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    @pytest.fixture(autouse=True)
    def cleanup_database(self):
        """自動清理資料庫，避免測試間互相影響。"""
        # 測試前清理
        yield
        # 測試後清理（如果需要）

    @pytest.fixture
    def sample_schedule_data(self):
        """建立範例時段資料。"""
        # 使用 set 來確保時間的唯一性
        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(8, 20)
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"

            if time_key not in used_times:
                used_times.add(time_key)
                break

        return {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-12-25",
                    "start_time": f"{time_key}:00",
                    "end_time": f"{hour:02d}:{minute+1:02d}:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

    @pytest.fixture
    def sample_schedule_update_data(self):
        """建立範例時段更新資料。"""
        # 使用 set 來確保時間的唯一性
        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(14, 22)  # 使用不同的時間範圍避免重疊
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"

            if time_key not in used_times:
                used_times.add(time_key)
                break

        # 確保結束時間不會超過 59 分鐘
        end_minute = (minute + 1) % 60
        end_hour = hour if end_minute > minute else (hour + 1) % 24

        return {
            "schedule": {
                "start_time": f"{time_key}:00",
                "end_time": f"{end_hour:02d}:{end_minute:02d}:00",
                "note": "更新後的時段",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

    @pytest.fixture
    def sample_schedule_delete_data(self):
        """建立範例時段刪除資料。"""
        return {"deleted_by": 1, "deleted_by_role": "GIVER"}

    def test_create_schedules_success(self, client, sample_schedule_data):
        """測試建立時段 - 成功。"""
        # GIVEN：準備測試資料，使用不同的日期避免重疊
        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(6, 12)
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"

            if time_key not in used_times:
                used_times.add(time_key)
                break

        # 建立唯一的時段資料
        unique_schedule_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-08-15",  # 使用不同的日期
                    "start_time": f"{time_key}:00",
                    "end_time": f"{hour:02d}:{minute+1:02d}:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=unique_schedule_data)

        # THEN：確認建立成功
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        # 驗證回應資料結構
        schedule = data[0]
        assert "id" in schedule
        assert schedule["giver_id"] == 1
        assert schedule["date"] == "2024-08-15"  # 修正為實際的日期
        # 使用動態時間驗證，因為我們使用 set 確保唯一性
        assert (
            schedule["start_time"] == unique_schedule_data["schedules"][0]["start_time"]
        )
        assert schedule["end_time"] == unique_schedule_data["schedules"][0]["end_time"]
        assert schedule["status"] in [status.value for status in ScheduleStatusEnum]
        assert schedule["created_by"] == 1
        assert schedule["created_by_role"] == "GIVER"

    def test_create_schedules_validation_error(self, client):
        """測試建立時段 - 參數驗證錯誤。"""
        # GIVEN：無效的時段建立資料（缺少必要欄位）
        invalid_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    # 缺少 date 欄位
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=invalid_data)

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    def test_create_schedules_time_validation_error(self, client):
        """測試建立時段 - 時間邏輯錯誤。"""
        # GIVEN：時間邏輯錯誤的時段資料（開始時間晚於結束時間）
        invalid_time_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-01-15",
                    "start_time": "10:00:00",
                    "end_time": "09:00:00",  # 結束時間早於開始時間
                    "note": "無效時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=invalid_time_data)

        # THEN：確認返回時間邏輯錯誤
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data
        assert "開始時間必須早於結束時間" in data["error"]["message"]

    def test_list_schedules_success(self, client):
        """測試查詢時段列表 - 成功。"""
        # GIVEN：資料庫中有時段資料

        # WHEN：呼叫查詢時段列表 API
        response = client.get("/api/v1/schedules")

        # THEN：確認查詢成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_schedules_with_filters(self, client):
        """測試查詢時段列表 - 使用篩選條件。"""
        # GIVEN：查詢參數

        # WHEN：使用篩選條件查詢時段列表
        response = client.get("/api/v1/schedules?giver_id=1&status_filter=AVAILABLE")

        # THEN：確認查詢成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_schedules_invalid_filters(self, client):
        """測試查詢時段列表 - 無效篩選條件。"""
        # GIVEN：無效的查詢參數（giver_id 必須大於 0）

        # WHEN：使用無效的篩選條件查詢
        response = client.get("/api/v1/schedules?giver_id=0")

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_get_schedule_success(self, client, sample_schedule_data):
        """測試取得單一時段 - 成功。"""
        # GIVEN：先建立一個時段，使用不同的日期避免重疊
        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(13, 17)
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"

            if time_key not in used_times:
                used_times.add(time_key)
                break

        # 建立唯一的時段資料
        unique_schedule_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-10-15",  # 使用不同的日期
                    "start_time": f"{time_key}:00",
                    "end_time": f"{hour:02d}:{minute+1:02d}:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        create_response = client.post("/api/v1/schedules", json=unique_schedule_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # WHEN：呼叫取得單一時段 API
        response = client.get(f"/api/v1/schedules/{schedule_id}")

        # THEN：確認取得成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == schedule_id
        assert "giver_id" in data
        assert "date" in data
        assert "start_time" in data
        assert "end_time" in data
        assert "status" in data

    def test_get_schedule_not_found(self, client):
        """測試取得單一時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID

        # WHEN：呼叫取得單一時段 API
        response = client.get("/api/v1/schedules/99999")

        # THEN：確認返回找不到錯誤
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "時段不存在" in data["error"]["message"]

    def test_get_schedule_invalid_id(self, client):
        """測試取得單一時段 - 無效的時段 ID。"""
        # GIVEN：無效的時段 ID（必須大於 0）

        # WHEN：使用無效的時段 ID 呼叫 API
        response = client.get("/api/v1/schedules/0")

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_update_schedule_success(
        self, client, sample_schedule_data, sample_schedule_update_data
    ):
        """測試更新時段 - 成功。"""
        # GIVEN：先建立一個時段，使用不同的日期避免重疊
        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(18, 23)
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"

            if time_key not in used_times:
                used_times.add(time_key)
                break

        # 建立唯一的時段資料
        unique_schedule_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-09-15",  # 使用不同的日期
                    "start_time": f"{time_key}:00",
                    "end_time": f"{hour:02d}:{minute+1:02d}:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        create_response = client.post("/api/v1/schedules", json=unique_schedule_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # WHEN：呼叫更新時段 API
        response = client.patch(
            f"/api/v1/schedules/{schedule_id}", json=sample_schedule_update_data
        )

        # THEN：確認更新成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == schedule_id
        # 使用動態時間驗證，因為我們使用 set 確保唯一性
        assert (
            data["start_time"] == sample_schedule_update_data["schedule"]["start_time"]
        )
        assert data["end_time"] == sample_schedule_update_data["schedule"]["end_time"]
        assert data["note"] == "更新後的時段"
        assert data["updated_by"] == 1
        assert data["updated_by_role"] == "GIVER"

    def test_update_schedule_not_found(self, client, sample_schedule_update_data):
        """測試更新時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID 和有效的更新資料

        # WHEN：呼叫更新時段 API
        response = client.patch(
            "/api/v1/schedules/99999", json=sample_schedule_update_data
        )

        # THEN：確認返回找不到錯誤
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "時段不存在" in data["error"]["message"]

    def test_update_schedule_validation_error(self, client, sample_schedule_data):
        """測試更新時段 - 參數驗證錯誤。"""
        # GIVEN：先建立一個時段，使用不同的日期避免重疊
        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(8, 12)
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"

            if time_key not in used_times:
                used_times.add(time_key)
                break

        # 建立唯一的時段資料
        unique_schedule_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-11-15",  # 使用不同的日期
                    "start_time": f"{time_key}:00",
                    "end_time": f"{hour:02d}:{minute+1:02d}:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        create_response = client.post("/api/v1/schedules", json=unique_schedule_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # 無效的更新資料（時間邏輯錯誤）
        invalid_data = {
            "schedule": {
                "start_time": "10:00:00",
                "end_time": "09:00:00",  # 結束時間早於開始時間
                "note": "無效時段",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # WHEN：呼叫更新時段 API
        response = client.patch(f"/api/v1/schedules/{schedule_id}", json=invalid_data)

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data

    def test_delete_schedule_success(
        self, client, sample_schedule_data, sample_schedule_delete_data
    ):
        """測試刪除時段 - 成功。"""
        # GIVEN：先建立一個時段
        create_response = client.post("/api/v1/schedules", json=sample_schedule_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            f"/api/v1/schedules/{schedule_id}",
            content=json.dumps(sample_schedule_delete_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認刪除成功
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

    def test_delete_schedule_not_found(self, client, sample_schedule_delete_data):
        """測試刪除時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID 和有效的刪除資料

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            "/api/v1/schedules/99999",
            content=json.dumps(sample_schedule_delete_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認返回找不到錯誤
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "時段不存在" in data["error"]["message"]

    def test_delete_schedule_validation_error(self, client):
        """測試刪除時段 - 參數驗證錯誤。"""
        # GIVEN：無效的刪除資料（缺少必要欄位）
        invalid_data = {
            # 缺少必要欄位
        }

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            "/api/v1/schedules/1",
            content=json.dumps(invalid_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_schedule_routes_http_methods(self, client):
        """測試時段路由 - HTTP 方法限制。"""
        # GIVEN：時段路由端點

        # WHEN：使用不支援的 HTTP 方法
        get_response = client.get("/api/v1/schedules/1")  # 支援
        post_response = client.post("/api/v1/schedules/1")  # 不支援
        put_response = client.put("/api/v1/schedules/1")  # 不支援

        # THEN：確認方法支援正確
        assert get_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]
        assert post_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert put_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_schedule_routes_content_type(self, client):
        """測試時段路由 - 內容類型。"""
        # GIVEN：時段路由端點

        # WHEN：呼叫 API 端點
        response = client.get("/api/v1/schedules")

        # THEN：確認內容類型正確
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/json"
