"""
測試 app/data/givers.py 模組。

測試 Giver 資料相關的功能，包括查詢、篩選和統計功能。
"""

# ===== 本地模組 =====
from app.routers.api.givers import (
    MOCK_GIVERS,
    get_all_givers,
    get_giver_by_id,
)
from tests.logger import log_test_info


class TestGiversData:
    """測試 Giver 資料模組的功能。"""

    def test_get_all_givers(self):
        """測試取得所有 Giver 資料。"""
        log_test_info("測試取得所有 Giver 資料")

        # 執行測試
        result = get_all_givers()

        # 驗證結果
        assert isinstance(result, list)
        assert len(result) > 0
        assert result == MOCK_GIVERS

        # 驗證每個 Giver 都有必要的欄位
        for giver in result:
            assert "id" in giver
            assert "name" in giver
            assert "title" in giver
            assert "company" in giver
            assert "giverCard__topic" in giver

    def test_get_giver_by_id_existing(self):
        """測試根據 ID 取得存在的 Giver。"""
        log_test_info("測試根據 ID 取得存在的 Giver")

        # 測試取得第一個 Giver
        giver_id = 1
        result = get_giver_by_id(giver_id)

        # 驗證結果
        assert result is not None
        assert result["id"] == giver_id
        assert result["name"] == "王零一"
        assert result["title"] == "Python 工程師"

    def test_get_giver_by_id_not_existing(self):
        """測試根據 ID 取得不存在的 Giver。"""
        log_test_info("測試根據 ID 取得不存在的 Giver")

        # 測試取得不存在的 Giver
        giver_id = 999
        result = get_giver_by_id(giver_id)

        # 驗證結果
        assert result is None

    def test_mock_givers_data_structure(self):
        """測試 MOCK_GIVERS 資料結構的完整性。"""
        log_test_info("測試 MOCK_GIVERS 資料結構的完整性")

        # 驗證 MOCK_GIVERS 的基本結構
        assert isinstance(MOCK_GIVERS, list)
        assert len(MOCK_GIVERS) > 0

        # 驗證每個 Giver 的資料結構
        for i, giver in enumerate(MOCK_GIVERS):
            assert isinstance(giver, dict), f"Giver {i} 應該是字典"
            assert "id" in giver, f"Giver {i} 缺少 id 欄位"
            assert "name" in giver, f"Giver {i} 缺少 name 欄位"
            assert "title" in giver, f"Giver {i} 缺少 title 欄位"
            assert "company" in giver, f"Giver {i} 缺少 company 欄位"
            assert "giverCard__topic" in giver, f"Giver {i} 缺少 giverCard__topic 欄位"

            # 驗證 giverCard__topic 是列表
            assert isinstance(
                giver["giverCard__topic"], list
            ), f"Giver {i} 的 giverCard__topic 應該是列表"

    def test_giver_ids_unique(self):
        """測試所有 Giver ID 都是唯一的。"""
        log_test_info("測試所有 Giver ID 都是唯一的")

        # 取得所有 ID
        ids = [giver["id"] for giver in MOCK_GIVERS]

        # 驗證 ID 唯一性
        assert len(ids) == len(set(ids)), "所有 Giver ID 應該是唯一的"

    def test_giver_topics_consistency(self):
        """測試 Giver 服務項目的一致性。"""
        log_test_info("測試 Giver 服務項目的一致性")

        # 收集所有服務項目
        all_topics = set()
        for giver in MOCK_GIVERS:
            all_topics.update(giver["giverCard__topic"])

        # 驗證服務項目不為空
        assert len(all_topics) > 0, "應該有至少一個服務項目"

        # 驗證常見的服務項目存在
        expected_topics = ["履歷健診", "模擬面試", "職涯諮詢", "英文履歷健診"]
        for topic in expected_topics:
            assert topic in all_topics, f"服務項目 '{topic}' 應該存在"
