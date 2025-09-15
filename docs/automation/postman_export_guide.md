# Postman 自動匯出指南

## 概述

本指南說明如何設定自動化流程，在更新路由或 schema 後自動從 Swagger 匯出 JSON 並更新 Postman 集合。

## 快速開始

### 1. 安裝依賴套件

```bash
# 安裝 Python 依賴
poetry install

# 安裝檔案監控依賴（用於監控模式）
poetry add watchdog
```

### 2. 設定 Postman API 金鑰

1. 前往 [Postman API Keys](https://web.postman.co/settings/me/api-keys)
2. 建立新的 API 金鑰
3. 設定環境變數：

```bash
# Linux/macOS
export POSTMAN_API_KEY="your_api_key_here"
export POSTMAN_COLLECTION_ID="your_collection_id_here"  # 可選

# Windows
set POSTMAN_API_KEY=your_api_key_here
set POSTMAN_COLLECTION_ID=your_collection_id_here
```

或建立 `.env.postman` 檔案：

```bash
POSTMAN_API_KEY=your_api_key_here
POSTMAN_COLLECTION_ID=your_collection_id_here
```

## 使用方法

### 方法 1：手動匯出

```bash
# 使用 Python 腳本
python scripts/export_to_postman.py

# 使用 Makefile
make export-postman

# 使用 Windows 批次檔
scripts\export_postman.bat
```

### 方法 2：監控模式（推薦）

監控檔案變更並自動匯出：

```bash
# 啟動監控
python scripts/watch_and_export.py

# 或使用 Makefile
make watch-export
```

監控的檔案包括：

- `app/routers/*.py`
- `app/schemas/*.py`
- `app/models/*.py`
- `app/main.py`
- `app/factory.py`

### 方法 3：Git Hooks（自動化）

設定 Git hooks 在提交時自動匯出：

```bash
# 設定 Git hooks
python scripts/setup_git_hooks.py

# 或使用 Makefile
make setup-hooks
```

設定的 hooks：

- `pre-commit`: 提交前匯出 OpenAPI JSON
- `post-commit`: 提交後更新 Postman 集合
- `pre-push`: 推送前確保 Postman 集合是最新的

### 方法 4：VS Code 整合

在 VS Code 中使用任務：

1. 按 `Ctrl+Shift+P` 開啟命令面板
2. 輸入 "Tasks: Run Task"
3. 選擇以下任務之一：
   - "Export to Postman" - 手動匯出
   - "Watch and Export" - 監控模式
   - "Setup Git Hooks" - 設定 Git hooks

## 輸出檔案

匯出會產生以下檔案：

```
exports/
├── openapi_latest.json          # 最新的 OpenAPI JSON
├── openapi_20240101_120000.json # 帶時間戳的備份
└── postman_20240101_120000.json # Postman 格式檔案
```

## 配置選項

### 環境變數

| 變數名稱                | 說明             | 預設值                  |
| ----------------------- | ---------------- | ----------------------- |
| `POSTMAN_API_KEY`       | Postman API 金鑰 | 無                      |
| `POSTMAN_COLLECTION_ID` | 要更新的集合 ID  | 無（會建立新集合）      |
| `BASE_URL`              | API 基礎 URL     | `http://localhost:8000` |

### 監控設定

在 `scripts/watch_and_export.py` 中可以調整：

```python
# 監控的副檔名
self.watched_extensions = {'.py'}

# 監控的目錄
self.watched_dirs = {
    'app/routers',
    'app/schemas',
    'app/models',
    'app/main.py',
    'app/factory.py'
}

# 防抖時間（秒）
self.debounce_time = 2.0
```

## 故障排除

### 常見問題

#### 1. 找不到模組

```bash
# 錯誤：ModuleNotFoundError: No module named 'app'
# 解決方案：確保在專案根目錄執行腳本
cd /path/to/project
python scripts/export_to_postman.py
```

#### 2. Postman API 金鑰無效

```bash
# 錯誤：401 Unauthorized
# 解決方案：檢查 API 金鑰是否正確
echo $POSTMAN_API_KEY
```

#### 3. 集合 ID 不存在

```bash
# 錯誤：404 Not Found
# 解決方案：檢查集合 ID 或移除該環境變數讓系統建立新集合
unset POSTMAN_COLLECTION_ID
```

#### 4. 檔案監控權限問題

```bash
# 錯誤：Permission denied
# 解決方案：確保有讀取檔案的權限
chmod +r app/routers/*.py
```

### 除錯模式

啟用詳細日誌：

```bash
# 設定日誌級別
export LOG_LEVEL=DEBUG
python scripts/export_to_postman.py
```

## 進階用法

### 自訂匯出格式

修改 `scripts/export_to_postman.py` 中的 `_convert_to_postman_format` 方法來自訂 Postman 集合格式。

### 多環境支援

```bash
# 開發環境
export POSTMAN_COLLECTION_ID_DEV=dev_collection_id
python scripts/export_to_postman.py

# 測試環境
export POSTMAN_COLLECTION_ID_TEST=test_collection_id
python scripts/export_to_postman.py
```

### 整合 CI/CD

在 GitHub Actions 中：

```yaml
- name: Export to Postman
  run: |
    export POSTMAN_API_KEY=${{ secrets.POSTMAN_API_KEY }}
    python scripts/export_to_postman.py
  env:
    POSTMAN_COLLECTION_ID: ${{ secrets.POSTMAN_COLLECTION_ID }}
```

## 最佳實踐

1. **使用監控模式**：在開發時使用 `watch_and_export.py` 自動匯出
2. **設定 Git hooks**：確保每次提交都更新 Postman 集合
3. **版本控制**：將匯出的 JSON 檔案加入版本控制
4. **環境分離**：為不同環境使用不同的 Postman 集合
5. **定期備份**：定期備份 Postman 集合

## 相關檔案

- `scripts/export_to_postman.py` - 主要匯出腳本
- `scripts/watch_and_export.py` - 檔案監控腳本
- `scripts/setup_git_hooks.py` - Git hooks 設定腳本
- `Makefile` - 常用命令
- `.vscode/tasks.json` - VS Code 任務配置
