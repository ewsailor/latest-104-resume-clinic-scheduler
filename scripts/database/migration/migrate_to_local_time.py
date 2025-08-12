#!/usr/bin/env python3
"""
將資料庫中的 UTC 時間轉換為本地時間。

此腳本會：
1. 備份現有資料
2. 將所有 UTC 時間戳記轉換為本地時間
3. 更新資料庫 schema 註解
"""

import logging
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def backup_existing_data():
    """備份現有資料"""
    logger.info("=== 備份現有資料 ===")

    # 建立資料庫連線
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        # 備份使用者資料
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS users_backup AS SELECT * FROM users")
        )
        logger.info("使用者資料備份完成")

        # 備份時段資料
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schedules_backup AS SELECT * FROM schedules"
            )
        )
        logger.info("時段資料備份完成")

        conn.commit()


def migrate_to_local_time():
    """將 UTC 時間轉換為本地時間"""
    logger.info("=== 轉換 UTC 時間為本地時間 ===")

    # 建立資料庫連線
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        # 設定時區為台灣時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 轉換使用者資料表的時間戳記
        logger.info("轉換使用者資料表時間戳記...")
        conn.execute(
            text(
                """
            UPDATE users
            SET
                created_at = CONVERT_TZ(created_at, '+00:00', '+08:00'),
                updated_at = CONVERT_TZ(updated_at, '+00:00', '+08:00')
            WHERE created_at IS NOT NULL
        """
            )
        )

        # 轉換時段資料表的時間戳記
        logger.info("轉換時段資料表時間戳記...")
        conn.execute(
            text(
                """
            UPDATE schedules
            SET
                created_at = CONVERT_TZ(created_at, '+00:00', '+08:00'),
                updated_at = CONVERT_TZ(updated_at, '+00:00', '+08:00')
            WHERE created_at IS NOT NULL
        """
            )
        )

        conn.commit()
        logger.info("時間戳記轉換完成")


def update_schema_comments():
    """更新資料表註解"""
    logger.info("=== 更新資料表註解 ===")

    # 建立資料庫連線
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        # 設定時區為台灣時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 更新使用者資料表註解
        conn.execute(
            text(
                """
            ALTER TABLE users
            MODIFY created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '建立時間 (本地時間)',
            MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間 (本地時間)'
        """
            )
        )

        # 更新時段資料表註解
        conn.execute(
            text(
                """
            ALTER TABLE schedules
            MODIFY created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '建立時間 (本地時間)',
            MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間 (本地時間)'
        """
            )
        )

        conn.commit()
        logger.info("資料表註解更新完成")


def verify_migration():
    """驗證遷移結果"""
    logger.info("=== 驗證遷移結果 ===")

    # 建立資料庫連線
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        # 設定時區為台灣時間
        conn.execute(text("SET time_zone = '+08:00'"))

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
            LIMIT 5
        """
            )
        )

        logger.info("最近的時段記錄：")
        logger.info("ID | 建立時間 | 更新時間")
        logger.info("----------------------------------------")

        for row in result:
            logger.info(f"{row[0]:2d} | {row[3]} | {row[4]}")

        # 檢查資料庫當前時間
        result = conn.execute(text("SELECT NOW(), UTC_TIMESTAMP()"))
        row = result.fetchone()
        logger.info(f"資料庫當前時間: {row[0]}")
        logger.info(f"資料庫 UTC 時間: {row[1]}")


def main():
    """主函數"""
    logger.info("=== 開始遷移到本地時間 ===")

    try:
        # 1. 備份資料
        backup_existing_data()

        # 2. 轉換時間戳記
        migrate_to_local_time()

        # 3. 更新 schema 註解
        update_schema_comments()

        # 4. 驗證結果
        verify_migration()

        logger.info("=== 遷移完成 ===")
        logger.info("現在資料庫直接儲存本地時間，MySQL Workbench 會顯示正確的本地時間")

    except Exception as e:
        logger.error(f"遷移失敗: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
