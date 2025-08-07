// 測試 Giver ID 修復
console.log('🧪 測試 Giver ID 修復');

// 模擬點擊王拾壹的「我要諮詢」按鈕
function testWangShiYi() {
  console.log('📋 測試王拾壹的諮詢流程');
  
  // 模擬王拾壹的資料
  const wangShiYi = {
    id: 11,
    name: "王拾一",
    title: "產品經理",
    company: "王拾一-資訊科技公司"
  };
  
  console.log('👤 王拾壹資料:', wangShiYi);
  
  // 模擬初始化聊天會話
  if (window.ChatStateManager) {
    window.ChatStateManager.initChatSession(wangShiYi);
    console.log('✅ 聊天會話已初始化');
    
    // 檢查 currentGiver 是否正確設定
    const currentGiver = window.ChatStateManager.get('currentGiver');
    console.log('📋 當前 Giver:', currentGiver);
    
    if (currentGiver && currentGiver.id === 11) {
      console.log('✅ currentGiver 設定正確');
    } else {
      console.log('❌ currentGiver 設定錯誤');
    }
  } else {
    console.log('❌ ChatStateManager 未找到');
  }
}

// 模擬點擊王零三的「我要諮詢」按鈕
function testWangLingSan() {
  console.log('📋 測試王零三的諮詢流程');
  
  // 模擬王零三的資料
  const wangLingSan = {
    id: 3,
    name: "王零三",
    title: "後端工程師",
    company: "王零三-資訊科技公司"
  };
  
  console.log('👤 王零三資料:', wangLingSan);
  
  // 模擬初始化聊天會話
  if (window.ChatStateManager) {
    window.ChatStateManager.initChatSession(wangLingSan);
    console.log('✅ 聊天會話已初始化');
    
    // 檢查 currentGiver 是否正確設定
    const currentGiver = window.ChatStateManager.get('currentGiver');
    console.log('📋 當前 Giver:', currentGiver);
    
    if (currentGiver && currentGiver.id === 3) {
      console.log('✅ currentGiver 設定正確');
    } else {
      console.log('❌ currentGiver 設定錯誤');
    }
  } else {
    console.log('❌ ChatStateManager 未找到');
  }
}

// 測試 cleanup 後 currentGiver 是否保留
function testCleanupPreservesGiver() {
  console.log('📋 測試 cleanup 後 currentGiver 是否保留');
  
  if (window.ChatStateManager) {
    const currentGiver = window.ChatStateManager.get('currentGiver');
    console.log('📋 cleanup 前的 currentGiver:', currentGiver);
    
    if (currentGiver) {
      console.log('✅ currentGiver 在 cleanup 後仍然保留');
    } else {
      console.log('❌ currentGiver 在 cleanup 後被清空');
    }
  }
}

// 執行測試
console.log('🚀 開始執行測試...');

// 測試王拾壹
testWangShiYi();

// 測試王零三
testWangLingSan();

// 測試 cleanup 保留
testCleanupPreservesGiver();

console.log('🏁 測試完成');

