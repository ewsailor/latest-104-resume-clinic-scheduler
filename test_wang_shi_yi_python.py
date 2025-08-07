#!/usr/bin/env python3
"""
測試王拾壹的時段提交功能
"""

import requests


def test_wang_shi_yi_schedule():
    """測試王拾壹的時段提交"""

    # 測試資料
    test_schedules = [
        {
            "giver_id": 11,  # 王拾壹的 ID
            "taker_id": 1,
            "date": "2025-08-15",
            "start_time": "20:00:00",
            "end_time": "22:00:00",
            "note": "測試王拾壹的時段",
            "status": "AVAILABLE",
            "role": "TAKER",
        }
    ]

    try:
        # 發送 POST 請求
        response = requests.post(
            "http://localhost:8000/api/schedules",
            json=test_schedules,
            headers={"Content-Type": "application/json"},
        )

        print(f"狀態碼: {response.status_code}")
        print(f"回應標頭: {response.headers}")

        if response.status_code == 201:
            print("✅ 王拾壹時段提交成功!")
            print(f"回應內容: {response.json()}")
        else:
            print("❌ 王拾壹時段提交失敗!")
            print(f"錯誤內容: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務，請確認服務是否正在運行")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")


if __name__ == "__main__":
    test_wang_shi_yi_schedule()
