"""
測試 app/routers/api/v1/givers.py 模組。

測試 Giver 相關的 API 端點，包括查詢、篩選和統計功能。
"""

# ===== 標準函式庫 =====
from unittest.mock import patch

# ===== 第三方套件 =====
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.main import app
from app.routers.api.givers import MOCK_GIVERS
from tests.logger import log_test_info

# 建立測試客戶端
client = TestClient(app)


class TestGiversAPI:
    """測試 Giver API 端點。"""

    def test_get_givers_success(self):
        """測試成功取得 Giver 列表。"""
        log_test_info("測試成功取得 Giver 列表")

        # 執行測試
        response = client.get("/api/v1/givers")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證回應結構
        assert "results" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data

        # 驗證資料
        assert isinstance(data["results"], list)
        assert data["total"] == len(MOCK_GIVERS)
        assert data["page"] == 1
        assert data["per_page"] == 12

    def test_get_givers_with_pagination(self):
        """測試分頁功能。"""
        log_test_info("測試分頁功能")

        # 執行測試
        response = client.get("/api/v1/givers?page=2&per_page=5")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證分頁參數
        assert data["page"] == 2
        assert data["per_page"] == 5
        assert len(data["results"]) <= 5

    def test_get_givers_with_invalid_page(self):
        """測試無效的頁碼參數。"""
        log_test_info("測試無效的頁碼參數")

        # 執行測試
        response = client.get("/api/v1/givers?page=0")

        # 驗證回應
        assert response.status_code == 422  # Validation error

    def test_get_givers_with_invalid_per_page(self):
        """測試無效的每頁數量參數。"""
        log_test_info("測試無效的每頁數量參數")

        # 執行測試
        response = client.get("/api/v1/givers?per_page=0")

        # 驗證回應
        assert response.status_code == 422  # Validation error

    def test_get_givers_with_large_per_page(self):
        """測試超過限制的每頁數量參數。"""
        log_test_info("測試超過限制的每頁數量參數")

        # 執行測試
        response = client.get("/api/v1/givers?per_page=101")

        # 驗證回應
        assert response.status_code == 422  # Validation error

    def test_get_giver_by_id_success(self):
        """測試成功根據 ID 取得 Giver。"""
        log_test_info("測試成功根據 ID 取得 Giver")

        # 執行測試
        response = client.get("/api/v1/givers/1")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證資料
        assert data["id"] == 1
        assert data["name"] == "王零一"
        assert data["title"] == "Python 工程師"

    def test_get_giver_by_id_not_found(self):
        """測試取得不存在的 Giver。"""
        log_test_info("測試取得不存在的 Giver")

        # 執行測試
        response = client.get("/api/v1/givers/999")

        # 驗證回應
        assert response.status_code == 404
        data = response.json()
        assert "找不到 ID 為 999 的 Giver" in data["error"]["message"]

    @patch('app.routers.api.givers.get_all_givers')
    def test_get_givers_exception_handling(self, mock_get_all_givers):
        """測試取得 Giver 列表時的異常處理。"""
        log_test_info("測試取得 Giver 列表時的異常處理")

        # 模擬異常
        mock_get_all_givers.side_effect = Exception("資料庫錯誤")

        # 執行測試
        response = client.get("/api/v1/givers")

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "取得 Giver 列表失敗" in data["error"]["message"]

    @patch('app.routers.api.givers.get_giver_by_id')
    def test_get_giver_exception_handling(self, mock_get_giver_by_id):
        """測試取得單一 Giver 時的異常處理。"""
        log_test_info("測試取得單一 Giver 時的異常處理")

        # 模擬異常
        mock_get_giver_by_id.side_effect = Exception("資料庫錯誤")

        # 執行測試
        response = client.get("/api/v1/givers/1")

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "取得 Giver 資料失敗" in data["error"]["message"]
