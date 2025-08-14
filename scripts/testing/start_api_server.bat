@echo off
chcp 65001 >nul
echo ==================================================
echo 104 履歷診療室排程系統 - API 伺服器
echo ==================================================
echo.

REM 檢查是否在正確的目錄
if not exist "app\main.py" (
    echo ❌ 找不到 app\main.py，請在專案根目錄執行此腳本
    pause
    exit /b 1
)

echo 📁 工作目錄: %CD%
echo.

REM 設定環境變數
set APP_ENV=development
set DEBUG=true

echo 🚀 啟動 API 伺服器...
echo 📍 主機: 0.0.0.0
echo 🔌 端口: 8000
echo 🔄 自動重載: 是
echo.

echo 📚 API 文件:
echo    Swagger UI: http://localhost:8000/docs
echo    ReDoc: http://localhost:8000/redoc
echo.

echo 🏥 健康檢查:
echo    GET http://localhost:8000/health
echo.

echo 🔧 Postman 測試:
echo    基礎 URL: http://localhost:8000
echo    集合檔案: docs/testing/104_resume_clinic_api_collection.json
echo.

echo ==================================================
echo.

REM 啟動 uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 👋 伺服器已停止
pause
