#!/usr/bin/env python3
"""
批量替換測試檔案中的 print 語句為統一的日誌記錄。

這個腳本會掃描所有測試檔案，將 print() 語句替換為 log_test_info() 調用。
"""

import os
import re
from pathlib import Path


def replace_print_statements(file_path: Path) -> bool:
    """
    替換檔案中的 print 語句。

    Args:
        file_path: 要處理的檔案路徑

    Returns:
        bool: 是否有修改
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 檢查是否已經導入了 log_test_info
        if 'from tests.logger import log_test_info' not in content:
            # 在 import 區塊後添加導入語句
            import_pattern = r'^(\s*from\s+.*\n)+'
            match = re.search(import_pattern, content, re.MULTILINE)
            if match:
                import_end = match.end()
                content = (
                    content[:import_end]
                    + 'from tests.logger import log_test_info\n'
                    + content[import_end:]
                )

        # 替換 print 語句
        # 匹配 print("訊息") 或 print('訊息') 格式
        print_pattern = r'print\("([^"]*)"\)'
        content = re.sub(print_pattern, r'log_test_info("\1")', content)

        print_pattern = r"print\('([^']*)'\)"
        content = re.sub(print_pattern, r"log_test_info('\1')", content)

        # 如果有修改，寫回檔案
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"處理檔案 {file_path} 時發生錯誤: {e}")
        return False


def main():
    """主函數"""
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / 'tests'

    if not tests_dir.exists():
        print(f"測試目錄不存在: {tests_dir}")
        return

    # 統計資訊
    total_files = 0
    modified_files = 0

    # 掃描所有 Python 測試檔案
    for py_file in tests_dir.rglob('*.py'):
        if py_file.name.startswith('__'):
            continue

        total_files += 1
        print(f"處理檔案: {py_file.relative_to(project_root)}")

        if replace_print_statements(py_file):
            modified_files += 1
            print(f"  ✓ 已修改")
        else:
            print(f"  - 無需修改")

    print(f"\n處理完成:")
    print(f"  總檔案數: {total_files}")
    print(f"  修改檔案數: {modified_files}")


if __name__ == "__main__":
    main()
