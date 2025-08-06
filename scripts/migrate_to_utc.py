#!/usr/bin/env python3
"""
資料庫遷移到 UTC 時間戳記腳本。

將現有的資料庫從本地時間戳記遷移到 UTC 時間戳記。
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


def backup_existing_data():
    """備份現有資料"""
    logger.info("開始備份現有資料...")

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
            # 建立備份表
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS users_backup AS 
                SELECT * FROM users
            """
                )
            )
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS schedules_backup AS 
                SELECT * FROM schedules
            """
                )
            )
            conn.commit()

            logger.info("資料備份完成")
            return True

    except Exception as e:
        logger.error(f"備份資料時發生錯誤: {e}")
        return False


def migrate_to_utc():
    """遷移到 UTC 時間戳記"""
    logger.info("開始遷移到 UTC 時間戳記...")

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
            # 檢查現有資料
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.fetchone()[0]

            result = conn.execute(text("SELECT COUNT(*) FROM schedules"))
            schedules_count = result.fetchone()[0]

            logger.info(f"現有資料：users={users_count}, schedules={schedules_count}")

            # 更新 users 表的時間戳記
            logger.info("更新 users 表的時間戳記...")
            conn.execute(
                text(
                    """
                UPDATE users 
                SET 
                    created_at = CONVERT_TZ(created_at, '+08:00', '+00:00'),
                    updated_at = CONVERT_TZ(updated_at, '+08:00', '+00:00')
                WHERE created_at IS NOT NULL
            """
                )
            )

            # 更新 schedules 表的時間戳記
            logger.info("更新 schedules 表的時間戳記...")
            conn.execute(
                text(
                    """
                UPDATE schedules 
                SET 
                    created_at = CONVERT_TZ(created_at, '+08:00', '+00:00'),
                    updated_at = CONVERT_TZ(updated_at, '+08:00', '+00:00')
                WHERE created_at IS NOT NULL
            """
                )
            )

            conn.commit()
            logger.info("時間戳記遷移完成")

            # 驗證遷移結果
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

            logger.info("遷移後的資料範例:")
            for row in result.fetchall():
                logger.info(f"ID: {row[0]}, 建立時間: {row[1]}, 更新時間: {row[2]}")

            return True

    except Exception as e:
        logger.error(f"遷移時發生錯誤: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


def update_schema_to_utc():
    """更新資料庫 schema 使用 UTC 時間戳記"""
    logger.info("更新資料庫 schema 使用 UTC 時間戳記...")

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
            # 設定資料庫時區為 UTC
            logger.info("設定資料庫時區為 UTC...")
            conn.execute(text("SET time_zone = '+00:00'"))

            # 更新 users 表的 schema
            logger.info("更新 users 表的 schema...")
            conn.execute(
                text(
                    """
                ALTER TABLE users 
                MODIFY created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '建立時間 (UTC)',
                MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間 (UTC)'
            """
                )
            )

            # 更新 schedules 表的 schema
            logger.info("更新 schedules 表的 schema...")
            conn.execute(
                text(
                    """
                ALTER TABLE schedules 
                MODIFY created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '建立時間 (UTC)',
                MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間 (UTC)'
            """
                )
            )

            conn.commit()
            logger.info("Schema 更新完成")

            return True

    except Exception as e:
        logger.error(f"更新 schema 時發生錯誤: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


def verify_migration():
    """驗證遷移結果"""
    logger.info("驗證遷移結果...")

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
            # 檢查當前時間
            result = conn.execute(text("SELECT NOW(), UTC_TIMESTAMP()"))
            now_time, utc_time = result.fetchone()

            logger.info(f"資料庫當前時間: {now_time}")
            logger.info(f"資料庫 UTC 時間: {utc_time}")

            # 檢查最近的資料
            result = conn.execute(
                text(
                    """
                SELECT 
                    id, 
                    created_at, 
                    updated_at,
                    CONVERT_TZ(created_at, '+00:00', '+08:00') as created_local,
                    CONVERT_TZ(updated_at, '+00:00', '+08:00') as updated_local
                FROM schedules 
                ORDER BY created_at DESC 
                LIMIT 5
            """
                )
            )

            logger.info("遷移驗證結果:")
            logger.info("ID | UTC時間 | 本地時間")
            logger.info("-" * 40)

            for row in result.fetchall():
                logger.info(f"{row[0]:2d} | {row[1]} | {row[3]}")

            return True

    except Exception as e:
        logger.error(f"驗證時發生錯誤: {e}")
        return False


if __name__ == "__main__":
    logger.info("=== 資料庫遷移到 UTC 時間戳記 ===")

    # 確認操作
    response = input("此操作將修改資料庫結構和資料，是否繼續？(y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        logger.info("操作已取消")
        sys.exit(0)

    # 執行遷移步驟
    steps = [
        ("備份現有資料", backup_existing_data),
        ("遷移時間戳記", migrate_to_utc),
        ("更新資料庫 schema", update_schema_to_utc),
        ("驗證遷移結果", verify_migration),
    ]

    for step_name, step_func in steps:
        logger.info(f"\n=== {step_name} ===")
        if step_func():
            logger.info(f"{step_name}成功")
        else:
            logger.error(f"{step_name}失敗")
            sys.exit(1)

    logger.info("\n=== 遷移完成 ===")
    logger.info("現在資料庫使用 UTC 時間戳記，應用程式會在顯示時自動轉換為本地時間")
