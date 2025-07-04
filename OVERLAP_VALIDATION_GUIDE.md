# 重疊時段驗證修復指南

## 問題描述

原本的重疊時段驗證沒有正常運作，使用者可以新增多筆相同時段（如 2025/07/04 20:00~22:00）的資料。

**根本原因**：時段被添加到 `draftSchedules` 而不是 `providedSchedules`，而重疊檢查只在 `providedSchedules` 中進行。

**狀態問題**：時段應該先作為草稿時段添加，只有點擊「已新增完成所有時段，請協助送出給 Giver」後才轉為正式提供時段。

## 修復內容

### 1. EventManager.handleScheduleFormSubmit 方法

- ✅ 改用 `ChatStateManager.addDraftSchedule` 方法
- ✅ 處理添加失敗的情況
- ✅ 顯示錯誤訊息
- ✅ 時段先添加為草稿狀態

### 2. ChatStateManager.addDraftSchedule 方法

- ✅ 新增草稿時段添加方法
- ✅ 新增重複時段檢查（包含 draftSchedules）
- ✅ 新增重疊時段檢查（包含 draftSchedules）
- ✅ 返回 false 表示添加失敗
- ✅ 標記時段為草稿狀態（isDraft: true）

### 3. ChatStateManager.addSchedule 方法

- ✅ 新增重複時段檢查（包含 draftSchedules）
- ✅ 新增重疊時段檢查（包含 draftSchedules）
- ✅ 返回 false 表示添加失敗

### 4. ChatStateManager.addSchedules 方法

- ✅ 新增與現有時段的重複檢查（包含 draftSchedules）
- ✅ 新增批次內時段的重複檢查
- ✅ 新增批次內時段的重疊檢查
- ✅ 返回 false 表示添加失敗

### 5. 草稿轉正式時段邏輯

- ✅ 點擊「已新增完成所有時段，請協助送出給 Giver」時
- ✅ 將草稿時段轉換為正式提供時段
- ✅ 移除 isDraft 標記
- ✅ 清空草稿列表

### 6. 調用方法的地方

- ✅ `submitScheduleForm` 處理單筆時段添加失敗
- ✅ `handleMultipleTimesSubmission` 處理多筆時段添加失敗

## 重疊檢查邏輯

### 完全重複檢查

```javascript
const isExactDuplicate =
  schedule1.date === schedule2.date &&
  schedule1.startTime === schedule2.startTime &&
  schedule1.endTime === schedule2.endTime;
```

### 時間重疊檢查

```javascript
const isOverlapping = newStart < existingEnd && newEnd > existingStart;
```

## 測試案例

### 單筆時段測試

1. 新增時段：2025/07/04 20:00~22:00
2. 再次新增相同時段：2025/07/04 20:00~22:00
3. **預期結果**：顯示錯誤訊息，不允許添加

### 重疊時段測試

1. 新增時段：2025/07/04 20:00~22:00
2. 新增重疊時段：2025/07/04 21:00~23:00
3. **預期結果**：顯示錯誤訊息，不允許添加

### 多筆時段測試

1. 輸入多筆時段：
   ```
   2025/07/04 20:00~22:00
   2025/07/04 20:00~22:00
   ```
2. **預期結果**：顯示錯誤訊息，不允許添加

### 多筆重疊時段測試

1. 輸入多筆時段：
   ```
   2025/07/04 20:00~22:00
   2025/07/04 21:00~23:00
   ```
2. **預期結果**：顯示錯誤訊息，不允許添加

### 草稿狀態測試

1. 新增時段：2025/07/04 20:00~22:00
2. 點擊「查看我已提供給 Giver 的時段」
3. **預期結果**：顯示「草稿：尚未送出給 Giver」

### 正式狀態測試

1. 新增時段：2025/07/04 20:00~22:00
2. 點擊「已新增完成所有時段，請協助送出給 Giver」
3. 點擊「查看我已提供給 Giver 的時段」
4. **預期結果**：顯示「成功提供時間，待 Giver 回覆」

### 編輯時段重複測試

1. 新增時段：2025/07/04 20:00~22:00
2. 新增時段：2025/07/05 20:00~22:00
3. 編輯第二個時段，修改為：2025/07/04 20:00~22:00
4. **預期結果**：顯示錯誤訊息「您正輸入的時段，和您之前曾輸入的以下時段重複或重疊，請重新輸入：\n2025/07/04 20:00~22:00」

### 編輯時段重疊測試

1. 新增時段：2025/07/04 20:00~22:00
2. 新增時段：2025/07/05 20:00~22:00
3. 編輯第二個時段，修改為：2025/07/04 21:00~23:00
4. **預期結果**：顯示錯誤訊息「您正輸入的時段，和您之前曾輸入的以下時段重複或重疊，請重新輸入：\n2025/07/04 20:00~22:00」

## 錯誤訊息顯示方式

### 統一錯誤訊息顯示

- ✅ 所有重複時段錯誤訊息都使用 `FormValidator.showValidationError` 顯示
- ✅ 不再使用 `DOM.chat.addGiverResponse` 在聊天區域顯示錯誤訊息
- ✅ 錯誤訊息以彈出視窗形式顯示

### 單筆時段錯誤

```
您正輸入的時段，和您之前曾輸入的以下時段重複或重疊，請重新輸入：
2025/07/04 20:00~22:00
```

### 多筆時段錯誤

```
抱歉，您輸入的時段中有與已提供的時段重複或重疊的部分，請重新輸入。
```

## 修復歷程

### 第一次修復：修正延遲時間常數使用錯誤

- **問題**：`DELAY_TIMES.CHAT.FORM_SUBMIT` 被錯誤地用作 `DELAY_TIMES.CHAT.MESSAGE_SEND`
- **修復**：將 `DELAY_TIMES.CHAT.MESSAGE_SEND` 改為正確的 `DELAY_TIMES.CHAT.FORM_SUBMIT`

### 第二次修復：修正時段重複檢查邏輯

- **問題**：時段重複檢查未生效，因為時段被添加到草稿列表而非正式提供列表
- **修復**：
  1. 在 `ChatStateManager.addDraftSchedule` 方法中加入重疊檢查
  2. 修改調用處理函數以正確處理添加失敗情況

### 第三次修復：修正 EventManager 表單提交邏輯

- **問題**：`EventManager.handleScheduleFormSubmit` 仍將時段加入草稿列表，未使用重疊檢查方法
- **修復**：
  1. 修改為使用新增的 `addDraftSchedule` 方法
  2. 在點擊「已新增完成所有時段，請協助送出給 Giver」時將草稿時段轉為正式時段
  3. 移除草稿標記並清空草稿列表

### 第四次修復：改進重複時段錯誤訊息顯示

- **問題**：重複時段錯誤訊息顯示為簡單的系統訊息，而不是詳細的重複時段列表
- **修復**：
  1. 修改 `EventManager.handleScheduleFormSubmit` 方法中的重複時段檢測部分
  2. 使用 `FormValidator.generateDuplicateScheduleMessage` 生成詳細錯誤訊息
  3. 使用 `DOM.chat.addGiverResponse` 在聊天區域顯示詳細錯誤訊息
  4. 同時修改 `addDraftSchedule` 失敗時的錯誤處理，也使用詳細錯誤訊息

### 第五次修復：統一錯誤訊息顯示方式

- **問題**：重複時段錯誤訊息在不同地方使用不同的顯示方式（聊天區域 vs 彈出視窗）
- **修復**：
  1. 統一所有重複時段錯誤訊息都使用 `FormValidator.showValidationError` 顯示
  2. 修改 `EventManager.handleScheduleFormSubmit` 中的重複時段檢測
  3. 修改 `addDraftSchedule` 失敗時的錯誤處理
  4. 修改 `DOM.chat.handleMultipleTimesSubmission` 中的重複時段檢測
  5. 修改 `DOM.chat.submitScheduleForm` 中的錯誤處理

### 第六次修復：編輯時段重複檢查

- **問題**：編輯時段時沒有進行重複檢查，可以修改為與其他時段重複的時段
- **修復**：
  1. 在 `EventManager.handleScheduleFormSubmit` 的編輯模式中加入重複檢查
  2. 排除正在編輯的時段，檢查修改後的時段是否與其他時段重複或重疊
  3. 使用 `FormValidator.generateDuplicateScheduleMessage` 生成詳細錯誤訊息
  4. 使用 `FormValidator.showValidationError` 顯示錯誤訊息

## 修復檔案

- `static/script.js`：ChatStateManager 相關方法

## 驗證步驟

1. 開啟瀏覽器開發者工具
2. 嘗試新增重複或重疊時段
3. 檢查 console 中的警告訊息
4. 確認錯誤訊息正確顯示
5. 確認時段沒有被添加到列表中
