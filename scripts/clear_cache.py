#!/usr/bin/env python3
"""
清除 Python 快取文件的腳本。

這個腳本會清除專案中的所有 Python 快取文件，包括：
- __pycache__ 目錄
- .pyc 文件
- .pyo 文件
"""

import shutil  # 刪除目錄和文件
import sys  # 退出腳本
from pathlib import Path


def clear_python_cache():
    """清除 Python 快取文件"""
    print("🧹 開始清除 Python 快取文件...")

    # 獲取專案根目錄
    project_root = Path(__file__).parent.parent.parent
    print(f"📁 專案根目錄: {project_root}")

    # 統計清除的文件數量
    removed_dirs = 0
    removed_files = 0

    # 清除 __pycache__ 目錄
    for pycache_dir in project_root.rglob("__pycache__"):  # 遞迴搜尋 __pycache__ 目錄
        try:
            shutil.rmtree(pycache_dir)  # 刪除目錄
            print(f"🗑️  已刪除目錄: {pycache_dir}")
            removed_dirs += 1
        except Exception as e:
            print(f"❌ 刪除目錄失敗 {pycache_dir}: {e}")

    # 清除 .pyc 文件
    for pyc_file in project_root.rglob("*.pyc"):
        try:
            pyc_file.unlink()  # 刪除文件
            print(f"🗑️  已刪除文件: {pyc_file}")
            removed_files += 1
        except Exception as e:
            print(f"❌ 刪除文件失敗 {pyc_file}: {e}")

    # 清除 .pyo 文件
    for pyo_file in project_root.rglob("*.pyo"):
        try:
            pyo_file.unlink()  # 刪除文件
            print(f"🗑️  已刪除文件: {pyo_file}")
            removed_files += 1
        except Exception as e:
            print(f"❌ 刪除文件失敗 {pyo_file}: {e}")

    print("\n✅ 清除完成！")
    print("📊 統計結果:")
    print(f"   - 刪除目錄: {removed_dirs} 個")
    print(f"   - 刪除文件: {removed_files} 個")

    # 驗證清除結果
    remaining_cache = (
        list(project_root.rglob("__pycache__"))
        + list(project_root.rglob("*.pyc"))
        + list(project_root.rglob("*.pyo"))
    )

    if remaining_cache:
        print(f"⚠️  警告: 仍有 {len(remaining_cache)} 個快取文件未清除")
        for item in remaining_cache[:5]:  # 只顯示前5個
            print(f"   - {item}")
        if len(remaining_cache) > 5:
            print(f"   ... 還有 {len(remaining_cache) - 5} 個文件")
    else:
        print("🎉 所有快取文件已完全清除！")


if __name__ == "__main__":
    try:
        clear_python_cache()
    except KeyboardInterrupt:
        print("\n⏹️  操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        sys.exit(1)
