# Python-Multipart 使用指南

## 概述

本專案已將 `python-multipart` 添加為依賴，以取代舊的 `multipart` 套件，解決棄用警告。

## 依賴配置

在 `pyproject.toml` 中已添加：

```toml
python-multipart = ">=0.0.7"  # 用於處理表單資料，取代舊的 multipart 套件
```

## 正確的使用方式

### 1. 導入 Form 類別

```python
from fastapi import Form, File, UploadFile
```

### 2. 處理表單資料

```python
from fastapi import APIRouter, Form
from typing import Optional

router = APIRouter()

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    處理檔案上傳和表單資料
    """
    return {
        "filename": file.filename,
        "description": description
    }
```

### 3. 處理純表單資料

```python
@router.post("/submit-form/")
async def submit_form(
    name: str = Form(...),
    email: str = Form(...),
    message: Optional[str] = Form(None)
):
    """
    處理純表單資料（不包含檔案）
    """
    return {
        "name": name,
        "email": email,
        "message": message
    }
```

## 注意事項

1. **不要直接導入 multipart**：避免使用 `import multipart` 或 `from multipart import ...`
2. **使用 FastAPI 的 Form 類別**：讓 FastAPI 自動處理 `python-multipart` 的整合
3. **依賴注入**：使用 FastAPI 的依賴注入系統來處理表單資料

## 測試

確保表單處理功能正常運作：

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_form_submission():
    """測試表單提交功能"""
    response = client.post(
        "/submit-form/",
        data={
            "name": "測試用戶",
            "email": "test@example.com",
            "message": "測試訊息"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "測試用戶"
```

## 相關連結

- [FastAPI Form 文件](https://fastapi.tiangolo.com/tutorial/request-forms/)
- [Python-Multipart GitHub](https://github.com/andrew-d/python-multipart)
