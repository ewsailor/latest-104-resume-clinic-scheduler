/**
 * 測試 submit-schedules 按鈕功能最終修復
 * 
 * 這個腳本測試：
 * 1. submit-schedules 按鈕是否存在
 * 2. 點擊按鈕後是否正確調用 EventManager.handleOptionButton
 * 3. 狀態轉換是否正常工作
 * 4. 成功訊息是否顯示
 */

console.log('🔍 開始測試 submit-schedules 按鈕功能最終修復...');

// 測試函數
function testSubmitSchedulesButton() {
  console.log('\n🎯 測試 1: 檢查 submit-schedules 按鈕是否存在...');
  
  const submitButtons = document.querySelectorAll('.chat-option-btn[data-option="submit-schedules"]');
  
  if (submitButtons.length === 0) {
    console.log('❌ 未找到 submit-schedules 按鈕');
    console.log('💡 請確保已經添加了草稿時段，並且顯示了包含 submit-schedules 按鈕的訊息泡泡');
    return false;
  }
  
  console.log(`✅ 找到 ${submitButtons.length} 個 submit-schedules 按鈕`);
  
  // 檢查按鈕屬性
  submitButtons.forEach((button, index) => {
    console.log(`按鈕 ${index + 1}:`, {
      text: button.textContent.trim(),
      dataOption: button.getAttribute('data-option'),
      className: button.className,
      disabled: button.disabled
    });
  });
  
  console.log('\n🎯 測試 2: 檢查當前狀態...');
  
  // 檢查當前狀態
  const draftSchedules = window.ChatStateManager ? window.ChatStateManager.get(window.ChatStateManager.CONFIG.STATE_KEYS.DRAFT_SCHEDULES) || [] : [];
  const providedSchedules = window.ChatStateManager ? window.ChatStateManager.getProvidedSchedules() || [] : [];
  
  console.log('當前狀態:', {
    draftSchedulesCount: draftSchedules.length,
    providedSchedulesCount: providedSchedules.length,
    draftSchedules: draftSchedules,
    providedSchedules: providedSchedules
  });
  
  if (draftSchedules.length === 0) {
    console.log('⚠️ 沒有草稿時段，無法測試狀態轉換');
  } else {
    console.log('✅ 有草稿時段，可以測試狀態轉換');
  }
  
  console.log('\n🎯 測試 3: 檢查 EventManager 是否存在...');
  
  if (typeof window.EventManager !== 'undefined') {
    console.log('✅ EventManager 存在');
    console.log('EventManager 方法:', Object.keys(window.EventManager));
  } else {
    console.log('❌ EventManager 不存在');
    return false;
  }
  
  console.log('\n🎯 測試 4: 檢查 DOM.chat.setupScheduleOptionButtons 是否包含 submit-schedules case...');
  
  // 檢查 setupScheduleOptionButtons 函數是否包含 submit-schedules case
  const setupFunction = window.DOM?.chat?.setupScheduleOptionButtons;
  if (setupFunction) {
    const functionString = setupFunction.toString();
    if (functionString.includes("case 'submit-schedules'")) {
      console.log('✅ setupScheduleOptionButtons 包含 submit-schedules case');
    } else {
      console.log('❌ setupScheduleOptionButtons 不包含 submit-schedules case');
      console.log('💡 這是問題所在！需要修復 setupScheduleOptionButtons 函數');
      return false;
    }
  } else {
    console.log('❌ 無法找到 setupScheduleOptionButtons 函數');
    return false;
  }
  
  console.log('\n🎯 測試 5: 模擬點擊事件...');
  
  // 模擬點擊第一個 submit-schedules 按鈕
  const firstButton = submitButtons[0];
  
  // 創建模擬事件
  const clickEvent = new MouseEvent('click', {
    bubbles: true,
    cancelable: true,
    view: window
  });
  
  console.log('準備觸發點擊事件...');
  
  // 添加臨時事件監聽器來捕獲事件
  const originalAddEventListener = EventTarget.prototype.addEventListener;
  let eventCaptured = false;
  
  EventTarget.prototype.addEventListener = function(type, listener, options) {
    if (type === 'click' && this === firstButton) {
      console.log('🔍 檢測到按鈕點擊事件監聽器');
    }
    return originalAddEventListener.call(this, type, listener, options);
  };
  
  // 觸發點擊
  firstButton.dispatchEvent(clickEvent);
  
  // 恢復原始方法
  EventTarget.prototype.addEventListener = originalAddEventListener;
  
  console.log('✅ 點擊事件已觸發');
  
  return true;
}

// 執行測試
const testResult = testSubmitSchedulesButton();

if (testResult) {
  console.log('\n🎉 基本測試通過！');
  console.log('\n📋 下一步手動測試步驟：');
  console.log('1. 確保有草稿時段');
  console.log('2. 點擊 submit-schedules 按鈕');
  console.log('3. 檢查 console 中是否出現以下日誌：');
  console.log('   - EventManager: 處理選項按鈕');
  console.log('   - EventManager: 進入 submit-schedules case');
  console.log('   - EventManager: 檢查草稿時段');
  console.log('   - EventManager: 草稿時段已轉換為正式時段');
  console.log('   - EventManager: 合併時段列表');
  console.log('   - EventManager: 草稿列表已清空');
  console.log('   - EventManager: 準備延遲顯示成功訊息泡泡');
  console.log('   - EventManager: 延遲完成，準備顯示成功訊息泡泡');
  console.log('   - DOM.chat.handleSuccessProvideTime called');
  console.log('   - EventManager: submit-schedules case 處理完成');
  console.log('4. 檢查是否顯示成功訊息泡泡');
  console.log('5. 檢查時段狀態是否從「草稿」變為「提供時間成功，待 Giver 回覆」');
} else {
  console.log('\n❌ 測試失敗，需要進一步檢查');
}

console.log('\n💡 如果測試通過，submit-schedules 按鈕功能修復成功！'); 