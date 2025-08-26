"""
測試 app/routers/api/v1/users.py 模組。

測試使用者相關的 API 端點，包括查詢和建立功能。
"""

# ===== 標準函式庫 =====
import time
from unittest.mock import patch

# ===== 第三方套件 =====
from fastapi.testclient import TestClient

# ===== 本地模組 =====
from app.main import app

# 建立測試客戶端
client = TestClient(app)


class TestUsersAPI:
    """測試使用者 API 端點。"""

    def test_get_users_success(self):
        """測試成功取得使用者列表。"""
        response = client.get("/api/v1/users")
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data

        # 檢查結果是列表
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)
        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_get_users_with_pagination(self):
        """測試分頁功能。"""
        response = client.get("/api/v1/users?page=1&per_page=3")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 3
        assert len(data["results"]) <= 3

    def test_get_users_with_invalid_page(self):
        """測試無效的頁碼參數。"""
        response = client.get("/api/v1/users?page=0")
        assert response.status_code == 422  # Validation error

    def test_get_users_with_invalid_per_page(self):
        """測試無效的每頁數量參數。"""
        response = client.get("/api/v1/users?per_page=0")
        assert response.status_code == 422  # Validation error

    def test_get_users_with_large_per_page(self):
        """測試超過限制的每頁數量參數。"""
        response = client.get("/api/v1/users?per_page=101")
        assert response.status_code == 422  # Validation error

    @patch('app.routers.api.users.user_crud.get_users')
    def test_get_users_exception_handling(self, mock_get_users):
        """測試異常處理。"""
        # 模擬異常
        mock_get_users.side_effect = Exception("資料庫錯誤")

        # 執行測試
        response = client.get("/api/v1/users")

        # 驗證回應 - 修正：使用 error.message 欄位
        assert response.status_code == 500
        data = response.json()
        assert "取得使用者列表失敗" in data["error"]["message"]

    def test_create_user_success(self):
        """測試成功建立使用者。"""
        # 使用時間戳來確保每次測試都使用唯一的 email
        timestamp = int(time.time())
        user_data = {
            "name": "測試使用者",
            "email": f"unique_test_user_{timestamp}@example.com",
        }

        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert "message" in data
        assert "user" in data
        assert data["message"] == "使用者建立成功"

    def test_create_user_duplicate_email(self):
        """測試建立重複 email 的使用者。"""
        user_data = {
            "name": "測試使用者",
            "email": "wang01@example.com",  # 使用已存在的 email
        }

        response = client.post("/api/v1/users", json=user_data)
        # 修正：ValueError 現在返回 409 錯誤
        assert response.status_code == 409

        data = response.json()
        # 修正：使用 error.message 欄位
        assert "此電子信箱已被使用" in data["error"]["message"]

    def test_create_user_invalid_data(self):
        """測試無效的使用者資料。"""
        user_data = {
            "name": "",  # 空名稱
            "email": "invalid-email-format",  # 無效的 email 格式
        }

        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 422  # Validation error
