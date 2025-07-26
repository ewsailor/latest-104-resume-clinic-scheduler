# Submit Schedules 按鈕調試總結

## 問題描述

用戶報告點擊「已新增完成所有時段，請協助送出給 Giver」按鈕後：

1. 系統沒有跳出訊息泡泡
2. 時段狀態仍然顯示為「草稿：尚未送出給 Giver」
3. 期望的行為是顯示成功訊息泡泡，狀態變為「提供時間成功，待 Giver 回覆」

## 問題分析

根據用戶提供的 console 日誌分析：

- 按鈕點擊事件確實被觸發
- `DOM.chat.addUserMessage` 被執行
- 但是沒有看到任何來自 `submit-schedules` case 的日誌訊息
- 這表示 `UIComponents.handleOptionButton` 中的 `submit-schedules` 處理邏輯沒有被執行

## 調試修改

### 1. 在 `handleOptionButton` 中添加調試日誌

**位置**: `static/script.js` 第 7318 行

```javascript
handler: async (data, btn, e) => {
  const { option } = data;

  Logger.info('EventManager: 處理選項按鈕', { option, data });

  // 處理不同選項
  switch (option) {
```

### 2. 在 `submit-schedules` case 開始處添加調試日誌

**位置**: `static/script.js` 第 7364 行

```javascript
case 'submit-schedules':
  Logger.info('EventManager: 進入 submit-schedules case');
  DOM.chat.addUserMessage(`${CONFIG.UI_TEXT.BUTTONS.SUBMIT_SCHEDULES}`);
```

### 3. 在狀態轉換邏輯中添加詳細調試日誌

**位置**: `static/script.js` 第 7368-7390 行

```javascript
// 將草稿時段轉為正式提供時段
const draftSchedules = ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.DRAFT_SCHEDULES) || [];
Logger.info('EventManager: 檢查草稿時段', { draftSchedulesCount: draftSchedules.length, draftSchedules });

if (draftSchedules.length > 0) {
  // 將草稿時段轉為正式提供時段（移除 isDraft 標記）
  const formalSchedules = draftSchedules.map(schedule => {
    const { isDraft, ...formalSchedule } = schedule;
    return formalSchedule;
  });
  Logger.info('EventManager: 草稿時段已轉換為正式時段', { formalSchedules });

  // 添加到正式提供時段列表
  const existingSchedules = ChatStateManager.getProvidedSchedules();
  const allSchedules = [...existingSchedules, ...formalSchedules];
  Logger.info('EventManager: 合併時段列表', { existingSchedulesCount: existingSchedules.length, formalSchedulesCount: formalSchedules.length, allSchedulesCount: allSchedules.length });
  ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, allSchedules);

  // 清空草稿列表
  ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.DRAFT_SCHEDULES, []);
  Logger.info('EventManager: 草稿列表已清空');
```

### 4. 在成功訊息顯示邏輯中添加調試日誌

**位置**: `static/script.js` 第 7395-7400 行

```javascript
// 延遲顯示成功訊息泡泡
Logger.info("EventManager: 準備延遲顯示成功訊息泡泡");
await delay(DELAY_TIMES.CHAT.SUCCESS_MESSAGE);
Logger.info("EventManager: 延遲完成，準備顯示成功訊息泡泡");
DOM.chat.handleSuccessProvideTime();
Logger.info("EventManager: submit-schedules case 處理完成");
```

## 測試腳本

創建了 `test_submit_schedules_debug.js` 測試腳本，包含：

1. 檢查按鈕是否存在
2. 檢查按鈕的 HTML 結構
3. 檢查當前狀態（草稿時段和正式提供時段）
4. 檢查事件處理器設置
5. 檢查 Logger 功能
6. 監聽 console 日誌以檢測 submit-schedules 相關訊息

## 預期結果

添加調試日誌後，當點擊 submit-schedules 按鈕時，應該在 console 中看到：

1. `EventManager: 處理選項按鈕` - 確認按鈕點擊被處理
2. `EventManager: 進入 submit-schedules case` - 確認進入正確的 case
3. `EventManager: 檢查草稿時段` - 顯示草稿時段資訊
4. `EventManager: 草稿時段已轉換為正式時段` - 確認狀態轉換
5. `EventManager: 合併時段列表` - 顯示合併結果
6. `EventManager: 草稿列表已清空` - 確認草稿清空
7. `EventManager: 準備延遲顯示成功訊息泡泡` - 開始顯示流程
8. `EventManager: 延遲完成，準備顯示成功訊息泡泡` - 延遲完成
9. `EventManager: submit-schedules case 處理完成` - 處理完成

## 下一步

1. 請重新載入頁面並執行測試
2. 添加草稿時段後點擊 submit-schedules 按鈕
3. 查看 console 中的調試日誌
4. 根據日誌結果進一步診斷問題

如果仍然沒有看到 `submit-schedules` 相關的日誌，可能的原因：

- 按鈕的 `data-option` 屬性值不正確
- 事件委派沒有正確設置
- 按鈕被其他事件處理器攔截
- JavaScript 錯誤阻止了事件處理
