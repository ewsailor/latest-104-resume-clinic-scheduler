# 【MVP】104 履歷診療室 - 站內諮詢時間媒合系統

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.16+-purple.svg)](https://alembic.sqlalchemy.org/)
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

## 專案結構

```
104-resume-clinic-scheduler/
├── app/                          # 應用程式主目錄
│   ├── core/                     # 核心功能模組
│   │   ├── __init__.py           # 核心模組初始化
│   │   └── settings.py           # 應用程式設定管理
│   ├── models/                   # 資料模型
│   │   ├── database.py           # 資料庫連線和會話管理
│   │   ├── schedule.py           # 排程模型
│   │   └── user.py               # 使用者模型
│   ├── routers/                  # 路由模組
│   │   ├── api/                  # API 路由
│   │   │   └── schedule.py       # 時段管理 API
│   │   ├── health.py             # 健康檢查端點
│   │   └── main.py               # 主要路由
│   ├── crud/                     # 資料庫操作
│   │   └── crud_schedule.py      # 時段 CRUD 操作
│   ├── schemas/                  # 資料驗證模式
│   │   └── schedule.py           # 時段資料模式
│   ├── middleware/               # 中間件
│   │   └── cors.py               # CORS 中間件
│   ├── utils/                    # 工具模組
│   │   └── timezone.py           # 時區處理工具
│   ├── services/                 # 業務邏輯服務層
│   ├── templates/                # HTML 模板
│   │   └── index.html            # 首頁模板
│   ├── factory.py                # 應用程式工廠
│   └── main.py                   # 應用程式入口點
├── tests/                        # 測試檔案
│   ├── conftest.py               # Pytest 配置
│   ├── constants.py              # 測試常數
│   ├── test_api_schedule_comprehensive.py  # 完整 API 測試
│   ├── test_api_schedule_simple.py         # 簡單 API 測試
│   ├── test_config.py            # 配置測試
│   ├── test_cors_middleware.py   # CORS 中間件測試
│   ├── test_crud_schedule.py     # 時段 CRUD 測試
│   ├── test_database.py          # 資料庫模組測試
│   ├── test_health.py            # 健康檢查測試
│   ├── test_main.py              # 主應用程式測試
│   └── test_timezone.py          # 時區工具測試
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
├── static/                       # 靜態檔案
│   ├── style.css                 # 樣式表
│   ├── script.js                 # JavaScript
│   ├── chat-avatar.svg           # 聊天頭像
│   ├── favicon.png               # 網站圖標
│   └── logo-header.svg           # 標題 Logo
├── alembic/                      # 資料庫遷移管理
│   ├── env.py                    # Alembic 環境配置
│   ├── script.py.mako            # 遷移腳本模板
│   └── versions/                 # 遷移檔案目錄
├── database/                     # 資料庫檔案
│   ├── schema.sql                # 資料庫結構（參考用）
│   └── schema_utc.sql            # UTC 時區資料庫結構（參考用）
├── docs/                         # 文件目錄
│   ├── alembic_guide.md          # Alembic 資料庫遷移指南
│   ├── database_connection_best_practices.md # 資料庫連線最佳實踐
│   ├── import_guidelines.md      # 匯入指南
│   ├── python_multipart_migration.md # Python multipart 遷移
│   ├── python_multipart_usage.md # Python multipart 使用
│   ├── test_constants_guide.md   # 測試常數指南
│   ├── test_constants_restructure.md # 測試常數重構
│   └── timezone_solution.md      # 時區解決方案
├── logs/                         # 日誌檔案
├── .env                          # 環境變數（本地開發）
├── .env.example                  # 環境變數範例
├── .gitignore                    # Git 忽略檔案
├── alembic.ini                   # Alembic 主配置檔案
├── pyproject.toml                # Poetry 專案配置
├── poetry.lock                   # Poetry 依賴鎖定
├── pytest.ini                    # Pytest 配置
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

## 測試

### 測試工具

- **Pytest**: 測試框架
- **Pytest-asyncio**: 異步測試支援
- **HTTPX**: FastAPI 測試客戶端
- **測試常數管理**: 集中化管理測試常數，確保一致性
- **測試覆蓋率**: 使用 pytest-cov 進行覆蓋率分析

### 測試策略

- **單元測試**: 測試個別函數和類別
- **整合測試**: 測試 API 端點和資料庫操作
- **端到端測試**: 測試完整的業務流程
- **配置測試**: 確保設定和環境變數正確
- **中間件測試**: 測試 CORS 和其他中間件功能

### 執行測試

```bash
# 方法 1：使用測試腳本（推薦，自動抑制警告）
python scripts/run_tests.py

# 方法 2：使用 Windows 批處理檔案
scripts/run_tests.bat

# 方法 3：使用環境變數抑制警告
PYTHONWARNINGS="ignore::PendingDeprecationWarning" poetry run pytest --cov=app.models.database --cov-report=term-missing

# 執行特定測試檔案
python scripts/run_tests.py tests/test_health.py

# 執行測試並顯示覆蓋率
python scripts/run_tests.py --cov=app

# 直接使用 pytest（可能顯示棄用警告）
poetry run pytest

# 執行特定測試檔案
poetry run pytest tests/test_main.py

# 執行測試並生成覆蓋率報告
poetry run pytest --cov=app --cov-report=html
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

## API 端點

### 健康檢查端點

- **基本健康檢查**: `GET /healthz` - 檢查應用程式是否正在運行
- **就緒檢查**: `GET /readyz` - 檢查應用程式和資料庫是否準備好接收流量

### API 文件

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

### v1.1.0 (2025-01-XX)

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

### v1.0.0 (2024-01-XX)

- 初始版本發布
- 實現時間媒合系統核心功能
- 添加開發者工具和伺服器監控
- 完善文件和使用說明
