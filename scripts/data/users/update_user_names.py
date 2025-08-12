#!/usr/bin/env python3
"""
更新使用者姓名腳本

將所有使用者的姓名更新為統一格式：王零一 到 王拾四
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

    logger.info("開始更新使用者姓名...")

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

        # 定義新的姓名對應表
        name_mapping = {
            1: "王零一",
            2: "王零二",
            3: "王零三",
            4: "王零四",
            5: "王零五",
            6: "王零六",
            7: "王零七",
            8: "王零八",
            9: "王零九",
            10: "王拾",
            11: "王拾一",
            12: "王拾二",
            13: "王拾三",
            14: "王拾四",
        }

        updated_count = 0
        for user_id, new_name in name_mapping.items():
            try:
                result = conn.execute(
                    text(
                        """
                    UPDATE users
                    SET name = :new_name, updated_at = NOW()
                    WHERE id = :user_id AND deleted_at IS NULL
                """
                    ),
                    {"new_name": new_name, "user_id": user_id},
                )

                if result.rowcount > 0:
                    updated_count += 1
                    logger.info(f"✅ 已更新 ID {user_id} 的姓名為: {new_name}")
                else:
                    logger.warning(f"⚠️  ID {user_id} 沒有更新（可能不存在或已刪除）")
            except Exception as e:
                logger.error(f"❌ 更新 ID {user_id} 失敗: {str(e)}")

        # 提交變更
        conn.commit()
        logger.info(f"總共更新了 {updated_count} 個使用者的姓名")

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
            print(f"ID {row[0]:2d}: {row[1]:<10} | {row[2]:<30} | {row[3]}")

    # 驗證格式
    logger.info("=== 驗證結果 ===")
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT
                id,
                name,
                CASE
                    WHEN name REGEXP '^王(零[一二三四五六七八九]|拾[一二三四]?)$' THEN '✅ 格式正確'
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
            print(f"ID {row[0]:2d}: {row[1]:<10} {status}")
            if "錯誤" in row[2]:
                all_correct = False

        if all_correct:
            logger.info("🎉 所有姓名格式都正確！")
        else:
            logger.warning("⚠️  部分姓名格式有問題")


if __name__ == "__main__":
    try:
        main()
        print("\n✅ 姓名更新完成！")
    except Exception as e:
        logger.error(f"腳本執行失敗: {str(e)}")
        print(f"\n❌ 更新失敗: {str(e)}")
