#!/usr/bin/env python3
"""
備份 users 資料表腳本

在移除 updated_by 欄位前，先備份完整的 users 資料表內容。
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text  # noqa: E402

from app.core.settings import Settings  # noqa: E402

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def backup_users_table():
    """備份 users 資料表"""

    # 建立備份檔案名稱（包含時間戳記）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"users_backup_before_remove_updated_by_{timestamp}.json"
    backup_path = (
        project_root / "database" / "backups" / "data_backups" / backup_filename
    )

    logger.info(f"開始備份 users 資料表...")
    logger.info(f"備份檔案路徑: {backup_path}")

    # 建立資料庫連接
    settings = Settings()
    engine = create_engine(settings.mysql_connection_string)

    try:
        with engine.connect() as conn:
            # 設定時區
            conn.execute(text("SET time_zone = '+08:00'"))

            # 查詢所有使用者資料（包含已刪除的）
            result = conn.execute(
                text(
                    """
                SELECT 
                    id,
                    name,
                    email,
                    created_at,
                    updated_at,
                    updated_by,
                    deleted_at
                FROM users
                ORDER BY id
            """
                )
            )

            users_data = []
            for row in result:
                user_dict = {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "created_at": row[3].isoformat() if row[3] else None,
                    "updated_at": row[4].isoformat() if row[4] else None,
                    "updated_by": row[5],
                    "deleted_at": row[6].isoformat() if row[6] else None,
                }
                users_data.append(user_dict)

            # 建立備份資料結構
            backup_data = {
                "backup_info": {
                    "timestamp": datetime.now().isoformat(),
                    "table_name": "users",
                    "total_records": len(users_data),
                    "description": "備份 users 資料表，準備移除 updated_by 欄位",
                    "backup_type": "full_table_backup",
                },
                "table_schema": {
                    "columns": [
                        {"name": "id", "type": "INT UNSIGNED", "primary_key": True},
                        {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                        {
                            "name": "email",
                            "type": "VARCHAR(191)",
                            "unique": True,
                            "nullable": False,
                        },
                        {"name": "created_at", "type": "DATETIME", "nullable": False},
                        {"name": "updated_at", "type": "DATETIME", "nullable": False},
                        {
                            "name": "updated_by",
                            "type": "INT UNSIGNED",
                            "nullable": True,
                            "foreign_key": "users.id",
                        },
                        {"name": "deleted_at", "type": "DATETIME", "nullable": True},
                    ]
                },
                "data": users_data,
            }

            # 寫入 JSON 檔案
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 成功備份 {len(users_data)} 筆使用者記錄")
            logger.info(f"備份檔案: {backup_path}")

            # 顯示備份統計
            active_users = len([u for u in users_data if u["deleted_at"] is None])
            deleted_users = len([u for u in users_data if u["deleted_at"] is not None])
            users_with_updated_by = len(
                [u for u in users_data if u["updated_by"] is not None]
            )

            logger.info(f"📊 備份統計:")
            logger.info(f"  - 總記錄數: {len(users_data)}")
            logger.info(f"  - 活躍使用者: {active_users}")
            logger.info(f"  - 已刪除使用者: {deleted_users}")
            logger.info(f"  - 有 updated_by 的使用者: {users_with_updated_by}")

            # 顯示前幾筆資料作為範例
            logger.info(f"📋 前 5 筆資料範例:")
            for i, user in enumerate(users_data[:5]):
                logger.info(
                    f"  {i+1}. ID {user['id']}: {user['name']} ({user['email']}) - updated_by: {user['updated_by']}"
                )

            return backup_path

    except Exception as e:
        logger.error(f"❌ 備份失敗: {str(e)}")
        raise


def verify_backup(backup_path):
    """驗證備份檔案"""

    logger.info(f"驗證備份檔案: {backup_path}")

    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        # 驗證備份資料結構
        required_keys = ["backup_info", "table_schema", "data"]
        for key in required_keys:
            if key not in backup_data:
                raise ValueError(f"備份檔案缺少必要欄位: {key}")

        # 驗證資料完整性
        users_data = backup_data["data"]
        logger.info(f"✅ 備份檔案驗證成功")
        logger.info(f"  - 記錄數: {len(users_data)}")
        logger.info(f"  - 備份時間: {backup_data['backup_info']['timestamp']}")

        return True

    except Exception as e:
        logger.error(f"❌ 備份檔案驗證失敗: {str(e)}")
        return False


def main():
    """主函數"""

    logger.info("=== 開始備份 users 資料表 ===")

    try:
        # 執行備份
        backup_path = backup_users_table()

        # 驗證備份
        if verify_backup(backup_path):
            logger.info("🎉 備份完成！可以安全地進行資料表結構修改")
        else:
            logger.error("❌ 備份驗證失敗，請檢查備份檔案")
            sys.exit(1)

    except Exception as e:
        logger.error(f"備份過程發生錯誤: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
