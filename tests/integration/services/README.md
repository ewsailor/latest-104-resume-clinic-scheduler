# 服務層整合測試

本目錄包含服務層的整合測試，測試業務邏輯、錯誤處理和效能。

## 測試檔案

- `test_schedule_service_integration.py` - ScheduleService 整合測試
- `test_service_business_logic_integration.py` - 服務層業務邏輯整合測試
- `test_service_error_handling_integration.py` - 服務層錯誤處理整合測試
- `test_service_performance_integration.py` - 服務層效能整合測試

## 測試範圍

### ScheduleService 整合測試

- 時段重疊檢查
- 時段建立、更新、刪除
- 時段查詢和篩選
- 狀態決定邏輯
- ORM 物件建立

### 業務邏輯整合測試

- 複雜業務流程
- 多步驟操作
- 資料一致性
- 業務規則驗證

### 錯誤處理整合測試

- 衝突錯誤處理
- 驗證錯誤處理
- 資料庫錯誤處理
- 服務層錯誤轉換

### 效能整合測試

- 批量操作效能
- 查詢效能
- 記憶體使用
- 並發處理

## 執行方式

```bash
# 執行所有服務層整合測試
pytest tests/integration/services/ -v

# 執行特定測試檔案
pytest tests/integration/services/test_schedule_service_integration.py -v
```
