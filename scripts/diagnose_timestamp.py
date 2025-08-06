#!/usr/bin/env python3
"""
時間戳記診斷腳本。

詳細分析資料庫時間戳記問題。
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def diagnose_timestamp_issue():
    """診斷時間戳記問題"""
    logger.info("=== 時間戳記問題診斷 ===")

    try:
        from app.core.settings import settings

        engine = create_engine(
            settings.mysql_connection_string,
            echo=False,
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False,
                "sql_mode": (
                    "STRICT_TRANS_TABLES,NO_ZERO_DATE,"
                    "NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO"
                ),
            },
        )

        with engine.connect() as conn:
            # 設定時區
            conn.execute(text("SET time_zone = '+08:00'"))

            logger.info("=== 系統時間資訊 ===")
            system_now = datetime.now()
            utc_now = datetime.now(timezone.utc)
            logger.info(f"系統本地時間: {system_now}")
            logger.info(f"系統 UTC 時間: {utc_now}")
            logger.info(f"時區差異: {system_now.hour - utc_now.hour} 小時")

            logger.info("\n=== 資料庫時間資訊 ===")
            result = conn.execute(
                text("SELECT @@global.time_zone, @@session.time_zone")
            )
            global_tz, session_tz = result.fetchone()
            logger.info(f"全域時區: {global_tz}")
            logger.info(f"會話時區: {session_tz}")

            result = conn.execute(
                text("SELECT NOW(), UTC_TIMESTAMP(), UNIX_TIMESTAMP()")
            )
            now_time, utc_time, unix_timestamp = result.fetchone()
            logger.info(f"資料庫 NOW(): {now_time}")
            logger.info(f"資料庫 UTC_TIMESTAMP(): {utc_time}")
            logger.info(f"資料庫 UNIX_TIMESTAMP(): {unix_timestamp}")

            logger.info("\n=== 最近的資料記錄分析 ===")
            result = conn.execute(
                text(
                    """
                SELECT 
                    id, 
                    created_at, 
                    updated_at,
                    UNIX_TIMESTAMP(created_at) as created_unix,
                    UNIX_TIMESTAMP(updated_at) as updated_unix,
                    CONVERT_TZ(created_at, '+08:00', '+00:00') as created_utc,
                    CONVERT_TZ(updated_at, '+08:00', '+00:00') as updated_utc
                FROM schedules 
                ORDER BY created_at DESC 
                LIMIT 10
            """
                )
            )

            logger.info("最近的 10 筆資料記錄:")
            logger.info(
                "ID | 建立時間(本地) | 建立時間(UTC) | 更新時間(本地) | 更新時間(UTC)"
            )
            logger.info("-" * 80)

            for row in result.fetchall():
                logger.info(f"{row[0]:2d} | {row[1]} | {row[5]} | {row[2]} | {row[6]}")

            logger.info("\n=== 時區轉換測試 ===")
            # 測試時區轉換
            test_time = "2025-08-06 19:52:00"
            result = conn.execute(
                text(
                    f"""
                SELECT 
                    '{test_time}' as original_time,
                    CONVERT_TZ('{test_time}', '+08:00', '+00:00') as to_utc,
                    CONVERT_TZ('{test_time}', '+00:00', '+08:00') as from_utc
            """
                )
            )

            original, to_utc, from_utc = result.fetchone()
            logger.info(f"原始時間 (假設為台灣時間): {original}")
            logger.info(f"轉換為 UTC: {to_utc}")
            logger.info(f"從 UTC 轉回台灣時間: {from_utc}")

            logger.info("\n=== 問題分析 ===")
            logger.info("根據您的描述：")
            logger.info("- 您在 8/6 約 19:52 送出資料")
            logger.info("- MySQL Workbench 顯示 11:51")
            logger.info("- 差異約 8 小時")
            logger.info("")
            logger.info("可能的原因：")
            logger.info("1. MySQL Workbench 顯示的是 UTC 時間")
            logger.info("2. 資料庫時區設定不一致")
            logger.info("3. 應用程式和資料庫時區不同步")
            logger.info("")
            logger.info("建議解決方案：")
            logger.info("1. 在 MySQL Workbench 中設定時區顯示為 +08:00")
            logger.info("2. 確保應用程式每次連接都設定正確的時區")
            logger.info("3. 考慮將所有時間戳記統一儲存為 UTC，顯示時再轉換")

            return True

    except Exception as e:
        logger.error(f"診斷時發生錯誤: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    diagnose_timestamp_issue()
