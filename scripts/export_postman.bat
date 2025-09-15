@echo off
REM Windows 批次腳本：自動匯出到 Postman

echo 🚀 開始匯出到 Postman...

REM 檢查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安裝或不在 PATH 中
    pause
    exit /b 1
)

REM 檢查是否在正確的目錄
if not exist "app\main.py" (
    echo ❌ 請在專案根目錄執行此腳本
    pause
    exit /b 1
)

REM 執行匯出腳本
echo 🔄 正在匯出 OpenAPI JSON...
python scripts\export_to_postman.py

if errorlevel 1 (
    echo ❌ 匯出失敗
    pause
    exit /b 1
)

echo ✅ 匯出完成！
echo.
echo 📁 匯出檔案位置:
echo    - exports\openapi_latest.json
echo    - exports\postman_*.json
echo.
echo 💡 提示:
echo    - 設定 POSTMAN_API_KEY 環境變數可自動更新 Postman 集合
echo    - 使用 "make watch-export" 可監控檔案變更並自動匯出
echo.
pause
