"""整合測試 Fixtures 使用範例。

展示如何在整合測試中正確使用各種 fixtures。
"""

# ===== 標準函式庫 =====

# ===== 第三方套件 =====
from fastapi import status
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum
from app.main import app

# ===== 測試 Fixtures =====


class TestFixturesUsage:
    """Fixtures 使用範例測試類別。"""

    def test_basic_client_fixture(self):
        """測試基本客戶端 fixture。"""
        # GIVEN：使用基本的 TestClient fixture

        # WHEN：建立客戶端
        client = TestClient(app)

        # THEN：確認客戶端正常運作
        response = client.get("/healthz")
        assert response.status_code == status.HTTP_200_OK

    def test_integration_database_fixtures(
        self, integration_db_session, integration_test_data
    ):
        """測試資料庫相關 fixtures。"""
        # GIVEN：資料庫會話和測試資料已準備

        # WHEN：查詢測試資料
        users = integration_test_data["users"]
        schedules = integration_test_data["schedules"]

        # THEN：確認資料正確載入
        assert len(users) == 3  # giver, taker, system
        assert len(schedules) == 3  # available, pending, accepted

        # 驗證使用者資料
        giver_user = integration_test_data["giver_user"]
        assert giver_user.name == "測試 Giver"
        assert giver_user.email == "giver@test.com"
        assert giver_user.is_active is True

        # 驗證時段資料
        available_schedule = integration_test_data["available_schedule"]
        assert available_schedule.status == ScheduleStatusEnum.AVAILABLE
        assert available_schedule.giver_id == 1

    def test_integration_client_fixture(self, integration_test_client):
        """測試整合測試客戶端 fixture。"""
        # GIVEN：使用整合測試客戶端（包含測試資料庫）

        # WHEN：呼叫健康檢查端點
        response = integration_test_client.get("/healthz")

        # THEN：確認客戶端正常運作
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_route_data_fixtures(
        self, sample_schedule_create_data, sample_schedule_update_data
    ):
        """測試路由資料 fixtures。"""
        # GIVEN：路由資料 fixtures

        # WHEN：檢查資料結構
        create_data = sample_schedule_create_data
        update_data = sample_schedule_update_data

        # THEN：確認資料格式正確
        assert "schedules" in create_data
        assert "created_by" in create_data
        assert "created_by_role" in create_data

        assert "schedule" in update_data
        assert "updated_by" in update_data
        assert "updated_by_role" in update_data

        # 驗證時段資料
        schedule = create_data["schedules"][0]
        assert schedule["giver_id"] == 1
        assert schedule["date"] == "2024-01-15"
        assert schedule["start_time"] == "09:00:00"
        assert schedule["end_time"] == "10:00:00"

    def test_error_data_fixtures(self, invalid_schedule_data, time_logic_error_data):
        """測試錯誤資料 fixtures。"""
        # GIVEN：錯誤資料 fixtures

        # WHEN：檢查錯誤資料
        invalid_data = invalid_schedule_data
        time_error_data = time_logic_error_data

        # THEN：確認錯誤資料格式
        # 無效資料應該缺少必要欄位
        schedule = invalid_data["schedules"][0]
        assert "date" not in schedule  # 缺少 date 欄位

        # 時間邏輯錯誤資料
        time_error_schedule = time_error_data["schedules"][0]
        assert time_error_schedule["start_time"] == "10:00:00"
        assert time_error_schedule["end_time"] == "09:00:00"  # 結束時間早於開始時間

    def test_query_params_fixtures(self, sample_query_params):
        """測試查詢參數 fixtures。"""
        # GIVEN：查詢參數 fixture

        # WHEN：檢查參數
        params = sample_query_params

        # THEN：確認參數格式正確
        assert params["giver_id"] == 1
        assert params["taker_id"] == 2
        assert params["status_filter"] == "AVAILABLE"

    def test_response_fixtures(self, sample_schedule_responses, sample_error_responses):
        """測試回應資料 fixtures。"""
        # GIVEN：回應資料 fixtures

        # WHEN：檢查回應資料
        success_responses = sample_schedule_responses
        error_responses = sample_error_responses

        # THEN：確認回應格式正確
        # 成功回應
        assert len(success_responses) == 2
        schedule = success_responses[0]
        assert "id" in schedule
        assert "giver_id" in schedule
        assert "status" in schedule

        # 錯誤回應
        assert "validation_error" in error_responses
        assert "business_logic_error" in error_responses
        assert "not_found_error" in error_responses

    def test_complete_integration_flow(
        self,
        integration_test_client,
        integration_test_data,
        sample_schedule_create_data,
        sample_schedule_update_data,
        sample_schedule_delete_data,
    ):
        """測試完整的整合流程。"""
        # GIVEN：所有必要的 fixtures 都已準備

        # 使用 set 確保時間唯一性
        import random

        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(19, 23)
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
                    "date": "2024-07-15",
                    "start_time": f"{time_key}:00",
                    "end_time": f"{hour:02d}:{minute+1:02d}:00",
                    "note": "唯一測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # WHEN：執行完整的時段管理流程

        # 1. 建立時段
        create_response = integration_test_client.post(
            "/api/v1/schedules", json=unique_schedule_data
        )

        # 2. 查詢時段列表
        list_response = integration_test_client.get("/api/v1/schedules")

        # 3. 取得單一時段
        get_response = integration_test_client.get("/api/v1/schedules/1")

        # 4. 更新時段
        update_response = integration_test_client.patch(
            "/api/v1/schedules/1", json=sample_schedule_update_data
        )

        # 5. 刪除時段
        import json

        delete_response = integration_test_client.request(
            "DELETE",
            "/api/v1/schedules/1",
            content=json.dumps(sample_schedule_delete_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認所有操作都成功
        assert create_response.status_code == status.HTTP_201_CREATED
        assert list_response.status_code == status.HTTP_200_OK
        assert get_response.status_code == status.HTTP_200_OK
        assert update_response.status_code == status.HTTP_200_OK
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    def test_fixtures_isolation(
        self, integration_db_session, integration_clean_database
    ):
        """測試 fixtures 隔離性。"""
        # GIVEN：資料庫會話和清理 fixture

        # WHEN：在測試中修改資料
        from app.models.user import User

        new_user = User(name="測試使用者", email="test@example.com")
        integration_db_session.add(new_user)
        integration_db_session.commit()

        # THEN：確認資料已加入
        users = integration_db_session.query(User).all()
        assert len(users) > 0

        # 清理 fixture 會在測試結束後自動執行
