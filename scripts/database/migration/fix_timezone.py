#!/usr/bin/env python3
"""
時區修復腳本。

檢查和修復資料庫時區設定問題。
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


def check_timezone_settings():
    """檢查資料庫時區設定"""
    logger.info("開始檢查資料庫時區設定...")

    try:
        # 建立資料庫連接
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
            # 檢查 MySQL 時區設定
            result = conn.execute(
                text("SELECT @@global.time_zone, @@session.time_zone")
            )
            global_tz, session_tz = result.fetchone()

            logger.info(f"全域時區設定: {global_tz}")
            logger.info(f"會話時區設定: {session_tz}")

            # 檢查當前時間
            result = conn.execute(text("SELECT NOW(), UTC_TIMESTAMP()"))
            now_time, utc_time = result.fetchone()

            logger.info(f"資料庫當前時間 (NOW): {now_time}")
            logger.info(f"資料庫 UTC 時間: {utc_time}")

            # 檢查系統時間
            system_now = datetime.now()
            utc_now = datetime.now(timezone.utc)

            logger.info(f"系統當前時間: {system_now}")
            logger.info(f"系統 UTC 時間: {utc_now}")

            # 檢查時區差異
            if global_tz != "+08:00":
                logger.warning(f"全域時區不是 +08:00，目前是: {global_tz}")

            if session_tz != "+08:00":
                logger.warning(f"會話時區不是 +08:00，目前是: {session_tz}")

            # 檢查最近的資料記錄
            result = conn.execute(
                text(
                    """
                SELECT id, created_at, updated_at
                FROM schedules
                ORDER BY created_at DESC
                LIMIT 5
            """
                )
            )

            logger.info("最近的 5 筆資料記錄:")
            for row in result.fetchall():
                logger.info(f"ID: {row[0]}, 建立時間: {row[1]}, 更新時間: {row[2]}")

            return True

    except Exception as e:
        logger.error(f"檢查時區設定時發生錯誤: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


def fix_timezone_settings():
    """修復時區設定"""
    logger.info("開始修復時區設定...")

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
            # 設定會話時區
            conn.execute(text("SET time_zone = '+08:00'"))
            conn.commit()

            # 驗證設定
            result = conn.execute(text("SELECT @@session.time_zone"))
            session_tz = result.fetchone()[0]

            logger.info(f"會話時區已設定為: {session_tz}")

            # 檢查設定後的時間
            result = conn.execute(text("SELECT NOW(), UTC_TIMESTAMP()"))
            now_time, utc_time = result.fetchone()

            logger.info(f"設定後資料庫時間 (NOW): {now_time}")
            logger.info(f"設定後資料庫 UTC 時間: {utc_time}")

            return True

    except Exception as e:
        logger.error(f"修復時區設定時發生錯誤: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    logger.info("=== 資料庫時區檢查和修復工具 ===")

    # 檢查當前設定
    if check_timezone_settings():
        logger.info("時區檢查完成")

        # 詢問是否要修復
        response = input("\n是否要修復時區設定？(y/N): ").strip().lower()
        if response in ['y', 'yes']:
            if fix_timezone_settings():
                logger.info("時區修復完成")
            else:
                logger.error("時區修復失敗")
        else:
            logger.info("跳過時區修復")
    else:
        logger.error("時區檢查失敗")
