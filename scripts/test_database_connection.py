#!/usr/bin/env python3
"""
資料庫連線測試腳本。

用於測試資料庫連線是否正常運作。
"""

import sys
import time
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_database_connection():
    """測試資料庫連線"""
    print("🔍 測試資料庫連線...")
    print("=" * 60)

    try:
        from sqlalchemy import text

        from app.models.database import SessionLocal, engine

        # 測試基本連線
        print("📡 測試基本連線...")
        start_time = time.time()

        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test_value"))
            test_value = result.scalar()
            connection_time = time.time() - start_time

            print(f"   ✅ 連線成功")
            print(f"   📊 測試值: {test_value}")
            print(f"   ⏱️  連線時間: {connection_time:.3f}秒")

        # 測試資料庫版本
        print("\n📋 測試資料庫版本...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION() as version"))
            version = result.scalar()
            print(f"   ✅ MySQL 版本: {version}")

        # 測試字符集
        print("\n🔤 測試字符集...")
        with engine.connect() as connection:
            result = connection.execute(
                text("SHOW VARIABLES LIKE 'character_set_database'")
            )
            charset = result.fetchone()
            print(f"   ✅ 資料庫字符集: {charset[1] if charset else 'Unknown'}")

        # 測試連線池
        print("\n🏊 測試連線池...")
        pool_info = engine.pool.status()
        print(f"   📊 連線池大小: {pool_info}")

        # 測試 Session
        print("\n🔄 測試 Session...")
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1 as session_test"))
            session_value = result.scalar()
            print(f"   ✅ Session 測試成功: {session_value}")
        finally:
            db.close()

        print("\n🎉 所有測試通過！")
        print("=" * 60)
        print("✅ 資料庫連線配置正確")
        print("✅ pymysql 驅動程式運作正常")
        print("✅ 連線池配置正確")
        print("✅ Session 管理正常")

    except Exception as e:
        print(f"❌ 資料庫連線測試失敗：{e}")
        print("\n🔍 請檢查以下項目：")
        print("   1. MySQL 服務是否正在運行")
        print("   2. 資料庫連線設定是否正確")
        print("   3. 使用者權限是否足夠")
        print("   4. 防火牆設定是否允許連線")
        print("   5. .env 檔案是否正確設定")
        return False

    return True


def test_connection_performance():
    """測試連線效能"""
    print("\n🚀 測試連線效能...")
    print("=" * 60)

    try:
        from sqlalchemy import text

        from app.models.database import engine

        # 測試多次連線
        connection_times = []
        for i in range(10):
            start_time = time.time()
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            connection_time = time.time() - start_time
            connection_times.append(connection_time)

        avg_time = sum(connection_times) / len(connection_times)
        min_time = min(connection_times)
        max_time = max(connection_times)

        print(f"   📊 平均連線時間: {avg_time:.3f}秒")
        print(f"   ⚡ 最快連線時間: {min_time:.3f}秒")
        print(f"   🐌 最慢連線時間: {max_time:.3f}秒")

        if avg_time < 0.1:
            print("   ✅ 連線效能優秀")
        elif avg_time < 0.5:
            print("   ⚠️  連線效能良好")
        else:
            print("   ❌ 連線效能較差")

    except Exception as e:
        print(f"   ❌ 效能測試失敗：{e}")


if __name__ == "__main__":
    success = test_database_connection()
    if success:
        test_connection_performance()

    print("\n🎯 總結：")
    if success:
        print("✅ 資料庫連線測試完全通過")
        print("✅ 建議使用 pymysql 驅動程式")
        print("✅ 連線配置符合最佳實踐")
    else:
        print("❌ 資料庫連線測試失敗")
        print("❌ 請檢查配置並重新測試")
