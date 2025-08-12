// 測試 API 修復
console.log('🧪 測試 API 修復');

// 測試資料
const testSchedule = {
  giver_id: 11,  // 王拾壹的 ID
  taker_id: 1,
  date: "2025-08-15",
  start_time: "20:00:00",  // 添加秒數
  end_time: "22:00:00",    // 添加秒數
  note: "測試時段",
  status: "AVAILABLE",
  role: "GIVER"  // 使用大寫
};

console.log('📋 測試資料:', testSchedule);

// 發送 API 請求
async function testAPISubmission() {
  try {
    console.log('🚀 發送 API 請求...');
    
    const response = await fetch('/api/schedules', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify([testSchedule])
    });
    
    console.log('📊 回應狀態:', response.status);
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ API 請求成功！');
      console.log('📋 回應資料:', result);
      
      // 驗證回應
      if (Array.isArray(result) && result.length > 0) {
        const schedule = result[0];
        console.log('🔍 驗證結果:');
        console.log(`- giver_id: ${schedule.giver_id} (期望: 11)`);
        console.log(`- role: ${schedule.role} (期望: GIVER)`);
        console.log(`- status: ${schedule.status} (期望: AVAILABLE)`);
      }
    } else {
      const errorText = await response.text();
      console.log('❌ API 請求失敗:', errorText);
    }
  } catch (error) {
    console.error('❌ 請求錯誤:', error);
  }
}

// 執行測試
testAPISubmission();
