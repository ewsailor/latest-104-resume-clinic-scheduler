// 測試王拾壹的時段提交功能
console.log('📋 測試王拾壹的時段提交功能');

// 模擬王拾壹的時段資料
const testSchedule = {
  giver_id: 11,  // 王拾壹的 ID
  taker_id: 1,
  date: "2025-08-15",
  start_time: "20:00:00",
  end_time: "22:00:00",
  note: "測試王拾壹的時段",
  status: "AVAILABLE",
  role: "GIVER"
};

console.log('📋 測試資料:', testSchedule);

// 發送 POST 請求
fetch('http://localhost:8000/api/v1/schedules', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify([testSchedule])
})
.then(response => {
  console.log('📋 回應狀態:', response.status);
  console.log('📋 回應標頭:', response.headers);
  return response.json();
})
.then(data => {
  console.log('✅ 成功回應:', data);
})
.catch(error => {
  console.error('❌ 錯誤:', error);
});
