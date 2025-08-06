#!/usr/bin/env python3
"""
測試 API 腳本
用於測試時段建立的 API 功能
"""

import json
import logging
import sys
from pathlib import Path

import requests

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_create_schedule():
    """測試建立時段"""
    logger.info("=== 測試建立時段 API ===")

    url = "http://localhost:8000/api/schedules"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # 測試資料
    test_data = [
        {
            "giver_id": 1,
            "date": "2025-08-13",
            "start_time": "20:00:00",
            "end_time": "22:00:00",
            "note": "測試應用程式時段建立",
            "status": "AVAILABLE",
            "role": "GIVER",
        }
    ]

    try:
        logger.info(f"發送請求到: {url}")
        logger.info(f"請求資料: {json.dumps(test_data, ensure_ascii=False, indent=2)}")

        response = requests.post(url, headers=headers, json=test_data)

        logger.info(f"回應狀態碼: {response.status_code}")
        logger.info(f"回應標頭: {dict(response.headers)}")

        if response.status_code == 201:
            logger.info("✅ 時段建立成功")
            result = response.json()
            logger.info(f"回應內容: {json.dumps(result, ensure_ascii=False, indent=2)}")

            # 檢查時間戳記
            if result and len(result) > 0:
                latest_schedule = result[0]
                created_at = latest_schedule.get('created_at')
                updated_at = latest_schedule.get('updated_at')
                logger.info(f"建立時間: {created_at}")
                logger.info(f"更新時間: {updated_at}")

                # 檢查是否為本地時間（應該包含 T 分隔符）
                if created_at and 'T' in created_at:
                    time_part = created_at.split('T')[1]
                    hour = int(time_part.split(':')[0])
                    logger.info(f"建立時間小時: {hour}")
                    if hour >= 20:  # 本地時間應該是 20:00 或之後
                        logger.info("✅ 時間戳記是本地時間")
                    else:
                        logger.warning("⚠️ 時間戳記可能不是本地時間")
        else:
            logger.error("❌ 時段建立失敗")
            logger.error(f"錯誤內容: {response.text}")

    except Exception as e:
        logger.error(f"測試失敗: {e}")


def test_get_schedules():
    """測試取得時段列表"""
    logger.info("=== 測試取得時段列表 API ===")

    url = "http://localhost:8000/api/schedules"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)

        logger.info(f"回應狀態碼: {response.status_code}")

        if response.status_code == 200:
            logger.info("✅ 取得時段列表成功")
            result = response.json()

            if result:
                latest_schedule = max(result, key=lambda x: x['id'])
                logger.info(f"最新時段 ID: {latest_schedule['id']}")
                logger.info(f"建立時間: {latest_schedule['created_at']}")
                logger.info(f"更新時間: {latest_schedule['updated_at']}")
            else:
                logger.info("沒有時段資料")
        else:
            logger.error("❌ 取得時段列表失敗")
            logger.error(f"錯誤內容: {response.text}")

    except Exception as e:
        logger.error(f"測試失敗: {e}")


def main():
    """主函式"""
    logger.info("=== API 測試開始 ===")

    try:
        # 測試取得時段列表
        test_get_schedules()

        # 測試建立時段
        test_create_schedule()

        # 再次測試取得時段列表
        test_get_schedules()

        logger.info("=== API 測試完成 ===")

    except Exception as e:
        logger.error(f"測試失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
