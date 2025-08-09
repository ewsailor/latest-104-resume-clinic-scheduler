#!/usr/bin/env python3
"""
清理 Alembic 版本表的腳本。

用於重置 Alembic 遷移狀態。
"""

import sys
from pathlib import Path

from sqlalchemy import text

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.models.database import engine  # noqa: E402


def clear_alembic_version():
    """清理 Alembic 版本表"""
    try:
        with engine.connect() as conn:
            # 檢查是否存在 alembic_version 表
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = 'scheduler_db'
                AND table_name = 'alembic_version'
            """
                )
            )

            table_exists = result.fetchone()[0] > 0

            if table_exists:
                # 清理版本記錄
                conn.execute(text("DELETE FROM alembic_version"))
                conn.commit()
                print("✅ Alembic 版本記錄已清理")
            else:
                print("ℹ️  alembic_version 表不存在，無需清理")

    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    clear_alembic_version()
