#!/bin/bash

echo "🧹 清除 Python 快取文件..."
echo

# 切換到專案根目錄
cd "$(dirname "$0")/.."

# 統計清除的文件數量
removed_dirs=0
removed_files=0

# 刪除 __pycache__ 目錄
while IFS= read -r -d '' dir; do
    echo "🗑️  刪除目錄: $dir"
    rm -rf "$dir"
    ((removed_dirs++))
done < <(find . -type d -name "__pycache__" -print0 2>/dev/null)

# 刪除 .pyc 文件
while IFS= read -r -d '' file; do
    echo "🗑️  刪除文件: $file"
    rm -f "$file"
    ((removed_files++))
done < <(find . -name "*.pyc" -print0 2>/dev/null)

# 刪除 .pyo 文件
while IFS= read -r -d '' file; do
    echo "🗑️  刪除文件: $file"
    rm -f "$file"
    ((removed_files++))
done < <(find . -name "*.pyo" -print0 2>/dev/null)

echo
echo "✅ 清除完成！"
echo "📊 統計結果:"
echo "   - 刪除目錄: $removed_dirs 個"
echo "   - 刪除文件: $removed_files 個"
echo 