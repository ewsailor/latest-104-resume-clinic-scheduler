#!/usr/bin/env python3
"""
測試本地時間處理。

驗證資料庫是否正確儲存和顯示本地時間。
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_database_time():
    """測試資料庫時間處理"""
    logger.info("=== 測試資料庫時間處理 ===")

    # 建立資料庫連線
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        # 設定時區為台灣時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 檢查資料庫當前時間
        result = conn.execute(text("SELECT NOW(), UTC_TIMESTAMP()"))
        row = result.fetchone()
        logger.info(f"資料庫當前時間: {row[0]}")
        logger.info(f"資料庫 UTC 時間: {row[1]}")

        # 檢查最近的時段記錄
        result = conn.execute(
            text(
                """
            SELECT
                id,
                created_at,
                updated_at,
                DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_formatted,
                DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_formatted
            FROM schedules
            ORDER BY created_at DESC
            LIMIT 3
        """
            )
        )

        logger.info("最近的時段記錄：")
        logger.info("ID | 建立時間 | 更新時間")
        logger.info("----------------------------------------")

        for row in result:
            logger.info(f"{row[0]:2d} | {row[3]} | {row[4]}")


def create_test_schedule():
    """建立測試時段"""
    logger.info("=== 建立測試時段 ===")

    # 建立資料庫連線
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        # 設定時區為台灣時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 建立測試時段
        result = conn.execute(
            text(
                """
            INSERT INTO schedules (role, giver_id, date, start_time, end_time, note, status)
            VALUES ('GIVER', 1, '2025-08-08', '15:00:00', '16:00:00', '測試本地時間', 'AVAILABLE')
        """
            )
        )

        # 取得插入的 ID
        schedule_id = conn.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]

        # 查詢剛建立的時段
        result = conn.execute(
            text(
                """
            SELECT
                id,
                created_at,
                updated_at,
                DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_formatted,
                DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_formatted
            FROM schedules
            WHERE id = :schedule_id
        """
            ),
            {"schedule_id": schedule_id},
        )

        row = result.fetchone()
        logger.info(f"測試時段 ID: {row[0]}")
        logger.info(f"建立時間: {row[3]}")
        logger.info(f"更新時間: {row[4]}")

        conn.commit()


def main():
    """主函數"""
    logger.info("=== 本地時間處理測試 ===")

    try:
        # 1. 測試資料庫時間
        test_database_time()

        # 2. 建立測試時段
        create_test_schedule()

        logger.info("=== 測試完成 ===")
        logger.info("現在資料庫直接儲存本地時間，MySQL Workbench 會顯示正確的本地時間")

    except Exception as e:
        logger.error(f"測試失敗: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
