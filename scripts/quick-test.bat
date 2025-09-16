@echo off
echo 🚀 快速測試開始...
echo.

echo 🔧 自動格式化代碼...
poetry run black --check .
if %errorlevel% neq 0 (
    echo ❌ 代碼格式化檢查失敗
    exit /b 1
)
echo ✅ 代碼格式化檢查通過

echo.
echo 🧪 運行單元測試...
poetry run pytest tests/unit/ -v --tb=short
if %errorlevel% neq 0 (
    echo ❌ 單元測試失敗
    exit /b 1
)

echo.
echo ✅ 快速測試完成！
echo 💡 提示：運行完整 CI 流程請使用 scripts\run-ci-locally.bat
