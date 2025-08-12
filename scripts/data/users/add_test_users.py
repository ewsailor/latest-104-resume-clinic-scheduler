#!/usr/bin/env python3
"""
新增測試使用者腳本

建立兩個測試使用者：
1. 正常的 Demo 使用者
2. 特殊的 Debug 測試使用者
"""

import logging
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text  # noqa: E402

from app.core.settings import Settings  # noqa: E402

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """主函數"""

    logger.info("開始新增測試使用者...")

    # 建立資料庫連接
    settings = Settings()
    engine = create_engine(settings.mysql_connection_string)

    # 要新增的使用者資料
    test_users = [
        {
            "name": "【Demo】Taker_1",
            "email": "demo_taker_1@example.com",
            "description": "正常的 Demo 測試使用者",
        },
        {
            "name": "[DEBUG] Invalid User",
            "email": "debug_invalid_user@test.local",
            "description": "Debug 測試用的特殊使用者（模擬異常資料）",
        },
    ]

    # 顯示計劃新增的使用者
    logger.info("=== 計劃新增的使用者 ===")
    for i, user in enumerate(test_users, 1):
        print(f"{i}. 姓名: {user['name']}")
        print(f"   Email: {user['email']}")
        print(f"   說明: {user['description']}")
        print()

    # 執行新增
    with engine.connect() as conn:
        conn.execute(text("SET time_zone = '+08:00'"))

        added_count = 0
        for user in test_users:
            try:
                # 檢查 email 是否已存在
                check_result = conn.execute(
                    text(
                        """
                    SELECT id FROM users WHERE email = :email
                """
                    ),
                    {"email": user["email"]},
                )

                if check_result.fetchone():
                    logger.warning(f"⚠️  Email 已存在，跳過: {user['email']}")
                    continue

                # 新增使用者
                result = conn.execute(
                    text(
                        """
                    INSERT INTO users (name, email, created_at, updated_at)
                    VALUES (:name, :email, NOW(), NOW())
                """
                    ),
                    {"name": user["name"], "email": user["email"]},
                )

                # 取得新建立的使用者 ID
                new_id = result.lastrowid
                added_count += 1

                logger.info(
                    f"✅ 成功新增使用者 ID {new_id}: {user['name']} ({user['email']})"
                )

            except Exception as e:
                logger.error(f"❌ 新增使用者失敗: {user['name']} - {str(e)}")

        # 提交變更
        if added_count > 0:
            conn.commit()
            logger.info(f"總共新增了 {added_count} 個使用者")
        else:
            logger.info("沒有新增任何使用者（可能都已存在）")

    # 顯示最新的使用者列表
    logger.info("=== 最新的使用者列表 ===")
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT id, name, email, created_at FROM users
            WHERE deleted_at IS NULL
            ORDER BY id DESC
            LIMIT 10
        """
            )
        )

        for row in result:
            print(f"ID {row[0]:2d}: {row[1]:<25} | {row[2]:<35} | {row[3]}")


if __name__ == "__main__":
    try:
        main()
        print("\n✅ 測試使用者新增完成！")
    except Exception as e:
        logger.error(f"腳本執行失敗: {str(e)}")
        print(f"\n❌ 新增失敗: {str(e)}")
