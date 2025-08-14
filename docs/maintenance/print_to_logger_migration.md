# Print 語句到 Logger 遷移記錄

## 概述

本專案已成功將所有測試檔案中的 `print()` 語句替換為統一的日誌記錄系統，提升了程式碼品質和可維護性。

## 遷移內容

### 1. 建立統一日誌管理模組

**檔案**: `tests/logger.py`

建立了專用的測試日誌管理模組，提供以下功能：

- 統一的日誌記錄介面
- 支援不同日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 環境變數控制日誌輸出
- 單例模式避免重複初始化
- 便捷函數供測試使用

### 2. 批量替換腳本

**檔案**: `scripts/maintenance/replace_print_statements.py`

建立了自動化腳本來批量替換所有測試檔案中的 `print()` 語句：

- 自動掃描所有測試檔案
- 智能添加導入語句
- 支援多種 print 格式
- 提供處理統計報告

### 3. 處理的檔案統計

**總檔案數**: 20 個測試檔案
**修改檔案數**: 17 個檔案
**替換的 print 語句**: 約 50+ 個

#### 主要修改的檔案：

1. `tests/fixtures/test_data_givers.py` - 13 個 print 語句
2. `tests/integration/api/test_api_schedule_routes.py` - 22 個 print 語句
3. `tests/integration/api/test_api_givers.py` - 20+ 個 print 語句
4. `tests/integration/api/test_api_schedule_comprehensive.py` - 多個 print 語句
5. `tests/integration/api/test_api_schedule_simple.py` - 多個 print 語句
6. `tests/integration/api/test_api_users.py` - 多個 print 語句
7. 其他測試檔案 - 剩餘的 print 語句

## 改進效果

### 1. 程式碼品質提升

**之前**:

```python
def test_something():
    print("測試某個功能")
    # 測試邏輯
```

**之後**:

```python
from tests.logger import log_test_info

def test_something():
    log_test_info("測試某個功能")
    # 測試邏輯
```

### 2. 日誌管理優勢

- **統一格式**: 所有日誌都有統一的時間戳和格式
- **級別控制**: 可以根據環境設定不同的日誌級別
- **可配置性**: 支援環境變數控制日誌輸出
- **可擴展性**: 容易添加新的日誌功能

### 3. 維護性提升

- **集中管理**: 所有日誌邏輯集中在一個模組中
- **易於修改**: 修改日誌格式只需要改一個地方
- **一致性**: 所有測試檔案使用相同的日誌記錄方式

## 使用方式

### 基本使用

```python
from tests.logger import log_test_info, log_test_debug, log_test_warning, log_test_error

def test_example():
    log_test_info("開始測試")
    log_test_debug("除錯資訊")
    log_test_warning("警告訊息")
    log_test_error("錯誤訊息")
```

### 環境變數控制

```bash
# 設定日誌級別
export TEST_LOG_LEVEL=DEBUG  # 顯示所有日誌
export TEST_LOG_LEVEL=INFO   # 只顯示 INFO 及以上級別
export TEST_LOG_LEVEL=WARNING # 只顯示 WARNING 及以上級別
```

## 驗證結果

### 測試通過率

- ✅ 所有修改的測試檔案都能正常執行
- ✅ 日誌輸出格式正確
- ✅ 沒有循環導入問題
- ✅ 功能完整性保持不變

### 執行範例

```bash
# 執行特定測試
pytest tests/integration/api/test_api_schedule_routes.py::TestScheduleAPI::test_create_schedules_success -v

# 執行所有測試
pytest tests/ -v
```

## 後續建議

### 1. 日誌級別優化

根據不同環境設定適當的日誌級別：

- **開發環境**: DEBUG 或 INFO
- **測試環境**: INFO 或 WARNING
- **生產環境**: WARNING 或 ERROR

### 2. 日誌格式自定義

可以根據需求自定義日誌格式：

```python
# 在 tests/logger.py 中修改
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### 3. 日誌檔案輸出

可以添加檔案輸出功能：

```python
# 添加檔案 handler
file_handler = logging.FileHandler('test.log')
file_handler.setFormatter(formatter)
self._logger.addHandler(file_handler)
```

## 總結

這次遷移成功提升了專案的程式碼品質：

1. **統一性**: 所有測試檔案使用統一的日誌記錄方式
2. **可維護性**: 日誌邏輯集中管理，易於維護
3. **可配置性**: 支援環境變數控制日誌輸出
4. **專業性**: 使用標準的日誌記錄而非 print 語句

這為後續的程式碼品質改進奠定了良好的基礎。
