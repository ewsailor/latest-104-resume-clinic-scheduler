#!/usr/bin/env python3
"""
測試時段提交功能的腳本。

驗證提交時段時是否正確設定：
- role: 'TAKER'
- taker_id: 1
- giver_id: 根據點擊的 Giver 而定
"""

import json

import requests


def test_schedule_submission():
    """測試時段提交功能"""

    # 測試資料
    test_schedules = [
        {
            "giver_id": 4,  # 王零四的 ID
            "taker_id": 1,
            "date": "2025-08-15",
            "start_time": "20:00:00",
            "end_time": "22:00:00",
            "note": "測試時段",
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

        if response.status_code == 201:
            result = response.json()
            print("✅ 時段提交成功！")
            print("回應資料:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 驗證回應格式
            if isinstance(result, list) and len(result) > 0:
                schedule = result[0]

                # 檢查必要欄位
                required_fields = [
                    'id',
                    'role',
                    'giver_id',
                    'taker_id',
                    'date',
                    'start_time',
                    'end_time',
                    'status',
                    'created_at',
                    'updated_at',
                ]

                print("\n📋 欄位驗證:")
                for field in required_fields:
                    if field in schedule:
                        print(f"✅ {field}: {schedule[field]}")
                    else:
                        print(f"❌ {field}: 缺失")

                # 特別檢查關鍵欄位
                print("\n🔍 關鍵欄位檢查:")
                role_check = '✅' if schedule.get('role') == 'TAKER' else '❌'
                print(f"role 是否為 'TAKER': {role_check}")

                taker_check = '✅' if schedule.get('taker_id') == 1 else '❌'
                print(f"taker_id 是否為 1: {taker_check}")

                giver_check = '✅' if schedule.get('giver_id') == 4 else '❌'
                print(f"giver_id 是否為 4: {giver_check}")

                status_check = '✅' if schedule.get('status') == 'AVAILABLE' else '❌'
                print(f"status 是否為 'AVAILABLE': {status_check}")

            else:
                print("❌ 回應格式不正確")

        else:
            print(f"❌ 時段提交失敗: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器，請確認伺服器正在運行")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")


if __name__ == "__main__":
    print("🧪 開始測試時段提交功能...")
    test_schedule_submission()
