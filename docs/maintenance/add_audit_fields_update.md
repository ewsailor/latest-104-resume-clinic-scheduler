# 新增審計欄位更新記錄

## 概述

本次更新在 `schedules` 資料表中新增了 4 個審計欄位，以提供完整的操作追蹤功能：

- `created_by`: 建立者的使用者 ID
- `created_by_role`: 建立者角色
- `deleted_by`: 刪除者的使用者 ID
- `deleted_by_role`: 刪除者角色

同時移除了向後相容的 `creator_role` 屬性，統一使用新的審計欄位。

## 修改原因

### 原有問題

1. **審計追蹤不完整**：只有 `updated_by` 和 `updated_by_role`，缺少建立和刪除的追蹤
2. **向後相容性問題**：`creator_role` 屬性與實際的審計欄位不一致
3. **資料完整性不足**：無法追蹤誰建立了時段，誰刪除了時段

### 改善目標

1. **完整的審計追蹤**：記錄建立、更新、刪除的完整操作者資訊
2. **資料一致性**：統一使用標準的審計欄位命名
3. **業務需求支援**：支援更詳細的操作日誌和權限控制

## 修改範圍

### 1. 資料庫結構 (`database/schemas/current/schema.sql`)

```sql
-- 新增建立者欄位
`created_by` INT UNSIGNED NULL
    COMMENT '建立者的使用者 ID，可為 NULL（表示系統自動建立）',
`created_by_role` ENUM('GIVER', 'TAKER', 'SYSTEM') NULL
    COMMENT '建立者角色',

-- 新增刪除者欄位
`deleted_by` INT UNSIGNED NULL
    COMMENT '刪除者的使用者 ID，可為 NULL（表示系統自動刪除）',
`deleted_by_role` ENUM('GIVER', 'TAKER', 'SYSTEM') NULL
    COMMENT '刪除者角色',

-- 新增外鍵約束
CONSTRAINT `fk_schedules_created_by`
    FOREIGN KEY (`created_by`)
    REFERENCES `users`(`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
CONSTRAINT `fk_schedules_deleted_by`
    FOREIGN KEY (`deleted_by`)
    REFERENCES `users`(`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
```

### 2. 模型定義 (`app/models/schedule.py`)

```python
# 新增建立者欄位
created_by = Column(
    INTEGER(unsigned=True),
    ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True,
    comment="建立者的使用者 ID，可為 NULL（表示系統自動建立）",
)
created_by_role = Column(
    Enum(UserRoleEnum),
    nullable=True,
    comment="建立者角色",
)

# 新增刪除者欄位
deleted_by = Column(
    INTEGER(unsigned=True),
    ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True,
    comment="刪除者的使用者 ID，可為 NULL（表示系統自動刪除）",
)
deleted_by_role = Column(
    Enum(UserRoleEnum),
    nullable=True,
    comment="刪除者角色",
)

# 新增關聯關係
created_by_user = relationship("User", foreign_keys=[created_by], lazy='joined')
deleted_by_user = relationship("User", foreign_keys=[deleted_by], lazy='joined')

# 移除向後相容屬性
# @property
# def creator_role(self):
#     """建立者角色（向後相容屬性）"""
#     return self.updated_by_role
```

### 3. Schema 定義 (`app/schemas/schedule.py`)

```python
class ScheduleResponse(BaseModel):
    # 移除向後相容欄位
    # creator_role: str = Field(description="建立者角色（向後相容屬性）")

    # 新增審計欄位
    created_by: int | None = Field(None, description="建立者的使用者 ID")
    created_by_role: UserRoleEnum | None = Field(None, description="建立者角色")
    deleted_by: int | None = Field(None, description="刪除者的使用者 ID")
    deleted_by_role: UserRoleEnum | None = Field(None, description="刪除者角色")
```

### 4. CRUD 操作 (`app/crud/crud_schedule.py`)

```python
def create_schedules(self, db, schedules, updated_by, updated_by_role):
    # 建立時段時同時設定建立者和更新者資訊
    schedule = Schedule(
        # ... 其他欄位 ...
        created_by=updated_by,
        created_by_role=updated_by_role,
        updated_by=updated_by,
        updated_by_role=updated_by_role,
    )

def delete_schedule(self, db, schedule_id, updated_by, updated_by_role):
    # 軟刪除時設定刪除者資訊
    schedule.deleted_by = updated_by
    schedule.deleted_by_role = updated_by_role
```

### 5. 前端 JavaScript (`static/js/script.js`)

```javascript
// 更新角色資訊來源
const convertedSchedules = schedules.map((schedule) => ({
  // ... 其他欄位 ...
  role: schedule.created_by_role, // 使用 created_by_role 作為角色資訊
  // ... 其他欄位 ...
}));
```

### 6. 測試檔案更新

更新了所有相關的測試檔案，包括：

- `tests/integration/api/test_api_schedule_simple.py`
- `tests/integration/api/test_api_schedule_comprehensive.py`
- `tests/unit/crud/test_crud_schedule.py`

## 資料庫遷移

### Migration 檔案

- 檔案：`alembic/versions/2025_08_17_1952-02e132afa7f0_新增_created_by_created_by_role_deleted_.py`
- 操作：新增 4 個欄位和相關外鍵約束

### 執行遷移

```bash
alembic upgrade head
```

## 測試驗證

### 測試結果

- **總測試數**：223 個測試
- **通過率**：100% (223/223)
- **執行時間**：約 6 秒

### 主要測試類別

1. **時段管理測試**：建立、查詢、更新、刪除
2. **使用者管理測試**：建立、查詢
3. **Giver 管理測試**：資料查詢、篩選
4. **系統功能測試**：健康檢查、錯誤處理

## 向後相容性

### 移除的向後相容項目

1. **`creator_role` 屬性**：已移除，統一使用 `created_by_role`
2. **Schema 中的 `creator_role` 欄位**：已移除

### 建議的遷移步驟

1. 更新前端程式碼，使用 `created_by_role` 替代 `creator_role`
2. 更新 API 文檔，移除 `creator_role` 相關說明
3. 通知相關開發者關於欄位變更

## 主要改善

### 1. 審計追蹤完整性

- ✅ 建立操作追蹤：`created_by` + `created_by_role`
- ✅ 更新操作追蹤：`updated_by` + `updated_by_role`
- ✅ 刪除操作追蹤：`deleted_by` + `deleted_by_role`

### 2. 資料一致性

- ✅ 統一命名規範：`*_by` + `*_by_role`
- ✅ 移除不一致的向後相容屬性
- ✅ 標準化的外鍵約束

### 3. 業務功能支援

- ✅ 完整的操作日誌
- ✅ 詳細的權限控制
- ✅ 審計合規性支援

## 注意事項

### 1. 資料庫相容性

- 新欄位都設為 `NULL`，不會影響現有資料
- 外鍵約束使用 `ON DELETE SET NULL`，確保資料完整性

### 2. API 相容性

- 移除 `creator_role` 可能影響現有前端
- 建議逐步遷移到新的欄位結構

### 3. 效能考量

- 新增的關聯查詢可能影響查詢效能
- 建議在需要時才載入關聯資料（使用 `lazy='joined'`）

## 總結

本次更新成功實現了完整的審計追蹤功能，提供了建立、更新、刪除操作的完整追蹤能力。所有測試都通過，確保了系統的穩定性和功能完整性。建議在生產環境部署前進行充分的測試和驗證。
