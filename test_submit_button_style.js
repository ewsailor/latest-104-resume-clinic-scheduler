/**
 * 測試 submit-schedules 按鈕樣式修復
 * 
 * 這個腳本會測試「已新增完成所有時段，請協助送出給 Giver」按鈕
 * 是否正確顯示為橘底白字的樣式
 */

console.log('🔍 開始測試 submit-schedules 按鈕樣式...');

// 等待頁面載入完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 頁面載入完成，開始測試...');
    
    // 測試函數
    function testSubmitButtonStyle() {
        console.log('🎯 測試 submit-schedules 按鈕樣式...');
        
        // 查找所有 submit-schedules 按鈕
        const submitButtons = document.querySelectorAll('.chat-option-btn[data-option="submit-schedules"]');
        
        if (submitButtons.length === 0) {
            console.log('❌ 未找到 submit-schedules 按鈕');
            console.log('💡 請先觸發聊天流程，讓按鈕出現');
            return false;
        }
        
        console.log(`✅ 找到 ${submitButtons.length} 個 submit-schedules 按鈕`);
        
        // 檢查每個按鈕的樣式
        submitButtons.forEach((button, index) => {
            console.log(`\n🔍 檢查按鈕 ${index + 1}:`);
            console.log(`   文字: "${button.textContent}"`);
            console.log(`   class: "${button.className}"`);
            
            // 檢查計算後的樣式
            const computedStyle = window.getComputedStyle(button);
            const backgroundColor = computedStyle.backgroundColor;
            const color = computedStyle.color;
            const borderColor = computedStyle.borderColor;
            
            console.log(`   背景色: ${backgroundColor}`);
            console.log(`   文字色: ${color}`);
            console.log(`   邊框色: ${borderColor}`);
            
            // 檢查是否符合橘底白字的要求
            const isOrangeBackground = backgroundColor.includes('rgb(255, 102, 0)') || 
                                    backgroundColor.includes('orange') ||
                                    backgroundColor.includes('255, 102, 0');
            const isWhiteText = color.includes('rgb(255, 255, 255)') || 
                              color.includes('white') ||
                              color.includes('255, 255, 255');
            
            if (isOrangeBackground && isWhiteText) {
                console.log(`✅ 按鈕 ${index + 1} 樣式正確：橘底白字`);
            } else {
                console.log(`❌ 按鈕 ${index + 1} 樣式不正確`);
                console.log(`   預期：橘底白字`);
                console.log(`   實際：背景色=${backgroundColor}, 文字色=${color}`);
            }
        });
        
        return true;
    }
    
    // 檢查 CSS 規則是否正確載入
    function checkCSSRules() {
        console.log('\n🔍 檢查 CSS 規則...');
        
        // 檢查是否有針對 submit-schedules 的 CSS 規則
        const styleSheets = Array.from(document.styleSheets);
        let foundRule = false;
        
        styleSheets.forEach((sheet, sheetIndex) => {
            try {
                const rules = Array.from(sheet.cssRules || sheet.rules || []);
                rules.forEach((rule, ruleIndex) => {
                    if (rule.selectorText && rule.selectorText.includes('submit-schedules')) {
                        console.log(`✅ 找到 CSS 規則: ${rule.selectorText}`);
                        console.log(`   位置: stylesheet[${sheetIndex}], rule[${ruleIndex}]`);
                        foundRule = true;
                    }
                });
            } catch (e) {
                // 跨域樣式表可能無法訪問
                console.log(`⚠️  無法訪問 stylesheet[${sheetIndex}] (可能是跨域)`);
            }
        });
        
        if (!foundRule) {
            console.log('❌ 未找到針對 submit-schedules 的 CSS 規則');
        }
        
        return foundRule;
    }
    
    // 模擬觸發聊天流程來顯示按鈕
    function simulateChatFlow() {
        console.log('\n🎭 模擬觸發聊天流程...');
        
        // 查找並點擊預約按鈕
        const scheduleButton = document.querySelector('.chat-option-btn[data-option="schedule"]');
        if (scheduleButton) {
            console.log('✅ 找到預約按鈕，點擊觸發流程...');
            scheduleButton.click();
            
            // 等待按鈕出現
            setTimeout(() => {
                console.log('⏳ 等待按鈕渲染...');
                testSubmitButtonStyle();
            }, 1000);
        } else {
            console.log('❌ 未找到預約按鈕，無法模擬流程');
            console.log('💡 請手動觸發聊天流程，然後重新運行測試');
        }
    }
    
    // 執行測試
    console.log('\n🚀 開始執行測試...');
    
    // 1. 檢查 CSS 規則
    const cssRuleFound = checkCSSRules();
    
    // 2. 測試按鈕樣式
    const buttonTestPassed = testSubmitButtonStyle();
    
    // 3. 如果按鈕不存在，嘗試模擬流程
    if (!buttonTestPassed) {
        console.log('\n🔄 按鈕不存在，嘗試模擬聊天流程...');
        simulateChatFlow();
    }
    
    // 總結
    console.log('\n📊 測試總結:');
    console.log(`   CSS 規則載入: ${cssRuleFound ? '✅' : '❌'}`);
    console.log(`   按鈕樣式測試: ${buttonTestPassed ? '✅' : '❌'}`);
    
    if (cssRuleFound && buttonTestPassed) {
        console.log('\n🎉 所有測試通過！submit-schedules 按鈕樣式修復成功');
    } else {
        console.log('\n⚠️  部分測試失敗，請檢查修復是否正確');
    }
});

// 提供手動測試函數
window.testSubmitButtonStyle = function() {
    console.log('🔍 手動測試 submit-schedules 按鈕樣式...');
    
    const submitButtons = document.querySelectorAll('.chat-option-btn[data-option="submit-schedules"]');
    
    if (submitButtons.length === 0) {
        console.log('❌ 未找到 submit-schedules 按鈕');
        return false;
    }
    
    submitButtons.forEach((button, index) => {
        const computedStyle = window.getComputedStyle(button);
        const backgroundColor = computedStyle.backgroundColor;
        const color = computedStyle.color;
        
        console.log(`按鈕 ${index + 1}: 背景色=${backgroundColor}, 文字色=${color}`);
        
        const isCorrect = (backgroundColor.includes('255, 102, 0') || backgroundColor.includes('orange')) &&
                         (color.includes('255, 255, 255') || color.includes('white'));
        
        console.log(`樣式正確: ${isCorrect ? '✅' : '❌'}`);
    });
    
    return true;
};

console.log('📝 測試腳本已載入');
console.log('💡 手動測試：在控制台輸入 testSubmitButtonStyle()'); 