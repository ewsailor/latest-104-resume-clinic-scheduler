# 日期選擇器修復總結

## 問題描述

用戶反映日期選擇器存在以下問題：

1. **點擊外部會關閉日期選擇器**：用戶希望點擊日曆選擇器外的任何一處都無法跳出日曆選擇器
2. **錯誤訊息殘留**：選擇 3 個月後的日期會顯示錯誤訊息，但如果不點擊 X 而是點擊外部關閉，下次再進入時錯誤訊息會一直顯示

## 修復方案

### 1. 防止點擊外部關閉

#### HTML 修改

```html
<!-- 修改前 -->
<div
  class="modal fade"
  id="date-picker-modal"
  tabindex="-1"
  aria-labelledby="datePickerModalLabel"
  aria-hidden="true"
  role="dialog"
>
  <!-- 修改後 -->
  <div
    class="modal fade"
    id="date-picker-modal"
    tabindex="-1"
    aria-labelledby="datePickerModalLabel"
    aria-hidden="true"
    role="dialog"
    data-bs-backdrop="static"
    data-bs-keyboard="false"
  ></div>
</div>
```

**修改說明**：

- `data-bs-backdrop="static"`：防止點擊 backdrop 關閉 modal
- `data-bs-keyboard="false"`：防止按 ESC 鍵關閉 modal

#### JavaScript 修改

```javascript
// 修改 Modal 實例化
const datePickerModal = new bootstrap.Modal(datePickerModalElement, {
  backdrop: "static",
  keyboard: false,
});

// 備案方式也防止點擊關閉
const backdrop = document.createElement("div");
backdrop.className = "modal-backdrop fade show";
backdrop.style.pointerEvents = "none"; // 防止點擊 backdrop 關閉 modal
```

### 2. 移除自動關閉按鈕

#### HTML 修改

```html
<!-- 修改前 -->
<button
  type="button"
  class="btn-close"
  data-bs-dismiss="modal"
  aria-label="關閉日期選擇器"
></button>

<!-- 修改後 -->
<button
  type="button"
  class="btn-close"
  id="date-picker-close-btn"
  aria-label="關閉日期選擇器"
></button>
```

**修改說明**：

- 移除 `data-bs-dismiss="modal"` 屬性
- 添加自定義 ID 以便手動控制關閉事件

#### JavaScript 添加關閉按鈕事件

```javascript
// 設定關閉按鈕事件
const closeBtn = document.getElementById("date-picker-close-btn");
if (closeBtn) {
  DOM.events.add(closeBtn, "click", () => {
    const datePickerModal = bootstrap.Modal.getInstance(
      document.getElementById("date-picker-modal")
    );
    if (datePickerModal) {
      datePickerModal.hide();
    }
    // 清理和重置
    setTimeout(() => {
      document.querySelectorAll(".modal-backdrop").forEach((bd) => bd.remove());
      document.body.classList.remove("modal-open");
      document.body.style.overflow = "";
      document.body.style.paddingRight = "";
      DOM_CACHE.resetDatePicker();
    }, 200);
  });
}
```

### 3. 清除錯誤訊息

#### 在關鍵位置添加錯誤訊息清除

```javascript
// 1. 初始化時清除
initDatePicker: () => {
  // 清除任何現有的錯誤訊息
  DOM.chat.clearDatePickerError();
  // ... 其他初始化代碼
};

// 2. 顯示時清除
showDatePicker: () => {
  // 清除任何現有的錯誤訊息
  DOM.chat.clearDatePickerError();
  // ... 其他顯示代碼
};

// 3. 隱藏時清除
_onModalHidden: () => {
  // 清除錯誤訊息
  DOM.chat.clearDatePickerError();
  // ... 其他隱藏代碼
};

// 4. 清理時清除
cleanup: () => {
  // 關閉日期選擇器 Modal
  const datePickerModal = bootstrap.Modal.getInstance(
    document.getElementById("date-picker-modal")
  );
  if (datePickerModal) {
    datePickerModal.hide();
    // 清除錯誤訊息
    DOM.chat.clearDatePickerError();
    // 重置日期選擇器快取
    DOM_CACHE.resetDatePicker();
  }
};
```

## 修復效果

### ✅ 已修復的問題

1. **點擊外部不會關閉**：

   - Modal 設定為靜態 backdrop
   - 禁用鍵盤 ESC 關閉
   - Backdrop 設定為不可點擊

2. **錯誤訊息不會殘留**：

   - 每次開啟時清除錯誤訊息
   - 每次關閉時清除錯誤訊息
   - 每次初始化時清除錯誤訊息

3. **關閉按鈕正常工作**：
   - 自定義關閉按鈕事件
   - 正確的清理和重置流程

### 🔧 測試方法

1. **測試點擊外部**：

   - 開啟日期選擇器
   - 點擊 Modal 外部區域
   - 確認 Modal 不會關閉

2. **測試錯誤訊息清除**：

   - 選擇 3 個月後的日期
   - 點擊外部關閉（應該不會關閉）
   - 點擊 X 按鈕關閉
   - 再次開啟日期選擇器
   - 確認沒有殘留的錯誤訊息

3. **測試關閉按鈕**：
   - 開啟日期選擇器
   - 點擊右上角的 X 按鈕
   - 確認 Modal 正常關閉

## 技術細節

### Bootstrap Modal 配置

```javascript
{
  backdrop: 'static',  // 靜態 backdrop，不允許點擊關閉
  keyboard: false      // 禁用鍵盤 ESC 關閉
}
```

### 錯誤訊息清除機制

```javascript
clearDatePickerError: () => {
  const datePickerModal = document.getElementById("date-picker-modal");
  if (datePickerModal) {
    const existingError = datePickerModal.querySelector(".date-picker-error");
    if (existingError) {
      existingError.remove();
    }
  }
};
```

### 事件處理優化

- 使用事件委託避免重複綁定
- 正確的事件清理和重置
- 防止記憶體洩漏

## 注意事項

1. **用戶體驗**：現在用戶只能通過 X 按鈕關閉日期選擇器，確保了操作的明確性
2. **錯誤處理**：錯誤訊息會在適當的時機被清除，避免混淆
3. **性能優化**：正確的事件清理和快取重置，避免記憶體洩漏

## 驗證清單

- [x] 點擊外部不會關閉日期選擇器
- [x] 錯誤訊息不會殘留到下次開啟
- [x] 關閉按鈕正常工作
- [x] 日期選擇器正確重置
- [x] 沒有記憶體洩漏
- [x] 用戶體驗流暢
