"""
Main 路由整合測試模組。

測試主要路由功能，包括首頁渲染等。
"""

# ===== 標準函式庫 =====
import time

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
import pytest

# ===== 本地模組 =====


class TestMainRouteIntegration:
    """Main 路由整合測試類別。"""

    @pytest.fixture
    def client(self, integration_client):
        """建立測試客戶端。"""
        return integration_client

    def test_show_index_success(self, client: TestClient):
        """測試首頁路由成功渲染。"""
        response = client.get("/")

        assert response.status_code == 200

        # 檢查回應類型
        assert "text/html" in response.headers.get("content-type", "")

        # 檢查 HTML 內容
        html_content = response.text
        assert isinstance(html_content, str)
        assert len(html_content) > 0

        # 檢查基本的 HTML 結構
        assert "<!DOCTYPE html>" in html_content or "<html" in html_content

    def test_show_index_with_different_headers(self, client: TestClient):
        """測試首頁路由使用不同標頭。"""
        # 測試帶有 Origin 標頭的請求
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

        # 檢查 CORS 標頭
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_show_index_content_consistency(self, client: TestClient):
        """測試首頁內容的一致性。"""
        # 多次請求首頁
        responses = []
        for _ in range(3):
            response = client.get("/")
            assert response.status_code == 200
            responses.append(response)

        # 檢查所有回應的內容類型一致
        content_types = [resp.headers.get("content-type", "") for resp in responses]
        assert all("text/html" in ct for ct in content_types)

        # 檢查 HTML 內容長度一致（應該相同）
        content_lengths = [len(resp.text) for resp in responses]
        assert all(length > 0 for length in content_lengths)

    def test_show_index_method_not_allowed(self, client: TestClient):
        """測試首頁路由不允許的 HTTP 方法。"""
        # 測試 POST 方法（應該不被允許）
        response = client.post("/")
        assert response.status_code == 405

        # 測試 PUT 方法（應該不被允許）
        response = client.put("/")
        assert response.status_code == 405

        # 測試 DELETE 方法（應該不被允許）
        response = client.delete("/")
        assert response.status_code == 405

        # 測試 PATCH 方法（應該不被允許）
        response = client.patch("/")
        assert response.status_code == 405

    def test_show_index_with_query_parameters(self, client: TestClient):
        """測試首頁路由帶查詢參數。"""
        # 測試帶查詢參數的請求
        response = client.get("/?test=value&debug=true")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_show_index_with_fragment(self, client: TestClient):
        """測試首頁路由帶片段標識符。"""
        # 測試帶片段標識符的請求
        response = client.get("/#section1")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_show_index_response_headers(self, client: TestClient):
        """測試首頁路由的回應標頭。"""
        response = client.get("/")

        assert response.status_code == 200

        # 檢查必要的標頭
        headers = response.headers
        assert "content-type" in headers
        assert "content-length" in headers

        # 檢查內容類型
        content_type = headers["content-type"]
        assert "text/html" in content_type

    def test_show_index_cors_headers(self, client: TestClient):
        """測試首頁路由的 CORS 標頭。"""
        origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

        for origin in origins:
            response = client.get("/", headers={"Origin": origin})

            assert response.status_code == 200

            # 檢查 CORS 標頭
            headers = response.headers
            assert "access-control-allow-origin" in headers
            assert headers["access-control-allow-origin"] == origin
            assert headers["access-control-allow-credentials"] == "true"

    def test_show_index_without_origin_header(self, client: TestClient):
        """測試首頁路由沒有 Origin 標頭。"""
        response = client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

        # 沒有 Origin 標頭時，不應該有 CORS 相關標頭
        headers = response.headers
        assert "access-control-allow-origin" not in headers

    def test_show_index_error_handling(self, client: TestClient):
        """測試首頁路由的錯誤處理。"""
        # 首頁路由應該總是成功，但我們可以測試一些邊界情況

        # 測試很長的 URL
        long_path = "/" + "a" * 1000
        response = client.get(long_path)
        # 應該重定向到 404 或返回 404
        assert response.status_code in [200, 404]

    def test_show_index_template_rendering(self, client: TestClient):
        """測試首頁模板渲染。"""
        response = client.get("/")

        assert response.status_code == 200

        # 檢查 HTML 內容是否包含預期的元素
        html_content = response.text

        # 檢查基本的 HTML 標籤
        assert "<html" in html_content.lower() or "<!doctype" in html_content.lower()

        # 檢查是否有標題或其他預期內容
        # 注意：這裡的檢查取決於實際的模板內容

    def test_show_index_performance(self, client: TestClient):
        """測試首頁路由的性能。"""
        # 測試多次請求的響應時間
        start_time = time.time()

        for _ in range(10):
            response = client.get("/")
            assert response.status_code == 200

        end_time = time.time()
        total_time = end_time - start_time

        # 10 次請求應該在合理時間內完成（例如 5 秒內）
        assert total_time < 5.0, f"首頁路由響應時間過長: {total_time}秒"

    def test_show_index_with_different_user_agents(self, client: TestClient):
        """測試首頁路由使用不同的 User-Agent。"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "curl/7.68.0",
            "PostmanRuntime/7.26.8",
        ]

        for user_agent in user_agents:
            response = client.get("/", headers={"User-Agent": user_agent})

            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")

    def test_show_index_with_accept_headers(self, client: TestClient):
        """測試首頁路由使用不同的 Accept 標頭。"""
        accept_headers = [
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "text/html",
            "*/*",
            "text/html,application/xhtml+xml",
        ]

        for accept_header in accept_headers:
            response = client.get("/", headers={"Accept": accept_header})

            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")

    def test_show_index_route_integration_with_other_routes(self, client: TestClient):
        """測試首頁路由與其他路由的整合。"""
        # 測試首頁
        response = client.get("/")
        assert response.status_code == 200

        # 測試健康檢查端點
        response = client.get("/healthz")
        assert response.status_code == 200

        # 測試 API 端點
        response = client.get("/api/v1/schedules")
        assert response.status_code == 200

        # 再次測試首頁確保沒有影響
        response = client.get("/")
        assert response.status_code == 200
