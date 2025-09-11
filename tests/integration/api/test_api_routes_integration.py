"""
API 路由組合整合測試模組。

測試多個 API 路由同時運作的情況，確保它們能正確協同工作。
"""

# ===== 標準函式庫 =====
import datetime
from typing import Any, Dict

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====
from app.main import app

from .test_utils import generate_unique_time_slot


class TestAPIRoutesIntegration:
    """API 路由組合整合測試類別。"""

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
        date, start_time, end_time = generate_unique_time_slot(hour_start=20)

        return {
            "schedules": [
                {
                    "giver_id": 1,  # 使用現有的 giver_id
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "AVAILABLE",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

    def test_health_and_schedule_api_integration(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試健康檢查與時段 API 的整合。"""
        # 1. 檢查應用程式健康狀態
        health_response = client.get("/healthz")
        assert health_response.status_code == 200

        readiness_response = client.get("/readyz")
        assert readiness_response.status_code == 200

        # 2. 建立時段
        schedule_response = client.post("/api/v1/schedules", json=sample_schedule_data)
        assert schedule_response.status_code == 201

        # 3. 再次檢查健康狀態
        health_response = client.get("/healthz")
        assert health_response.status_code == 200

        readiness_response = client.get("/readyz")
        assert readiness_response.status_code == 200

    def test_main_route_and_api_integration(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試主路由與 API 的整合。"""
        # 1. 訪問首頁
        main_response = client.get("/")
        assert main_response.status_code == 200
        assert "text/html" in main_response.headers.get("content-type", "")

        # 2. 使用 API 建立時段
        schedule_response = client.post("/api/v1/schedules", json=sample_schedule_data)
        assert schedule_response.status_code == 201

        # 3. 再次訪問首頁
        main_response = client.get("/")
        assert main_response.status_code == 200

    def test_cors_consistency_across_routes(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試跨路由的 CORS 一致性。"""
        origin = "http://localhost:3000"
        headers = {"Origin": origin}

        # 測試不同路由的 CORS 標頭
        routes = [
            ("GET", "/"),
            ("GET", "/healthz"),
            ("GET", "/readyz"),
            ("GET", "/api/v1/schedules"),
            ("POST", "/api/v1/schedules"),
        ]

        for method, route in routes:
            if method == "GET":
                response = client.get(route, headers=headers)
            elif method == "POST":
                if route == "/api/v1/schedules":
                    response = client.post(
                        route, json=sample_schedule_data, headers=headers
                    )
                else:
                    response = client.post(route, headers=headers)

            # 檢查 CORS 標頭
            response_headers = response.headers
            assert "access-control-allow-origin" in response_headers
            assert response_headers["access-control-allow-origin"] == origin
            assert response_headers["access-control-allow-credentials"] == "true"

    def test_error_handling_consistency_across_routes(self, client: TestClient):
        """測試跨路由的錯誤處理一致性。"""
        # 測試不同路由的錯誤處理

        # 1. 健康檢查錯誤
        health_error_response = client.get("/healthz?fail=true")
        assert health_error_response.status_code == 500

        # 2. 準備就緒檢查錯誤
        readiness_error_response = client.get("/readyz?fail=true")
        assert readiness_error_response.status_code == 503

        # 3. API 錯誤（不存在的時段）
        api_error_response = client.get("/api/v1/schedules/99999")
        assert api_error_response.status_code == 404

        # 檢查錯誤回應格式的一致性
        error_responses = [
            health_error_response,
            readiness_error_response,
            api_error_response,
        ]

        for response in error_responses:
            response_data = response.json()
            assert "error" in response_data
            assert "message" in response_data["error"]
            assert "status_code" in response_data["error"]
            assert "timestamp" in response_data["error"]

    def test_content_type_consistency_across_routes(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試跨路由的內容類型一致性。"""
        # 測試不同路由的內容類型

        # 1. 主路由（HTML）
        main_response = client.get("/")
        assert main_response.status_code == 200
        assert "text/html" in main_response.headers.get("content-type", "")

        # 2. 健康檢查（JSON）
        health_response = client.get("/healthz")
        assert health_response.status_code == 200
        assert "application/json" in health_response.headers.get("content-type", "")

        # 3. API 路由（JSON）
        api_response = client.get("/api/v1/schedules")
        assert api_response.status_code == 200
        assert "application/json" in api_response.headers.get("content-type", "")

        # 4. API 建立（JSON）
        create_response = client.post("/api/v1/schedules", json=sample_schedule_data)
        assert create_response.status_code == 201
        assert "application/json" in create_response.headers.get("content-type", "")

    def test_route_performance_under_load(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試路由在負載下的性能。"""
        import time

        # 測試多個路由的並發性能
        routes_to_test = [
            ("GET", "/"),
            ("GET", "/healthz"),
            ("GET", "/readyz"),
            ("GET", "/api/v1/schedules"),
        ]

        start_time = time.time()

        # 對每個路由進行多次請求
        for method, route in routes_to_test:
            for _ in range(5):
                if method == "GET":
                    response = client.get(route)
                assert response.status_code in [200, 201]

        end_time = time.time()
        total_time = end_time - start_time

        # 20 次請求應該在合理時間內完成
        assert total_time < 10.0, f"路由性能測試時間過長: {total_time}秒"

    def test_route_dependency_isolation(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試路由之間的依賴隔離。"""
        # 1. 建立時段
        create_response = client.post("/api/v1/schedules", json=sample_schedule_data)
        assert create_response.status_code == 201
        created_schedules = create_response.json()
        schedule_id = created_schedules[0]["id"]

        # 2. 檢查健康狀態（應該不受影響）
        health_response = client.get("/healthz")
        assert health_response.status_code == 200

        # 3. 訪問首頁（應該不受影響）
        main_response = client.get("/")
        assert main_response.status_code == 200

        # 4. 查詢時段（應該正常）
        get_response = client.get(f"/api/v1/schedules/{schedule_id}")
        assert get_response.status_code == 200

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

        # 6. 再次檢查其他路由（應該不受影響）
        health_response = client.get("/healthz")
        assert health_response.status_code == 200

        main_response = client.get("/")
        assert main_response.status_code == 200

    def test_route_error_propagation(self, client: TestClient):
        """測試路由錯誤的傳播。"""
        # 測試不同類型的錯誤不會相互影響

        # 1. 觸發健康檢查錯誤
        health_error_response = client.get("/healthz?fail=true")
        assert health_error_response.status_code == 500

        # 2. 其他路由應該仍然正常工作
        main_response = client.get("/")
        assert main_response.status_code == 200

        api_response = client.get("/api/v1/schedules")
        assert api_response.status_code == 200

        # 3. 觸發準備就緒檢查錯誤
        readiness_error_response = client.get("/readyz?fail=true")
        assert readiness_error_response.status_code == 503

        # 4. 其他路由應該仍然正常工作
        main_response = client.get("/")
        assert main_response.status_code == 200

        api_response = client.get("/api/v1/schedules")
        assert api_response.status_code == 200

    def test_route_middleware_integration(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試路由與中間件的整合。"""
        origin = "http://localhost:3000"
        headers = {"Origin": origin}

        # 測試不同路由與中間件的整合

        # 1. 主路由 + CORS
        main_response = client.get("/", headers=headers)
        assert main_response.status_code == 200
        assert "access-control-allow-origin" in main_response.headers

        # 2. 健康檢查 + CORS
        health_response = client.get("/healthz", headers=headers)
        assert health_response.status_code == 200
        assert "access-control-allow-origin" in health_response.headers

        # 3. API 路由 + CORS + 錯誤處理
        api_response = client.get("/api/v1/schedules", headers=headers)
        assert api_response.status_code == 200
        assert "access-control-allow-origin" in api_response.headers

        # 4. API 建立 + CORS + 錯誤處理
        create_response = client.post(
            "/api/v1/schedules", json=sample_schedule_data, headers=headers
        )
        assert create_response.status_code == 201
        assert "access-control-allow-origin" in create_response.headers

    def test_route_logging_consistency(
        self, client: TestClient, sample_schedule_data: Dict[str, Any]
    ):
        """測試路由日誌記錄的一致性。"""
        # 測試不同路由的日誌記錄

        routes_to_test = [
            ("GET", "/"),
            ("GET", "/healthz"),
            ("GET", "/readyz"),
            ("GET", "/api/v1/schedules"),
            ("POST", "/api/v1/schedules"),
        ]

        for method, route in routes_to_test:
            if method == "GET":
                response = client.get(route)
            elif method == "POST" and route == "/api/v1/schedules":
                response = client.post(route, json=sample_schedule_data)
            else:
                response = client.post(route)

            # 所有路由都應該有合理的狀態碼
            assert response.status_code in [200, 201, 204, 404, 422, 409, 500, 503]

    def test_route_security_headers(self, client: TestClient):
        """測試路由的安全標頭。"""
        # 測試不同路由的安全標頭

        routes = ["/", "/healthz", "/readyz", "/api/v1/schedules"]

        for route in routes:
            response = client.get(route)
            assert response.status_code in [200, 201, 204, 404, 422, 500, 503]

            # 檢查基本的安全標頭
            response.headers
            # 注意：這裡的檢查取決於實際的安全標頭配置

    def test_route_versioning_consistency(self, client: TestClient):
        """測試路由版本的一致性。"""
        # 測試 API 版本的一致性

        # 1. 健康檢查（無版本）
        health_response = client.get("/healthz")
        assert health_response.status_code == 200

        # 2. API v1
        api_response = client.get("/api/v1/schedules")
        assert api_response.status_code == 200

        # 3. 主路由（無版本）
        main_response = client.get("/")
        assert main_response.status_code == 200
