# Scripts 目錄

這個目錄包含各種實用腳本，用於開發、測試和維護專案。

## 📁 目錄結構

```
scripts/
├── database/                   # 資料庫相關腳本
│   ├── migration/              # 資料庫遷移腳本
│   │   ├── migrate_to_utc.py
│   │   ├── migrate_to_local_time.py
│   │   └── fix_timezone.py
│   ├── maintenance/            # 資料庫維護腳本
│   │   ├── clear_alembic_version.py
│   │   ├── backup_and_preview.bat
│   │   └── backup_and_preview.sh
│   └── testing/                # 資料庫測試腳本
│       ├── test_database_connection.py
│       └── test_database_config.py
├── data/                       # 資料管理腳本
│   ├── users/                  # 使用者資料腳本
│   │   ├── add_test_users.py
│   │   ├── create_giver_users.py
│   │   ├── update_user_emails.py
│   │   └── update_user_emails.sql
│   └── test_data/              # 測試資料腳本
│       └── create_test_data.py
├── testing/                    # 測試相關腳本
│   ├── run_tests.py
│   ├── test_schedule_submission.py
│   └── test_local_time.py
├── maintenance/                # 系統維護腳本
│   ├── clear_cache.py
│   ├── health_check.py
│   └── config_validator.py
├── security/                   # 安全性檢查腳本
│   ├── cors/                   # CORS 相關腳本
│   │   ├── cors_check.py
│   │   ├── security_checker.py
│   │   ├── config_checker.py
│   │   └── validator.py
│   └── cors_legacy/            # 舊版 CORS 腳本
│       ├── cors_config_checker.py
│       └── cors_security_check.py
├── debug/                      # 除錯腳本
│   ├── diagnose_timestamp.py
│   ├── test_settings_validators.py
│   └── debug/                  # 除錯子目錄
│       ├── README.md
│       ├── test_wang_shi_yi_python.py
│       ├── test_wang_shi_yi_fix.js
│       ├── test_api_fix.js
│       ├── test_giver_id_fix.js
│       ├── test_chat_session_debug.js
│       └── test_giver_id_debug.js
├── batch/                      # 批次檔案
│   ├── run_tests.bat
│   ├── clear_cache.bat
│   └── backup_and_preview.bat
├── shell/                      # Shell 腳本
│   ├── clear_cache.sh
│   └── backup_and_preview.sh
└── README.md                   # 本文件
```

## 🚀 腳本分類

### 資料庫腳本 (`database/`)

#### 遷移腳本 (`database/migration/`)

- **`migrate_to_utc.py`**: 將資料庫時間遷移到 UTC
- **`migrate_to_local_time.py`**: 將資料庫時間遷移到本地時間
- **`fix_timezone.py`**: 修復時區相關問題

#### 維護腳本 (`database/maintenance/`)

- **`clear_alembic_version.py`**: 清理 Alembic 版本記錄
- **`backup_and_preview.bat/.sh`**: 資料庫備份和預覽

#### 測試腳本 (`database/testing/`)

- **`test_database_connection.py`**: 測試資料庫連線
- **`test_database_config.py`**: 測試資料庫配置

### 資料管理腳本 (`data/`)

#### 使用者資料腳本 (`data/users/`)

- **`add_test_users.py`**: 新增測試使用者
- **`create_giver_users.py`**: 建立諮詢師使用者
- **`update_user_emails.py`**: 更新使用者電子郵件
- **`update_user_emails.sql`**: 使用者電子郵件更新 SQL

#### 測試資料腳本 (`data/test_data/`)

- **`create_test_data.py`**: 建立測試資料

### 測試腳本 (`testing/`)

- **`run_tests.py`**: 執行測試套件
- **`test_schedule_submission.py`**: 測試排程提交功能
- **`test_local_time.py`**: 測試本地時間功能

### 系統維護腳本 (`maintenance/`)

- **`clear_cache.py`**: 清理快取
- **`health_check.py`**: 系統健康檢查
- **`config_validator.py`**: 配置驗證

### 安全性腳本 (`security/`)

#### CORS 腳本 (`security/cors/`)

- **`cors_check.py`**: 統一 CORS 檢查工具
- **`security_checker.py`**: CORS 安全性檢查器
- **`config_checker.py`**: CORS 配置檢查器
- **`validator.py`**: CORS 驗證器

#### 舊版 CORS 腳本 (`security/cors_legacy/`)

- **`cors_config_checker.py`**: 舊版配置檢查器
- **`cors_security_check.py`**: 舊版安全性檢查器

### 除錯腳本 (`debug/`)

- **`diagnose_timestamp.py`**: 時間戳診斷
- **`test_settings_validators.py`**: 設定驗證器測試

### 批次檔案 (`batch/`)

- **`run_tests.bat`**: Windows 測試執行批次檔
- **`clear_cache.bat`**: Windows 快取清理批次檔
- **`backup_and_preview.bat`**: Windows 備份批次檔

### Shell 腳本 (`shell/`)

- **`clear_cache.sh`**: Linux/Mac 快取清理腳本
- **`backup_and_preview.sh`**: Linux/Mac 備份腳本

## 🚀 CORS 檢查工具

### 統一工具：`cors_check.py`

這是推薦使用的統一 CORS 檢查工具，提供多種檢查模式：

```bash
# 檢查專案 CORS 配置
python scripts/cors_check.py config

# 檢查專案 CORS 配置（簡潔模式）
python scripts/cors_check.py config --simple

# 驗證特定的 CORS 來源字串
python scripts/cors_check.py validate "http://localhost,https://api.example.com"

# 安全性檢查（模擬資料）
python scripts/cors_check.py security

# 匯出報告為 JSON
python scripts/cors_check.py config --export json
```

### 模組化架構

#### 1. `CORSecurityChecker` - 安全性檢查器

通用的 CORS 安全性檢查功能：

```python
from scripts.cors import CORSecurityChecker

checker = CORSecurityChecker()

# 檢查來源
result = checker.check_origins(["http://localhost:3000", "https://api.example.com"])

# 檢查方法
result = checker.check_methods(["GET", "POST", "DELETE"])

# 全面檢查
result = checker.comprehensive_check(origins, methods, headers, environment)
```

#### 2. `CORSConfigChecker` - 配置檢查器

專門用於檢查專案中的 CORS 配置：

```python
from scripts.cors import CORSConfigChecker

checker = CORSConfigChecker()

# 取得目前配置
config = checker.get_current_config()

# 執行全面檢查
result = checker.comprehensive_check()

# 印出報告
checker.print_config_report(detailed=True)

# 匯出報告
json_report = checker.export_report("json")
```

#### 3. `CORSValidator` - 驗證器

用於驗證特定的 CORS 設定：

```python
from scripts.cors import CORSValidator

validator = CORSValidator()

# 驗證來源字串
result = validator.validate_origin_string("http://localhost,https://api.example.com")

# 驗證完整配置
result = validator.validate_cors_config(origins, methods, headers, environment)
```

## 🔧 其他工具

### `config_validator.py`

用於驗證應用程式配置檔案：

```bash
python scripts/config_validator.py
```

## 📊 功能對比

| 功能             | 統一工具      | 舊版工具                    | 模組化                  |
| ---------------- | ------------- | --------------------------- | ----------------------- |
| **專案配置檢查** | ✅ `config`   | ✅ `cors_config_checker.py` | ✅ `CORSConfigChecker`  |
| **來源字串驗證** | ✅ `validate` | ❌                          | ✅ `CORSValidator`      |
| **安全性檢查**   | ✅ `security` | ✅ `cors_security_check.py` | ✅ `CORSecurityChecker` |
| **報告匯出**     | ✅ JSON/YAML  | ❌                          | ✅ 多種格式             |
| **命令列介面**   | ✅ 統一       | ❌ 分散                     | ✅ 可程式化             |
| **模組重用**     | ✅ 完整       | ❌ 有限                     | ✅ 高度可重用           |

## 🎯 最佳實踐建議

### 1. **使用統一工具**

推薦使用 `cors_check.py` 作為主要的 CORS 檢查工具：

```bash
# 日常檢查
python scripts/cors_check.py config

# 驗證新設定
python scripts/cors_check.py validate "https://new-domain.com"

# 安全性評估
python scripts/cors_check.py security --environment production
```

### 2. **程式化使用**

在 CI/CD 或自動化腳本中使用模組化組件：

```python
from scripts.cors import CORSConfigChecker

checker = CORSConfigChecker()
result = checker.comprehensive_check()

if result['overall_score'] < 70:
    print("CORS 安全性評分過低，需要改進")
    exit(1)
```

### 3. **定期檢查**

建議在以下時機執行 CORS 檢查：

- 部署前
- 修改 CORS 設定後
- 定期安全審查
- CI/CD 流程中

### 4. **環境分離**

根據不同環境使用不同的檢查策略：

```bash
# 開發環境
python scripts/cors_check.py config --simple

# 生產環境
python scripts/cors_check.py config --export json
```

## 🔄 遷移指南

### 從舊版工具遷移

如果您目前使用舊版工具，建議遷移到統一工具：

```bash
# 舊版
python scripts/cors_config_checker.py
python scripts/cors_security_check.py

# 新版
python scripts/cors_check.py config
python scripts/cors_check.py security
```

### 保留舊版工具

舊版工具仍然可用，但建議逐步遷移到新工具：

- `cors_config_checker.py` - 將在未來版本中移除
- `cors_security_check.py` - 將在未來版本中移除

## 📈 未來規劃

1. **整合測試**：添加自動化測試
2. **更多格式**：支援更多報告格式
3. **CI/CD 整合**：提供 GitHub Actions 範例
4. **Web 介面**：開發 Web 版本的檢查工具
5. **即時監控**：提供即時 CORS 監控功能

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這些工具！

### 開發指南

1. 遵循現有的程式碼風格
2. 添加適當的測試
3. 更新文件
4. 確保向後相容性
