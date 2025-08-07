#!/usr/bin/env python3
"""
建立 Giver 使用者資料腳本
為所有 Giver 建立對應的使用者資料
"""

import logging
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings  # noqa: E402
from app.data.givers import MOCK_GIVERS  # noqa: E402

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_giver_users():
    """為所有 Giver 建立對應的使用者資料"""
    logger.info("=== 建立 Giver 使用者資料 ===")

    engine = create_engine(settings.mysql_connection_string)
    conn = engine.connect()

    try:
        # 設定時區為本地時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 檢查是否已有 Giver 使用者資料
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE name LIKE '王%'"))
        giver_count = result.scalar()
        logger.info(f"目前 Giver 使用者數量: {giver_count}")

        if giver_count == 0:
            # 為每個 Giver 建立對應的使用者
            for giver in MOCK_GIVERS:
                # 檢查使用者是否已存在
                result = conn.execute(
                    text("SELECT id FROM users WHERE id = :giver_id"),
                    {"giver_id": giver["id"]},
                )
                existing_user = result.fetchone()

                if not existing_user:
                    # 建立新使用者
                    conn.execute(
                        text(
                            """
                        INSERT INTO users (id, name, email)
                        VALUES (:id, :name, :email)
                    """
                        ),
                        {
                            "id": giver["id"],
                            "name": giver["name"],
                            "email": (
                                f"{giver['name'].lower().replace('王', 'wang')}"
                                "@example.com"
                            ),
                        },
                    )
                    logger.info(
                        f"建立 Giver 使用者: {giver['name']} "
                        f"(ID: {giver['id']})"
                    )
                else:
                    logger.info(
                        f"Giver 使用者已存在: {giver['name']} (ID: {giver['id']})"
                    )

            # 提交變更
            conn.commit()
            logger.info("Giver 使用者資料建立完成")
        else:
            logger.info("Giver 使用者資料已存在，跳過建立")

        # 顯示所有 Giver 使用者
        result = conn.execute(
            text(
                """
            SELECT id, name, email, created_at 
            FROM users 
            WHERE name LIKE '王%'
            ORDER BY id
        """
            )
        )

        logger.info("=== 目前 Giver 使用者列表 ===")
        for row in result:
            logger.info(
                f"ID: {row[0]}, 姓名: {row[1]}, 信箱: {row[2]}, "
                f"建立時間: {row[3]}"
            )

    except Exception as e:
        logger.error(f"建立 Giver 使用者資料失敗: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """主函數"""
    logger.info("=== 建立 Giver 使用者資料 ===")
    create_giver_users()
    logger.info("=== Giver 使用者資料建立完成 ===")


if __name__ == "__main__":
    main()
