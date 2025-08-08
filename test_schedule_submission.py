#!/usr/bin/env python3
"""
測試時段提交功能
"""


import requests


def test_schedule_submission() -> None:
    """測試時段提交功能"""
    # 測試資料
    test_schedules = [
        {
            "giver_id": 1,
            "taker_id": 2,
            "date": "2025-01-15",
            "start_time": "14:00:00",
            "end_time": "16:00:00",
            "note": "測試時段 1",
            "status": "AVAILABLE",
            "role": "TAKER",
        },
        {
            "giver_id": 2,
            "taker_id": 3,
            "date": "2025-01-16",
            "start_time": "10:00:00",
            "end_time": "12:00:00",
            "note": "測試時段 2",
            "status": "AVAILABLE",
            "role": "TAKER",
        },
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
            print("✅ 時段提交成功!")
            print(f"回應內容: {response.json()}")
        else:
            print("❌ 時段提交失敗!")
            print(f"錯誤內容: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務，請確認服務是否正在運行")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")


if __name__ == "__main__":
    test_schedule_submission()
