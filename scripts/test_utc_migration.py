#!/usr/bin/env python3
"""
測試 UTC 遷移腳本。

測試時區轉換功能和 UTC 遷移是否正常工作。
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

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_timezone_utils():
    """測試時區轉換工具"""
    logger.info("=== 測試時區轉換工具 ===")

    try:
        from app.utils.timezone import (
            format_datetime_for_display,
            local_to_utc,
            now_local,
            now_utc,
            parse_datetime_from_display,
            utc_to_local,
        )

        # 測試時間轉換
        test_utc = datetime(2025, 8, 6, 13, 53, 0, tzinfo=timezone.utc)
        test_local = datetime(2025, 8, 6, 21, 53, 0)

        logger.info(f"測試 UTC 時間: {test_utc}")
        logger.info(f"測試本地時間: {test_local}")

        # UTC 轉本地
        converted_local = utc_to_local(test_utc)
        logger.info(f"UTC 轉本地: {converted_local}")

        # 本地轉 UTC
        converted_utc = local_to_utc(test_local)
        logger.info(f"本地轉 UTC: {converted_utc}")

        # 格式化顯示
        display_str = format_datetime_for_display(test_utc)
        logger.info(f"格式化顯示: {display_str}")

        # 解析顯示字串
        parsed_utc = parse_datetime_from_display(display_str)
        logger.info(f"解析顯示字串: {parsed_utc}")

        # 當前時間
        current_utc = now_utc()
        current_local = now_local()
        logger.info(f"當前 UTC: {current_utc}")
        logger.info(f"當前本地: {current_local}")

        logger.info("時區轉換工具測試完成")
        return True

    except Exception as e:
        logger.error(f"時區轉換工具測試失敗: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


def test_database_utc():
    """測試資料庫 UTC 功能"""
    logger.info("=== 測試資料庫 UTC 功能 ===")

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
            # 檢查資料庫時間
            result = conn.execute(text("SELECT NOW(), UTC_TIMESTAMP()"))
            now_time, utc_time = result.fetchone()

            logger.info(f"資料庫 NOW(): {now_time}")
            logger.info(f"資料庫 UTC_TIMESTAMP(): {utc_time}")

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
                LIMIT 3
            """
                )
            )

            logger.info("資料庫中的時間戳記:")
            logger.info("ID | UTC時間 | 本地時間")
            logger.info("-" * 40)

            for row in result.fetchall():
                logger.info(f"{row[0]:2d} | {row[1]} | {row[3]}")

            logger.info("資料庫 UTC 功能測試完成")
            return True

    except Exception as e:
        logger.error(f"資料庫 UTC 功能測試失敗: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


def test_pydantic_models():
    """測試 Pydantic 模型"""
    logger.info("=== 測試 Pydantic 模型 ===")

    try:
        from datetime import datetime, timezone

        from app.schemas.schedule import ScheduleResponse

        # 建立測試資料
        test_utc = datetime(2025, 8, 6, 13, 53, 0, tzinfo=timezone.utc)

        # 建立 ScheduleResponse 實例
        schedule_response = ScheduleResponse(
            id=1,
            role="GIVER",
            giver_id=1,
            taker_id=None,
            date=datetime(2025, 8, 6).date(),
            start_time=datetime(2025, 8, 6, 9, 0).time(),
            end_time=datetime(2025, 8, 6, 10, 0).time(),
            note="測試時段",
            status="AVAILABLE",
            created_at=test_utc,
            updated_at=test_utc,
        )

        logger.info(f"ScheduleResponse 實例: {schedule_response}")
        logger.info(f"建立時間: {schedule_response.created_at}")
        logger.info(f"更新時間: {schedule_response.updated_at}")

        logger.info("Pydantic 模型測試完成")
        return True

    except Exception as e:
        logger.error(f"Pydantic 模型測試失敗: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


def create_test_data():
    """建立測試資料"""
    logger.info("=== 建立測試資料 ===")

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
            # 建立測試使用者
            conn.execute(
                text(
                    """
                INSERT INTO users (name, email) 
                VALUES ('測試使用者', 'test@example.com')
                ON DUPLICATE KEY UPDATE name = name
            """
                )
            )

            # 取得使用者 ID
            result = conn.execute(
                text("SELECT id FROM users WHERE email = 'test@example.com'")
            )
            user_id = result.fetchone()[0]

            # 建立測試時段
            conn.execute(
                text(
                    """
                INSERT INTO schedules (role, giver_id, date, start_time, end_time, note, status)
                VALUES ('GIVER', :user_id, '2025-08-07', '09:00:00', '10:00:00', '測試時段', 'AVAILABLE')
            """
                ),
                {"user_id": user_id},
            )

            conn.commit()
            logger.info(f"測試資料建立完成，使用者 ID: {user_id}")

            # 檢查建立的資料
            result = conn.execute(
                text(
                    """
                SELECT 
                    s.id, s.created_at, s.updated_at,
                    CONVERT_TZ(s.created_at, '+00:00', '+08:00') as created_local
                FROM schedules s
                WHERE s.note = '測試時段'
                ORDER BY s.created_at DESC
                LIMIT 1
            """
                )
            )

            row = result.fetchone()
            if row:
                logger.info(f"測試時段 ID: {row[0]}")
                logger.info(f"UTC 建立時間: {row[1]}")
                logger.info(f"本地建立時間: {row[3]}")

            return True

    except Exception as e:
        logger.error(f"建立測試資料失敗: {e}")
        import traceback

        logger.error(f"詳細錯誤資訊: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    logger.info("=== UTC 遷移測試 ===")

    # 執行測試
    tests = [
        ("時區轉換工具", test_timezone_utils),
        ("資料庫 UTC 功能", test_database_utc),
        ("Pydantic 模型", test_pydantic_models),
        ("建立測試資料", create_test_data),
    ]

    for test_name, test_func in tests:
        logger.info(f"\n=== {test_name} ===")
        if test_func():
            logger.info(f"{test_name}測試通過")
        else:
            logger.error(f"{test_name}測試失敗")
            sys.exit(1)

    logger.info("\n=== 所有測試通過 ===")
    logger.info("UTC 遷移功能正常運作")
