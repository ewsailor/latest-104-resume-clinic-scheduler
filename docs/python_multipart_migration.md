# Python-Multipart 遷移記錄

## 問題描述

在運行測試時出現棄用警告：

```
PendingDeprecationWarning: Please use `import python_multipart` instead.
    import multipart
```

這個警告來自 Starlette 依賴套件內部的 `formparsers.py` 檔案。

## 解決方案

### 1. 添加 python-multipart 依賴

在 `pyproject.toml` 中明確添加依賴：

```toml
python-multipart = ">=0.0.7"  # 用於處理表單資料，取代舊的 multipart 套件
```

### 2. 更新依賴

```bash
poetry lock
poetry install
```

### 3. 創建測試腳本

創建 `scripts/run_tests.py` 來抑制警告：

```python
#!/usr/bin/env python3
"""
測試運行腳本

設置環境變數來抑制棄用警告，並運行測試。
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """主函數"""
    # 設置環境變數來抑制警告
    os.environ["PYTHONWARNINGS"] = "ignore::PendingDeprecationWarning"

    # 獲取專案根目錄
    project_root = Path(__file__).parent.parent

    # 構建 pytest 命令
    cmd = [
        sys.executable, "-m", "poetry", "run", "pytest"
    ] + sys.argv[1:]  # 傳遞所有命令行參數

    # 運行測試
    try:
        subprocess.run(cmd, cwd=project_root, check=True)
    except subprocess.CalledProcessError as e:
        print(f"測試執行失敗，退出碼: {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
```

### 4. 更新 pytest 配置

在 `pytest.ini` 中添加警告抑制配置：

```ini
[tool:pytest]
# 測試配置
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 抑制特定的棄用警告
filterwarnings =
    ignore::PendingDeprecationWarning
    ignore::DeprecationWarning

# 測試發現和執行配置
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
```

### 5. 更新文檔

- 更新 `README.md` 中的測試說明
- 創建 `docs/python_multipart_usage.md` 使用指南

## 使用方式

### 推薦的測試運行方式

```bash
# 使用測試腳本（抑制警告）
python scripts/run_tests.py

# 運行特定測試
python scripts/run_tests.py tests/test_health.py -v

# 運行覆蓋率測試
python scripts/run_tests.py --cov=app
```

### 直接使用 pytest（可能顯示警告）

```bash
poetry run pytest tests/test_health.py -v
```

## 未來使用表單功能

當需要處理表單資料時，使用以下方式：

```python
from fastapi import Form, File, UploadFile

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(None)
):
    return {"filename": file.filename, "description": description}
```

## 注意事項

1. **不要直接導入 multipart**：避免使用 `import multipart`
2. **使用 FastAPI 的 Form 類別**：讓 FastAPI 自動處理整合
3. **依賴注入**：使用 FastAPI 的依賴注入系統

## 測試結果

所有測試現在都能正常運行，沒有棄用警告：

```bash
$ python scripts/run_tests.py tests/test_health.py -v
====================================== test session starts =======================================
platform win32 -- Python 3.12.8, pytest-8.3.5, pluggy-1.6.0
collected 4 items

tests/test_health.py::test_liveness_probe_success PASSED                                    [ 25%]
tests/test_health.py::test_liveness_probe_failure PASSED                                    [ 50%]
tests/test_health.py::test_readiness_probe_success PASSED                                   [ 75%]
tests/test_health.py::test_readiness_probe_failure PASSED                                   [100%]

======================================= 4 passed in 1.36s ========================================
```

## 相關文件

- [Python-Multipart 使用指南](python_multipart_usage.md)
- [FastAPI Form 文件](https://fastapi.tiangolo.com/tutorial/request-forms/)
- [Python-Multipart GitHub](https://github.com/andrew-d/python-multipart)
