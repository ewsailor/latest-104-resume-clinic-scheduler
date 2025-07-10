// 日期選擇器測試腳本
// 用於驗證日期選擇器的修復是否有效

console.log('🔧 開始測試日期選擇器修復...');

// 測試函數
function testDatePicker() {
  console.log('📅 測試日期選擇器功能...');
  
  // 1. 測試點擊外部不會關閉
  console.log('✅ 測試 1: 點擊外部不會關閉 Modal');
  const datePickerModal = document.getElementById('date-picker-modal');
  if (datePickerModal) {
    const backdrop = datePickerModal.querySelector('.modal-backdrop') || 
                    document.querySelector('.modal-backdrop');
    if (backdrop) {
      console.log('   - Backdrop 存在，檢查是否為靜態模式');
      console.log('   - Backdrop pointer-events:', backdrop.style.pointerEvents);
      console.log('   - Modal data-bs-backdrop:', datePickerModal.getAttribute('data-bs-backdrop'));
    }
  }
  
  // 2. 測試錯誤訊息清除
  console.log('✅ 測試 2: 錯誤訊息清除功能');
  const errorElements = document.querySelectorAll('.date-picker-error');
  console.log('   - 當前錯誤訊息數量:', errorElements.length);
  
  // 3. 測試關閉按鈕功能
  console.log('✅ 測試 3: 關閉按鈕功能');
  const closeBtn = document.getElementById('date-picker-close-btn');
  if (closeBtn) {
    console.log('   - 關閉按鈕存在');
    console.log('   - 關閉按鈕 ID:', closeBtn.id);
  } else {
    console.log('   - 關閉按鈕不存在');
  }
  
  // 4. 測試 Modal 配置
  console.log('✅ 測試 4: Modal 配置');
  if (datePickerModal) {
    console.log('   - data-bs-backdrop:', datePickerModal.getAttribute('data-bs-backdrop'));
    console.log('   - data-bs-keyboard:', datePickerModal.getAttribute('data-bs-keyboard'));
  }
}

// 模擬測試場景
function simulateDatePickerTest() {
  console.log('🎯 模擬測試場景...');
  
  // 模擬開啟日期選擇器
  console.log('1. 模擬開啟日期選擇器');
  if (typeof DOM !== 'undefined' && DOM.chat && DOM.chat.showDatePicker) {
    DOM.chat.showDatePicker();
  }
  
  // 模擬選擇 3 個月後的日期
  setTimeout(() => {
    console.log('2. 模擬選擇 3 個月後的日期');
    const futureDate = new Date();
    futureDate.setMonth(futureDate.getMonth() + 3);
    console.log('   - 選擇日期:', futureDate.toDateString());
    
    // 模擬點擊日期
    const dateCells = document.querySelectorAll('.date-cell');
    if (dateCells.length > 0) {
      console.log('   - 找到日期單元格，數量:', dateCells.length);
    }
  }, 1000);
  
  // 模擬點擊外部
  setTimeout(() => {
    console.log('3. 模擬點擊外部');
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
      console.log('   - 找到 backdrop，嘗試點擊');
      backdrop.click();
    }
  }, 2000);
  
  // 檢查錯誤訊息
  setTimeout(() => {
    console.log('4. 檢查錯誤訊息狀態');
    const errorElements = document.querySelectorAll('.date-picker-error');
    console.log('   - 錯誤訊息數量:', errorElements.length);
    if (errorElements.length > 0) {
      console.log('   - 錯誤訊息內容:', errorElements[0].textContent);
    }
  }, 3000);
}

// 執行測試
if (typeof window !== 'undefined') {
  // 等待頁面載入完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(testDatePicker, 1000);
      setTimeout(simulateDatePickerTest, 2000);
    });
  } else {
    setTimeout(testDatePicker, 1000);
    setTimeout(simulateDatePickerTest, 2000);
  }
}

console.log('🔧 日期選擇器測試腳本已載入'); 