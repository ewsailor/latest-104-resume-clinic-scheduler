#!/usr/bin/env python3
"""
資料庫配置測試腳本。

用於測試資料庫連線配置是否正確。
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_database_config():
    """測試資料庫配置"""
    print("🔍 測試資料庫配置...")
    print("=" * 60)

    # 檢查環境變數
    print("📋 環境變數檢查：")
    mysql_vars = [
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
        "MYSQL_CHARSET",
    ]

    for var in mysql_vars:
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var:
                print(f"   {var}: {'*' * len(value)}")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: ❌ 未設定")

    print()

    # 測試 settings 配置
    print("⚙️  Settings 配置檢查：")
    try:
        from app.core import settings

        print(f"   mysql_host: {settings.mysql_host}")
        print(f"   mysql_port: {settings.mysql_port}")
        print(f"   mysql_user: {settings.mysql_user}")
        print(f"   mysql_password: {'*' * 8 if settings.mysql_password else 'None'}")
        print(f"   mysql_database: {settings.mysql_database}")
        print(f"   mysql_charset: {settings.mysql_charset}")

        print()
        print("🔗 連線字串：")
        connection_string = settings.mysql_connection_string
        # 隱藏密碼
        if settings.mysql_password:
            password = settings.mysql_password.get_secret_value()
            masked_string = connection_string.replace(password, '*' * len(password))
            print(f"   {masked_string}")
        else:
            print(f"   {connection_string}")

    except Exception as e:
        print(f"   ❌ Settings 載入失敗：{e}")

    print()
    print("🎯 建議：")
    print("   1. 建立 .env 檔案並設定以下環境變數：")
    print("      MYSQL_HOST=localhost")
    print("      MYSQL_PORT=3306")
    print("      MYSQL_USER=fastapi_user")
    print("      MYSQL_PASSWORD=fastapi123")
    print("      MYSQL_DATABASE=scheduler_db")
    print("      MYSQL_CHARSET=utf8mb4")
    print("   2. 確保 MySQL 服務正在運行")
    print("   3. 確保使用者存在且有適當權限")


if __name__ == "__main__":
    test_database_config()
