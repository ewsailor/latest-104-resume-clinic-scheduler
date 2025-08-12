# 安裝指南

## 環境需求

### 系統需求

- **Python**: 3.12+
- **Poetry**: 1.8+
- **資料庫**: MySQL/MariaDB 8.0+

### 作業系統支援

- Windows 10/11
- macOS 10.15+
- Ubuntu 20.04+

## 安裝步驟

### 1. 複製專案

```bash
git clone https://github.com/ewsailor/104-resume-clinic-scheduler.git
cd 104-resume-clinic-scheduler
```

### 2. 安裝 Python 依賴

```bash
# 安裝 Poetry（如果尚未安裝）
pip install poetry

# 安裝專案依賴
poetry install
```

### 3. 設定環境變數

```bash
# 複製環境變數範例檔案
cp .env.example .env

# 編輯環境變數檔案
# 填入您的資料庫連線資訊
```

### 4. 資料庫設定

```bash
# 啟動 MySQL 服務
# 建立資料庫和使用者

# 執行資料庫遷移
poetry run alembic upgrade head
```

### 5. 啟動應用程式

```bash
# 開發模式啟動
uvicorn app.main:app --reload --reload-dir app

# 或使用 Poetry
poetry run uvicorn app.main:app --reload
```

## 驗證安裝

### 1. 檢查健康狀態

訪問 http://127.0.0.1:8000/healthz

### 2. 查看 API 文件

訪問 http://127.0.0.1:8000/docs

### 3. 執行測試

```bash
# 執行所有測試
poetry run pytest

# 執行特定測試
poetry run pytest tests/unit/
```

## 故障排除

### 常見問題

1. **Poetry 安裝失敗**

   - 確保 Python 版本正確
   - 更新 pip: `pip install --upgrade pip`

2. **資料庫連線失敗**

   - 檢查 MySQL 服務是否啟動
   - 驗證環境變數設定
   - 確認資料庫使用者權限

3. **依賴安裝失敗**
   - 清除 Poetry 快取: `poetry cache clear --all pypi`
   - 重新安裝: `poetry install --no-cache`

## 下一步

安裝完成後，請參考：

- **[配置指南](configuration.md)** - 詳細的配置說明
- **[資料庫設定](database-setup.md)** - 資料庫配置和遷移
- **[開發指南](../development/coding-standards.md)** - 開發規範和標準
