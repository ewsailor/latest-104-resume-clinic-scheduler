# 【MVP】104 履歷診療室 - 站內諮詢時間媒合系統

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![Poetry](https://img.shields.io/badge/Poetry-1.8+-orange.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 專案概述

104 履歷診療室是一個專業的職涯諮詢平台，提供履歷健診、模擬面試、職涯諮詢等服務。本系統專注於解決 Giver（諮詢師）與 Taker（求職者）之間的時間媒合問題，讓雙方能夠方便地設定可面談時段並完成配對。讓 Giver、Taker 在平台內，方便地設定可面談時段並完成配對媒合，同時能快速發送預計回覆時間通知，以減少等待回應時的不確定與焦慮感。

## 🎯 核心功能

### 主要功能

- **時間媒合系統**：Giver 和 Taker 可以設定可面談時段並完成配對
- **即時通知**：快速發送預計回覆時間通知，減少等待回應時的不確定感
- **履歷健診**：專業的履歷檢視和建議服務
- **模擬面試**：提供面試練習和回饋
- **職涯諮詢**：個人化的職涯規劃建議

### 使用者故事 (User Stories)

- 作為 Giver，我希望能夠設定我的可諮詢時段，讓 Taker 可以預約
- 作為 Taker，我希望能夠搜尋合適的 Giver 並預約諮詢時段
- 作為系統，我希望能夠自動媒合最佳的時間配對
- 作為使用者，我希望能夠收到即時的通知和狀態更新

## 🚀 快速開始

### 環境需求

- **Python**: 3.12+
- **Poetry**: 1.8+
- **資料庫**: MySQL/MariaDB, MongoDB, Redis

### 安裝步驟

1. **複製專案**

   ```bash
   git clone https://github.com/ewsailor/104-resume-clinic-scheduler.git
   cd 104-resume-clinic-scheduler
   ```

2. **安裝 Poetry (如果尚未安裝)**

   ```bash
   pip install poetry
   ```

3. **安裝專案依賴**

   ```bash
   poetry install
   ```

4. **設定環境變數**

   ```bash
   cp .env.example .env
   # 編輯 .env 檔案，填入必要的資料庫連線資訊
   ```

5. **啟動開發伺服器**

   ```bash
   poetry run uvicorn app.main:app --reload --reload-dir app
   ```

6. **開啟瀏覽器**
   訪問 http://127.0.0.1:8000

## 🛠️ 開發工具

### 程式碼品質工具

- **Black**: 自動程式碼格式化
- **isort**: 自動整理 import 語句
- **MyPy**: 靜態型別檢查
- **Flake8**: 程式碼風格檢查
- **Pre-commit**: 提交前自動檢查

### 測試工具

- **Pytest**: 測試框架
- **Pytest-asyncio**: 異步測試支援
- **HTTPX**: FastAPI 測試客戶端

## 🏗️ 技術架構

### 後端技術棧

- **框架**: FastAPI (現代、高效能的 Python Web 框架)
- **資料庫**:
  - **MySQL/MariaDB**: 核心業務資料儲存
  - **MongoDB**: 彈性資料儲存（日誌、使用者偏好等）
  - **Redis**: 快取和即時資料
- **ORM**: SQLAlchemy (Python 最強大的 ORM)
- **驗證**: Pydantic (資料驗證和序列化)
- **模板引擎**: Jinja2 (HTML 模板渲染)

### 前端技術棧

- **框架**: Bootstrap 5.1.3 (響應式 UI 框架)
- **圖標**: Font Awesome (豐富的圖標庫)
- **JavaScript**: 原生 JS + 現代 ES6+ 語法

### 部署和 DevOps

- **容器化**: Docker 支援
- **CI/CD**: GitHub Actions
- **監控**: 整合日誌系統
- **AWS 整合**: Boto3 SDK 支援


- 開發環境：[Visual Studio Code](https://visualstudio.microsoft.com/zh-hant/)
- 執行環境(1)：[Node.js v18.15.0](https://github.com/coreybutler/nvm-windows)
- 執行環境(2)：[MySQL v8.0.15](https://downloads.mysql.com/archives/installer/)
- 自動重啟伺服器套件：[nodemon @3.1.7](https://nodemon.io/)
- 應用程式框架：[express ^4.21.1](https://www.npmjs.com/package/express) 
- HTTP method 套件：[method-override ^3.0.0](https://www.npmjs.com/package/method-override)
- 資料庫套件：[mysql2 v3.2.0](https://www.npmjs.com/package/mysql2) 
- 資料庫管理工具：[MySQL Workbench 8.0.15](https://downloads.mysql.com/archives/installer/) 

## 📁 專案結構

```
104-resume-clinic-scheduler/
├── app/                    # 主要應用程式目錄
│   ├── main.py            # FastAPI 應用程式入口
│   ├── models/            # 資料模型定義
│   ├── routers/           # API 路由定義
│   ├── schemas/           # Pydantic 資料驗證模型
│   ├── templates/         # Jinja2 模板檔案
│   └── utils/             # 工具函數和輔助模組
├── static/                # 靜態檔案 (CSS, JS, 圖片)
├── logs/                  # 日誌檔案
├── tests/                 # 測試檔案
├── pyproject.toml         # Poetry 專案配置
├── poetry.lock           # 依賴鎖定檔案
└── README.md             # 專案說明文件
```

## 🧪 測試

### 執行測試

```bash
# 執行所有測試
poetry run pytest

# 執行測試並顯示覆蓋率
poetry run pytest --cov=app

# 執行特定測試檔案
poetry run pytest tests/test_main.py
```

### 程式碼品質檢查

```bash
# 格式化程式碼
poetry run black app/

# 整理 import 語句
poetry run isort app/

# 型別檢查
poetry run mypy app/

# 程式碼風格檢查
poetry run flake8 app/
```

## 📝 API 文件

啟動伺服器後，可以訪問以下文件：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🤝 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 開發規範

- 遵循 PEP 8 程式碼風格
- 撰寫測試案例
- 更新相關文件
- 使用有意義的 commit 訊息

## 📄 授權

本專案採用 MIT 授權條款

## 👨‍💻 開發者

**Oscar Chung** - [GitHub](https://github.com/ewsailor)