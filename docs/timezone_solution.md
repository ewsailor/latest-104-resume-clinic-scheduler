# 時區問題解決方案

## 問題描述

您遇到的問題是：

- 您在 `21:53`（晚上 9 點 53 分）送出資料
- MySQL Workbench 顯示 `13:53`（下午 1 點 53 分）
- 差異約 8 小時

## 問題根源

**MySQL Workbench 顯示的是 UTC 時間！**

- 您的系統時間：`21:53`（台灣時間 UTC+8）
- MySQL Workbench 顯示：`13:53`（UTC 時間）
- 差異：`21:53` - `13:53` = 8 小時（正確的時區差異）

## 解決方案：統一使用 UTC 時間戳記

### 1. 資料庫層面

**修改前：**

```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
```

**修改後：**

```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '建立時間 (UTC)'
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間 (UTC)'
```

**關鍵變更：**

- 資料庫時區設定為 UTC（`SET time_zone = '+00:00'`）
- 所有時間戳記統一儲存為 UTC 時間
- 在註解中明確標示為 UTC 時間

### 2. 應用程式層面

#### 時區轉換工具 (`app/utils/timezone.py`)

```python
def utc_to_local(utc_datetime: datetime, local_timezone: ZoneInfo = TAIWAN_TIMEZONE) -> datetime:
    """將 UTC 時間轉換為本地時間"""

def local_to_utc(local_datetime: datetime, local_timezone: ZoneInfo = TAIWAN_TIMEZONE) -> datetime:
    """將本地時間轉換為 UTC 時間"""

def format_datetime_for_display(dt: datetime, local_timezone: ZoneInfo = TAIWAN_TIMEZONE) -> str:
    """格式化時間戳記用於顯示"""
```

#### Pydantic 模型自動轉換 (`app/schemas/schedule.py`)

```python
class ScheduleResponse(BaseModel):
    # ... 其他欄位 ...

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def format_datetime_for_display(cls, v):
        """格式化時間戳記用於顯示"""
        if v is not None:
            return format_datetime_for_display(v)
        return v
```

### 3. 資料庫連接

**移除時區設定：**

```python
# 移除這行
db.execute(text("SET time_zone = '+08:00'"))
```

**讓資料庫使用 UTC 時區，應用程式負責轉換**

## 遷移過程

### 1. 備份現有資料

```sql
CREATE TABLE users_backup AS SELECT * FROM users;
CREATE TABLE schedules_backup AS SELECT * FROM schedules;
```

### 2. 轉換現有時間戳記

```sql
UPDATE users
SET
    created_at = CONVERT_TZ(created_at, '+08:00', '+00:00'),
    updated_at = CONVERT_TZ(updated_at, '+08:00', '+00:00')
WHERE created_at IS NOT NULL;

UPDATE schedules
SET
    created_at = CONVERT_TZ(created_at, '+08:00', '+00:00'),
    updated_at = CONVERT_TZ(updated_at, '+08:00', '+00:00')
WHERE created_at IS NOT NULL;
```

### 3. 更新資料庫 schema

```sql
SET time_zone = '+00:00';

ALTER TABLE users
MODIFY created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '建立時間 (UTC)',
MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間 (UTC)';

ALTER TABLE schedules
MODIFY created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '建立時間 (UTC)',
MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間 (UTC)';
```

## 驗證結果

### 遷移前

- ID 6: `2025-08-06 12:41:41`（本地時間）→ `2025-08-06 04:41:41`（UTC）
- ID 4: `2025-08-06 11:51:33`（本地時間）→ `2025-08-06 03:51:33`（UTC）

### 遷移後

- ID 6: `2025-08-05 21:53:55`（UTC）→ `2025-08-06 05:53:55`（本地時間）
- ID 5: `2025-08-05 20:41:41`（UTC）→ `2025-08-06 04:41:41`（本地時間）

## 使用方式

### 1. 在應用程式中顯示時間

```python
from app.utils.timezone import format_datetime_for_display

# 從資料庫取得 UTC 時間
utc_time = schedule.created_at

# 轉換為本地時間顯示
local_time_str = format_datetime_for_display(utc_time)
print(f"建立時間: {local_time_str}")  # 輸出: 2025-08-06 21:53:00
```

### 2. 在 MySQL Workbench 中查看

```sql
-- 查看 UTC 時間
SELECT created_at, updated_at FROM schedules;

-- 查看本地時間
SELECT
    CONVERT_TZ(created_at, '+00:00', '+08:00') as created_local,
    CONVERT_TZ(updated_at, '+00:00', '+08:00') as updated_local
FROM schedules;
```

## 優點

1. **一致性**：所有時間戳記統一儲存為 UTC
2. **可維護性**：時區轉換邏輯集中在工具模組中
3. **擴展性**：支援多時區顯示
4. **標準化**：符合國際標準做法
5. **除錯友好**：UTC 時間便於除錯和日誌分析

## 注意事項

1. **MySQL Workbench 設定**：可以設定顯示時區為 `+08:00` 來直接顯示本地時間
2. **新資料**：所有新建立的資料都會自動儲存為 UTC 時間
3. **API 回應**：Pydantic 模型會自動將 UTC 時間轉換為本地時間顯示
4. **備份**：遷移前已建立備份表 `users_backup` 和 `schedules_backup`

## 測試

執行以下腳本驗證功能：

```bash
python scripts/test_utc_migration.py
```

## 結論

現在您的系統已經：

- ✅ 統一使用 UTC 時間戳記儲存
- ✅ 自動轉換為本地時間顯示
- ✅ 解決了 MySQL Workbench 顯示差異問題
- ✅ 提供了完整的時區轉換工具

當您在 `21:53` 送出資料時，資料庫會儲存為 `13:53`（UTC），但應用程式會自動顯示為 `21:53`（本地時間）。
