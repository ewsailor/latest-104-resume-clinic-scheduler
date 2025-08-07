@echo off
REM 測試執行批處理檔案
REM 自動設置環境變數來抑制第三方套件的警告

echo 執行測試，抑制 multipart 警告...
echo.

REM 設置環境變數來抑制警告
set PYTHONWARNINGS=ignore::PendingDeprecationWarning

REM 執行測試
poetry run pytest --cov=app.models.database --cov-report=term-missing -v %*

REM 檢查退出碼
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 測試執行成功！
) else (
    echo.
    echo ❌ 測試執行失敗，退出碼: %ERRORLEVEL%
)

pause
