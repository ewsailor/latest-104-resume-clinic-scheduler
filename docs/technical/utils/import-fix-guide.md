# Import 語句自動修復指南

## 概述

本專案已配置自動化工具來處理函式內部的 `import` 和 `from import` 語句，確保所有 import 語句都位於檔案頂部，符合 Python 的 PEP 8 編碼規範。

## 功能說明

### 自動修復功能

當您在函式內部添加 `import` 或 `from import` 語句時，pre-commit hook 會自動：

1. **檢測函式內部的 import 語句**
2. **將這些語句移到檔案頂部**
3. **移除函式內部的原始 import 語句**
4. **避免重複的 import 語句**

### 範例

**修復前：**

```python
"""
模組說明文件。
"""

def my_function():
    import json
    from datetime import datetime
    import pdb; pdb.set_trace()

    data = {"test": "value"}
    return json.dumps(data)
```

**修復後：**

```python
"""
模組說明文件。
"""

from datetime import datetime
import json
import pdb

def my_function():
    pdb.set_trace()

    data = {"test": "value"}
    return json.dumps(data)
```

## 配置檔案

### 1. Pre-commit 配置 (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: local
    hooks:
      - id: fix-function-imports
        name: Fix function imports
        entry: python scripts/fix_imports.py
        language: system
        types: [python]
        pass_filenames: true
```

### 2. 自定義腳本 (`scripts/fix_imports.py`)

這個腳本負責：

- 解析 Python 檔案的 AST（抽象語法樹）
- 識別函式內部的 import 語句
- 將這些語句移到檔案頂部
- 移除函式內部的原始語句

## 使用方法

### 自動執行

每次執行 `git commit` 時，pre-commit hook 會自動運行並修復所有 Python 檔案中的函式內部 import 語句。

### 手動執行

您也可以手動執行修復：

```bash
# 修復單一檔案
python scripts/fix_imports.py path/to/your/file.py

# 運行所有 pre-commit hooks
poetry run pre-commit run --all-files
```

## 工作流程

1. **開發時**：您可以正常在函式內部添加 import 語句
2. **提交前**：pre-commit hook 自動修復這些語句
3. **提交後**：所有 import 語句都在檔案頂部，符合編碼規範

## 注意事項

### 支援的語句類型

- `import module_name`
- `from module_name import item`
- `from module_name import item as alias`
- 複雜語句（如 `import pdb; pdb.set_trace()`）會被正確分離：
  - `import pdb` 移到檔案頂部
  - `pdb.set_trace()` 保留在函式內部

### 不支援的情況

- 條件式 import（如 `if condition: import module`）
- 動態 import（如 `__import__()`）
- 字串形式的 import

### 錯誤處理

如果檔案有語法錯誤，腳本會跳過該檔案的處理並顯示警告訊息。

## 相關工具

除了自定義的 import 修復腳本外，專案還配置了：

- **isort**：排序和組織 import 語句
- **autoflake**：移除未使用的 import 語句
- **black**：程式碼格式化
- **flake8**：程式碼品質檢查

## 故障排除

### 常見問題

1. **腳本無法執行**

   - 確保 Python 環境正確安裝
   - 檢查檔案權限

2. **某些 import 沒有被修復**

   - 檢查 import 語句是否在函式內部
   - 確認語句格式正確

3. **重複的 import 語句**
   - 腳本會自動避免重複
   - 如果仍有問題，檢查檔案結構

### 除錯模式

如需詳細的除錯資訊，可以修改 `scripts/fix_imports.py` 中的 `print` 語句或添加更多日誌輸出。

## 貢獻指南

如果您需要修改 import 修復邏輯：

1. 編輯 `scripts/fix_imports.py`
2. 測試修改後的腳本
3. 更新本文檔
4. 提交變更

## 總結

這個自動化工具能夠：

1. **正確處理 docstring**：import 語句會被放在 docstring 之後，而不是內部
2. **智能排序**：與 isort 配合，自動排序 import 語句
3. **處理複雜語句**：正確分離 `import pdb; pdb.set_trace()` 這樣的複雜語句
4. **移除未使用的 import**：與 autoflake 配合，自動移除未使用的 import
5. **保持程式碼整潔**：確保所有 import 語句都在檔案頂部，符合 PEP 8 規範

## 相關連結

- [PEP 8 - Import 語句規範](https://www.python.org/dev/peps/pep-0008/#imports)
- [Pre-commit 官方文件](https://pre-commit.com/)
- [Python AST 模組文件](https://docs.python.org/3/library/ast.html)
