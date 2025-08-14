#!/usr/bin/env python3
"""
API 健康檢查測試腳本。

用於快速測試 API 伺服器是否正常運行。
"""

import json
import sys
from datetime import datetime

import requests


def test_health_endpoint(base_url="http://localhost:8000"):
    """測試健康檢查端點"""
    print(f"🏥 測試健康檢查端點: {base_url}/health")

    try:
        response = requests.get(f"{base_url}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("✅ 健康檢查通過")
            print(f"   狀態: {data.get('status', 'N/A')}")
            print(f"   時間戳: {data.get('timestamp', 'N/A')}")
            print(f"   版本: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ 健康檢查失敗: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器，請確認伺服器是否正在運行")
        return False
    except requests.exceptions.Timeout:
        print("❌ 請求超時")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def test_docs_endpoint(base_url="http://localhost:8000"):
    """測試 API 文件端點"""
    print(f"\n📚 測試 API 文件端點: {base_url}/docs")

    try:
        response = requests.get(f"{base_url}/docs", timeout=5)

        if response.status_code == 200:
            print("✅ API 文件可訪問")
            return True
        else:
            print(f"❌ API 文件無法訪問: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def test_givers_endpoint(base_url="http://localhost:8000"):
    """測試 Givers API 端點"""
    print(f"\n👥 測試 Givers API 端點: {base_url}/api/givers")

    try:
        response = requests.get(f"{base_url}/api/givers", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("✅ Givers API 正常")
            print(f"   返回 {len(data)} 個 Giver")
            return True
        else:
            print(f"❌ Givers API 失敗: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def test_schedules_endpoint(base_url="http://localhost:8000"):
    """測試 Schedules API 端點"""
    print(f"\n📅 測試 Schedules API 端點: {base_url}/api/schedules")

    try:
        response = requests.get(f"{base_url}/api/schedules", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("✅ Schedules API 正常")
            print(f"   返回 {len(data)} 個時段")
            return True
        else:
            print(f"❌ Schedules API 失敗: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 50)
    print("104 履歷診療室排程系統 - API 健康檢查")
    print("=" * 50)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 預設基礎 URL
    base_url = "http://localhost:8000"

    # 如果提供了命令列參數，使用指定的 URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"🌐 基礎 URL: {base_url}")
    print()

    # 執行測試
    tests = [
        test_health_endpoint,
        test_docs_endpoint,
        test_givers_endpoint,
        test_schedules_endpoint,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test(base_url):
            passed += 1

    # 顯示結果
    print("\n" + "=" * 50)
    print("📊 測試結果")
    print("=" * 50)
    print(f"✅ 通過: {passed}/{total}")
    print(f"❌ 失敗: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 所有測試通過！API 伺服器運行正常。")
        print("\n🔧 下一步:")
        print("   1. 在 Postman 中匯入集合檔案")
        print("   2. 設定環境變數 base_url = " + base_url)
        print("   3. 開始測試各個 API 端點")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 個測試失敗，請檢查伺服器狀態。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
