# Database 資料夾結構說明

## 概述
此資料夾包含專案的所有資料庫相關檔案，包括結構定義、備份、腳本等。

## 資料夾結構

### 📁 schemas/
資料庫結構定義檔案

#### 📁 current/
- `schema.sql` - 當前使用的資料庫結構

#### 📁 versions/
不同版本的資料庫結構
- `schema_v2_corrected.sql` - 修正版本
- `schema_v3_utc.sql` - UTC 時區版本
- `schema_v4_best_practice.sql` - 最佳實踐版本

#### 📁 migrations/
資料庫遷移相關檔案
- `README.md` - 遷移說明文件

### 📁 backups/
資料庫備份檔案

#### 📁 full_backups/
完整資料庫備份
- 格式：`backup_YYYYMMDD_HHMMSS.sql`

#### 📁 data_backups/
特定資料備份
- 格式：`{table_name}_backup_YYYYMMDD_HHMMSS.json`

#### 📁 migration_backups/
遷移前的備份
- 格式：`backup_before_migration_YYYYMMDD_HHMMSS.sql`

### 📁 scripts/
資料庫相關腳本

#### 📁 maintenance/
維護腳本
- 資料庫清理
- 效能優化
- 索引重建

#### 📁 data_management/
資料管理腳本
- 資料匯入/匯出
- 資料轉換
- 資料驗證

#### 📁 utilities/
工具腳本
- 連線測試
- 設定檢查
- 其他實用工具

## 命名規範

### 檔案命名規則
1. **Schema 檔案**：`schema_v{版本號}_{描述}.sql`
2. **備份檔案**：`{類型}_backup_YYYYMMDD_HHMMSS.{副檔名}`
3. **腳本檔案**：`{功能}_{描述}.{副檔名}`

### 版本號規則
- v1: 初始版本
- v2: 修正版本
- v3: UTC 時區版本
- v4: 最佳實踐版本

## 使用指南

### 新增 Schema 版本
1. 複製當前 schema 到 versions 資料夾
2. 命名為 `schema_v{新版本號}_{描述}.sql`
3. 更新此 README 文件

### 建立備份
1. 完整備份：放在 `backups/full_backups/`
2. 資料備份：放在 `backups/data_backups/`
3. 遷移備份：放在 `backups/migration_backups/`

### 新增腳本
根據腳本功能放入對應的資料夾：
- 維護相關：`scripts/maintenance/`
- 資料管理：`scripts/data_management/`
- 工具腳本：`scripts/utilities/`

## 注意事項
- 定期清理舊的備份檔案
- 重要變更前務必建立備份
- 保持檔案命名的一致性
- 更新此 README 文件以反映結構變更
