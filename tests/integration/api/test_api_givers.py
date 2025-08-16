"""
測試 app/routers/api/v1/givers.py 模組。

測試 Giver 相關的 API 端點，包括查詢、篩選和統計功能。
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.data.givers import MOCK_GIVERS
from app.main import app
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

    def test_get_givers_with_topic_filter(self):
        """測試根據服務項目篩選 Giver。"""
        log_test_info("測試根據服務項目篩選 Giver")

        # 執行測試
        response = client.get("/api/v1/givers?topic=履歷健診")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        assert len(data["results"]) > 0
        for giver in data["results"]:
            assert "履歷健診" in giver["giverCard__topic"]

    def test_get_givers_with_industry_filter(self):
        """測試根據產業篩選 Giver。"""
        log_test_info("測試根據產業篩選 Giver")

        # 執行測試
        response = client.get("/api/v1/givers?industry=電子資訊／軟體／半導體相關業")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果
        assert len(data["results"]) > 0
        for giver in data["results"]:
            assert giver["industry"] == "電子資訊／軟體／半導體相關業"

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

    def test_get_givers_by_topic_endpoint_success(self):
        """測試根據服務項目取得 Giver 列表端點。"""
        log_test_info("測試根據服務項目取得 Giver 列表端點")

        # 執行測試
        response = client.get("/api/v1/givers/topics/履歷健診")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證回應結構
        assert "results" in data
        assert "total" in data
        assert "topic" in data

        # 驗證資料
        assert data["topic"] == "履歷健診"
        assert len(data["results"]) > 0
        for giver in data["results"]:
            assert "履歷健診" in giver["giverCard__topic"]

    def test_get_givers_by_topic_endpoint_empty(self):
        """測試根據不存在的服務項目取得 Giver 列表。"""
        log_test_info("測試根據不存在的服務項目取得 Giver 列表")

        # 執行測試
        response = client.get("/api/v1/givers/topics/不存在的服務")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證資料
        assert data["topic"] == "不存在的服務"
        assert len(data["results"]) == 0
        assert data["total"] == 0

    def test_get_givers_by_industry_endpoint_success(self):
        """測試根據產業取得 Giver 列表端點。"""
        log_test_info("測試根據產業取得 Giver 列表端點")

        # 執行測試
        response = client.get("/api/v1/givers/industries/電子資訊／軟體／半導體相關業")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證回應結構
        assert "results" in data
        assert "total" in data
        assert "industry" in data

        # 驗證資料
        assert data["industry"] == "電子資訊／軟體／半導體相關業"
        assert len(data["results"]) > 0
        for giver in data["results"]:
            assert giver["industry"] == "電子資訊／軟體／半導體相關業"

    def test_get_givers_by_industry_endpoint_empty(self):
        """測試根據不存在的產業取得 Giver 列表。"""
        log_test_info("測試根據不存在的產業取得 Giver 列表")

        # 執行測試
        response = client.get("/api/v1/givers/industries/不存在的產業")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證資料
        assert data["industry"] == "不存在的產業"
        assert len(data["results"]) == 0
        assert data["total"] == 0

    def test_get_givers_count_endpoint_success(self):
        """測試取得 Giver 總數統計端點。"""
        log_test_info("測試取得 Giver 總數統計端點")

        # 執行測試
        response = client.get("/api/v1/givers/stats/count")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證回應結構
        assert "count" in data

        # 驗證資料
        assert data["count"] == len(MOCK_GIVERS)
        assert data["count"] > 0

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

    @patch('app.routers.api.givers.get_givers_by_topic')
    def test_get_givers_by_topic_exception_handling(self, mock_get_givers_by_topic):
        """測試根據服務項目篩選時的異常處理。"""
        log_test_info("測試根據服務項目篩選時的異常處理")

        # 模擬異常
        mock_get_givers_by_topic.side_effect = Exception("篩選錯誤")

        # 執行測試
        response = client.get("/api/v1/givers/topics/履歷健診")

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "根據服務項目篩選 Giver 失敗" in data["error"]["message"]

    @patch('app.routers.api.givers.get_givers_by_industry')
    def test_get_givers_by_industry_exception_handling(
        self, mock_get_givers_by_industry
    ):
        """測試根據產業篩選時的異常處理。"""
        log_test_info("測試根據產業篩選時的異常處理")

        # 模擬異常
        mock_get_givers_by_industry.side_effect = Exception("篩選錯誤")

        # 執行測試
        response = client.get("/api/v1/givers/industries/電子資訊／軟體／半導體相關業")

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "根據產業篩選 Giver 失敗" in data["error"]["message"]

    @patch('app.routers.api.givers.get_givers_count')
    def test_get_givers_count_exception_handling(self, mock_get_givers_count):
        """測試取得 Giver 統計時的異常處理。"""
        log_test_info("測試取得 Giver 統計時的異常處理")

        # 模擬異常
        mock_get_givers_count.side_effect = Exception("統計錯誤")

        # 執行測試
        response = client.get("/api/v1/givers/stats/count")

        # 驗證回應
        assert response.status_code == 500
        data = response.json()
        assert "取得 Giver 統計失敗" in data["error"]["message"]

    def test_get_givers_combined_filters(self):
        """測試組合篩選條件。"""
        log_test_info("測試組合篩選條件")

        # 執行測試 - 同時使用 topic 和 industry 篩選
        response = client.get(
            "/api/v1/givers?topic=履歷健診&industry=電子資訊／軟體／半導體相關業"
        )

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證篩選結果 - 當同時使用兩個篩選條件時，結果可能為空
        # 因為先根據 topic 篩選，再根據 industry 篩選
        # 由於沒有同時符合兩個條件的 Giver，結果應該為空
        assert len(data["results"]) == 0
        assert data["total"] == 0

    def test_get_givers_edge_cases(self):
        """測試邊界情況。"""
        log_test_info("測試邊界情況")

        # 測試非常大的頁碼
        response = client.get("/api/v1/givers?page=999999")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0

        # 測試空字串篩選
        response = client.get("/api/v1/givers?topic=")
        assert response.status_code == 200

        response = client.get("/api/v1/givers?industry=")
        assert response.status_code == 200

    def test_get_topics_endpoint(self):
        """測試取得所有服務項目列表端點。"""
        response = client.get("/api/v1/givers/topics")
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "description" in data

        # 檢查結果是列表
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)

        # 檢查是否有服務項目
        assert data["total"] > 0
        assert len(data["results"]) > 0

        # 檢查服務項目內容
        expected_topics = [
            "履歷健診",
            "模擬面試",
            "職業/產業經驗分享",
            "職涯諮詢",
            "英文履歷健診",
            "英文履歷面試",
        ]
        for topic in expected_topics:
            assert topic in data["results"]

    def test_get_industries_endpoint(self):
        """測試取得所有產業列表端點。"""
        response = client.get("/api/v1/givers/industries")
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "description" in data

        # 檢查結果是列表
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)

        # 檢查是否有產業
        assert data["total"] > 0
        assert len(data["results"]) > 0

        # 檢查產業內容（至少包含幾個已知的產業）
        expected_industries = [
            "電子資訊／軟體／半導體相關業",
            "金融投顧及保險業",
            "醫療保健及環境衛生業",
        ]
        for industry in expected_industries:
            assert industry in data["results"]
