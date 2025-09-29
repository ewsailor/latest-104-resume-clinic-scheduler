"""健康檢查整合測試 - 簡化版。

急著投履歷用的最簡化版本。
"""

from fastapi.testclient import TestClient

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.main import app


class TestHealth:
    """健康檢查整合測試 - 最簡化版。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    def test_healthz_works(self, client):
        """測試存活探測端點。"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_readyz_works(self, client):
        """測試就緒探測端點。"""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
