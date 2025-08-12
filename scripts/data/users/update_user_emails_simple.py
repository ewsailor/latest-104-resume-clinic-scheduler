#!/usr/bin/env python3
"""
簡化版使用者 email 更新腳本

將所有使用者的 email 更新為統一格式：wang01@example.com 到 wang14@example.com
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

    logger.info("開始更新使用者 email 地址...")

    # 建立資料庫連接
    settings = Settings()
    engine = create_engine(settings.mysql_connection_string)

    # 更新前顯示資料
    logger.info("=== 更新前的資料 ===")
    with engine.connect() as conn:
        conn.execute(text("SET time_zone = '+08:00'"))
        result = conn.execute(
            text(
                """
            SELECT id, name, email FROM users
            WHERE deleted_at IS NULL
            ORDER BY id
        """
            )
        )

        for row in result:
            print(f"ID {row[0]:2d}: {row[1]:<20} | {row[2]}")

    # 執行更新
    logger.info("=== 開始更新 ===")
    with engine.connect() as conn:
        conn.execute(text("SET time_zone = '+08:00'"))

        # 直接執行更新（自動提交）
        update_statements = []
        for i in range(1, 15):
            email = f"wang{i:02d}@example.com"
            sql = (
                "UPDATE users SET email = :email, updated_at = NOW() "
                "WHERE id = :user_id"
            )
            update_statements.append((sql, i, email))

        updated_count = 0
        for sql, user_id, email in update_statements:
            try:
                result = conn.execute(text(sql), {"email": email, "user_id": user_id})
                if result.rowcount > 0:
                    updated_count += 1
                    logger.info(f"✅ 已更新 ID {user_id} 的 email")
                else:
                    logger.warning(f"⚠️  ID {user_id} 沒有更新（可能不存在）")
            except Exception as e:
                logger.error(f"❌ 更新 ID {user_id} 失敗: {str(e)}")

        # 提交變更
        conn.commit()
        logger.info(f"總共更新了 {updated_count} 個使用者的 email")

    # 更新後顯示資料
    logger.info("=== 更新後的資料 ===")
    with engine.connect() as conn:
        conn.execute(text("SET time_zone = '+08:00'"))
        result = conn.execute(
            text(
                """
            SELECT id, name, email, updated_at FROM users
            WHERE deleted_at IS NULL
            ORDER BY id
        """
            )
        )

        for row in result:
            print(f"ID {row[0]:2d}: {row[1]:<20} | {row[2]:<30} | {row[3]}")

    # 驗證格式
    logger.info("=== 驗證結果 ===")
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT
                id,
                email,
                CASE
                    WHEN email REGEXP '^wang[0-9]{2}@example\\.com$' THEN '✅ 格式正確'
                    ELSE '❌ 格式錯誤'
                END AS format_check
            FROM users
            WHERE deleted_at IS NULL
            ORDER BY id
        """
            )
        )

        all_correct = True
        for row in result:
            status = "✅" if "正確" in row[2] else "❌"
            print(f"ID {row[0]:2d}: {row[1]:<30} {status}")
            if "錯誤" in row[2]:
                all_correct = False

        if all_correct:
            logger.info("🎉 所有 email 格式都正確！")
        else:
            logger.warning("⚠️  部分 email 格式有問題")


if __name__ == "__main__":
    try:
        main()
        print("\n✅ Email 更新完成！")
    except Exception as e:
        logger.error(f"腳本執行失敗: {str(e)}")
        print(f"\n❌ 更新失敗: {str(e)}")
