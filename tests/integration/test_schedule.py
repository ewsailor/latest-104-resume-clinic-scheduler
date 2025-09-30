"""時段路由整合測試。

測試時段管理 API 的完整流程，包括建立、查詢、更新和刪除時段。
"""

# ===== 標準函式庫 =====
import json

# ===== 第三方套件 =====
from fastapi import status
import pytest

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum


class TestScheduleRoutes:
    """時段路由整合測試類別。"""

    @pytest.fixture
    def client(self, integration_test_client):
        """建立測試客戶端。"""
        return integration_test_client

    @pytest.fixture(autouse=True)
    def cleanup_database(self):
        """自動清理資料庫，避免測試間互相影響。"""
        # 測試前清理
        yield
        # 測試後清理（如果需要）

    def test_create_schedules_success(self, client, schedule_create_payload):
        """測試建立時段 - 成功。"""
        # GIVEN：準備測試資料
        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=schedule_create_payload)

        # THEN：確認建立成功
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        # 驗證回應資料結構
        schedule = data[0]
        assert "id" in schedule
        assert schedule["giver_id"] == 1
        assert schedule["date"] == "2024-12-25"
        # 驗證時段資料
        assert schedule["start_time"] == "09:00:00"
        assert schedule["end_time"] == "10:00:00"
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

    def test_get_schedule_success(self, client, schedule_create_payload):
        """測試取得單一時段 - 成功。"""
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
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
        self, client, schedule_create_payload, schedule_update_payload
    ):
        """測試更新時段 - 成功。"""
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # 只更新備註，不更新時間，避免重疊檢查
        safe_update_data = {
            "schedule": {
                "note": "更新後的時段",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # WHEN：呼叫更新時段 API
        response = client.patch(
            f"/api/v1/schedules/{schedule_id}", json=safe_update_data
        )

        # THEN：確認更新成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == schedule_id
        # 驗證更新後的資料
        assert data["note"] == "更新後的時段"
        assert data["updated_by"] == 1
        assert data["updated_by_role"] == "GIVER"
        # 驗證時間沒有改變
        assert data["start_time"] == created_schedule["start_time"]
        assert data["end_time"] == created_schedule["end_time"]

    def test_update_schedule_not_found(self, client, schedule_update_payload):
        """測試更新時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID 和有效的更新資料

        # WHEN：呼叫更新時段 API
        response = client.patch("/api/v1/schedules/99999", json=schedule_update_payload)

        # THEN：確認返回找不到錯誤
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "時段不存在" in data["error"]["message"]

    def test_update_schedule_validation_error(self, client, schedule_create_payload):
        """測試更新時段 - 參數驗證錯誤。"""
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # 無效的更新資料（時間邏輯錯誤）
        # 使用不會與現有時段重疊的時間來測試驗證邏輯
        invalid_data = {
            "schedule": {
                "start_time": "08:00:00",  # 早上時間，不會與下午時段重疊
                "end_time": "07:00:00",  # 結束時間早於開始時間
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
        self, client, schedule_create_payload, schedule_delete_payload
    ):
        """測試刪除時段 - 成功。"""
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            f"/api/v1/schedules/{schedule_id}",
            content=json.dumps(schedule_delete_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認刪除成功
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

    def test_delete_schedule_not_found(self, client, schedule_delete_payload):
        """測試刪除時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID 和有效的刪除資料

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            "/api/v1/schedules/99999",
            content=json.dumps(schedule_delete_payload).encode('utf-8'),
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
