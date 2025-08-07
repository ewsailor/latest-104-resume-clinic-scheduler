#!/usr/bin/env python3
"""
測試執行腳本。

自動設置環境變數來抑制第三方套件的警告，並執行測試。
"""

import os
import subprocess
import sys
from pathlib import Path


def run_tests():
    """
    執行測試，自動設置環境變數來抑制警告。
    """
    # 設置環境變數來抑制警告
    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore::PendingDeprecationWarning"

    # 獲取專案根目錄
    project_root = Path(__file__).parent.parent

    # 構建測試命令
    test_command = [
        "poetry",
        "run",
        "pytest",
        "--cov=app.models.database",
        "--cov-report=term-missing",
        "-v",
    ]

    # 如果有額外的參數，添加到命令中
    if len(sys.argv) > 1:
        test_command.extend(sys.argv[1:])

    print(f"執行測試命令: {' '.join(test_command)}")
    print(f"環境變數 PYTHONWARNINGS: {env['PYTHONWARNINGS']}")
    print("-" * 80)

    try:
        # 執行測試
        result = subprocess.run(test_command, cwd=project_root, env=env, check=True)
        print("-" * 80)
        print("✅ 測試執行成功！")
        return result.returncode

    except subprocess.CalledProcessError as e:
        print("-" * 80)
        print(f"❌ 測試執行失敗，退出碼: {e.returncode}")
        return e.returncode
    except Exception as e:
        print("-" * 80)
        print(f"❌ 執行測試時發生錯誤: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
