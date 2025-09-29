"""主要路由整合測試。

測試首頁路由的完整流程，包括 HTML 渲染和資料傳遞。
"""

# ===== 標準函式庫 =====
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from jinja2.exceptions import TemplateNotFound

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.core.giver_data import MOCK_GIVERS
from app.main import app


class TestMainRoutes:
    """主要路由整合測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    def test_index_page_success(self, client):
        """測試首頁 - 成功。"""
        # GIVEN：應用程式正常運行

        # WHEN：訪問首頁
        response = client.get("/")

        # THEN：確認返回 HTML 頁面
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        # 驗證 HTML 內容包含預期元素
        html_content = response.text
        assert "<html" in html_content.lower()
        assert "<head" in html_content.lower()
        assert "<body" in html_content.lower()

    def test_index_page_with_givers_data(self, client):
        """測試首頁 - 包含 Giver 資料。"""
        # GIVEN：應用程式正常運行，包含 Giver 資料

        # WHEN：訪問首頁
        response = client.get("/")

        # THEN：確認頁面包含 Giver 資料
        assert response.status_code == status.HTTP_200_OK
        html_content = response.text

        # 驗證 Giver 資料是否正確傳遞到模板
        # 這裡可以根據實際的 HTML 模板內容進行驗證
        # 例如：檢查是否包含 Giver 的姓名、專業領域等資訊
        for giver in MOCK_GIVERS:
            if hasattr(giver, 'name'):
                assert (
                    giver.name in html_content
                    or giver.name.replace(' ', '&nbsp;') in html_content
                )

    def test_index_page_template_rendering(self, client):
        """測試首頁 - 模板渲染。"""
        # GIVEN：應用程式正常運行

        # WHEN：訪問首頁
        response = client.get("/")

        # THEN：確認模板正確渲染
        assert response.status_code == status.HTTP_200_OK
        html_content = response.text

        # 驗證基本 HTML 結構
        assert "<!DOCTYPE html>" in html_content or "<html" in html_content
        assert "</html>" in html_content

    def test_index_page_http_methods(self, client):
        """測試首頁 - HTTP 方法限制。"""
        # GIVEN：首頁路由

        # WHEN：使用不同的 HTTP 方法
        get_response = client.get("/")
        post_response = client.post("/")
        put_response = client.put("/")
        delete_response = client.delete("/")

        # THEN：確認只有 GET 方法被支援
        assert get_response.status_code == status.HTTP_200_OK
        assert post_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert put_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert delete_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_index_page_headers(self, client):
        """測試首頁 - HTTP 標頭。"""
        # GIVEN：應用程式正常運行

        # WHEN：訪問首頁
        response = client.get("/")

        # THEN：確認 HTTP 標頭正確
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        # 驗證其他重要的 HTTP 標頭
        assert "content-length" in response.headers
        assert int(response.headers["content-length"]) > 0

    def test_index_page_with_template_error(self, client):
        """測試首頁 - 模板錯誤處理。"""
        # GIVEN：模擬模板渲染錯誤
        with patch(
            'fastapi.templating.Jinja2Templates.TemplateResponse'
        ) as mock_template:
            mock_template.side_effect = Exception("Template rendering error")

            # WHEN：訪問首頁
            response = client.get("/")

            # THEN：確認錯誤被正確處理
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_index_page_with_missing_template(self, client):
        """測試首頁 - 缺少模板檔案。"""
        # GIVEN：模擬缺少模板檔案
        with patch(
            'fastapi.templating.Jinja2Templates.TemplateResponse'
        ) as mock_template:
            mock_template.side_effect = TemplateNotFound("giver_list.html")

            # WHEN：訪問首頁
            response = client.get("/")

            # THEN：確認錯誤被正確處理
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_index_page_performance(self, client):
        """測試首頁 - 效能測試。"""
        # GIVEN：應用程式正常運行

        # WHEN：多次訪問首頁
        responses = []
        for _ in range(5):
            response = client.get("/")
            responses.append(response)

        # THEN：確認所有請求都成功
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "text/html; charset=utf-8"

    def test_index_page_with_different_accept_headers(self, client):
        """測試首頁 - 不同的 Accept 標頭。"""
        # GIVEN：應用程式正常運行

        # WHEN：使用不同的 Accept 標頭訪問首頁
        html_response = client.get("/", headers={"Accept": "text/html"})
        json_response = client.get("/", headers={"Accept": "application/json"})
        all_response = client.get("/", headers={"Accept": "*/*"})

        # THEN：確認所有請求都返回 HTML 內容
        assert html_response.status_code == status.HTTP_200_OK
        assert html_response.headers["content-type"] == "text/html; charset=utf-8"

        assert json_response.status_code == status.HTTP_200_OK
        assert json_response.headers["content-type"] == "text/html; charset=utf-8"

        assert all_response.status_code == status.HTTP_200_OK
        assert all_response.headers["content-type"] == "text/html; charset=utf-8"

    def test_index_page_redirect_handling(self, client):
        """測試首頁 - 重定向處理。"""
        # GIVEN：應用程式正常運行

        # WHEN：訪問首頁（可能的重定向情況）
        response = client.get("/", follow_redirects=True)

        # THEN：確認最終返回正確的頁面
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/html; charset=utf-8"
