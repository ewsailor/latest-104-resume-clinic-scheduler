// 測試 Giver ID 設定的腳本
// 在瀏覽器控制台中執行此腳本來檢查 Giver ID 是否正確

console.log('🧪 開始測試 Giver ID 設定...');

// 檢查靜態 HTML 中的 Giver 卡片
const staticGiverCards = document.querySelectorAll('#giver-panel .giverCard');
console.log('📋 靜態 HTML 中的 Giver 卡片數量:', staticGiverCards.length);

staticGiverCards.forEach((card, index) => {
  const dataId = card.getAttribute('data-id');
  const button = card.querySelector('.giverCard__action-button');
  const buttonDataId = button ? button.getAttribute('data-id') : 'N/A';
  
  console.log(`📋 靜態卡片 ${index + 1}:`, {
    cardDataId: dataId,
    buttonDataId: buttonDataId,
    cardHTML: card.outerHTML.substring(0, 200) + '...'
  });
});

// 檢查動態載入的 Giver 資料
console.log('📋 應用程式狀態中的 Giver 資料:', window.appState?.givers || '未載入');

// 檢查 ChatStateManager 中的當前 Giver
console.log('📋 ChatStateManager 中的當前 Giver:', window.ChatStateManager?.get('currentGiver') || '未設定');

// 檢查所有按鈕的 data-id
const allButtons = document.querySelectorAll('.giverCard__action-button');
console.log('📋 所有「我要諮詢」按鈕的 data-id:');
allButtons.forEach((button, index) => {
  const dataId = button.getAttribute('data-id');
  const ariaLabel = button.getAttribute('aria-label');
  console.log(`  按鈕 ${index + 1}: data-id="${dataId}", aria-label="${ariaLabel}"`);
});

// 檢查按鈕點擊事件是否正確綁定
console.log('📋 檢查按鈕點擊事件綁定:');
allButtons.forEach((button, index) => {
  const dataId = button.getAttribute('data-id');
  const parsedId = parseInt(dataId, 10);
  const giver = window.appState?.givers?.find(g => g.id === parsedId);
  
  console.log(`  按鈕 ${index + 1}:`, {
    dataId: dataId,
    parsedId: parsedId,
    foundGiver: giver ? { id: giver.id, name: giver.name } : '未找到'
  });
});

// 模擬點擊王零三的按鈕
console.log('🧪 模擬點擊王零三的按鈕...');
const wang03Button = Array.from(allButtons).find(button => {
  const ariaLabel = button.getAttribute('aria-label');
  return ariaLabel && ariaLabel.includes('王零三');
});

if (wang03Button) {
  console.log('📋 找到王零三的按鈕:', {
    dataId: wang03Button.getAttribute('data-id'),
    ariaLabel: wang03Button.getAttribute('aria-label')
  });
  
  // 模擬點擊
  wang03Button.click();
} else {
  console.log('❌ 未找到王零三的按鈕');
}

console.log('✅ 測試完成！');
