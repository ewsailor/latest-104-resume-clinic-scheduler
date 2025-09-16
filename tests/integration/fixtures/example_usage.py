"""
整合測試 Fixtures 使用範例。

展示如何使用整合測試 fixtures 進行測試。
"""

# ===== 第三方套件 =====
import pytest  # 測試框架

# ===== 本地模組 =====
from app.models.schedule import Schedule
from app.models.user import User


class TestIntegrationFixturesExample:
    """整合測試 Fixtures 使用範例測試類別。"""

    def test_database_fixtures_example(
        self, integration_db_engine, integration_db_session
    ):
        """測試資料庫 fixtures 的使用。"""
        # 測試資料庫引擎和會話是否正常工作
        assert integration_db_engine is not None
        assert integration_db_session is not None

        # 測試基本的資料庫操作
        user = User(name="測試使用者", email="test@example.com")
        integration_db_session.add(user)
        integration_db_session.commit()
        integration_db_session.refresh(user)

        assert user.id is not None
        assert user.name == "測試使用者"

    def test_service_fixtures_example(
        self, schedule_service, schedule_service_with_session
    ):
        """測試服務 fixtures 的使用。"""
        # 測試服務實例是否正常創建
        assert schedule_service is not None
        assert schedule_service_with_session is not None

    def test_api_fixtures_example(self, integration_app, integration_client):
        """測試 API fixtures 的使用。"""
        # 測試應用程式和客戶端是否正常創建
        assert integration_app is not None
        assert integration_client is not None

        # 測試 API 端點是否可訪問
        response = integration_client.get("/healthz")
        assert response.status_code in [200, 404]  # 404 如果路由不存在

    def test_test_data_fixtures_example(
        self, sample_users_data, sample_schedule_data, sample_users, sample_schedules
    ):
        """測試測試資料 fixtures 的使用。"""
        # 測試資料 fixtures
        assert len(sample_users_data) == 3
        assert "giver" in sample_schedule_data
        assert "giver" in sample_users
        assert len(sample_schedules) == 3

        # 測試實際物件
        giver_user = sample_users["giver"]
        assert giver_user.id is not None
        assert giver_user.name == "Giver 使用者"

        first_schedule = sample_schedules[0]
        assert first_schedule.id is not None
        assert first_schedule.giver_id == 1

    def test_complex_integration_example(
        self,
        integration_db_session,
        schedule_service,
        sample_users,
        sample_schedule_data,
    ):
        """測試複雜的整合場景。"""
        # 使用多個 fixtures 進行複雜的整合測試
        giver_user = sample_users["giver"]

        # 建立時段
        schedule_data = sample_schedule_data.copy()
        schedule_data["giver_id"] = giver_user.id

        schedule = Schedule(**schedule_data)
        integration_db_session.add(schedule)
        integration_db_session.commit()
        integration_db_session.refresh(schedule)

        # 驗證結果
        assert schedule.id is not None
        assert schedule.giver_id == giver_user.id

        # 測試服務層功能
        retrieved_schedule = schedule_service.get_schedule_by_id(
            integration_db_session, schedule.id
        )
        assert retrieved_schedule is not None
        assert retrieved_schedule.id == schedule.id
