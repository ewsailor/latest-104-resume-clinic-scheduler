# 104 Resume Clinic Scheduler - Makefile
# 提供常用的開發和部署命令

.PHONY: help install dev test lint format export-postman watch-export setup-hooks clean

# 預設目標
help:
	@echo "🚀 104 Resume Clinic Scheduler - 可用命令:"
	@echo ""
	@echo "📦 安裝和設定:"
	@echo "  install        - 安裝依賴套件"
	@echo "  setup-hooks    - 設定 Git hooks 自動匯出到 Postman"
	@echo ""
	@echo "🔧 開發:"
	@echo "  dev            - 啟動開發伺服器"
	@echo "  test           - 執行測試"
	@echo "  lint           - 程式碼檢查"
	@echo "  format         - 程式碼格式化"
	@echo ""
	@echo "📤 Postman 匯出:"
	@echo "  export-postman - 手動匯出到 Postman"
	@echo "  watch-export   - 監控檔案變更並自動匯出"
	@echo ""
	@echo "🧹 清理:"
	@echo "  clean          - 清理暫存檔案"

# 安裝依賴套件
install:
	@echo "📦 安裝依賴套件..."
	poetry install
	@echo "✅ 安裝完成"

# 啟動開發伺服器
dev:
	@echo "🚀 啟動開發伺服器..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 執行測試
test:
	@echo "🧪 執行測試..."
	poetry run pytest

# 程式碼檢查
lint:
	@echo "🔍 程式碼檢查..."
	poetry run flake8 app tests
	poetry run mypy app

# 程式碼格式化
format:
	@echo "✨ 程式碼格式化..."
	poetry run black app tests
	poetry run isort app tests

# 手動匯出到 Postman
export-postman:
	@echo "📤 匯出到 Postman..."
	python scripts/export_to_postman.py

# 監控檔案變更並自動匯出
watch-export:
	@echo "👀 啟動檔案監控..."
	python scripts/watch_and_export.py

# 設定 Git hooks
setup-hooks:
	@echo "🔧 設定 Git hooks..."
	python scripts/setup_git_hooks.py

# 清理暫存檔案
clean:
	@echo "🧹 清理暫存檔案..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	@echo "✅ 清理完成"
