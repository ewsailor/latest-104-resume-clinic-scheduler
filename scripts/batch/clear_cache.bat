@echo off
echo 🧹 清除 Python 快取文件...
echo.

REM 切換到專案根目錄
cd /d "%~dp0.."

REM 刪除 __pycache__ 目錄
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo 🗑️  刪除目錄: %%d
    rmdir /s /q "%%d" 2>nul
)

REM 刪除 .pyc 文件
for /r . %%f in (*.pyc) do @if exist "%%f" (
    echo 🗑️  刪除文件: %%f
    del "%%f" 2>nul
)

REM 刪除 .pyo 文件
for /r . %%f in (*.pyo) do @if exist "%%f" (
    echo 🗑️  刪除文件: %%f
    del "%%f" 2>nul
)

echo.
echo ✅ 快取文件清除完成！
echo.
pause 