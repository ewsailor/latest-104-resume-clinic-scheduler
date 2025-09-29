"""主要路由整合測試。

測試首頁路由的完整流程，包括 HTML 渲染和資料傳遞。
"""

from fastapi import status
from fastapi.testclient import TestClient

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.main import app


class TestMainRoutes:
    """主要路由整合測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    def test_index_page(self, client):
        """測試首頁路由是否正常回應"""
        # GIVEN: 準備測試客戶端

        # WHEN: 請求首頁路由
        response = client.get("/")

        # THEN: 驗證回應
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        # 檢查 HTML 內容包含關鍵元素
        html_content = response.text
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content

    def test_health_check(self, client):
        """測試健康檢查 API 是否正常回應"""
        # GIVEN: 準備測試客戶端

        # WHEN: 請求健康檢查端點
        response = client.get("/healthz")

        # THEN: 驗證回應
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_ready_check(self, client):
        """測試就緒檢查 API 是否正常回應"""
        # GIVEN: 準備測試客戶端

        # WHEN: 請求就緒檢查端點
        response = client.get("/readyz")

        # THEN: 驗證回應
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_root_not_found(self, client):
        """測試未知路由是否正確回傳 404"""
        # GIVEN: 準備測試客戶端

        # WHEN: 請求不存在的路由
        response = client.get("/unknown")

        # THEN: 驗證錯誤回應
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not Found"}

    def test_schedule_list_response(self, client):
        """測試 schedule API 回應格式正確"""
        # GIVEN: 準備測試客戶端

        # WHEN: 請求 schedule 列表 API
        response = client.get("/api/v1/schedules")

        # THEN: 驗證回應格式
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # 如果有資料，檢查必填欄位
        if data:
            schedule = data[0]
            # 檢查必填欄位
            required_fields = [
                "id",
                "giver_id",
                "date",
                "start_time",
                "end_time",
                "status",
                "created_at",
                "updated_at",
                "created_by_role",
                "updated_by_role",
            ]
            for field in required_fields:
                assert field in schedule, f"缺少必填欄位: {field}"
        else:
            # 無資料時確認返回空陣列
            assert data == []
