# 104 履歷診療室 - 平台內諮詢時間媒合系統

[![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)](https://github.com/ewsailor/104-resume-clinic-scheduler)
[![Python](https://img.shields.io/badge/Python-3.12.8-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%2FMariaDB-blue.svg)](https://www.mysql.com/)
[![Poetry](https://img.shields.io/badge/Poetry-2.1.3-green.svg)](https://python-poetry.org/)
[![CI/CD](https://github.com/ewsailor/104-resume-clinic-scheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/ewsailor/104-resume-clinic-scheduler/actions/workflows/ci.yml)
[![Test Coverage](https://img.shields.io/badge/Coverage-83%25-brightgreen.svg)](https://github.com/ewsailor/104-resume-clinic-scheduler)

- [專案概述](#專案概述)
  - [核心目標](#核心目標)、[使用者故事](#使用者故事)、[使用者流程圖](#使用者流程圖)、[使用者介面截圖](#使用者介面截圖)
- [快速開始](#快速開始)
  - 環境需求、安裝步驟、啟動方式
- [技術架構與設計理念](#技術架構與設計理念)
  - 技術棧
    - 專案結構、後端、前端、資料庫、開發工具、後續擴充
  - [API 文檔](#api-文檔)
    - Swagger、API 端點概覽、RESTful API 範例請求與回應、版本控制、狀態碼的使用
  - [測試](#測試)
    - 測試覆蓋率、夾具 Fixtures 集中化管理測試常數、單元測試、整合測試、
  - [自動化測試](#cicd)
    - CI/CD 的 CI、pre-commit
  - [安全性](安全性)
    - 驗證、授權、資料加密、防攻擊
  - 錯誤處理與例外處理 Error & Exception Handling
  - 可靠性 Reliability
    - 健康檢查、重試、監控
  - 健壯性 Robustness
    - 輸入驗證、降級策略、異常情境處理
  - [效能](效能)
  - [團隊合作](團隊合作)
    - Jira、
- [未來規劃](未來規劃)
  - 專案的潛在發展與改進方向、JWT、Redis、MongoDB、Docker、AWS 部署
- [開發者](開發者)
  - Email、LinkedIn、GitHub

提供 CI/CD 流水線的截圖或簡單說明。

## <a name="專案概述"></a>專案概述 [返回目錄 ↑](#目錄)

### <a name="核心目標"></a>核心目標 [返回目錄 ↑](#目錄)

讓 Giver（診療服務提供者）與 Taker（診療服務接受者）能在平台內，方便地設定可面談時段並完成配對媒合，同時提供即時通知，以減少等待回應時的不確定與焦慮感。

### <a name="使用者故事"></a>使用者故事 User Stories [返回目錄 ↑](#目錄)

完整使用者故事請[點此](./docs/user-stories.md)查看，以下簡述本專案的主要使用者故事：

- Giver 提供可預約的時段，讓 Taker 預約面談
- Taker 提供方便的時段，待 Giver 回覆是否方便面談
  - 因 Giver 尚未提供可預約的時段，Taker 無法預約面談
  - 因 Giver 已提供的方便時段，Taker 均不方便面談

#### **已完成功能**

- ✅ 時段的 CRUD 操作：使用者新增、查詢、編輯、刪除時段
- ✅ 時段重疊檢查，避免新增或更新時段時造成衝突
- ✅ 查詢支援多種篩選條件
- ✅ 軟刪除機制和審計追蹤
- ✅ 時段狀態 ENUM 管理：DRAFT、AVAILABLE、PENDING、ACCEPTED、REJECTED、CANCELLED、COMPLETED

#### **待開發功能**

- 登入功能
- 通知系統：即時訊息通知、預計回覆時間通知、自動提醒功能（逾期回覆提醒）
- 鎖定已被預約的時段，避免時段被重複預約
- 媒合與使用數據報表

### <a name="使用者流程圖"></a>使用者流程圖 [返回目錄 ↑](#目錄)

完整流程請詳下圖，以下簡述本專案的主要使用者流程：

- **Giver 流程**
  - Giver 提供可預約的時段，讓 Taker 預約面談
  - Giver 查看 Taker 提供的時段，並回覆自己是否方便
- **Taker 流程**
  - Taker 查看 Giver 提供的時段，並進行預約
  - Taker 提供方便的時段，待 Giver 回覆是否方便面談
- **回覆流程**
  - 收到方不行：流程重來
  - 收到方可以
    - 送出方不行：流程重來
    - 送出方可以：進行諮詢

![104 履歷診療室 - 平台內諮詢時間媒合系統用戶流程](./static/images/content/user-flow.png)

### <a name="使用者介面截圖"></a>使用者介面截圖 [返回目錄 ↑](#目錄)

- Giver 列表
  - ![Giver 列表總覽](./static/images/ui/01-giver-list-overview.png)
- Taker 預約 Giver 時段
  - ![Taker 預約 Giver 時段](./static/images/ui/02-taker-scheduling-giver-time.png)
  - ![Taker 預約 Giver 時段結果](./static/images/ui/03-taker-scheduling-giver-time-result.png)
- Taker 提供方便時段給 Giver
  - ![Taker 提供方便時段給 Giver](./static/images/ui/04-taker-provide-available-time.png)
  - ![Taker 提供方便時段給 Giver 結果](./static/images/ui/05-taker-provide-available-time-result.png)

## <a name="快速開始"></a>快速開始 [返回目錄 ↑](#目錄)

### 1. 環境需求

- **Python**: 3.9+
  - Python 3.9+ 支援語法：使用 `dict`、`list`、`set`、`tuple` 而非 `Dict`、`List`、`Set`、`Tuple`，不需額外匯入 `typing` 模組
  - Python 3.10+ 支援語法：
    - `match`/`case` 模式匹配，避免大量 `if-elif-else`
    - `X | Y` 聯合類型，替代 `Union[X, Y]`
    - `X | None` 可選類型，替代 `Optional[X]`
- **FastAPI**
  - Web 框架：現代化 Python Web API 框架，支援非同步
  - 自動文檔：自動依路由、Pydantic 型別，生成 OpenAPI 文檔和 Swagger UI，減少維護工作
  - 型別安全：完整的型別提示支援
- **Uvicorn**
  - ASGI 伺服器：運行 FastAPI 應用程式
  - 高效能：支援非同步、高併發處理
- **Poetry**
  - 依賴管理：用 `pyproject.toml` 定義依賴的版本範圍，用 `poetry.lock` 鎖定確切依賴版本，確保環境一致性
  - 虛擬環境：自動建立虛擬環境，避免專案依賴與系統環境的其他專案衝突
  - 打包發佈：簡化打包和發佈流程
- **資料庫**
  - MySQL 或 MariaDB：儲存使用者資料和預約資訊
  - SQLite：測試環境使用

### 2. 安裝步驟

1. **複製專案**

   ```bash
   git clone https://github.com/ewsailor/104-resume-clinic-scheduler.git
   cd 104-resume-clinic-scheduler
   ```

2. **安裝 Python 3.9+ (如果尚未安裝)**

    - 下載並安裝 [Python 3.9+](https://www.python.org/downloads/)
    - 確認版本：
      ```bash
      python --version
      ```

3. **安裝 Poetry**

   ```bash
   pip install poetry
   ```

4. **用 Poetry 安裝 FastAPI、Uvicorn 等所有依賴套件**

   ```bash
   poetry install
   ```

5. **安裝資料庫**

   - 下載並安裝 [MySQL Installer](https://dev.mysql.com/downloads/installer/)
   - SQLite 通常內建在 Python 中，無需額外安裝

6. **設定環境變數**

   1. 複製 .env.example 檔案，命名為 .env
      ```bash
      cp .env.example .env
      ```

   2. 確保 `.env` 被 `.gitignore` 忽略：在專案根目錄建立 .gitignore，並在 .gitignore 中加入以下程式碼
      ```bash
      .env
      ```

   3. 在 .env 檔案填入密碼、資料庫設定等
      ```bash
      # ===== 應用程式基本設定 =====
      APP_NAME="104 Resume Clinic Scheduler"
      APP_ENV=development # development, staging, production
      DEBUG=true
      SECRET_KEY=hs9H7!vZqkT2dLmP0$wX3@eCr1FgUbYkT2dLmP0$ # 密碼建議至少 12 個字元，包含大小寫字母、數字、特殊符號

      # ===== 資料庫設定 =====
      # MySQL 設定
      # DATABASE_URL=mysql+pymysql://fastapi_user:your_password@mysql:3306/resume_clinic_scheduler
      # MYSQL_ROOT_PASSWORD=root_password 
      MYSQL_HOST=localhost
      MYSQL_PORT=3306
      MYSQL_DATABASE=scheduler_db
      MYSQL_USER=fastapi_user # ⚠️ 安全提醒：不要使用 root，請建立專用帳號如：fastapi_user
      MYSQL_PASSWORD=fastapi123 # 建議至少 12 個字元，包含大小寫字母、數字、特殊符號
      MYSQL_CHARSET=utf8mb4
      ```

7. **以 root 身份登入 MySQL**

   ```bash
   mysql -u root -p
   ```
   - 連接到 MySQL：使用者以 root 身份登入 MySQL，並輸入 root 密碼以登入 MySQL

8. **資料庫初始化**
   
   1. 刪除並重新建立資料庫，加上字符集和排序規則，然後切換到 scheduler_db 資料庫
      ```
      DROP DATABASE IF EXISTS `scheduler_db`;
      CREATE DATABASE `scheduler_db` 
          DEFAULT CHARACTER SET utf8mb4 
          COLLATE utf8mb4_unicode_ci;
      USE `scheduler_db`; 
      ```
   
   2. 刪除並重新建立名為 fastapi_user 的使用者，避免使用 root 進行日常操作，提升安全性
  
      ```
      DROP USER IF EXISTS 'fastapi_user'@'localhost';
      CREATE USER 'fastapi_user'@'localhost' 
          IDENTIFIED BY 'fastapi123';
      ```

   3. 撤銷任何意外預設權限，並遵循最小權限原則，重新給予 fastapi_user 在 scheduler_db 這個資料庫上所有資料表必要的權限，確保安全性（通常 DROP USER 後不需要，但加上更保險）
  
      ```
      REVOKE ALL PRIVILEGES ON `scheduler_db`.* 
          FROM 'fastapi_user'@'localhost'; 
      GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER 
          ON `scheduler_db`.* 
          TO 'fastapi_user'@'localhost';
      ```

   4. 重新整理權限表，讓權限即時生效
      ```
      FLUSH PRIVILEGES;
      ```

   5. 檢查資料庫使用者權限：顯示 fastapi_user 的所有授權清單，確認是否設置成功
      ```
      SHOW GRANTS FOR 'fastapi_user'@'localhost';
      ```

9. **用 Alembic 升級資料庫到最新版本**

   ```bash
   poetry run alembic upgrade head
   ```

### 3. 啟動方式

1. **用 Poetry 啟動伺服器，確保環境一致性**

   ```bash
   poetry run uvicorn app.main:app --reload --reload-dir app
   ```

2. **瀏覽器輸入網址**

   訪問 http://127.0.0.1:8000

## <a name="技術架構與設計理念"></a>技術架構與設計理念 [返回目錄 ↑](#目錄)

### 後端技術棧

- **框架**: FastAPI (現代、快速、基於 Python 3.7+ 的 Web 框架)
- **ASGI 伺服器**: Uvicorn (輕量級 ASGI 伺服器)
- **配置管理**: Pydantic Settings (型別安全的配置管理)
- **架構模式**: 分層架構 (API → Service → CRUD → Model)
- **資料庫**:
  - **MySQL/MariaDB**: 核心業務資料儲存
  - SQLite（測試）
    ERD
    Alembic
- **ORM**: SQLAlchemy (Python 最強大的 ORM)
- **資料庫遷移**: Alembic (SQLAlchemy 官方遷移工具)
- **驗證**: Pydantic (資料驗證和序列化)
- **模板引擎**: Jinja2 (HTML 模板渲染)
- **中間件**: CORS 支援、自定義中間件
- **文件**: Swagger UI / Redoc
- **測試**: pytest

### 前端技術棧

- **框架**: Bootstrap 5.1.3 (響應式 UI 框架)
- **圖標**: Font Awesome (豐富的圖標庫)
- **JavaScript**: 原生 JS + 現代 ES6+ 語法
  HTML
  CSS

### 開發工具

- **IDE**: Visual Studio Code
  Cursor
- **資料庫管理**: MySQL Workbench 8.0.15
- **版本控制**: Git
- **套件管理**: Poetry
- **資料庫遷移**: Alembic (自動版本控制)
- **自動程式碼格式化**: Black
- **自動整理 import 語句**: isort
- **靜態型別檢查**: MyPy
- **程式碼風格檢查**: Flake8
- **提交前自動檢查**: Pre-commit
- **程式碼風格**: black, isort, flake8, mypy
- **自動化工具**: pre-commit, GitHub Actions (CI/CD)
  sourcetree
  Postman

### 後續擴充

- **資料庫**:
  - **MongoDB**: 彈性資料儲存（日誌、使用者偏好等）
  - **Redis**: 快取和即時資料
- **部署和 DevOps**:

  - **容器化**: Docker 支援
  - **CI/CD**: GitHub Actions
  - **監控**: 整合日誌系統
  - **AWS 整合**: Boto3 SDK 支援

安全性
   # 複製 .env.example  .env， 密碼建議至少 12 個字元，包含大小寫字母、數字、特殊符號
## <a name="專案結構"></a>專案結構 [返回目錄 ↑](#目錄)

app/
├── crud/ # 資料庫 CRUD 操作
│ └── schedule.py
├── routers/ # API 路由
├── services/ # 業務邏輯
├── models/ # SQLAlchemy 資料模型
├── schemas/ # Pydantic Schema
├── utils/ # 工具函式（ex: 時區處理）
├── decorators/ # 共用裝飾器（log_operation）
└── errors/ # 自定義錯誤
tests/ # 單元測試與整合測試
.github/workflows/ # CI/CD 設定

```
104-resume-clinic-scheduler/
├── alembic/                      # 資料庫遷移管理
├── app/                          # 應用程式主目錄
│   ├── core/                     # 核心功能模組（設定管理）
│   ├── crud/                     # 資料庫操作層
│   ├── decorators/               # 裝飾器（日誌、錯誤處理）
│   │   ├── logging.py            # 日誌裝飾器
│   │   └── error_handlers.py     # 錯誤處理裝飾器
│   ├── enums/                    # 列舉型別定義
│   ├── errors/                   # 錯誤處理系統
│   │   ├── error_codes           # 各層級錯誤代碼
│   │   ├── exceptions.py         # 自定義異常
│   │   ├── formatters.py         # 錯誤格式化
│   │   └── handlers.py           # 錯誤處理器
│   ├── middleware/               # 中間件（CORS、錯誤處理）
│   ├── models/                   # SQLAlchemy 資料模型
│   │   ├── database.py           # 資料庫連線和會話管理
│   │   ├── schedule.py           # 排程模型
│   ├── routers/                  # API 路由模組
│   │   ├── api/                  # API 端點
│   │   │   └── schedule.py       # 時段管理 API
│   │   ├── health.py             # 健康檢查端點
│   │   └── main.py               # 主要路由
│   ├── schemas/                  # Pydantic 資料驗證模式
│   ├── services/                 # 業務邏輯層
│   ├── templates/                # HTML 模板
│   ├── utils/                    # 工具模組（時區處理、模型輔助）
│   │   ├── timezone.py           # 時區處理工具
│   │   └── model_helpers.py      # 模型輔助工具
│   ├── factory.py                # 應用程式工廠
│   └── main.py                   # 應用程式入口點
├── database
├── docs/                         # 文件目錄
│   ├── technical/                # 技術文件
│   ├── guides/                   # 使用指南
│   └── testing/                  # 測試相關文件
├── htmlcov/                      # 測試覆蓋率報告
├── logs/                         # 日誌檔案
├── scripts/                      # 開發工具腳本
├── static/                       # 靜態檔案
│   ├── images/                   # 圖片資源
│   ├── css/                      # 樣式檔案
│   └── js/                       # JavaScript 檔案
├── tests/                        # 測試檔案
│   ├── unit/                     # 單元測試
│   ├── integration/              # 整合測試
│   ├── e2e/                      # 端到端測試
│   └── fixtures/                 # 測試資料和 Fixtures
├── .coverage                     # 測試覆蓋率報告
├── .env                          # 環境變數（本地開發）
├── .env.example                  # 環境變數範例
├── .flake8                       # Flake8 配置
├── .gitignore                    # Git 忽略檔案
├── .pre-commit-config.yaml       # Pre-commit 配置
├── alembic.ini                   # Alembic 主配置檔案
├── poetry.lock                   # Poetry 依賴鎖定
├── pyproject.toml                # Poetry 專案配置
├── pytest.ini                    # Pytest 配置
└── README.md                     # 專案說明文件
```

### **分層架構設計**

- **API 層** (`routers/`): 處理 HTTP 請求和回應
- **業務邏輯層** (`services/`): 處理業務規則和邏輯
- **資料存取層** (`crud/`): 資料庫 CRUD 操作
- **資料模型層** (`models/`): SQLAlchemy 模型定義
- **驗證層** (`schemas/`): Pydantic 資料驗證

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

# 執行測試（推薦）
poetry run pytest

# 快速測試（開發期間）
./scripts/quick-test.sh

# 完整 CI/CD 流程（本地）
./scripts/run-ci-locally.sh
```

### CI/CD 自動化測試

專案使用 GitHub Actions 進行自動化 CI/CD 流程：

#### 工作流程

1. **代碼品質檢查**：

   - Black 代碼格式化檢查
   - isort 導入排序檢查
   - flake8 代碼風格檢查
   - mypy 類型檢查

2. **測試執行**：

   - 支援 Python 3.9, 3.10, 3.11 多版本測試
   - 單元測試、整合測試、端到端測試
   - 測試覆蓋率報告

3. **安全檢查**：

   - safety 依賴漏洞檢查
   - bandit 安全代碼分析

4. **自動部署**：
   - develop 分支 → 測試環境
   - main 分支 → 生產環境

#### 狀態徽章

### 測試說明

專案使用 pytest 作為測試框架，提供完整的測試覆蓋率分析。

### 測試常數管理

專案使用 `tests/constants.py` 集中管理所有測試常數：

- **避免硬編碼**：所有測試值都使用常數
- **一致性保證**：確保所有測試使用相同的值
- **易於維護**：修改常數值時只需更新一個地方
- **可重用性**：常數可以在多個測試檔案中共享

詳細使用方式請參考：[測試管理指南](tests/README.md)

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

已整合 **pre-commit hooks**：

- `autoflake` → 移除未使用 import / 變數
- `isort` → 排序 import
- `black` → 自動格式化程式碼
- `flake8` → 靜態程式檢查
- `mypy` → 型別檢查

安裝 pre-commit：

```bash
pre-commit install

```

## <a name="cicd"></a>CI/CD [返回目錄 ↑](#目錄)

專案包含 GitHub Actions (`.github/workflows/ci.yml`)，在每次 `git push origin main` 時自動執行：

- Lint / 型別檢查
- 單元測試（pytest）

成功後會顯示綠色的 CI Badge，代表程式碼與測試通過。

## <a name="api-文檔"></a>API 文檔 [返回目錄 ↑](#目錄)

### **API 端點概覽**

#### 健康檢查端點

- **基本健康檢查**: `GET /healthz` - 檢查應用程式是否正在運行
- **就緒檢查**: `GET /readyz` - 檢查應用程式和資料庫是否準備好接收流量

#### 使用者管理 API

- **取得使用者列表**: `GET /api/v1/users/` - 取得所有使用者
- **取得特定使用者**: `GET /api/v1/users/{user_id}` - 取得特定使用者資訊
- **建立使用者**: `POST /api/v1/users/` - 建立新使用者
- **更新使用者**: `PUT /api/v1/users/{user_id}` - 更新使用者資訊

#### 排程管理 API

- **取得排程列表**: `GET /api/v1/schedules/` - 取得所有排程
- **取得特定排程**: `GET /api/v1/schedules/{schedule_id}` - 取得特定排程資訊
- **建立排程**: `POST /api/v1/schedules/` - 建立新排程
- **更新排程**: `PATCH /api/v1/schedules/{schedule_id}` - 更新排程資訊
- **刪除排程**: `DELETE /api/v1/schedules/{schedule_id}` - 刪除排程

### **API 文件**

啟動伺服器後，可以訪問以下文件：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### **API 使用範例**

```bash
# 健康檢查
curl http://127.0.0.1:8000/healthz

# 建立新排程
curl -X POST http://127.0.0.1:8000/api/v1/schedules/ \
  -H "Content-Type: application/json" \
  -d '{"giver_id": 1, "taker_id": 2, "start_time": "2025-01-15T10:00:00Z"}'
```

### 建立時段

```bash
curl -X POST "http://localhost:8000/schedules" \
     -H "Content-Type: application/json" \
     -d '{"giver_id": 1, "taker_id": 2, "date": "2025-09-01", "status": "PENDING"}'

```

### 查詢時段

```bash
curl -X GET "http://localhost:8000/schedules?giver_id=1"

```

## <a name="故障排除"></a>故障排除 [返回目錄 ↑](#目錄)

### **常見問題**

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
# 解決方案：使用標準 pytest 命令
poetry run pytest
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

### **尋求協助**

如果遇到其他問題，請：

1. 查看 [Issues](https://github.com/ewsailor/104-resume-clinic-scheduler/issues) 是否有類似問題
2. 檢查 [文檔目錄](docs/) 中的相關指南
3. 建立新的 Issue，並提供詳細的錯誤資訊

## <a name="開發指南"></a>開發指南 [返回目錄 ↑](#目錄)

### **開發環境設定**

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

### **貢獻流程**

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

### **開發規範**

#### 程式碼風格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 程式碼風格
- 使用 [Black](https://black.readthedocs.io/) 進行程式碼格式化
- 使用 [isort](https://pycqa.github.io/isort/) 整理 import 語句

#### 測試要求

- 新增功能必須包含對應的測試案例
- 測試覆蓋率不得低於 80%
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

## <a name="授權"></a>授權 [返回目錄 ↑](#目錄)

本專案採用 MIT 授權條款

## <a name="開發者"></a>開發者 [返回目錄 ↑](#目錄)

**Oscar Chung** - [GitHub](https://github.com/ewsailor)

## <a name="更新日誌"></a>更新日誌 [返回目錄 ↑](#目錄)

### v0.1.0 (2025-01-15)

- **Service 層架構完善**
  - 新增 `app/services/` 業務邏輯層，實現完整的分層架構
  - 建立 `ScheduleService` 和 `UserService` 類別，處理業務邏輯
  - 統一 Service 層的錯誤處理、日誌記錄和裝飾器使用
  - 實現 API → Service → CRUD → Model 的完整分層架構
- **架構對應關係統一**
  - 確保 SQL、Model、Schema、Route、Service、CRUD 六層完整對應
  - 修正 User 模組缺少 Service 層的問題
  - 統一所有模組的命名規範和程式碼結構
  - 實現職責分離：Route 處理 API、Service 處理業務邏輯、CRUD 處理資料庫
- **業務邏輯分離**
  - 將業務邏輯從 CRUD 層移至 Service 層
  - 實現時段重疊檢查、狀態決定、時間驗證等業務邏輯
  - 統一審計追蹤檢查和錯誤處理機制
  - 提供可重用和可測試的業務邏輯方法
- **文檔架構更新**
  - 更新 README.md 專案結構，加入 Service 層說明
  - 完善分層架構設計理念文檔
  - 更新技術架構說明，強調業務邏輯分離
- **測試架構優化**
  - 移除不存在的 validation 模組相關測試
  - 更新測試覆蓋率至 83%
  - 修正測試錯誤和模組導入問題
- **現代化更新**
  - 更新 FastAPI 版本至 0.116+
  - 優化 Pydantic v2 配置
  - 完善錯誤處理和日誌系統

### v1.3.0 (2025-01-15)

- **命名規範統一**
  - 統一 API 模型、CRUD 層、資料庫模型和前端之間的命名規範
  - 建立操作語義清晰的審計欄位命名（created_by, updated_by, deleted_by）
  - 優化 Pydantic v2 模型配置，支援 ORM 轉換和欄位名稱對應
  - 完善軟刪除機制，支援系統自動操作和審計追蹤
  - 確保所有測試通過，達到 221 passed, 2 skipped 的測試覆蓋率
- **API 模型優化**
  - 統一 `ScheduleCreateRequest`、`ScheduleDeleteRequest` 的欄位命名
  - 優化 `ScheduleData` 和 `ScheduleUpdateData` 的語義區分
  - 完善 API 請求/回應模型的型別安全
- **資料庫審計追蹤**
  - 實現完整的軟刪除機制（deleted_at, deleted_by, deleted_by_role）
  - 支援系統自動操作（NULL 值表示系統操作）
  - 建立完整的審計欄位追蹤（created_by, updated_by, deleted_by）
- **測試架構完善**
  - 修正所有測試中的參數名稱不一致問題
  - 統一 CRUD 測試、API 測試和整合測試的命名規範
  - 確保測試覆蓋率達到 90% 以上
- **技術文檔更新**
  - 新增 Pydantic v2 配置說明
  - 完善審計欄位設計理念文檔
  - 更新 API 模型命名規範指南

### v1.2.0 (2025-01-15)

- **專案架構重構**
  - 重新組織測試目錄結構（單元/整合/端到端測試）
  - 優化靜態檔案管理（圖片/CSS/JS 分類）
  - 建立完整的測試管理指南
  - 新增靜態檔案管理指南
- **測試架構改進**
  - 實現分層測試策略（unit/integration/e2e）
  - 建立測試命名規範和最佳實踐
  - 優化測試資料管理和 Fixtures
  - 新增測試覆蓋率目標設定
- **前端資源管理**
  - 重新組織靜態檔案目錄結構
  - 建立圖片資源分類（icons/ui/content）
  - 優化 CSS 和 JavaScript 檔案組織
  - 建立靜態檔案命名規範
- **文檔完善**
  - 更新專案結構文檔
  - 新增測試管理指南
  - 新增靜態檔案管理指南
  - 完善開發工具說明
- **團隊協作改進**
  - 建立團隊協作確認指標文檔
  - 提供跨角色協作檢查清單
  - 涵蓋 PM、前端工程師、QA、UI/UX 四個角色
  - 建立標準化的協作流程和品質標準
- **命名規範統一**
  - 統一 API 模型、CRUD 層、資料庫模型和前端之間的命名規範
  - 建立操作語義清晰的審計欄位命名（created_by, updated_by, deleted_by）
  - 優化 Pydantic v2 模型配置，支援 ORM 轉換和欄位名稱對應
  - 完善軟刪除機制，支援系統自動操作和審計追蹤
  - 確保所有測試通過，達到 221 passed, 2 skipped 的測試覆蓋率

### v1.1.0 (2025-01-10)

- **新增 Alembic 資料庫遷移工具**
  - 完整的資料庫版本控制
  - 自動檢測模型變更
  - 支援向前和向後遷移
  - 團隊協作資料庫同步
- **新增詳細文檔**
  - Alembic 使用指南
  - 遷移最佳實踐
  - 故障排除指南
- **開發工具改進**
  - 新增 Alembic 版本清理工具
  - 更新專案結構文檔

### v0.0.0 (2024-12-20)

- **初始版本發布**
  - 實現時間媒合系統核心功能
  - 建立 FastAPI 後端架構
  - 整合 MySQL 資料庫
  - 添加開發者工具和伺服器監控
  - 完善文件和使用說明
