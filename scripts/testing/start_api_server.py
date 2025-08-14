#!/usr/bin/env python3
"""
API 伺服器啟動腳本。

用於快速啟動 104 履歷診療室排程系統的 API 伺服器，
方便使用 Postman 進行測試。
"""

import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """檢查必要的依賴是否已安裝"""
    try:
        import fastapi
        import uvicorn

        print("✅ 依賴檢查通過")
        return True
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        print("請執行: pip install uvicorn fastapi")
        return False


def check_database():
    """檢查資料庫連線"""
    try:
        from sqlalchemy import text

        from app.models.database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 資料庫連線正常")
        return True
    except Exception as e:
        print(f"❌ 資料庫連線失敗: {e}")
        print("請確認資料庫服務正在運行")
        return False


def start_server(host="0.0.0.0", port=8000, reload=True):
    """啟動 API 伺服器"""
    print(f"🚀 啟動 API 伺服器...")
    print(f"📍 主機: {host}")
    print(f"🔌 端口: {port}")
    print(f"🔄 自動重載: {'是' if reload else '否'}")
    print()

    # 設定環境變數
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("DEBUG", "true")

    # 啟動 uvicorn
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
        "--reload" if reload else "",
    ]

    # 移除空字串
    cmd = [arg for arg in cmd if arg]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 伺服器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 啟動失敗: {e}")
        return False

    return True


def main():
    """主函數"""
    print("=" * 50)
    print("104 履歷診療室排程系統 - API 伺服器")
    print("=" * 50)
    print()

    # 檢查專案結構
    project_root = Path(__file__).parent.parent.parent
    if not (project_root / "app" / "main.py").exists():
        print("❌ 找不到 app/main.py，請在專案根目錄執行此腳本")
        return False

    # 切換到專案根目錄
    os.chdir(project_root)
    print(f"📁 工作目錄: {os.getcwd()}")
    print()

    # 檢查依賴
    if not check_dependencies():
        return False

    # 檢查資料庫
    if not check_database():
        print("⚠️  資料庫連線失敗，但繼續啟動伺服器...")
        print()

    # 顯示 API 資訊
    print("📚 API 文件:")
    print(f"   Swagger UI: http://localhost:8000/docs")
    print(f"   ReDoc: http://localhost:8000/redoc")
    print()
    print("🏥 健康檢查:")
    print(f"   GET http://localhost:8000/health")
    print()
    print("🔧 Postman 測試:")
    print(f"   基礎 URL: http://localhost:8000")
    print(f"   集合檔案: docs/testing/104_resume_clinic_api_collection.json")
    print()
    print("=" * 50)
    print()

    # 啟動伺服器
    return start_server()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
