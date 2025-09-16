@echo off
echo 🚀 開始本地 CI/CD 流程...
echo.

echo 🐍 使用 Python 版本:
python --version
echo.

echo 📋 執行代碼品質檢查...
echo.

echo 🔍 檢查代碼格式化 (Black)...
poetry run black --check .
if %errorlevel% neq 0 (
    echo ❌ Black 檢查失敗
    exit /b 1
)
echo ✅ Black 檢查通過

echo.
echo 🔍 檢查導入排序 (isort)...
poetry run isort --check-only .
if %errorlevel% neq 0 (
    echo ❌ isort 檢查失敗
    exit /b 1
)
echo ✅ isort 檢查通過

echo.
echo 🔍 檢查代碼風格 (flake8)...
poetry run flake8 .
if %errorlevel% neq 0 (
    echo ❌ flake8 檢查失敗
    exit /b 1
)
echo ✅ flake8 檢查通過

echo.
echo 🔍 檢查型別註解 (mypy)...
poetry run mypy app/ --ignore-missing-imports
if %errorlevel% neq 0 (
    echo ❌ mypy 檢查失敗
    exit /b 1
)
echo ✅ mypy 檢查通過

echo.
echo 🔍 檢查安全漏洞 (bandit)...
poetry run bandit -r app/ --skip B101,B601
if %errorlevel% neq 0 (
    echo ❌ bandit 檢查失敗
    exit /b 1
)
echo ✅ bandit 檢查通過

echo.
echo 🧪 執行測試...
echo.

echo 🔍 運行單元測試...
poetry run pytest tests/unit/ -v --cov=app --cov-report=xml --cov-report=html
if %errorlevel% neq 0 (
    echo ❌ 單元測試失敗
    exit /b 1
)
echo ✅ 單元測試通過

echo.
echo 🔍 運行整合測試...
poetry run pytest tests/integration/ -v
if %errorlevel% neq 0 (
    echo ❌ 整合測試失敗
    exit /b 1
)
echo ✅ 整合測試通過

echo.
echo 🎯 測試覆蓋率報告...
poetry run coverage report --show-missing
if %errorlevel% neq 0 (
    echo ⚠️ 覆蓋率報告生成失敗，但測試通過
)

echo.
echo 🎉 CI/CD 流程完成！
echo 📊 覆蓋率報告已生成：htmlcov/index.html
echo 💡 提示：使用瀏覽器開啟 htmlcov/index.html 查看詳細覆蓋率報告
