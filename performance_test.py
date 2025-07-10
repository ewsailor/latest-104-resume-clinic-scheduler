#!/usr/bin/env python3
"""
性能測試腳本
用於測試網站載入速度和響應時間
"""

import requests
import time
import statistics
from datetime import datetime
import json

class PerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    def test_page_load(self, endpoint="/", name="首頁"):
        """測試頁面載入時間"""
        print(f"測試 {name} 載入時間...")
        
        times = []
        for i in range(5):  # 測試5次取平均值
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                load_time = (end_time - start_time) * 1000  # 轉換為毫秒
                times.append(load_time)
                
                print(f"  第 {i+1} 次: {load_time:.2f}ms (狀態碼: {response.status_code})")
                
            except Exception as e:
                print(f"  第 {i+1} 次: 錯誤 - {e}")
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            result = {
                "name": name,
                "endpoint": endpoint,
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "times": times,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            print(f"  平均載入時間: {avg_time:.2f}ms")
            print(f"  最快載入時間: {min_time:.2f}ms")
            print(f"  最慢載入時間: {max_time:.2f}ms")
            print()
            
            return result
        return None
    
    def test_api_response(self, endpoint="/schedules", name="API 響應"):
        """測試 API 響應時間"""
        print(f"測試 {name} 響應時間...")
        
        times = []
        for i in range(5):  # 測試5次取平均值
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 轉換為毫秒
                times.append(response_time)
                
                print(f"  第 {i+1} 次: {response_time:.2f}ms (狀態碼: {response.status_code})")
                
            except Exception as e:
                print(f"  第 {i+1} 次: 錯誤 - {e}")
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            result = {
                "name": name,
                "endpoint": endpoint,
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "times": times,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            print(f"  平均響應時間: {avg_time:.2f}ms")
            print(f"  最快響應時間: {min_time:.2f}ms")
            print(f"  最慢響應時間: {max_time:.2f}ms")
            print()
            
            return result
        return None
    
    def test_static_resources(self):
        """測試靜態資源載入時間"""
        static_resources = [
            ("/static/style.css", "CSS 文件"),
            ("/static/script.js", "JavaScript 文件"),
            ("/static/logo-header.svg", "Logo 圖片"),
            ("/static/chat-avatar.svg", "聊天頭像")
        ]
        
        print("測試靜態資源載入時間...")
        
        for endpoint, name in static_resources:
            times = []
            for i in range(3):  # 每個資源測試3次
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}{endpoint}")
                    end_time = time.time()
                    
                    load_time = (end_time - start_time) * 1000
                    times.append(load_time)
                    
                except Exception as e:
                    print(f"  {name} 載入失敗: {e}")
                    continue
            
            if times:
                avg_time = statistics.mean(times)
                result = {
                    "name": name,
                    "endpoint": endpoint,
                    "average_time": avg_time,
                    "times": times,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.results.append(result)
                print(f"  {name}: {avg_time:.2f}ms")
        
        print()
    
    def generate_report(self):
        """生成性能測試報告"""
        if not self.results:
            print("沒有測試結果可生成報告")
            return
        
        print("=" * 50)
        print("性能測試報告")
        print("=" * 50)
        print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"測試目標: {self.base_url}")
        print()
        
        # 按類型分組結果
        page_loads = [r for r in self.results if "首頁" in r["name"] or "頁面" in r["name"]]
        api_responses = [r for r in self.results if "API" in r["name"]]
        static_resources = [r for r in self.results if r["name"] in ["CSS 文件", "JavaScript 文件", "Logo 圖片", "聊天頭像"]]
        
        if page_loads:
            print("頁面載入性能:")
            for result in page_loads:
                print(f"  {result['name']}: {result['average_time']:.2f}ms")
            print()
        
        if api_responses:
            print("API 響應性能:")
            for result in api_responses:
                print(f"  {result['name']}: {result['average_time']:.2f}ms")
            print()
        
        if static_resources:
            print("靜態資源載入性能:")
            for result in static_resources:
                print(f"  {result['name']}: {result['average_time']:.2f}ms")
            print()
        
        # 性能評估
        print("性能評估:")
        if page_loads:
            avg_page_load = statistics.mean([r['average_time'] for r in page_loads])
            if avg_page_load < 500:
                print("  ✅ 頁面載入速度: 優秀 (< 500ms)")
            elif avg_page_load < 1000:
                print("  ⚠️  頁面載入速度: 良好 (500-1000ms)")
            else:
                print("  ❌ 頁面載入速度: 需要改善 (> 1000ms)")
        
        if api_responses:
            avg_api_response = statistics.mean([r['average_time'] for r in api_responses])
            if avg_api_response < 200:
                print("  ✅ API 響應速度: 優秀 (< 200ms)")
            elif avg_api_response < 500:
                print("  ⚠️  API 響應速度: 良好 (200-500ms)")
            else:
                print("  ❌ API 響應速度: 需要改善 (> 500ms)")
        
        print()
        print("=" * 50)
    
    def save_results(self, filename="performance_test_results.json"):
        """保存測試結果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"測試結果已保存到 {filename}")
    
    def run_full_test(self):
        """運行完整性能測試"""
        print("開始性能測試...")
        print(f"測試目標: {self.base_url}")
        print()
        
        # 測試頁面載入
        self.test_page_load("/", "首頁")
        
        # 測試 API 響應
        self.test_api_response("/schedules", "排程 API")
        
        # 測試靜態資源
        self.test_static_resources()
        
        # 生成報告
        self.generate_report()
        
        # 保存結果
        self.save_results()

def main():
    """主函數"""
    import sys
    
    # 檢查命令行參數
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    # 創建測試器並運行測試
    tester = PerformanceTester(base_url)
    tester.run_full_test()

if __name__ == "__main__":
    main() 