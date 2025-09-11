# Schema 整合測試

本目錄包含 Pydantic 資料模型的整合測試。

## 測試範圍

### 基礎模型測試

- **ScheduleBase**: 單一時段資料模型
- **ScheduleUpdateBase**: 部分更新時段的基礎模型

### 請求模型測試

- **ScheduleCreateRequest**: 批量建立時段的 API 請求模型
- **ScheduleUpdateRequest**: 完整更新時段的 API 請求模型
- **SchedulePartialUpdateRequest**: 部分更新時段的 API 請求模型
- **ScheduleDeleteRequest**: 刪除時段的 API 請求模型

### 回應模型測試

- **ScheduleResponse**: 時段回應模型

## 測試功能

### 1. 資料驗證

- 必要欄位驗證
- 資料類型驗證
- 約束條件驗證（如 `gt=0`）
- 枚舉值驗證
- 字串長度限制

### 2. 序列化和反序列化

- Python 物件序列化
- JSON 序列化
- 反序列化驗證
- 別名處理（`date` ↔ `schedule_date`）

### 3. 錯誤處理

- 驗證錯誤類型檢查
- 錯誤訊息格式驗證
- 邊界條件測試

### 4. API 整合

- Schema 與 FastAPI 端點的整合
- 請求/回應資料驗證
- 錯誤回應格式驗證

## 執行測試

```bash
# 執行所有 Schema 整合測試
python -m pytest tests/integration/schemas/ -v

# 執行特定測試
python -m pytest tests/integration/schemas/test_schema_integration.py::TestScheduleSchemaIntegration::test_schedule_base_validation_success -v
```

## 測試資料

測試使用 `generate_unique_time_slot()` 工具函數生成唯一的時段資料，避免測試間的重疊衝突。

## 注意事項

1. **別名處理**: Pydantic 的別名機制需要特別注意：

   - 輸入時使用別名 `"date"`
   - 輸出時使用內部欄位名 `"schedule_date"`

2. **枚舉值**: 確保使用正確的枚舉值：

   - `ScheduleStatusEnum`: `DRAFT`, `AVAILABLE`, `PENDING`, `ACCEPTED`, `REJECTED`, `CANCELLED`, `COMPLETED`
   - `UserRoleEnum`: `GIVER`, `TAKER`, `SYSTEM`

3. **可選欄位**: 測試可選欄位的預設值和 None 值處理
