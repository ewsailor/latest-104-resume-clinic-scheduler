@echo off
chcp 65001 >nul
REM Alembic 備份和預覽腳本 (Windows 版本)
REM 使用方法: scripts\backup_and_preview.bat "變更描述"
REM 例如: scripts\backup_and_preview.bat "add_user_phone"

if "%1"=="" (
    echo 錯誤: 請提供變更描述
    echo 使用方法: %0 "變更描述"
    echo 例如: %0 "add_user_phone"
    exit /b 1
)

REM 設定變數
for /f "tokens=2 delims==" %%I in ('wmic OS Get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,4%
set DESCRIPTION=%~1
set MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin

REM 檔案路徑 - 處理包含空格的描述
set "DESCRIPTION_SAFE=%DESCRIPTION: =_%"
set "BACKUP_FILE=database\backups\backup_%TIMESTAMP%_before_%DESCRIPTION_SAFE%.sql"
set "PREVIEW_FILE=alembic\sql_previews\preview_%TIMESTAMP%_%DESCRIPTION_SAFE%.sql"

echo === Alembic 遷移準備腳本 ===
echo 時間戳記: %TIMESTAMP%
echo 變更描述: %DESCRIPTION%
echo.

REM 1. 建立目錄（如果不存在）
if not exist database\backups mkdir database\backups
if not exist alembic\sql_previews mkdir alembic\sql_previews

REM 2. 備份資料庫
echo 📦 正在備份資料庫...
"%MYSQL_PATH%\mysqldump.exe" -u fastapi_user -pfastapi123 --single-transaction --no-tablespaces scheduler_db > "%BACKUP_FILE%"

if %errorlevel% equ 0 (
    echo ✅ 備份成功: %BACKUP_FILE%
) else (
    echo ❌ 備份失敗!
    exit /b 1
)

REM 3. 生成 SQL 預覽
echo 📋 正在生成 SQL 預覽...
poetry run alembic upgrade head --sql > "%PREVIEW_FILE%"

if %errorlevel% equ 0 (
    echo ✅ 預覽生成成功: %PREVIEW_FILE%
) else (
    echo ❌ 預覽生成失敗!
    exit /b 1
)

REM 4. 顯示預覽內容
echo.
echo 📄 SQL 預覽內容:
echo ==================
type "%PREVIEW_FILE%"
echo ==================
echo.

REM 5. 詢問是否執行遷移
set /p confirm="🤔 是否要執行遷移? (y/N): "
if /i "%confirm%"=="y" (
    echo 🚀 正在執行遷移...
    poetry run alembic upgrade head
    if %errorlevel% equ 0 (
        echo ✅ 遷移完成!
    ) else (
        echo ❌ 遷移失敗!
        echo 💡 可以使用以下命令還原備份:
        echo    mysql -u fastapi_user -pfastapi123 scheduler_db ^< "%BACKUP_FILE%"
    )
) else (
    echo ⏸️  遷移已取消
    echo 💡 如果要手動執行遷移:
    echo    poetry run alembic upgrade head
)
