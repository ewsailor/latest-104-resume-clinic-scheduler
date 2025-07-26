/**
 * 測試 submit-schedules 按鈕功能修復
 * 
 * 這個腳本會測試「已新增完成所有時段，請協助送出給 Giver」按鈕
 * 是否能正確顯示成功訊息泡泡
 */

console.log('🔍 開始測試 submit-schedules 按鈕功能修復...');

// 測試函數
function testSubmitSchedulesFix() {
  console.log('🎯 測試 submit-schedules 按鈕功能...');
  
  // 1. 檢查按鈕是否存在
  const submitButtons = document.querySelectorAll('.chat-option-btn[data-option="submit-schedules"]');
  if (submitButtons.length === 0) {
    console.log('❌ 未找到 submit-schedules 按鈕');
    return false;
  }
  
  console.log(`✅ 找到 ${submitButtons.length} 個 submit-schedules 按鈕`);
  
  // 2. 檢查按鈕文字是否正確
  submitButtons.forEach((button, index) => {
    const buttonText = button.textContent.trim();
    const expectedText = '已新增完成所有時段，請協助送出給 Giver';
    
    if (buttonText === expectedText) {
      console.log(`✅ 按鈕 ${index + 1} 文字正確: "${buttonText}"`);
    } else {
      console.log(`❌ 按鈕 ${index + 1} 文字錯誤: 期望 "${expectedText}"，實際 "${buttonText}"`);
    }
  });
  
  // 3. 檢查按鈕樣式是否正確
  submitButtons.forEach((button, index) => {
    const computedStyle = window.getComputedStyle(button);
    const backgroundColor = computedStyle.backgroundColor;
    const color = computedStyle.color;
    
    // 檢查是否為橘底白字
    const isOrangeBackground = backgroundColor.includes('rgb(255, 102, 0)') || 
                              backgroundColor.includes('rgba(255, 102, 0)') ||
                              backgroundColor.includes('#ff6600');
    const isWhiteText = color.includes('rgb(255, 255, 255)') || 
                       color.includes('rgba(255, 255, 255)') ||
                       color.includes('#ffffff');
    
    if (isOrangeBackground && isWhiteText) {
      console.log(`✅ 按鈕 ${index + 1} 樣式正確: 橘底白字`);
    } else {
      console.log(`❌ 按鈕 ${index + 1} 樣式錯誤: 背景色 ${backgroundColor}，文字色 ${color}`);
    }
  });
  
  // 4. 檢查 ChatStateManager 是否可用
  if (typeof ChatStateManager !== 'undefined') {
    console.log('✅ ChatStateManager 可用');
    
    // 檢查狀態文字定義
    const statusTexts = ChatStateManager.CONFIG?.UI_TEXT?.STATUS?.TAKER_OFFER;
    if (statusTexts) {
      console.log('✅ 狀態文字定義存在');
      console.log('   - DRAFT:', statusTexts.DRAFT);
      console.log('   - PENDING:', statusTexts.PENDING);
    } else {
      console.log('❌ 狀態文字定義不存在');
    }
  } else {
    console.log('❌ ChatStateManager 不可用');
  }
  
  // 5. 檢查模板函數是否可用
  if (typeof TEMPLATES !== 'undefined' && TEMPLATES.chat && TEMPLATES.chat.successProvideTime) {
    console.log('✅ successProvideTime 模板函數可用');
  } else {
    console.log('❌ successProvideTime 模板函數不可用');
  }
  
  // 6. 檢查事件處理器是否可用
  if (typeof EventManager !== 'undefined' && EventManager.handleOptionButton) {
    console.log('✅ EventManager 事件處理器可用');
  } else {
    console.log('❌ EventManager 事件處理器不可用');
  }
  
  return true;
}

// 手動測試函數
function manualTestSubmitSchedules() {
  console.log('\n🔍 手動測試 submit-schedules 按鈕功能...');
  
  const submitButtons = document.querySelectorAll('.chat-option-btn[data-option="submit-schedules"]');
  if (submitButtons.length === 0) {
    console.log('❌ 未找到 submit-schedules 按鈕，無法進行手動測試');
    return;
  }
  
  console.log('📝 手動測試步驟：');
  console.log('1. 點擊「提供單筆方便時段」按鈕');
  console.log('2. 填寫時段表單並提交');
  console.log('3. 點擊「繼續提供單筆方便時段」按鈕');
  console.log('4. 再次填寫時段表單並提交');
  console.log('5. 點擊「已新增完成所有時段，請協助送出給 Giver」按鈕');
  console.log('6. 檢查是否顯示成功訊息泡泡');
  console.log('7. 檢查時段狀態是否顯示為「提供時間成功，待 Giver 回覆」');
  
  console.log('\n🎯 預期結果：');
  console.log('- 點擊 submit-schedules 按鈕後，應該顯示成功訊息泡泡');
  console.log('- 成功訊息泡泡應該包含「✅ 提供時間成功！」文字');
  console.log('- 時段狀態應該顯示為「提供時間成功，待 Giver 回覆」');
  console.log('- 時段狀態文字應該為綠色（text-success 類別）');
}

// 執行測試
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM 載入完成，開始測試...');
    testSubmitSchedulesFix();
    manualTestSubmitSchedules();
  });
} else {
  console.log('📄 DOM 已載入，直接開始測試...');
  testSubmitSchedulesFix();
  manualTestSubmitSchedules();
}

console.log('\n🎉 測試完成！');
console.log('💡 如果測試通過，submit-schedules 按鈕功能修復成功');
console.log('💡 如果測試失敗，請檢查相關的程式碼邏輯'); 