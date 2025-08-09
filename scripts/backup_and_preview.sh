#!/bin/bash

# Alembic 備份和預覽腳本
# 使用方法: ./scripts/backup_and_preview.sh "變更描述"
#
# 例如: ./scripts/backup_and_preview.sh "add_user_phone"

# 檢查參數
if [ -z "$1" ]; then
    echo "錯誤: 請提供變更描述"
    echo "使用方法: $0 \"變更描述\""
    echo "例如: $0 \"add_user_phone\""
    exit 1
fi

# 設定變數
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DESCRIPTION="$1"
MYSQL_PATH="/c/Program Files/MySQL/MySQL Server 8.0/bin"

# 檔案路徑
BACKUP_FILE="database/backups/backup_${TIMESTAMP}_before_${DESCRIPTION}.sql"
PREVIEW_FILE="alembic/sql_previews/preview_${TIMESTAMP}_${DESCRIPTION}.sql"

echo "=== Alembic 遷移準備腳本 ==="
echo "時間戳記: ${TIMESTAMP}"
echo "變更描述: ${DESCRIPTION}"
echo ""

# 1. 建立目錄（如果不存在）
mkdir -p database/backups
mkdir -p alembic/sql_previews

# 2. 備份資料庫
echo "📦 正在備份資料庫..."
"${MYSQL_PATH}/mysqldump.exe" \
    -u fastapi_user -pfastapi123 \
    --single-transaction \
    --no-tablespaces \
    scheduler_db > "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ 備份成功: ${BACKUP_FILE}"
else
    echo "❌ 備份失敗!"
    exit 1
fi

# 3. 生成 SQL 預覽
echo "📋 正在生成 SQL 預覽..."
poetry run alembic upgrade head --sql > "${PREVIEW_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ 預覽生成成功: ${PREVIEW_FILE}"
else
    echo "❌ 預覽生成失敗!"
    exit 1
fi

# 4. 顯示預覽內容
echo ""
echo "📄 SQL 預覽內容:"
echo "=================="
cat "${PREVIEW_FILE}"
echo "=================="
echo ""

# 5. 詢問是否執行遷移
read -p "🤔 是否要執行遷移? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    echo "🚀 正在執行遷移..."
    poetry run alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "✅ 遷移完成!"
    else
        echo "❌ 遷移失敗!"
        echo "💡 可以使用以下命令還原備份:"
        echo "   mysql -u fastapi_user -pfastapi123 scheduler_db < ${BACKUP_FILE}"
    fi
else
    echo "⏸️  遷移已取消"
    echo "💡 如果要手動執行遷移:"
    echo "   poetry run alembic upgrade head"
fi
