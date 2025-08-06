#!/usr/bin/env python3
"""
建立測試資料腳本
用於在遷移後重新建立測試使用者資料
"""

import logging
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings  # noqa: E402

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_users():
    """建立測試使用者資料"""
    logger.info("=== 建立測試使用者資料 ===")

    engine = create_engine(settings.mysql_connection_string)
    conn = engine.connect()

    try:
        # 設定時區為本地時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 檢查是否已有使用者資料
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        logger.info(f"目前使用者數量: {user_count}")

        if user_count == 0:
            # 建立測試使用者
            test_users = [
                {'name': '測試 Giver 1', 'email': 'giver1@test.com'},
                {'name': '測試 Giver 2', 'email': 'giver2@test.com'},
                {'name': '測試 Taker 1', 'email': 'taker1@test.com'},
                {'name': '測試 Taker 2', 'email': 'taker2@test.com'},
            ]

            for user in test_users:
                conn.execute(
                    text(
                        """
                    INSERT INTO users (name, email)
                    VALUES (:name, :email)
                """
                    ),
                    user,
                )
                logger.info(f"建立使用者: {user['name']} ({user['email']})")

            # 提交變更
            conn.commit()
            logger.info("測試使用者資料建立完成")
        else:
            logger.info("使用者資料已存在，跳過建立")

        # 顯示所有使用者
        result = conn.execute(
            text(
                """
            SELECT id, name, email, created_at 
            FROM users 
            ORDER BY id
        """
            )
        )

        logger.info("=== 目前使用者列表 ===")
        for row in result:
            logger.info(
                f"ID: {row[0]}, 姓名: {row[1]}, 信箱: {row[2]}, "
                f"建立時間: {row[3]}"
            )

    except Exception as e:
        logger.error(f"建立測試使用者資料失敗: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def create_test_schedules():
    """建立測試時段資料"""
    logger.info("=== 建立測試時段資料 ===")

    engine = create_engine(settings.mysql_connection_string)
    conn = engine.connect()

    try:
        # 設定時區為本地時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 檢查是否已有時段資料
        result = conn.execute(text("SELECT COUNT(*) FROM schedules"))
        schedule_count = result.scalar()
        logger.info(f"目前時段數量: {schedule_count}")

        if schedule_count == 0:
            # 建立測試時段
            test_schedules = [
                {
                    'role': 'GIVER',
                    'giver_id': 1,
                    'date': '2025-08-08',
                    'start_time': '15:00:00',
                    'end_time': '16:00:00',
                    'note': '測試本地時間時段 1',
                    'status': 'AVAILABLE',
                },
                {
                    'role': 'GIVER',
                    'giver_id': 1,
                    'date': '2025-08-09',
                    'start_time': '16:00:00',
                    'end_time': '17:00:00',
                    'note': '測試本地時間時段 2',
                    'status': 'AVAILABLE',
                },
                {
                    'role': 'GIVER',
                    'giver_id': 2,
                    'date': '2025-08-10',
                    'start_time': '14:00:00',
                    'end_time': '15:00:00',
                    'note': '測試本地時間時段 3',
                    'status': 'AVAILABLE',
                },
            ]

            for schedule in test_schedules:
                conn.execute(
                    text(
                        """
                    INSERT INTO schedules (role, giver_id, date, start_time,
                    end_time, note, status)
                    VALUES (:role, :giver_id, :date, :start_time,
                    :end_time, :note, :status)
                """
                    ),
                    schedule,
                )
                logger.info(
                    f"建立時段: {schedule['role']} - {schedule['date']} "
                    f"{schedule['start_time']}-{schedule['end_time']}"
                )

            # 提交變更
            conn.commit()
            logger.info("測試時段資料建立完成")
        else:
            logger.info("時段資料已存在，跳過建立")

        # 顯示所有時段
        result = conn.execute(
            text(
                """
            SELECT id, role, giver_id, date, start_time, end_time,
            status, created_at
            FROM schedules
            ORDER BY id
        """
            )
        )

        logger.info("=== 目前時段列表 ===")
        for row in result:
            logger.info(
                f"ID: {row[0]}, 角色: {row[1]}, Giver ID: {row[2]}, "
                f"日期: {row[3]}, 時間: {row[4]}-{row[5]}, 狀態: {row[6]}, "
                f"建立時間: {row[7]}"
            )

    except Exception as e:
        logger.error(f"建立測試時段資料失敗: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """主函式"""
    logger.info("=== 建立測試資料 ===")

    try:
        # 建立測試使用者
        create_test_users()

        # 建立測試時段
        create_test_schedules()

        logger.info("=== 測試資料建立完成 ===")

    except Exception as e:
        logger.error(f"建立測試資料失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
