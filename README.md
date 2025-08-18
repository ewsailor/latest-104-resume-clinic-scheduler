# 【MVP】104 履歷診療室 - 平台內諮詢時間媒合系統

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.16+-purple.svg)](https://alembic.sqlalchemy.org/)
[![Poetry](https://img.shields.io/badge/Poetry-1.8+-orange.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/ewsailor/104-resume-clinic-scheduler)
[![Test Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)](https://github.com/ewsailor/104-resume-clinic-scheduler)
[![Version](https://img.shields.io/badge/Version-1.2.0-blue.svg)](https://github.com/ewsailor/104-resume-clinic-scheduler)

## 目錄

- [專案概述](#專案概述)
- [核心功能](#核心功能)
- [專案特色](#專案特色)
- [技術架構](#技術架構)
- [快速開始](#快速開始)
- [專案結構](#專案結構)
- [API 文檔](#api-文檔)
- [測試指南](#測試指南)
- [開發指南](#開發指南)
- [故障排除](#故障排除)
- [貢獻指南](#貢獻指南)
- [更新日誌](#更新日誌)

## <a name="專案概述"></a>專案概述 [返回目錄 ↑](#目錄)

讓 Giver（諮詢師）與 Taker（求職者）使用 104 履歷診療室時，雙方能在平台內，設定可面談時段並完成配對媒合，同時快速發送預計回覆時間通知，以減少等待回應時的不確定與焦慮感。

### 用戶流程圖

![104 履歷診療室 - 平台內諮詢時間媒合系統用戶流程](./static/images/content/user-flow.png)

### 專案目標

- **提升媒合效率**：自動化時間配對，減少人工協調時間
- **改善用戶體驗**：即時通知和狀態更新，降低等待焦慮
- **標準化流程**：建立統一的諮詢預約和管理流程
- **資料分析**：提供諮詢數據分析，優化服務品質

## <a name="核心功能"></a>核心功能 [返回目錄 ↑](#目錄)

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

## <a name="專案特色"></a>專案特色 [返回目錄 ↑](#目錄)

### 🏗️ **現代化架構設計**

- **分層架構**: 清晰的 MVC 模式，易於維護和擴展
- **依賴注入**: 使用 FastAPI 的依賴注入系統，提高可測試性
- **工廠模式**: 應用程式工廠模式，便於配置和測試
- **模組化設計**: 功能模組化，便於團隊協作

### 🧪 **完整的測試策略**

- **分層測試**: 單元測試、整合測試、端到端測試
- **測試覆蓋率**: 90% 以上的程式碼覆蓋率
- **測試資料管理**: 集中化的測試資料和 Fixtures
- **自動化測試**: CI/CD 整合，確保程式碼品質
- **品質保證**: 完整的 QA 流程和測試策略

### 📁 **專業的檔案管理**

- **靜態資源管理**: 分類管理圖片、CSS、JavaScript 檔案
- **測試架構**: 結構化的測試目錄和命名規範
- **文檔完善**: 詳細的開發指南和最佳實踐
- **版本控制**: 完整的資料庫遷移和版本管理
- **團隊協作**: 標準化的協作確認指標和流程

### 🔧 **開發者體驗**

- **熱重載**: 開發時自動重載，提高開發效率
- **程式碼品質**: 自動格式化、型別檢查、風格檢查
- **除錯工具**: 完整的日誌系統和錯誤處理
- **開發腳本**: 豐富的開發工具和腳本

## <a name="技術架構"></a>技術架構 [返回目錄 ↑](#目錄)

### 後端技術棧

- **框架**: FastAPI (現代、快速、基於 Python 3.7+ 的 Web 框架)
- **ASGI 伺服器**: Uvicorn (輕量級 ASGI 伺服器)
- **配置管理**: Pydantic Settings (型別安全的配置管理)
- **資料庫**:
  - **MySQL/MariaDB**: 核心業務資料儲存
- **ORM**: SQLAlchemy (Python 最強大的 ORM)
- **資料庫遷移**: Alembic (SQLAlchemy 官方遷移工具)
- **驗證**: Pydantic (資料驗證和序列化)
- **模板引擎**: Jinja2 (HTML 模板渲染)
- **中間件**: CORS 支援、自定義中間件

### 前端技術棧

- **框架**: Bootstrap 5.1.3 (響應式 UI 框架)
- **圖標**: Font Awesome (豐富的圖標庫)
- **JavaScript**: 原生 JS + 現代 ES6+ 語法

### 開發工具

- **IDE**: Visual Studio Code
- **資料庫管理**: MySQL Workbench 8.0.15
- **版本控制**: Git
- **套件管理**: Poetry
- **資料庫遷移**: Alembic (自動版本控制)
- **自動程式碼格式化**: Black
- **自動整理 import 語句**: isort
- **靜態型別檢查**: MyPy
- **程式碼風格檢查**: Flake8
- **提交前自動檢查**: Pre-commit

### 後續擴充

- **資料庫**:
  - **MongoDB**: 彈性資料儲存（日誌、使用者偏好等）
  - **Redis**: 快取和即時資料
- **部署和 DevOps**:

  - **容器化**: Docker 支援
  - **CI/CD**: GitHub Actions
  - **監控**: 整合日誌系統
  - **AWS 整合**: Boto3 SDK 支援

## <a name="專案結構"></a>專案結構 [返回目錄 ↑](#目錄)

```
104-resume-clinic-scheduler/
├── app/                          # 應用程式主目錄
│   ├── core/                     # 核心功能模組
│   │   ├── __init__.py           # 核心模組初始化
│   │   └── settings.py           # 應用程式設定管理
│   ├── models/                   # 資料模型
│   │   ├── database.py           # 資料庫連線和會話管理
│   │   ├── schedule.py           # 排程模型
│   │   ├── user.py               # 使用者模型
│   │   └── enums.py              # 列舉型別定義
│   ├── routers/                  # 路由模組
│   │   ├── api/                  # API 路由
│   │   │   ├── schedule.py       # 時段管理 API
│   │   │   ├── users.py          # 使用者管理 API
│   │   │   └── givers.py         # 諮詢師管理 API
│   │   ├── health.py             # 健康檢查端點
│   │   └── main.py               # 主要路由
│   ├── crud/                     # 資料庫操作
│   │   ├── crud_schedule.py      # 時段 CRUD 操作
│   │   └── crud_user.py          # 使用者 CRUD 操作
│   ├── schemas/                  # 資料驗證模式
│   │   ├── schedule.py           # 時段資料模式
│   │   └── user.py               # 使用者資料模式
│   ├── middleware/               # 中間件
│   │   └── cors.py               # CORS 中間件
│   ├── utils/                    # 工具模組
│   │   ├── timezone.py           # 時區處理工具
│   │   └── model_helpers.py      # 模型輔助工具
│   ├── data/                     # 資料模組
│   │   └── givers.py             # 諮詢師資料
│   ├── templates/                # HTML 模板
│   │   └── index.html            # 首頁模板
│   ├── factory.py                # 應用程式工廠
│   └── main.py                   # 應用程式入口點
├── tests/                        # 測試檔案
│   ├── unit/                     # 單元測試
│   │   ├── models/               # 資料模型測試
│   │   │   └── test_database.py  # 資料庫模型測試
│   │   ├── crud/                 # CRUD 操作測試
│   │   │   └── test_crud_schedule.py # 時段 CRUD 測試
│   │   ├── utils/                # 工具函數測試
│   │   │   ├── test_model_helpers.py # 模型輔助工具測試
│   │   │   ├── test_timezone.py  # 時區工具測試
│   │   │   └── test_config.py    # 配置測試
│   │   └── middleware/           # 中間件測試
│   │       └── test_cors_middleware.py # CORS 中間件測試
│   ├── integration/              # 整合測試
│   │   ├── api/                  # API 端點測試
│   │   │   ├── test_main.py      # 主要路由測試
│   │   │   ├── test_api_users.py # 使用者 API 測試
│   │   │   ├── test_api_givers.py # 諮詢師 API 測試
│   │   │   ├── test_api_schedule_*.py # 排程 API 測試
│   │   │   └── test_health*.py   # 健康檢查測試
│   │   └── database/             # 資料庫整合測試
│   ├── e2e/                      # 端到端測試
│   ├── fixtures/                 # 測試資料和 Fixtures
│   │   └── test_data_givers.py   # 諮詢師測試資料
│   ├── conftest.py               # Pytest 配置
│   ├── constants.py              # 測試常數
│   └── README.md                 # 測試管理指南
├── static/                       # 靜態檔案
│   ├── images/                   # 圖片資源目錄
│   │   ├── icons/                # 圖示類檔案
│   │   │   ├── favicon.png       # 網站圖示
│   │   │   ├── chat-avatar.svg   # 聊天頭像
│   │   │   └── logo-header.svg   # 頁首標誌
│   │   ├── ui/                   # UI 元件圖片
│   │   └── content/              # 內容相關圖片
│   ├── css/                      # 樣式檔案
│   │   └── style.css             # 主要樣式檔案
│   ├── js/                       # JavaScript 檔案
│   │   └── script.js             # 主要腳本檔案
│   └── README.md                 # 靜態檔案管理指南
├── scripts/                      # 開發工具腳本
│   ├── clear_alembic_version.py  # Alembic 版本清理工具
│   ├── config_validator.py       # 配置驗證腳本
│   ├── cors/                     # CORS 相關腳本
│   ├── create_test_data.py       # 測試資料建立
│   ├── diagnose_timestamp.py     # 時間戳診斷
│   ├── fix_timezone.py           # 時區修復
│   ├── health_check.py           # 健康檢查
│   ├── migrate_to_local_time.py  # 本地時間遷移
│   ├── migrate_to_utc.py         # UTC 遷移
│   ├── run_tests.py              # 測試執行腳本
│   ├── test_database_config.py   # 資料庫配置測試
│   ├── test_database_connection.py # 資料庫連線測試
│   ├── test_local_time.py        # 本地時間測試
│   ├── test_settings_validators.py # 設定驗證測試
│   └── README.md                 # 腳本說明文件
├── alembic/                      # 資料庫遷移管理
│   ├── env.py                    # Alembic 環境配置
│   ├── script.py.mako            # 遷移腳本模板
│   ├── sql_previews/             # SQL 預覽檔案
│   └── versions/                 # 遷移檔案目錄
├── database/                     # 資料庫檔案
│   ├── backups/                  # 資料庫備份
│   ├── schema.sql                # 資料庫結構（參考用）
│   ├── schema_utc.sql            # UTC 時區資料庫結構（參考用）
│   └── schema_best_practice.sql  # 最佳實踐資料庫結構
├── docs/                         # 文件目錄
│   ├── collaboration/            # 團隊協作確認指標
│   │   ├── README.md             # 協作確認指標總覽
│   │   ├── collaboration-overview.md # 跨角色協作重點
│   │   ├── pm-collaboration-checklist.md # PM協作確認指標
│   │   ├── frontend-collaboration-checklist.md # 前端工程師協作確認指標
│   │   ├── qa-collaboration-checklist.md # QA協作確認指標
│   │   └── uiux-collaboration-checklist.md # UI/UX協作確認指標
│   ├── alembic_guide.md          # Alembic 資料庫遷移指南
│   ├── database_connection_best_practices.md # 資料庫連線最佳實踐
│   ├── import_guidelines.md      # 匯入指南
│   ├── message_optimization.md   # 訊息優化指南
│   ├── python_multipart_migration.md # Python multipart 遷移
│   ├── python_multipart_usage.md # Python multipart 使用
│   ├── test_constants_guide.md   # 測試常數指南
│   ├── test_constants_restructure.md # 測試常數重構
│   └── timezone_solution.md      # 時區解決方案
├── logs/                         # 日誌檔案
├── .env                          # 環境變數（本地開發）
├── .env.example                  # 環境變數範例
├── .gitignore                    # Git 忽略檔案
├── .flake8                       # Flake8 配置
├── .pre-commit-config.yaml       # Pre-commit 配置
├── alembic.ini                   # Alembic 主配置檔案
├── pyproject.toml                # Poetry 專案配置
├── poetry.lock                   # Poetry 依賴鎖定
├── pytest.ini                    # Pytest 配置
└── README.md                     # 專案說明文件
```

## 快速開始

### 🚀 **一鍵啟動（推薦）**

```bash
# 1. 複製專案
git clone https://github.com/ewsailor/104-resume-clinic-scheduler.git
cd 104-resume-clinic-scheduler

# 2. 使用 Poetry 安裝依賴
poetry install

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env 檔案，填入您的資料庫設定

# 4. 初始化資料庫
poetry run alembic upgrade head

# 5. 啟動開發伺服器
poetry run uvicorn app.main:app --reload --reload-dir app
```

### 📖 **文檔導覽**

- **[團隊協作確認指標](docs/collaboration/README.md)**: 跨角色協作檢查清單和最佳實踐
- **[測試管理指南](tests/README.md)**: 完整的測試策略和最佳實踐
- **[靜態檔案管理指南](static/README.md)**: 靜態資源組織和命名規範
- **[開發腳本說明](scripts/README.md)**: 開發工具和腳本使用指南
- **[資料庫遷移指南](docs/alembic_guide.md)**: Alembic 使用和最佳實踐

### 🗂️ **目錄結構**

- **`app/`**: 應用程式核心程式碼
- **`tests/`**: 分層測試架構（unit/integration/e2e）
- **`static/`**: 分類管理的靜態資源
- **`docs/`**: 詳細的開發文檔
  - **`docs/collaboration/`**: 團隊協作確認指標文檔
- **`scripts/`**: 開發工具和腳本

## <a name="快速開始"></a>快速開始 [返回目錄 ↑](#目錄)

### 🚀 **一鍵啟動（推薦）**

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

6. **資料庫遷移管理**

   本專案使用 Alembic 進行資料庫 schema 版本控制，提供以下優勢：

   - 🔄 **版本控制**: 追蹤所有資料庫結構變更
   - 🚀 **自動遷移**: 支援向前和向後遷移
   - 👥 **團隊協作**: 確保所有開發者資料庫同步
   - 🛡️ **安全性**: 避免手動 SQL 操作錯誤

   **基本命令：**

   ```bash
   # 查看當前資料庫版本
   poetry run alembic current

   # 應用所有遷移到最新版本（首次設置）
   poetry run alembic upgrade head

   # 查看遷移歷史
   poetry run alembic history

   # 創建新的遷移（修改模型後）
   poetry run alembic revision --autogenerate -m "描述變更"

   # 回滾到上一個版本
   poetry run alembic downgrade -1
   ```

   **注意事項：**

   - ⚠️ 生產環境應用遷移前務必備份資料庫
   - 📝 檢查自動生成的遷移檔案是否正確
   - 🧪 在測試環境先驗證遷移

   詳細使用方法請參考：[Alembic 使用指南](docs/alembic_guide.md)

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

## <a name="測試指南"></a>測試指南 [返回目錄 ↑](#目錄)

### 測試工具

- **Pytest**: 測試框架
- **Pytest-asyncio**: 異步測試支援
- **HTTPX**: FastAPI 測試客戶端
- **測試常數管理**: 集中化管理測試常數，確保一致性
- **測試覆蓋率**: 使用 pytest-cov 進行覆蓋率分析

### 測試策略

- **單元測試** (`tests/unit/`): 測試個別函數、類別和模組
  - 模型測試: 資料庫模型和驗證
  - CRUD 測試: 資料庫操作
  - 工具函數測試: 輔助工具和配置
  - 中間件測試: CORS 等中間件功能
- **整合測試** (`tests/integration/`): 測試多個組件之間的互動
  - API 測試: 端點功能和整合
  - 資料庫整合測試: 資料庫操作和整合
- **端到端測試** (`tests/e2e/`): 測試完整的用戶工作流程
- **測試資料管理** (`tests/fixtures/`): 集中管理測試資料和 Fixtures

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定類型的測試
pytest tests/unit/           # 單元測試
pytest tests/integration/    # 整合測試
pytest tests/e2e/           # 端到端測試

# 執行特定模組的測試
pytest tests/unit/models/    # 模型測試
pytest tests/integration/api/ # API 測試

# 執行測試並生成覆蓋率報告
pytest --cov=app --cov-report=html

# 使用測試腳本（推薦，自動抑制警告）
python scripts/run_tests.py

# 使用 Windows 批處理檔案
scripts/run_tests.bat
```

### 測試腳本說明

專案提供了多種測試執行方式來解決 `multipart` 棄用警告：

#### 1. Python 測試腳本 (`scripts/run_tests.py`)

- 自動設置環境變數來抑制棄用警告
- 確保測試環境的一致性
- 提供更好的測試體驗
- 支援傳遞額外參數

#### 2. Windows 批處理檔案 (`scripts/run_tests.bat`)

- 專為 Windows 環境設計
- 自動設置環境變數
- 執行完成後暫停，方便查看結果

#### 3. 環境變數方法

- 直接在命令列設置 `PYTHONWARNINGS` 環境變數
- 適用於所有作業系統
- 可以與任何 pytest 命令組合使用

#### 警告說明

由於 Starlette 框架內部使用已棄用的 `multipart` 模組，會產生 `PendingDeprecationWarning` 警告。這不影響功能，但建議使用上述方法之一來抑制警告。

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

## <a name="api-文檔"></a>API 文檔 [返回目錄 ↑](#目錄)

### 🔍 **API 端點概覽**

#### 健康檢查端點

- **基本健康檢查**: `GET /healthz` - 檢查應用程式是否正在運行
- **就緒檢查**: `GET /readyz` - 檢查應用程式和資料庫是否準備好接收流量

#### 使用者管理 API

- **取得使用者列表**: `GET /api/v1/users/` - 取得所有使用者
- **取得特定使用者**: `GET /api/v1/users/{user_id}` - 取得特定使用者資訊
- **建立使用者**: `POST /api/v1/users/` - 建立新使用者
- **更新使用者**: `PUT /api/v1/users/{user_id}` - 更新使用者資訊

#### 諮詢師管理 API

- **取得諮詢師列表**: `GET /api/v1/givers/` - 取得所有諮詢師
- **取得特定諮詢師**: `GET /api/v1/givers/{giver_id}` - 取得特定諮詢師資訊
- **建立諮詢師**: `POST /api/v1/givers/` - 建立新諮詢師

#### 排程管理 API

- **取得排程列表**: `GET /api/v1/schedules/` - 取得所有排程
- **取得特定排程**: `GET /api/v1/schedules/{schedule_id}` - 取得特定排程資訊
- **建立排程**: `POST /api/v1/schedules/` - 建立新排程
- **更新排程**: `PATCH /api/v1/schedules/{schedule_id}` - 更新排程資訊
- **刪除排程**: `DELETE /api/v1/schedules/{schedule_id}` - 刪除排程

### 📚 **API 文件**

啟動伺服器後，可以訪問以下文件：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 🔧 **API 使用範例**

```bash
# 健康檢查
curl http://127.0.0.1:8000/healthz

# 取得使用者列表
curl http://127.0.0.1:8000/api/v1/users/

# 建立新排程
curl -X POST http://127.0.0.1:8000/api/v1/schedules/ \
  -H "Content-Type: application/json" \
  -d '{"giver_id": 1, "taker_id": 2, "start_time": "2025-01-15T10:00:00Z"}'
```

## <a name="故障排除"></a>故障排除 [返回目錄 ↑](#目錄)

### 🔧 **常見問題**

#### 1. 資料庫連線問題

```bash
# 錯誤：OperationalError: (2003, "Can't connect to MySQL server")
# 解決方案：
# 1. 確認 MySQL 服務正在運行
sudo systemctl start mysql

# 2. 檢查資料庫連線設定
cat .env | grep DATABASE

# 3. 測試資料庫連線
poetry run python scripts/test_database_connection.py
```

#### 2. 環境變數問題

```bash
# 錯誤：KeyError: 'DATABASE_URL'
# 解決方案：
# 1. 確認 .env 檔案存在
ls -la .env

# 2. 檢查環境變數設定
poetry run python scripts/config_validator.py
```

#### 3. 測試警告問題

```bash
# 警告：PendingDeprecationWarning: multipart
# 解決方案：使用專案提供的測試腳本
python scripts/run_tests.py
```

#### 4. 資料庫遷移問題

```bash
# 錯誤：Alembic revision failed
# 解決方案：
# 1. 檢查模型變更
poetry run alembic check

# 2. 手動建立遷移
poetry run alembic revision --autogenerate -m "描述變更"

# 3. 應用遷移
poetry run alembic upgrade head
```

### 📞 **尋求協助**

如果遇到其他問題，請：

1. 查看 [Issues](https://github.com/ewsailor/104-resume-clinic-scheduler/issues) 是否有類似問題
2. 檢查 [文檔目錄](docs/) 中的相關指南
3. 建立新的 Issue，並提供詳細的錯誤資訊

## <a name="開發指南"></a>開發指南 [返回目錄 ↑](#目錄)

### 🛠️ **開發環境設定**

1. **安裝開發工具**

   ```bash
   # 安裝 pre-commit hooks
   poetry run pre-commit install

   # 設定 Git hooks
   poetry run pre-commit install --hook-type commit-msg
   ```

2. **程式碼品質檢查**

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

3. **測試執行**

   ```bash
   # 執行所有測試
   poetry run pytest

   # 執行測試並生成覆蓋率報告
   poetry run pytest --cov=app --cov-report=html
   ```

## <a name="貢獻指南"></a>貢獻指南 [返回目錄 ↑](#目錄)

### 🤝 **貢獻流程**

1. **Fork 專案**

   ```bash
   # 在 GitHub 上 Fork 本專案
   # 然後複製到本地
   git clone https://github.com/YOUR_USERNAME/104-resume-clinic-scheduler.git
   cd 104-resume-clinic-scheduler
   ```

2. **建立功能分支**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **開發和測試**

   ```bash
   # 安裝依賴
   poetry install

   # 執行測試
   poetry run pytest

   # 程式碼品質檢查
   poetry run black app/
   poetry run isort app/
   ```

4. **提交變更**

   ```bash
   git add .
   git commit -m "feat: 新增功能描述"
   git push origin feature/your-feature-name
   ```

5. **開啟 Pull Request**
   - 在 GitHub 上建立 Pull Request
   - 填寫詳細的變更說明
   - 確保所有測試通過

### 📋 **開發規範**

#### 程式碼風格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 程式碼風格
- 使用 [Black](https://black.readthedocs.io/) 進行程式碼格式化
- 使用 [isort](https://pycqa.github.io/isort/) 整理 import 語句

#### 測試要求

- 新增功能必須包含對應的測試案例
- 測試覆蓋率不得低於 90%
- 使用 `tests/constants.py` 中的測試常數

#### Commit 訊息規範

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```bash
feat: 新增使用者管理功能
fix: 修復資料庫連線問題
docs: 更新 API 文檔
test: 新增使用者測試案例
refactor: 重構資料庫模型
```

#### 文件要求

- 遵循 PEP 8 程式碼風格
- 撰寫測試案例
- 新增功能必須更新相關文檔
- 複雜功能需要提供使用範例
- 更新 README.md 中的相關章節

## 授權

本專案採用 MIT 授權條款

## 開發者

**Oscar Chung** - [GitHub](https://github.com/ewsailor)

## <a name="更新日誌"></a>更新日誌 [返回目錄 ↑](#目錄)

### v1.2.0 (2025-01-15)

- 🏗️ **專案架構重構**
  - 重新組織測試目錄結構（單元/整合/端到端測試）
  - 優化靜態檔案管理（圖片/CSS/JS 分類）
  - 建立完整的測試管理指南
  - 新增靜態檔案管理指南
- 📋 **測試架構改進**
  - 實現分層測試策略（unit/integration/e2e）
  - 建立測試命名規範和最佳實踐
  - 優化測試資料管理和 Fixtures
  - 新增測試覆蓋率目標設定
- 🎨 **前端資源管理**
  - 重新組織靜態檔案目錄結構
  - 建立圖片資源分類（icons/ui/content）
  - 優化 CSS 和 JavaScript 檔案組織
  - 建立靜態檔案命名規範
- 📚 **文檔完善**
  - 更新專案結構文檔
  - 新增測試管理指南
  - 新增靜態檔案管理指南
  - 完善開發工具說明
- 👥 **團隊協作改進**
  - 建立團隊協作確認指標文檔
  - 提供跨角色協作檢查清單
  - 涵蓋 PM、前端工程師、QA、UI/UX 四個角色
  - 建立標準化的協作流程和品質標準

### v1.1.0 (2025-01-10)

- 🔄 **新增 Alembic 資料庫遷移工具**
  - 完整的資料庫版本控制
  - 自動檢測模型變更
  - 支援向前和向後遷移
  - 團隊協作資料庫同步
- 📚 **新增詳細文檔**
  - Alembic 使用指南
  - 遷移最佳實踐
  - 故障排除指南
- 🛠️ **開發工具改進**
  - 新增 Alembic 版本清理工具
  - 更新專案結構文檔

### v1.0.0 (2024-12-20)

- 🚀 **初始版本發布**
  - 實現時間媒合系統核心功能
  - 建立 FastAPI 後端架構
  - 整合 MySQL 資料庫
  - 添加開發者工具和伺服器監控
  - 完善文件和使用說明
