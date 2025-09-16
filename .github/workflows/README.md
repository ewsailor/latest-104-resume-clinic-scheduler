# GitHub Actions CI/CD 工作流程

本目錄包含專案的 CI/CD 自動化工作流程。

## 工作流程說明

### 1. `ci.yml` - 主要 CI/CD 流程

**觸發條件**：

- 推送到 `main` 或 `develop` 分支
- 對 `main` 或 `develop` 分支的 Pull Request

**執行的工作**：

1. **代碼品質檢查**：

   - Black 代碼格式化檢查
   - isort 導入排序檢查
   - flake8 代碼風格檢查
   - mypy 類型檢查

2. **測試執行**：

   - 支援 Python 3.9, 3.10, 3.11 多版本測試
   - 運行單元測試、整合測試、端到端測試
   - 生成測試覆蓋率報告

3. **安全檢查**：

   - safety 依賴漏洞檢查
   - bandit 安全代碼分析

4. **建構檢查**：

   - 建構應用程式
   - 上傳建構產物

5. **部署**：
   - 自動部署到測試環境（develop 分支）
   - 自動部署到生產環境（main 分支）

### 2. `test-only.yml` - 測試專用流程

**觸發條件**：

- 推送到 `main` 或 `develop` 分支（僅當測試相關文件變更時）
- Pull Request（僅當測試相關文件變更時）

**執行的工作**：

1. **快速測試**：基本測試驗證
2. **完整測試**：單元、整合、端到端測試
3. **測試報告**：生成詳細的測試結果報告

### 3. `dependency-update.yml` - 依賴更新檢查

**觸發條件**：

- 每週一自動執行
- 手動觸發

**執行的工作**：

1. **檢查過期依賴**
2. **安全漏洞檢查**
3. **自動創建更新 PR**（如果有更新）

## 使用方式

### 本地測試

```bash
# 安裝依賴
poetry install

# 運行代碼品質檢查
poetry run black --check .
poetry run isort --check-only .
poetry run flake8 .
poetry run mypy .

# 運行測試
poetry run pytest tests/unit/ -v
poetry run pytest tests/integration/ -v
poetry run pytest tests/e2e/ -v

# 生成測試覆蓋率報告
poetry run pytest --cov=app --cov-report=html --cov-report=xml
```

### 查看 CI/CD 狀態

1. 前往 GitHub 專案的 "Actions" 頁面
2. 查看各個工作流程的執行狀態
3. 下載測試報告和覆蓋率報告

### 環境變數設置

在 GitHub 專案設置中添加以下環境變數：

- `GITHUB_TOKEN`：自動生成，用於創建 PR
- 其他部署相關的環境變數（根據您的部署需求）

## 狀態徽章

在 README.md 中添加以下徽章來顯示 CI/CD 狀態：

```markdown
[![CI/CD Pipeline](https://github.com/your-username/your-repo/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/ci.yml)
[![Tests](https://github.com/your-username/your-repo/actions/workflows/test-only.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/test-only.yml)
[![codecov](https://codecov.io/gh/your-username/your-repo/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/your-repo)
```

## 故障排除

### 常見問題

1. **測試失敗**：

   - 檢查測試依賴是否正確安裝
   - 確認測試資料庫配置
   - 查看測試日誌了解具體錯誤

2. **代碼品質檢查失敗**：

   - 運行 `poetry run black .` 自動格式化代碼
   - 運行 `poetry run isort .` 自動排序導入
   - 根據 flake8 和 mypy 的建議修復問題

3. **安全檢查失敗**：
   - 更新有漏洞的依賴套件
   - 修復 bandit 報告的安全問題

### 獲取幫助

- 查看 GitHub Actions 的執行日誌
- 檢查專案的 Issues 頁面
- 參考各工具的官方文檔
