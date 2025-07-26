/**
 * 測試 submit-schedules 按鈕調試日誌
 * 用於驗證按鈕點擊事件和狀態轉換邏輯
 */

console.log('🔍 開始測試 submit-schedules 按鈕調試日誌...');

// 等待頁面載入完成
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ 頁面載入完成，開始測試...');
  
  // 測試 1: 檢查按鈕是否存在
  console.log('\n🎯 測試 1: 檢查 submit-schedules 按鈕是否存在...');
  const submitButtons = document.querySelectorAll('.chat-option-btn[data-option="submit-schedules"]');
  
  if (submitButtons.length === 0) {
    console.log('❌ 未找到 submit-schedules 按鈕');
    console.log('💡 請確保已經添加了草稿時段，並且顯示了包含 submit-schedules 按鈕的訊息泡泡');
    return;
  }
  
  console.log(`✅ 找到 ${submitButtons.length} 個 submit-schedules 按鈕`);
  
  // 測試 2: 檢查按鈕的 HTML 結構
  console.log('\n🎯 測試 2: 檢查按鈕的 HTML 結構...');
  submitButtons.forEach((btn, index) => {
    console.log(`按鈕 ${index + 1}:`, {
      text: btn.textContent.trim(),
      dataOption: btn.getAttribute('data-option'),
      className: btn.className,
      isVisible: btn.offsetParent !== null
    });
  });
  
  // 測試 3: 檢查當前狀態
  console.log('\n🎯 測試 3: 檢查當前狀態...');
  
  // 檢查草稿時段
  const draftSchedules = window.ChatStateManager?.get(window.ChatStateManager.CONFIG.STATE_KEYS.DRAFT_SCHEDULES) || [];
  console.log('草稿時段:', {
    count: draftSchedules.length,
    schedules: draftSchedules
  });
  
  // 檢查正式提供時段
  const providedSchedules = window.ChatStateManager?.getProvidedSchedules() || [];
  console.log('正式提供時段:', {
    count: providedSchedules.length,
    schedules: providedSchedules
  });
  
  // 測試 4: 模擬按鈕點擊
  console.log('\n🎯 測試 4: 模擬按鈕點擊...');
  console.log('💡 請手動點擊 submit-schedules 按鈕，然後查看 console 中的調試日誌');
  
  // 測試 5: 檢查事件處理器
  console.log('\n🎯 測試 5: 檢查事件處理器...');
  
  // 檢查是否有全局點擊事件處理器
  const hasGlobalClickHandler = document.addEventListener && typeof EventManager !== 'undefined';
  console.log('全局點擊事件處理器:', hasGlobalClickHandler ? '✅ 已設置' : '❌ 未設置');
  
  // 檢查 EventManager 是否存在
  if (typeof EventManager !== 'undefined') {
    console.log('EventManager 狀態:', {
      hasHandleOptionButton: typeof EventManager.handleOptionButton === 'function',
      hasHandleGlobalClick: typeof EventManager.handleGlobalClick === 'function'
    });
  } else {
    console.log('❌ EventManager 未定義');
  }
  
  // 測試 6: 檢查 Logger 功能
  console.log('\n🎯 測試 6: 檢查 Logger 功能...');
  if (typeof Logger !== 'undefined') {
    console.log('Logger 狀態:', {
      hasInfo: typeof Logger.info === 'function',
      hasDebug: typeof Logger.debug === 'function',
      hasWarn: typeof Logger.warn === 'function',
      hasError: typeof Logger.error === 'function'
    });
    
    // 測試 Logger 功能
    Logger.info('測試 Logger.info 功能');
    Logger.debug('測試 Logger.debug 功能');
    Logger.warn('測試 Logger.warn 功能');
    Logger.error('測試 Logger.error 功能');
  } else {
    console.log('❌ Logger 未定義');
  }
  
  console.log('\n🎉 調試測試完成！');
  console.log('\n📋 測試步驟：');
  console.log('1. 確保已經添加了草稿時段');
  console.log('2. 點擊 submit-schedules 按鈕');
  console.log('3. 查看 console 中的調試日誌');
  console.log('4. 檢查是否顯示成功訊息泡泡');
  console.log('5. 檢查時段狀態是否從草稿變為正式提供');
});

// 監聽 console 日誌
const originalLog = console.log;
const originalInfo = console.info;
const originalWarn = console.warn;
const originalError = console.error;

console.log = function(...args) {
  originalLog.apply(console, args);
  if (args[0] && typeof args[0] === 'string' && args[0].includes('submit-schedules')) {
    originalLog('🔍 [DEBUG] 檢測到 submit-schedules 相關日誌:', ...args);
  }
};

console.info = function(...args) {
  originalInfo.apply(console, args);
  if (args[0] && typeof args[0] === 'string' && args[0].includes('submit-schedules')) {
    originalInfo('🔍 [DEBUG] 檢測到 submit-schedules 相關日誌:', ...args);
  }
};

console.warn = function(...args) {
  originalWarn.apply(console, args);
  if (args[0] && typeof args[0] === 'string' && args[0].includes('submit-schedules')) {
    originalWarn('🔍 [DEBUG] 檢測到 submit-schedules 相關日誌:', ...args);
  }
};

console.error = function(...args) {
  originalError.apply(console, args);
  if (args[0] && typeof args[0] === 'string' && args[0].includes('submit-schedules')) {
    originalError('🔍 [DEBUG] 檢測到 submit-schedules 相關日誌:', ...args);
  }
}; 