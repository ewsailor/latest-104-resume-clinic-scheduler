# Alembic 資料庫遷移指南

## 概述

本專案已成功導入 Alembic 作為資料庫遷移管理工具。Alembic 是 SQLAlchemy 的資料庫遷移工具，可以幫助你：

- 管理資料庫 schema 的變更
- 版本控制資料庫結構
- 在不同環境間同步資料庫變更
- 支援向前和向後遷移

## 專案結構

```
project-root/
├── alembic/                    # Alembic 配置目錄
│   ├── env.py                 # 環境配置檔案
│   ├── script.py.mako         # 遷移腳本模板
│   └── versions/              # 遷移檔案目錄
│       └── 2025_08_09_1114-c6dd3264fae3_建立基準線_現有資料庫結構.py
├── alembic.ini                # Alembic 主配置檔案
└── scripts/
    └── clear_alembic_version.py  # Alembic 版本清理工具
```

## 配置詳情

### 1. alembic.ini 配置

- **檔案命名格式**: 包含時間戳記的格式 `YYYY_MM_DD_HHMM-{rev}_{slug}`
- **資料庫連接**: 動態從 `app.core.settings` 載入
- **路徑配置**: 相對於專案根目錄

### 2. env.py 配置

- **自動導入模型**: 包含 `User` 和 `Schedule` 模型
- **動態資料庫 URL**: 使用應用程式設定中的連接字串
- **Base metadata**: 正確註冊所有模型的 metadata

## 基本使用方法

### 查看當前狀態

```bash
# 查看當前資料庫版本
poetry run alembic current

# 查看遷移歷史
poetry run alembic history

# 查看詳細歷史（包含分支）
poetry run alembic history --verbose
```

### 創建新遷移

```bash
# 自動檢測模型變更並生成遷移
poetry run alembic revision --autogenerate -m "描述變更內容"

# 手動創建空遷移
poetry run alembic revision -m "描述變更內容"
```

### 應用遷移

```bash
# 升級到最新版本
poetry run alembic upgrade head

# 升級到特定版本
poetry run alembic upgrade <revision_id>

# 升級一個版本
poetry run alembic upgrade +1
```

### 回滾遷移

```bash
# 回滾到基準版本
poetry run alembic downgrade base

# 回滾到特定版本
poetry run alembic downgrade <revision_id>

# 回滾一個版本
poetry run alembic downgrade -1
```

## 工作流程

### 1. 修改模型後創建遷移

```bash
# 1. 修改 app/models/ 中的模型檔案
# 2. 生成遷移檔案
poetry run alembic revision --autogenerate -m "新增使用者等級欄位"

# 3. 檢查生成的遷移檔案（在 alembic/versions/ 目錄）
# 4. 如有需要，手動調整遷移檔案

# 5. 應用遷移
poetry run alembic upgrade head
```

### 2. 協作開發流程

```bash
# 拉取最新程式碼後
git pull origin main

# 檢查是否有新的遷移需要應用
poetry run alembic current
poetry run alembic history

# 應用新遷移
poetry run alembic upgrade head
```

## 注意事項

### 1. 資料安全

- **生產環境**: 在應用遷移前務必備份資料庫
- **測試遷移**: 在測試環境先測試遷移
- **檢查遷移**: 仔細檢查自動生成的遷移檔案

### 2. 索引和約束

- 自動生成可能不完美，特別是索引和外鍵約束
- 手動檢查並調整複雜的 schema 變更
- 考慮資料庫效能影響

### 3. 資料遷移

```python
# 在遷移檔案中包含資料遷移
def upgrade():
    # Schema 變更
    op.add_column('users', sa.Column('status', sa.String(20)))

    # 資料遷移
    connection = op.get_bind()
    connection.execute(
        text("UPDATE users SET status = 'ACTIVE' WHERE deleted_at IS NULL")
    )
```

## 故障排除

### 1. 遷移衝突

```bash
# 查看當前狀態
poetry run alembic current

# 查看分支情況
poetry run alembic branches

# 合併分支
poetry run alembic merge -m "合併遷移分支" <rev1> <rev2>
```

### 2. 重置遷移狀態

如果遇到嚴重問題，可以使用清理腳本：

```bash
# 清理 Alembic 版本記錄
poetry run python scripts/clear_alembic_version.py

# 重新標記當前狀態
poetry run alembic stamp head
```

### 3. 常見錯誤

#### "Can't locate revision"

- 檢查遷移檔案是否存在
- 確認 alembic_version 表中的記錄

#### "Can't drop index: needed in foreign key constraint"

- 先刪除外鍵約束，再刪除索引
- 手動調整遷移順序

## 最佳實踐

### 1. 命名規範

- 使用描述性的遷移訊息
- 包含變更類型（add、remove、modify）
- 例如：`add_user_profile_table`、`modify_schedule_status_enum`

### 2. 遷移檔案管理

- 不要修改已應用的遷移檔案
- 如需修正，創建新的遷移檔案
- 保持遷移檔案的簡潔和專注

### 3. 版本控制

- 將遷移檔案納入版本控制
- 確保團隊成員同步遷移狀態
- 在 PR 中包含遷移檔案的審查

## 參考資源

- [Alembic 官方文檔](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 文檔](https://docs.sqlalchemy.org/)
- [專案資料庫模型](../app/models/)
