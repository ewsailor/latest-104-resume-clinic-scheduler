# 聊天訊息優化文檔

## 問題描述

在 JavaScript 程式碼中，發現多個重複的聊天訊息字串，導致：

1. 程式碼重複，維護困難
2. 訊息修改時需要修改多個地方
3. 容易出現不一致的訊息內容

## 重複訊息統計

### 原始重複訊息

- `'如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。'` - 出現 4 次
- `'有其他問題需要協助嗎？'` - 出現 6 次
- `'如果仍想預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。'` - 出現 3 次
- `'如果仍想提供方便時段，請使用聊天輸入區域下方的功能按鈕。'` - 出現 2 次

## 優化方案

### 1. 新增共用訊息常數

在 `CONFIG.MESSAGES` 中新增以下常數：

```javascript
MESSAGES: {
  FUTURE_BOOKING_HINT: '如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。',
  OTHER_QUESTIONS: '有其他問題需要協助嗎？',
  CANCEL_BOOKING_HINT: '如果仍想預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。',
  CANCEL_PROVIDE_HINT: '如果仍想提供方便時段，請使用聊天輸入區域下方的功能按鈕。'
}
```

### 2. 替換重複訊息

#### 替換位置

1. **BusinessLogic.chat.generateResponse** (第 2973 行)
2. **DOM.chat.handleSkipOption** (第 4308 行)
3. **DOM.chat.handleCancelSchedule** (第 5892 行)
4. **EventManager 刪除時段** (第 7857 行)
5. **DOM.chat.handleDemoTimeSelection** (第 4883 行)
6. **EventManager.handleCancelScheduleForm** (第 7932 行)
7. **其他取消相關函數** (第 4614, 4637, 4702, 5175 行)

#### 替換方式

```javascript
// 替換前
const response =
  "好的，您選擇暫不預約 Giver 時間。<br><br>如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。<br><br>有其他問題需要協助嗎？";

// 替換後
const response = `好的，您選擇暫不預約 Giver 時間。<br><br>${CONFIG.MESSAGES.FUTURE_BOOKING_HINT}<br><br>${CONFIG.MESSAGES.OTHER_QUESTIONS}`;
```

## 優化效果

### 優點

1. **維護性提升**：訊息內容集中管理，修改時只需改一個地方
2. **一致性保證**：避免不同地方使用不同版本的訊息
3. **程式碼簡潔**：減少重複字串，提高可讀性
4. **擴展性**：未來新增訊息時可以統一管理

### 統計

- **減少重複字串**：從 15 個重複字串減少到 4 個常數
- **程式碼行數**：減少約 10 行重複程式碼
- **維護點**：從 15 個維護點減少到 1 個維護點

## 使用建議

### 新增訊息時

1. 先在 `CONFIG.MESSAGES` 中定義常數
2. 使用模板字串引用常數
3. 避免直接寫入字串

### 修改訊息時

1. 只需修改 `CONFIG.MESSAGES` 中的常數
2. 所有使用該訊息的地方會自動更新

### 命名規範

- 使用大寫字母和下劃線
- 名稱要能清楚表達訊息的用途
- 例如：`FUTURE_BOOKING_HINT`、`CANCEL_PROVIDE_HINT`

## 未來改進

1. **國際化支援**：可以擴展為多語言支援
2. **動態訊息**：可以根據使用者狀態動態生成訊息
3. **訊息模板**：可以建立更複雜的訊息模板系統
