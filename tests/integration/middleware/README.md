# 中間件整合測試

本目錄包含所有中間件的整合測試，確保中間件能正確運作並協同工作。

## 測試結構

### 1. CORS 中間件測試 (`test_cors_middleware.py`)

測試 CORS 中間件的功能，包括：

- **預檢請求處理**：測試 OPTIONS 請求的 CORS 標頭設定
- **允許的來源**：驗證允許的來源列表（localhost:3000, localhost:8000, 127.0.0.1:3000, 127.0.0.1:8000）
- **允許的 HTTP 方法**：測試 GET, POST, PUT, PATCH, DELETE, OPTIONS
- **憑證支援**：驗證 `access-control-allow-credentials` 設定
- **CORS 標頭**：檢查回應中的 CORS 標頭
- **多來源處理**：測試多個來源的處理

### 2. 錯誤處理中間件測試 (`test_error_handler_middleware.py`)

測試錯誤處理中間件的功能，包括：

- **成功請求**：確保成功請求不受錯誤處理中間件影響
- **通用異常處理**：測試一般 Exception 的處理
- **HTTP 異常處理**：測試 FastAPI HTTPException 的處理（由內建處理器處理）
- **自定義錯誤處理**：測試各種自定義錯誤類型的處理：
  - ValidationError (422)
  - AuthenticationError (401)
  - AuthorizationError (403)
  - BusinessLogicError (400)
  - DatabaseError (500)
  - ScheduleNotFoundError (404)
  - UserNotFoundError (404)
  - ConflictError (409)
  - ServiceUnavailableError (503)
  - LivenessCheckError (500)
  - ReadinessCheckError (503)
- **錯誤回應格式**：驗證錯誤回應的結構和時間戳格式
- **錯誤回應一致性**：確保所有錯誤回應格式一致

### 3. 中間件整合測試 (`test_middleware_integration.py`)

測試多個中間件同時運作的情況，包括：

- **CORS 與成功回應整合**：測試 CORS 中間件與成功回應的協同工作
- **CORS 與錯誤回應整合**：測試 CORS 中間件與錯誤回應的協同工作
- **預檢請求與錯誤端點**：測試 OPTIONS 請求與錯誤端點的整合
- **POST 請求與錯誤處理**：測試 POST 請求的 CORS 和錯誤處理整合
- **HTTP 異常與 CORS**：測試 HTTP 異常與 CORS 的整合
- **多來源與錯誤處理**：測試多個來源與錯誤處理的整合
- **CORS 標頭保留**：測試錯誤回應中 CORS 標頭的保留
- **中間件執行順序**：測試中間件執行順序的一致性
- **時間戳一致性**：測試錯誤回應中時間戳的一致性
- **不同 HTTP 方法與錯誤**：測試不同 HTTP 方法與錯誤處理的 CORS 整合

## 測試覆蓋率

- **總覆蓋率**：90%
- **CORS 中間件**：71%（未覆蓋 `log_app_startup` 函式）
- **錯誤處理中間件**：100%

## 重要發現與修復

### 1. CORS 標頭保留問題

**問題**：錯誤處理中間件返回的 JSONResponse 沒有保留 CORS 標頭。

**解決方案**：在錯誤處理中間件中手動添加 CORS 標頭：

```python
# 保留原始請求的 CORS 相關標頭
origin = request.headers.get("origin")
if origin:
    response.headers["access-control-allow-origin"] = origin
    response.headers["access-control-allow-credentials"] = "true"
    response.headers["access-control-allow-methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["access-control-allow-headers"] = "*"
```

### 2. HTTP 異常處理差異

**問題**：FastAPI 的 HTTPException 被內建處理器處理，不會到達我們的錯誤處理中間件。

**解決方案**：在測試中區分處理方式：

- 自定義錯誤：由我們的錯誤處理中間件處理，使用 `{"error": {...}}` 格式
- HTTP 異常：由 FastAPI 內建處理器處理，使用 `{"detail": "..."}` 格式

### 3. CORS 標頭行為差異

**發現**：CORS 中間件在不同情況下添加不同的標頭：

- 成功請求：只添加基本 CORS 標頭
- 預檢請求：添加完整的 CORS 標頭
- 錯誤回應：由錯誤處理中間件添加完整 CORS 標頭

## 執行測試

```bash
# 執行所有中間件測試
python -m pytest tests/integration/middleware/ -v

# 執行特定測試
python -m pytest tests/integration/middleware/test_cors_middleware.py -v
python -m pytest tests/integration/middleware/test_error_handler_middleware.py -v
python -m pytest tests/integration/middleware/test_middleware_integration.py -v

# 檢查覆蓋率
python -m pytest tests/integration/middleware/ --cov=app.middleware --cov-report=term-missing
```

## 測試結果

- **總測試數**：34 個測試
- **通過率**：100%
- **執行時間**：約 0.67 秒
- **覆蓋率**：90%

所有中間件整合測試都已成功實現並通過驗證，確保了中間件的正確運作和協同工作。
