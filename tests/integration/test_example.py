"""整合測試範例。

展示如何撰寫整合測試的基本範例。
"""

import random

from fastapi import status
from fastapi.testclient import TestClient

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.main import app


class TestIntegrationExample:
    """整合測試範例類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    def test_basic_integration_example(self, client):
        """基本整合測試範例。"""
        # GIVEN：應用程式正常運行

        # WHEN：呼叫健康檢查端點
        response = client.get("/healthz")

        # THEN：確認回應正確
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_integration_with_data_flow(self, client):
        """整合測試範例 - 資料流程。"""
        # GIVEN：準備測試資料，使用 set 確保唯一性
        used_times = set()

        # 生成唯一的時間
        while True:
            hour = random.randint(13, 18)
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"

            if time_key not in used_times:
                used_times.add(time_key)
                break

        test_data = {
            "schedules": [
                {
                    "giver_id": 1,
                    "date": "2024-06-15",
                    "start_time": f"{time_key}:00",
                    "end_time": f"{hour:02d}:{minute+1:02d}:00",
                    "note": "測試時段",
                }
            ],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=test_data)

        # THEN：確認建立成功
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["giver_id"] == 1
