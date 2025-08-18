#!/usr/bin/env python3
"""
清除 Python 快取文件的腳本。

這個腳本會清除專案中的所有 Python 快取文件，包括：
- __pycache__ 目錄
- .pyc 文件
- .pyo 文件

使用方法:
    python scripts/clear_cache.py [--include-venv]

選項:
    --include-venv    同時清除虛擬環境中的快取文件
"""

import argparse  # 解析命令行參數
import shutil  # 刪除目錄和文件
import sys  # 退出腳本
from pathlib import Path


def clear_python_cache(include_venv=False):
    """清除 Python 快取文件"""
    print("🧹 開始清除 Python 快取文件...")

    # 獲取專案根目錄
    project_root = Path(__file__).parent.parent
    print(f"📁 專案根目錄: {project_root}")

    # 定義要排除的目錄（這些目錄通常很大且不需要清除快取）
    exclude_dirs = {
        '.git',
        '.svn',
        '.hg',  # 版本控制目錄
        'node_modules',  # Node.js 模組
        'dist',
        'build',  # 建置目錄
        '.pytest_cache',  # pytest 快取
        'htmlcov',  # 測試覆蓋率報告
        'logs',  # 日誌目錄
        'alembic/versions',  # 資料庫遷移版本
    }

    # 如果不包含虛擬環境，則排除虛擬環境目錄
    if not include_venv:
        exclude_dirs.update(
            {
                '.venv',
                'venv',
                'env',  # 虛擬環境
            }
        )

    # 定義要優先檢查的 Python 目錄
    priority_dirs = ['app', 'tests', 'scripts', 'alembic']
    if include_venv:
        priority_dirs.append('.venv')

    # 統計清除的文件數量
    removed_dirs = 0
    removed_files = 0
    cache_items = []
    failed_items = []

    print("🔍 搜尋快取文件...")

    # 首先檢查優先目錄（這些目錄最可能有快取文件）
    for priority_dir in priority_dirs:
        priority_path = project_root / priority_dir
        if priority_path.exists():
            print(f"  📂 檢查 {priority_dir} 目錄...")

            # 搜尋 __pycache__ 目錄
            for pycache_dir in priority_path.rglob("__pycache__"):
                if not any(exclude in str(pycache_dir) for exclude in exclude_dirs):
                    if pycache_dir.exists():
                        cache_items.append(('dir', pycache_dir))

            # 搜尋 .pyc 和 .pyo 文件
            for pyc_file in priority_path.rglob("*.pyc"):
                if not any(exclude in str(pyc_file) for exclude in exclude_dirs):
                    if pyc_file.exists():
                        cache_items.append(('file', pyc_file))

            for pyo_file in priority_path.rglob("*.pyo"):
                if not any(exclude in str(pyo_file) for exclude in exclude_dirs):
                    if pyo_file.exists():
                        cache_items.append(('file', pyo_file))

    # 然後檢查其他目錄（但跳過已知的大型目錄）
    print("  📂 檢查其他目錄...")
    for item in project_root.iterdir():
        if (
            item.is_dir()
            and item.name not in exclude_dirs
            and item.name not in priority_dirs
        ):
            # 只檢查第一層的 __pycache__ 目錄
            pycache_dir = item / "__pycache__"
            if pycache_dir.exists():
                cache_items.append(('dir', pycache_dir))

            # 檢查 .pyc 和 .pyo 文件
            for pyc_file in item.glob("*.pyc"):
                if pyc_file.exists():
                    cache_items.append(('file', pyc_file))
            for pyo_file in item.glob("*.pyo"):
                if pyo_file.exists():
                    cache_items.append(('file', pyo_file))

    print(f"📊 找到 {len(cache_items)} 個快取項目")

    if not cache_items:
        print("✅ 沒有找到需要清除的快取文件！")
        return

    # 清除找到的項目
    print("🗑️  開始清除...")
    for i, (item_type, item_path) in enumerate(cache_items, 1):
        try:
            # 再次檢查項目是否存在（可能在搜尋和刪除之間被其他進程刪除）
            if not item_path.exists():
                print(f"⚠️  跳過已不存在的項目: {item_path}")
                continue

            if item_type == 'dir':
                shutil.rmtree(item_path)
                removed_dirs += 1
                print(f"  ✅ 已刪除目錄: {item_path}")
            else:  # file
                item_path.unlink()
                removed_files += 1
                print(f"  ✅ 已刪除文件: {item_path}")

            # 顯示進度
            if i % 10 == 0 or i == len(cache_items):
                print(
                    f"  📈 進度: {i}/{len(cache_items)} ({i/len(cache_items)*100:.1f}%)"
                )

        except FileNotFoundError:
            print(f"⚠️  文件已不存在: {item_path}")
        except PermissionError as e:
            error_msg = f"權限不足: {e}"
            print(f"❌ 刪除失敗 {item_path}: {error_msg}")
            failed_items.append((item_type, item_path, error_msg))
        except Exception as e:
            error_msg = f"未知錯誤: {e}"
            print(f"❌ 刪除失敗 {item_path}: {error_msg}")
            failed_items.append((item_type, item_path, error_msg))

    print("\n✅ 清除完成！")
    print("📊 統計結果:")
    print(f"   - 成功刪除目錄: {removed_dirs} 個")
    print(f"   - 成功刪除文件: {removed_files} 個")

    if failed_items:
        print(f"   - 失敗項目: {len(failed_items)} 個")
        print("\n❌ 失敗項目詳情:")
        for item_type, item_path, error in failed_items:
            print(f"     {item_type}: {item_path} - {error}")

    # 快速驗證（只檢查主要目錄）
    print("\n🔍 快速驗證...")
    remaining_count = 0

    for priority_dir in priority_dirs:
        priority_path = project_root / priority_dir
        if priority_path.exists():
            remaining = list(priority_path.rglob("__pycache__"))
            remaining_count += len(remaining)

    if remaining_count > 0:
        print(f"⚠️  警告: 仍有 {remaining_count} 個快取目錄可能存在")
        print("💡 建議: 可能需要管理員權限或檢查文件鎖定狀態")
    else:
        print("🎉 所有快取文件已完全清除！")


def main():
    """主函數，處理命令行參數"""
    parser = argparse.ArgumentParser(
        description="清除 Python 快取文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python scripts/clear_cache.py              # 清除專案快取文件
  python scripts/clear_cache.py --include-venv  # 同時清除虛擬環境快取文件
        """,
    )

    parser.add_argument(
        '--include-venv', action='store_true', help='同時清除虛擬環境中的快取文件'
    )

    args = parser.parse_args()

    try:
        clear_python_cache(include_venv=args.include_venv)
    except KeyboardInterrupt:
        print("\n⏹️  操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
