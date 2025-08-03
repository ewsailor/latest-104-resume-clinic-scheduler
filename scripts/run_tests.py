#!/usr/bin/env python3
"""
測試運行腳本

設置環境變數來抑制棄用警告，並運行測試。
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """主函數"""
    # 設置環境變數來抑制警告
    os.environ["PYTHONWARNINGS"] = "ignore::PendingDeprecationWarning"

    # 獲取專案根目錄
    project_root = Path(__file__).parent.parent

    # 構建 pytest 命令
    cmd = [sys.executable, "-m", "poetry", "run", "pytest"] + sys.argv[
        1:
    ]  # 傳遞所有命令行參數

    # 運行測試
    try:
        subprocess.run(cmd, cwd=project_root, check=True)
    except subprocess.CalledProcessError as e:
        print(f"測試執行失敗，退出碼: {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
