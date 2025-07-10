# 性能優化指南

## 已實施的優化措施

### 1. HTML 優化

- ✅ **DNS 預解析**: 預解析外部 CDN 域名
- ✅ **關鍵資源預載入**: 預載入 CSS、JS、圖片等關鍵資源
- ✅ **內聯關鍵 CSS**: 將關鍵渲染路徑的 CSS 內聯到 HTML 中
- ✅ **JavaScript 載入優化**: 使用 `defer` 屬性延遲載入非關鍵 JS

### 2. CSS 優化

- ✅ **GPU 加速**: 使用 `transform: translateZ(0)` 啟用 GPU 加速
- ✅ **will-change 屬性**: 預告瀏覽器元素將要改變的屬性
- ✅ **優化過渡時間**: 將按鈕過渡時間從 0.3s 縮短到 0.15s
- ✅ **關鍵渲染路徑優化**: 優先載入關鍵樣式

### 3. JavaScript 優化

- ✅ **減少調試日誌**: 關閉生產環境的 debug 和 info 日誌
- ✅ **性能配置**: 添加 `PERFORMANCE_CONFIG` 統一管理性能設定
- ✅ **日誌級別調整**: 將預設日誌級別從 INFO 提高到 WARN
- ✅ **日誌數量限制**: 將最大日誌數量從 1000 減少到 100

### 4. 資源載入優化

- ✅ **圖片預載入**: 預載入關鍵圖片資源
- ✅ **字體預載入**: 預載入 Font Awesome 字體
- ✅ **Bootstrap 預載入**: 預載入 Bootstrap CSS

## 進一步優化建議

### 1. 代碼分割和懶載入

```javascript
// 建議實施代碼分割
const loadModule = async (moduleName) => {
  const module = await import(`./modules/${moduleName}.js`);
  return module.default;
};

// 懶載入非關鍵功能
document.addEventListener("DOMContentLoaded", () => {
  // 延遲載入聊天功能
  if (document.querySelector("#chat-messages")) {
    loadModule("chat").then((chatModule) => {
      chatModule.init();
    });
  }
});
```

### 2. 圖片優化

```html
<!-- 使用 WebP 格式和響應式圖片 -->
<picture>
  <source srcset="/static/logo-header.webp" type="image/webp" />
  <source srcset="/static/logo-header.svg" type="image/svg+xml" />
  <img src="/static/logo-header.png" alt="Logo" loading="lazy" />
</picture>
```

### 3. 緩存策略

```javascript
// 實施資源緩存
const cacheResources = async () => {
  const resources = [
    "/static/style.css",
    "/static/script.js",
    "/static/logo-header.svg",
  ];

  if ("caches" in window) {
    const cache = await caches.open("app-v1");
    await cache.addAll(resources);
  }
};
```

### 4. 服務工作者 (Service Worker)

```javascript
// 註冊服務工作者進行緩存
if ("serviceWorker" in navigator) {
  navigator.serviceWorker
    .register("/sw.js")
    .then((registration) => {
      console.log("SW registered");
    })
    .catch((error) => {
      console.log("SW registration failed");
    });
}
```

### 5. 數據庫查詢優化

```python
# 在 main.py 中添加查詢優化
from sqlalchemy.orm import joinedload

def get_optimized_schedules(db: Session):
    """優化的排程查詢"""
    return db.query(Schedule)\
        .options(joinedload(Schedule.giver))\
        .filter(Schedule.date >= datetime.now().date())\
        .order_by(Schedule.date.asc())\
        .limit(50)\
        .all()
```

### 6. API 響應優化

```python
# 添加響應壓縮
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 添加緩存標頭
@app.get("/schedules")
async def get_schedules(request: Request):
    response = templates.TemplateResponse("schedules.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=300"  # 5分鐘緩存
    return response
```

## 性能監控

### 1. 前端性能監控

```javascript
// 添加性能監控
const monitorPerformance = () => {
  // 監控頁面載入時間
  window.addEventListener("load", () => {
    const perfData = performance.getEntriesByType("navigation")[0];
    console.log(
      `頁面載入時間: ${perfData.loadEventEnd - perfData.loadEventStart}ms`
    );
  });

  // 監控資源載入時間
  performance.getEntriesByType("resource").forEach((resource) => {
    if (
      resource.initiatorType === "script" ||
      resource.initiatorType === "css"
    ) {
      console.log(`${resource.name}: ${resource.duration}ms`);
    }
  });
};
```

### 2. 後端性能監控

```python
import time
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} 執行時間: {(end_time - start_time) * 1000:.2f}ms")
        return result
    return wrapper
```

## 預期性能改善

### 載入時間改善

- **首次內容繪製 (FCP)**: 預期改善 30-40%
- **最大內容繪製 (LCP)**: 預期改善 25-35%
- **累積佈局偏移 (CLS)**: 預期改善 50-60%

### 交互響應改善

- **按鈕點擊響應**: 預期改善 40-50%
- **模態框開啟**: 預期改善 30-40%
- **表單提交**: 預期改善 25-35%

### 資源使用改善

- **JavaScript 執行時間**: 預期減少 20-30%
- **CSS 解析時間**: 預期減少 15-25%
- **記憶體使用**: 預期減少 10-20%

## 測試建議

### 1. 使用 Chrome DevTools

- 開啟 Performance 標籤
- 記錄頁面載入過程
- 分析關鍵渲染路徑

### 2. 使用 Lighthouse

```bash
# 安裝 Lighthouse
npm install -g lighthouse

# 運行性能測試
lighthouse https://your-site.com --output html --output-path ./lighthouse-report.html
```

### 3. 使用 WebPageTest

- 訪問 https://www.webpagetest.org/
- 輸入您的網站 URL
- 分析載入時間和性能指標

## 持續優化

### 1. 定期監控

- 每週檢查性能指標
- 監控用戶體驗數據
- 追蹤錯誤率和崩潰率

### 2. 用戶反饋

- 收集用戶性能反饋
- 監控用戶行為數據
- 根據反饋調整優化策略

### 3. 技術更新

- 定期更新依賴庫
- 採用新的性能優化技術
- 跟進瀏覽器新功能
