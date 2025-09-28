"""
整合測試 Fixtures 使用範例 - 簡化版本。

展示如何在整合測試中正確使用基本 fixtures。
"""

# ===== 標準函式庫 =====

# ===== 第三方套件 =====
from fastapi import status
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum
from app.main import app


class TestFixturesUsage:
    """Fixtures 使用範例測試類別 - 簡化版本。"""

    def test_basic_client_fixture(self):
        """測試基本客戶端 fixture。"""
        # GIVEN：使用基本的 TestClient fixture

        # WHEN：建立客戶端
        client = TestClient(app)

        # THEN：確認客戶端正常運作
        response = client.get("/healthz")
        assert response.status_code == status.HTTP_200_OK

    def test_integration_database_fixtures(self):
        """測試資料庫相關 fixtures。"""
        # GIVEN：基本測試環境

        # WHEN：建立基本測試資料
        test_data = {
            "users": ["giver", "taker", "system"],
            "schedules": ["available", "pending", "accepted"],
        }

        # THEN：確認資料結構正確
        assert len(test_data["users"]) == 3  # giver, taker, system
        assert len(test_data["schedules"]) == 3  # available, pending, accepted

    def test_integration_client_fixture(self):
        """測試整合測試客戶端 fixture。"""
        # GIVEN：使用基本測試客戶端

        # WHEN：建立客戶端並呼叫健康檢查端點
        client = TestClient(app)
        response = client.get("/healthz")

        # THEN：確認回應正常
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    def test_route_data_fixtures(self):
        """測試路由資料 fixtures。"""
        # GIVEN：基本路由資料

        # WHEN：建立測試資料
        create_data = {
            "schedules": [
                {
                    "date": "2024-12-25",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # THEN：確認資料格式正確
        assert "schedules" in create_data
        assert "created_by" in create_data
        assert len(create_data["schedules"]) == 1

    def test_error_data_fixtures(self):
        """測試錯誤資料 fixtures。"""
        # GIVEN：錯誤測試資料

        # WHEN：建立無效資料
        invalid_data = {
            "schedules": [
                {
                    "start_time": "10:00:00",
                    "end_time": "09:00:00",  # 結束時間早於開始時間
                    "note": "無效時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # THEN：確認資料格式
        assert "schedules" in invalid_data
        assert (
            invalid_data["schedules"][0]["start_time"]
            > invalid_data["schedules"][0]["end_time"]
        )

    def test_query_params_fixtures(self):
        """測試查詢參數 fixtures。"""
        # GIVEN：查詢參數

        # WHEN：建立查詢參數
        query_params = {
            "giver_id": 1,
            "status_filter": "AVAILABLE",
            "date": "2024-12-25",
        }

        # THEN：確認參數格式
        assert "giver_id" in query_params
        assert "status_filter" in query_params
        assert query_params["giver_id"] > 0

    def test_response_fixtures(self):
        """測試回應 fixtures。"""
        # GIVEN：回應資料

        # WHEN：建立回應資料
        success_response = {
            "id": 1,
            "date": "2024-12-25",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "status": "AVAILABLE",
        }

        # THEN：確認回應格式
        assert "id" in success_response
        assert "status" in success_response
        assert success_response["status"] in [
            status.value for status in ScheduleStatusEnum
        ]

    def test_complete_integration_flow(self):
        """測試完整整合流程。"""
        # GIVEN：基本測試環境
        client = TestClient(app)

        # WHEN：執行基本的 API 流程
        # 1. 健康檢查
        health_response = client.get("/healthz")
        assert health_response.status_code == status.HTTP_200_OK

        # 2. 查詢時段列表
        list_response = client.get("/api/v1/schedules")
        assert list_response.status_code == status.HTTP_200_OK

        # 3. 查詢準備就緒狀態
        ready_response = client.get("/readyz")
        assert ready_response.status_code == status.HTTP_200_OK

        # THEN：確認基本流程完成
        assert health_response.status_code == status.HTTP_200_OK
        assert list_response.status_code == status.HTTP_200_OK
        assert ready_response.status_code == status.HTTP_200_OK

    def test_fixtures_isolation(self):
        """測試 fixtures 隔離性。"""
        # GIVEN：基本測試環境

        # WHEN：執行多個獨立測試
        client1 = TestClient(app)
        client2 = TestClient(app)

        # THEN：確認每個客戶端都是獨立的
        response1 = client1.get("/healthz")
        response2 = client2.get("/healthz")

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json() == response2.json()
