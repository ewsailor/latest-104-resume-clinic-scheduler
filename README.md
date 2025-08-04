# 【MVP】104 履歷診療室 - 站內諮詢時間媒合系統

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![Poetry](https://img.shields.io/badge/Poetry-1.8+-orange.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 專案概述

讓 Giver（諮詢師）與 Taker（求職者）使用 104 履歷診療室時，雙方能在平台內，設定可面談時段並完成配對媒合，同時快速發送預計回覆時間通知，以減少等待回應時的不確定與焦慮感。

## 核心功能

### 主要功能

- **時間媒合系統**：Giver 和 Taker 可以設定可面談時段並完成配對
- **即時通知**：快速發送預計回覆時間通知，減少等待回應時的不確定感

### 使用者故事 (User Stories)

#### Giver（諮詢師）視角

- 作為 Giver，我希望能夠設定我的可諮詢時段，讓 Taker 可以預約
- 作為 Giver，我希望能夠查看預約請求並快速回覆
- 作為 Giver，我希望能夠管理我的諮詢時間表

#### Taker（求職者）視角

- 作為 Taker，我希望能夠搜尋合適的 Giver 並預約諮詢時段
- 作為 Taker，我希望能夠收到即時的通知和狀態更新
- 作為 Taker，我希望能夠查看諮詢歷史記錄

#### 系統自動化功能

- 作為系統，我希望能夠自動媒合最佳的時間配對
- 作為系統，我希望能夠發送預計回覆時間通知
- 作為系統，我希望能夠追蹤諮詢完成狀態

## 技術架構

### 後端技術棧

- **框架**: FastAPI (現代、快速、基於 Python 3.7+ 的 Web 框架)
- **ASGI 伺服器**: Uvicorn (輕量級 ASGI 伺服器)
- **配置管理**: Pydantic Settings (型別安全的配置管理)
- **資料庫**:
  - **MySQL/MariaDB**: 核心業務資料儲存
- **ORM**: SQLAlchemy (Python 最強大的 ORM)
- **驗證**: Pydantic (資料驗證和序列化)
- **模板引擎**: Jinja2 (HTML 模板渲染)

### 前端技術棧

- **框架**: Bootstrap 5.1.3 (響應式 UI 框架)
- **圖標**: Font Awesome (豐富的圖標庫)
- **JavaScript**: 原生 JS + 現代 ES6+ 語法

### 開發工具

- **IDE**: Visual Studio Code
- **資料庫管理**: MySQL Workbench 8.0.15
- **版本控制**: Git
- **套件管理**: Poetry
- **自動程式碼格式化**: Black
- **自動整理 import 語句**: isort
- **靜態型別檢查**: MyPy
- **程式碼風格檢查**: Flake8
- **提交前自動檢查**: Pre-commit

### 後續擴充

- **資料庫**:
  - **MongoDB**: 彈性資料儲存（日誌、使用者偏好等）
  - **Redis**: 快取和即時資料
- 部署和 DevOps
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

## 專案結構

```
104-resume-clinic-scheduler/
├── app/                          # 應用程式主目錄
│   ├── core/                     # 核心功能模組
│   │   ├── __init__.py           # 核心模組初始化
│   │   └── settings.py           # 應用程式設定管理
│   ├── models/                   # 資料模型
│   │   ├── database.py           # 資料庫模型
│   │   └── schedule.py           # 排程模型
│   ├── routers/                  # 路由模組
│   │   ├── __init__.py           # 核心模組初始化
│   │   ├── main.py               # 主要路由
│   │   └── schedule.py           # 排程路由
│   ├── schemas/                  # Pydantic 模式
│   │   └── schedule.py           # 排程相關模式
│   ├── templates/                # HTML 模板
│   │   └── index.html            # 首頁模板
│   ├── factory.py                # 應用程式工廠
│   └── main.py                   # 應用程式入口點
├── database/                     # 資料庫相關
│   └── schema.sql                # 資料庫結構
├── scripts/                      # 開發工具腳本
│   ├── config_validator.py       # 配置驗證腳本
│   └── README.md                 # 腳本說明文件
├── static/                       # 靜態檔案
│   ├── style.css                 # 樣式表
│   ├── script.js                 # JavaScript
│   └── images/                   # 圖片資源
├── tests/                        # 測試檔案
│   ├── test_config.py            # 配置測試
│   └── test_main.py              # 主要功能測試
├── logs/                         # 日誌檔案
├── .env                          # 環境變數（本地開發）
├── .env.example                  # 環境變數範例
├── .gitignore                    # Git 忽略檔案
├── pyproject.toml                # Poetry 專案配置
├── poetry.lock                   # Poetry 依賴鎖定
└── README.md                     # 專案說明文件
```

## 快速開始

### 1. 環境需求

- **Python**: 3.12+
- **Poetry**: 1.8+
- **資料庫**: MySQL/MariaDB, MongoDB, Redis

### 2. 安裝步驟

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
   # 將 .env.example 檔案複製成 .env 檔案，並在 .env 檔案填入環境變數*
   ```

5. **資料庫初始化（使用 root 建立專用帳號） ⚠️**

   ⚠️ 本步驟僅限開發者操作，用來建立資料庫與應用程式專用帳號

   ```bash
   mysql -u root -p
   # 連接到 MySQL：以使用者 root 的身份，登入 MySQL，並提示輸入密碼
   ```

### 3. 啟動方式

1. **啟動伺服器**

   ```bash
   uvicorn app.main:app --reload --reload-dir app
   ```

2. **瀏覽器輸入網址**

   訪問 http://127.0.0.1:8000

### 4. 安全提醒：

- ❌ 絕對不要使用 `root` 帳號，作為應用程式資料庫使用者
- ❌ 不要在版本控制中提交 `.env` 檔案
- ❌ 不要將資料庫憑證硬編碼在程式碼中
- ✅ 建立專用的應用程式帳號（如：`fastapi_user`）
- ✅ 將 `.env` 檔案加入 `.gitignore`
- ✅ 使用強密碼（至少 8 個字元，包含大小寫字母、數字、符號）
- ✅ 定期更換密碼
- ✅ 授予權限時，遵循最小權限原則
- ✅ 使用環境變數管理敏感資訊

## 測試

### 測試工具

- **Pytest**: 測試框架
- **Pytest-asyncio**: 異步測試支援
- **HTTPX**: FastAPI 測試客戶端
- **測試常數管理**: 集中化管理測試常數，確保一致性

### 執行測試

```bash
# 執行所有測試（推薦使用測試腳本，自動抑制警告）
python scripts/run_tests.py

# 執行特定測試檔案
python scripts/run_tests.py tests/test_health.py

# 執行測試並顯示覆蓋率
python scripts/run_tests.py --cov=app

# 直接使用 pytest（可能顯示棄用警告）
poetry run pytest

# 執行特定測試檔案
poetry run pytest tests/test_main.py
```

### 測試腳本說明

專案提供了 `scripts/run_tests.py` 腳本來運行測試，該腳本會：

- 自動設置環境變數來抑制棄用警告
- 確保測試環境的一致性
- 提供更好的測試體驗

### 測試常數管理

專案使用 `tests/constants.py` 集中管理所有測試常數：

- **避免硬編碼**：所有測試值都使用常數
- **一致性保證**：確保所有測試使用相同的值
- **易於維護**：修改常數值時只需更新一個地方
- **可重用性**：常數可以在多個測試檔案中共享

詳細使用方式請參考：[測試常數使用指南](docs/test_constants_guide.md)

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

## API 文件

啟動伺服器後，可以訪問以下文件：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 貢獻指南

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

## 授權

本專案採用 MIT 授權條款

## 開發者

**Oscar Chung** - [GitHub](https://github.com/ewsailor)

## 更新日誌

### v1.0.0 (2024-01-XX)

- 初始版本發布
- 實現時間媒合系統核心功能
- 添加開發者工具和伺服器監控
- 完善文件和使用說明
