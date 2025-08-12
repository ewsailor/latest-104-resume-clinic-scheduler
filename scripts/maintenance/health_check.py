#!/usr/bin/env python3
"""
健康檢查工具。

用於檢查應用程式的健康狀態和端點可用性。
"""

import sys
import time
from pathlib import Path
from typing import Any

import requests

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core import settings


class HealthChecker:
    """
    健康檢查器類別。

    提供應用程式健康狀態檢查功能。
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化健康檢查器。

        Args:
            base_url: 應用程式基礎 URL
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.timeout = 10  # 10 秒超時

    def check_ping(self) -> dict[str, Any]:
        """
        檢查 ping 端點。

        Returns:
            dict: 檢查結果
        """
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/ping")
            response_time = time.time() - start_time

            return {
                "endpoint": "/ping",
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "data": response.json() if response.status_code == 200 else None,
                "error": None,
            }
        except Exception as e:
            return {
                "endpoint": "/ping",
                "status": "error",
                "status_code": None,
                "response_time": round(time.time() - start_time, 3),
                "data": None,
                "error": str(e),
            }

    def check_health(self) -> dict[str, Any]:
        """
        檢查 health 端點。

        Returns:
            dict: 檢查結果
        """
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health")
            response_time = time.time() - start_time

            return {
                "endpoint": "/health",
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "data": response.json() if response.status_code == 200 else None,
                "error": None,
            }
        except Exception as e:
            return {
                "endpoint": "/health",
                "status": "error",
                "status_code": None,
                "response_time": round(time.time() - start_time, 3),
                "data": None,
                "error": str(e),
            }

    def check_root(self) -> dict[str, Any]:
        """
        檢查根端點。

        Returns:
            dict: 檢查結果
        """
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/")
            response_time = time.time() - start_time

            return {
                "endpoint": "/",
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "content_type": response.headers.get("content-type", ""),
                "content_length": len(response.content),
                "error": None,
            }
        except Exception as e:
            return {
                "endpoint": "/",
                "status": "error",
                "status_code": None,
                "response_time": round(time.time() - start_time, 3),
                "content_type": None,
                "content_length": 0,
                "error": str(e),
            }

    def comprehensive_check(self) -> dict[str, Any]:
        """
        執行全面健康檢查。

        Returns:
            dict: 完整檢查結果
        """
        print(f"🔍 健康檢查開始 - {self.base_url}")
        print("=" * 60)

        # 執行各項檢查
        ping_result = self.check_ping()
        health_result = self.check_health()
        root_result = self.check_root()

        # 計算總體狀態
        all_results = [ping_result, health_result, root_result]
        success_count = sum(1 for r in all_results if r["status"] == "success")
        total_count = len(all_results)

        overall_status = "healthy" if success_count == total_count else "unhealthy"

        # 顯示結果
        self._print_result("Ping 測試", ping_result)
        self._print_result("健康檢查", health_result)
        self._print_result("首頁測試", root_result)

        # 總結
        print(f"\n📊 檢查總結：")
        print(f"✅ 成功：{success_count}/{total_count}")
        print(f"❌ 失敗：{total_count - success_count}/{total_count}")
        print(f"🎯 總體狀態：{overall_status}")

        return {
            "overall_status": overall_status,
            "success_count": success_count,
            "total_count": total_count,
            "results": {
                "ping": ping_result,
                "health": health_result,
                "root": root_result,
            },
        }

    def _print_result(self, title: str, result: dict[str, Any]) -> None:
        """印出檢查結果。"""
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {title}")
        print(f"   端點：{result['endpoint']}")
        print(f"   狀態碼：{result['status_code']}")
        print(f"   回應時間：{result['response_time']}s")

        if result["error"]:
            print(f"   錯誤：{result['error']}")
        elif result["endpoint"] == "/ping" and result["data"]:
            print(f"   回應：{result['data']}")
        elif result["endpoint"] == "/health" and result["data"]:
            print(f"   應用程式：{result['data'].get('app_name', 'N/A')}")
            print(f"   版本：{result['data'].get('version', 'N/A')}")
            print(f"   環境：{result['data'].get('environment', 'N/A')}")
        elif result["endpoint"] == "/":
            print(f"   內容類型：{result['content_type']}")
            print(f"   內容長度：{result['content_length']} bytes")

        print()


def main():
    """主函數。"""
    import argparse

    parser = argparse.ArgumentParser(description="健康檢查工具")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="應用程式 URL (預設: http://localhost:8000)",
    )
    parser.add_argument("--ping-only", action="store_true", help="只檢查 ping 端點")
    parser.add_argument("--health-only", action="store_true", help="只檢查 health 端點")

    args = parser.parse_args()

    checker = HealthChecker(args.url)

    if args.ping_only:
        result = checker.check_ping()
        checker._print_result("Ping 測試", result)
    elif args.health_only:
        result = checker.check_health()
        checker._print_result("健康檢查", result)
    else:
        result = checker.comprehensive_check()

        # 根據結果設定退出碼
        if result["overall_status"] != "healthy":
            sys.exit(1)


if __name__ == "__main__":
    main()
