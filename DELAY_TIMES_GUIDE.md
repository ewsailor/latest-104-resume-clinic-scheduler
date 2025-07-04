# 延遲時間管理系統使用指南

## 概述

本系統統一管理所有 async/await 延遲時間，提供集中化的配置和更好的可維護性。

## 延遲時間常數定義

### 聊天相關延遲 (DELAY_TIMES.CHAT)

```javascript
CHAT: {
  RESPONSE: 1000,        // Giver 回覆延遲
  FORM_SUBMIT: 1000,     // 表單提交後延遲
  OPTION_SELECT: 1000,   // 選項選擇後延遲
  SUCCESS_MESSAGE: 1000, // 成功訊息延遲
  CANCEL_MESSAGE: 1000,  // 取消訊息延遲
  VIEW_TIMES: 1000,      // 查看時間延遲
  SINGLE_TIME: 100,      // 單筆時段處理延遲
  MULTIPLE_TIMES: 1000,  // 多筆時段處理延遲
  VALIDATION_ERROR: 1000, // 驗證錯誤延遲
  SUBMISSION_RESULT: 1000 // 提交結果延遲
}
```

### UI 相關延遲 (DELAY_TIMES.UI)

```javascript
UI: {
  MODAL_CLEANUP: 150,    // Modal 清理延遲
  FOCUS_TRANSFER: 0,     // 焦點轉移延遲
  FOCUS_RETRY: 50,       // 焦點重試延遲
  BACKDROP_CLEANUP: 0,   // Backdrop 清理延遲
  CLOSE_CONFIRMATION: 150 // 關閉確認延遲
}
```

### 錯誤處理延遲 (DELAY_TIMES.ERROR)

```javascript
ERROR: {
  AUTO_REMOVE: 5000,     // 錯誤訊息自動移除
  TOAST_DURATION: 3000,  // Toast 顯示時間
  SUCCESS_DURATION: 3000, // 成功訊息顯示時間
  INFO_DURATION: 3000    // 資訊訊息顯示時間
}
```

### 動畫和過渡延遲 (DELAY_TIMES.ANIMATION)

```javascript
ANIMATION: {
  TOPIC_OVERFLOW: 1000,  // 主題溢出檢查延遲
  DOM_UPDATE: 0,         // DOM 更新延遲
  RESIZE_DEBOUNCE: 300   // 視窗大小調整防抖延遲
}
```

### 資料載入延遲 (DELAY_TIMES.DATA)

```javascript
DATA: {
  RETRY_DELAY: 1000,     // 重試延遲
  LOADING_TIMEOUT: 30000 // 載入超時
}
```

## 使用方式

### 1. 基本使用

```javascript
// 舊方式
await delay(1000);

// 新方式
await delay(DELAY_TIMES.CHAT.RESPONSE);
```

### 2. 使用 nonBlockingDelay

```javascript
// 舊方式
await nonBlockingDelay(1000, () => {
  DOM.chat.addGiverResponse("訊息");
});

// 新方式
await nonBlockingDelay(DELAY_TIMES.CHAT.RESPONSE, () => {
  DOM.chat.addGiverResponse("訊息");
});
```

### 3. 實際應用範例

#### 聊天回覆

```javascript
// 模擬 Giver 回覆
await delay(DELAY_TIMES.CHAT.RESPONSE);
DOM.chat.addGiverResponse("回覆內容");
```

#### 表單提交

```javascript
// 表單提交後延遲
await nonBlockingDelay(DELAY_TIMES.CHAT.FORM_SUBMIT, () => {
  const responseHTML = TEMPLATES.chat.afterScheduleOptions(
    formattedSchedule,
    notes
  );
  chatMessages.insertAdjacentHTML("beforeend", responseHTML);
});
```

#### Modal 清理

```javascript
// Modal 清理延遲
await nonBlockingDelay(DELAY_TIMES.UI.MODAL_CLEANUP, () => {
  const backdrop = document.querySelector(".modal-backdrop");
  if (backdrop) backdrop.remove();
  document.body.classList.remove("modal-open");
});
```

#### 錯誤訊息自動移除

```javascript
// 錯誤訊息自動移除
await delay(DELAY_TIMES.ERROR.AUTO_REMOVE);
if (errorElement.parentNode) {
  errorElement.remove();
}
```

## 最佳實踐

### 1. 選擇合適的延遲類型

- 使用 `CHAT.RESPONSE` 用於聊天回覆
- 使用 `UI.MODAL_CLEANUP` 用於 UI 清理
- 使用 `ERROR.AUTO_REMOVE` 用於錯誤訊息

### 2. 保持一致性

- 相同類型的操作使用相同的延遲時間
- 避免在程式碼中硬編碼延遲時間

### 3. 適時調整

- 根據使用者體驗需求調整延遲時間
- 考慮網路延遲和設備效能

### 4. 註解說明

```javascript
// 等待 Giver 回覆延遲，提供自然的對話體驗
await delay(DELAY_TIMES.CHAT.RESPONSE);
```

## 修改延遲時間

如需修改延遲時間，只需在 `DELAY_TIMES` 常數中調整對應的值：

```javascript
// 修改 Giver 回覆延遲為 800ms
DELAY_TIMES.CHAT.RESPONSE = 800;

// 修改錯誤訊息自動移除時間為 10 秒
DELAY_TIMES.ERROR.AUTO_REMOVE = 10000;
```

## 優勢

1. **集中管理**：所有延遲時間在一個地方定義
2. **易於維護**：修改延遲時間只需改一個地方
3. **保持一致性**：確保相同操作使用相同延遲時間
4. **提高可讀性**：使用有意義的常數名稱
5. **便於調試**：可以輕鬆調整延遲時間進行測試
