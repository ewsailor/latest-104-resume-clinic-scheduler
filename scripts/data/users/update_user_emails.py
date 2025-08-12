#!/usr/bin/env python3
"""
更新使用者 email 地址腳本

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
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def update_user_emails():
    """更新所有使用者的 email 地址為統一格式"""

    # 建立資料庫連接
    settings = Settings()
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        # 設定時區為本地時間
        conn.execute(text("SET time_zone = '+08:00'"))

        # 開始交易
        trans = conn.begin()
        try:

            logger.info("開始更新使用者 email 地址...")

            # 取得所有使用者的當前資料
            result = conn.execute(
                text(
                    """
                SELECT id, name, email
                FROM users
                WHERE deleted_at IS NULL
                ORDER BY id
            """
                )
            )

            users = result.fetchall()
            logger.info(f"找到 {len(users)} 個使用者需要更新")

            # 建立更新語句清單
            update_statements = []

            for user in users:
                user_id = user[0]
                user_name = user[1]
                current_email = user[2]

                # 產生新的 email 格式：wang + 兩位數字編號
                new_email = f"wang{user_id:02d}@example.com"

                update_statements.append(
                    {
                        'id': user_id,
                        'name': user_name,
                        'old_email': current_email,
                        'new_email': new_email,
                    }
                )

                logger.info(
                    f"ID {user_id}: {user_name} - {current_email} → {new_email}"
                )

            # 確認是否要執行更新
            print("\n=== 即將執行以下更新 ===")
            for stmt in update_statements:
                print(
                    f"ID {stmt['id']:2d}: {stmt['name']:<20} | {stmt['old_email']:<30} → {stmt['new_email']}"
                )

            # 執行更新
            logger.info("執行 email 更新...")
            for stmt in update_statements:
                conn.execute(
                    text(
                        """
                    UPDATE users
                    SET email = :new_email,
                        updated_at = NOW()
                    WHERE id = :user_id
                """
                    ),
                    {'new_email': stmt['new_email'], 'user_id': stmt['id']},
                )

            # 提交交易
            trans.commit()
            logger.info(f"成功更新 {len(update_statements)} 個使用者的 email 地址")

            # 驗證更新結果
            logger.info("驗證更新結果...")
            result = conn.execute(
                text(
                    """
                SELECT id, name, email, updated_at
                FROM users
                WHERE deleted_at IS NULL
                ORDER BY id
            """
                )
            )

            print("\n=== 更新後的結果 ===")
            for row in result:
                print(
                    f"ID {row[0]:2d}: {row[1]:<20} | {row[2]:<30} | 更新時間: {row[3]}"
                )

        except Exception as e:
            # 發生錯誤時回滾
            trans.rollback()
            logger.error(f"更新失敗，已回滾: {str(e)}")
            raise
        finally:
            if 'trans' in locals():
                pass  # 交易已在 try/except 中處理


def create_backup():
    """在更新前建立備份"""

    settings = Settings()
    engine = create_engine(settings.mysql_connection_string)

    with engine.connect() as conn:
        logger.info("建立使用者資料備份...")

        # 匯出當前使用者資料
        result = conn.execute(
            text(
                """
            SELECT id, name, email, created_at, updated_at, updated_by, deleted_at
            FROM users
            ORDER BY id
        """
            )
        )

        backup_data = []
        for row in result:
            backup_data.append(
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'created_at': str(row[3]) if row[3] else None,
                    'updated_at': str(row[4]) if row[4] else None,
                    'updated_by': row[5],
                    'deleted_at': str(row[6]) if row[6] else None,
                }
            )

        # 寫入備份檔案
        import json
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = (
            f"database/backups/users_backup_before_email_update_{timestamp}.json"
        )

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        logger.info(f"備份完成: {backup_file}")
        return backup_file


if __name__ == "__main__":
    try:
        # 建立備份
        backup_file = create_backup()
        print(f"✅ 備份已建立: {backup_file}")

        # 執行更新
        update_user_emails()
        print("✅ Email 更新完成！")

    except Exception as e:
        logger.error(f"腳本執行失敗: {str(e)}")
        print(f"❌ 更新失敗: {str(e)}")
