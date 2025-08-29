"""Giver API 整合測試模組。

測試 Giver 相關的 API 端點。
"""

# ===== 標準函式庫 =====
from unittest.mock import patch

# ===== 第三方套件 =====
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.main import app
from tests.fixtures.test_data_givers import get_test_giver_by_id, get_test_givers

# 建立測試客戶端
client = TestClient(app)


class TestAPIGivers:
    """Giver API 測試類別。"""

    def test_get_givers_success(self):
        """測試成功取得 Giver 列表。"""
        with patch(
            'app.routers.api.givers.get_all_givers', return_value=get_test_givers()
        ):
            response = client.get("/api/v1/givers/")

            assert response.status_code == 200
            data = response.json()

            assert "results" in data
            assert "total_count" in data
            assert "page" in data
            assert "per_page" in data
            assert "total_pages" in data
            assert "has_next" in data
            assert "has_prev" in data

            assert len(data["results"]) == 2
            assert data["total_count"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 12

    def test_get_givers_with_pagination(self):
        """測試分頁功能。"""
        test_givers = get_test_givers()
        with patch('app.routers.api.givers.get_all_givers', return_value=test_givers):
            response = client.get("/api/v1/givers/?page=1&per_page=1")

            assert response.status_code == 200
            data = response.json()

            assert len(data["results"]) == 1
            assert data["total_count"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 1
            assert data["total_pages"] == 2
            assert data["has_next"] is True
            assert data["has_prev"] is False

    def test_get_giver_success(self):
        """測試成功取得特定 Giver。"""
        test_giver = get_test_giver_by_id(1)
        with patch('app.routers.api.givers.get_giver_by_id', return_value=test_giver):
            response = client.get("/api/v1/givers/1")

            assert response.status_code == 200
            data = response.json()

            assert data["id"] == 1
            assert data["name"] == "測試 Giver 1"
            assert data["title"] == "測試職位 1"

    def test_get_giver_not_found(self):
        """測試取得不存在的 Giver。"""
        with patch('app.routers.api.givers.get_giver_by_id', return_value=None):
            response = client.get("/api/v1/givers/999")

            assert response.status_code == 404
            data = response.json()
            assert "找不到 ID 為 999 的 Giver" in data["detail"]

    def test_get_givers_invalid_page(self):
        """測試無效的頁碼參數。"""
        response = client.get("/api/v1/givers/?page=0")

        assert response.status_code == 422

    def test_get_givers_invalid_per_page(self):
        """測試無效的每頁數量參數。"""
        response = client.get("/api/v1/givers/?per_page=0")

        assert response.status_code == 422
