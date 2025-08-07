// 測試聊天會話狀態的腳本
// 在瀏覽器控制台中執行此腳本來檢查聊天會話是否正確維持

console.log('🧪 開始測試聊天會話狀態...');

// 檢查 ChatStateManager 中的當前 Giver
const currentGiver = window.ChatStateManager?.get('currentGiver');
console.log('📋 當前 Giver:', currentGiver);

// 檢查聊天是否活躍
const isActive = window.ChatStateManager?.get('isActive');
console.log('📋 聊天是否活躍:', isActive);

// 檢查應用程式狀態中的 Giver 資料
const appStateGivers = window.appState?.givers;
console.log('📋 應用程式狀態中的 Giver 資料:', appStateGivers);

// 如果當前 Giver 存在，檢查其 ID
if (currentGiver) {
  console.log('✅ 聊天會話正常，當前 Giver:', {
    id: currentGiver.id,
    name: currentGiver.name
  });
  
  // 模擬提交時段的邏輯
  const giverId = currentGiver.id;
  console.log('📋 模擬提交時段時的 giver_id:', giverId);
  
  // 檢查是否與預期相符
  if (currentGiver.name === '王零三' && giverId === 3) {
    console.log('✅ 王零三的 ID 正確為 3');
  } else if (currentGiver.name === '王零四' && giverId === 4) {
    console.log('✅ 王零四的 ID 正確為 4');
  } else {
    console.log('❌ Giver ID 不正確:', { name: currentGiver.name, id: giverId });
  }
} else {
  console.log('❌ 聊天會話已結束，currentGiver 為 null');
  
  // 檢查是否有其他方式可以獲取 Giver 資訊
  console.log('📋 檢查是否有其他 Giver 資訊來源...');
  
  // 檢查 DOM 中的按鈕
  const buttons = document.querySelectorAll('.giverCard__action-button');
  console.log('📋 找到的按鈕數量:', buttons.length);
  
  buttons.forEach((button, index) => {
    const dataId = button.getAttribute('data-id');
    const ariaLabel = button.getAttribute('aria-label');
    console.log(`  按鈕 ${index + 1}:`, { dataId, ariaLabel });
  });
}

console.log('✅ 測試完成！');
