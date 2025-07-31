#!/usr/bin/env python3
"""
Settings 驗證器測試腳本。

測試所有 Settings 類別中的驗證器是否正常工作。
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import ValidationError
from app.core.settings import Settings


class SettingsValidatorTester:
    """
    Settings 驗證器測試器。
    
    測試各種配置組合的驗證結果。
    """
    
    def __init__(self):
        """初始化測試器。"""
        self.test_results = []
    
    def test_valid_config(self):
        """測試有效配置。"""
        print("✅ 測試有效配置...")
        try:
            settings = Settings()
            self.test_results.append({
                "test": "有效配置",
                "status": "pass",
                "message": "配置驗證通過"
            })
            print("   ✅ 配置驗證通過")
        except ValidationError as e:
            self.test_results.append({
                "test": "有效配置",
                "status": "fail",
                "message": str(e)
            })
            print(f"   ❌ 配置驗證失敗：{e}")
    
    def test_cors_origins_validation(self):
        """測試 CORS 來源驗證。"""
        print("🔍 測試 CORS 來源驗證...")
        
        # 測試有效配置
        test_cases = [
            ("有效配置", "http://localhost:3000,https://api.example.com", True),
            ("空字串", "", False),
            ("無效格式", "invalid-url", False),
            ("混合有效無效", "http://localhost:3000,invalid-url", False),
            ("缺少協議", "localhost:3000", False),
        ]
        
        for test_name, cors_origins, should_pass in test_cases:
            try:
                # 暫時設定環境變數
                original_cors = os.environ.get("CORS_ORIGINS")
                os.environ["CORS_ORIGINS"] = cors_origins
                
                settings = Settings()
                if should_pass:
                    self.test_results.append({
                        "test": f"CORS 來源 - {test_name}",
                        "status": "pass",
                        "message": "驗證通過"
                    })
                    print(f"   ✅ {test_name}: 驗證通過")
                else:
                    self.test_results.append({
                        "test": f"CORS 來源 - {test_name}",
                        "status": "fail",
                        "message": "應該失敗但通過了"
                    })
                    print(f"   ❌ {test_name}: 應該失敗但通過了")
                
                # 恢復原始環境變數
                if original_cors:
                    os.environ["CORS_ORIGINS"] = original_cors
                elif "CORS_ORIGINS" in os.environ:
                    del os.environ["CORS_ORIGINS"]
                    
            except ValidationError as e:
                if not should_pass:
                    self.test_results.append({
                        "test": f"CORS 來源 - {test_name}",
                        "status": "pass",
                        "message": f"正確捕獲錯誤：{e}"
                    })
                    print(f"   ✅ {test_name}: 正確捕獲錯誤")
                else:
                    self.test_results.append({
                        "test": f"CORS 來源 - {test_name}",
                        "status": "fail",
                        "message": f"不應該失敗：{e}"
                    })
                    print(f"   ❌ {test_name}: 不應該失敗")
                
                # 恢復原始環境變數
                if original_cors:
                    os.environ["CORS_ORIGINS"] = original_cors
                elif "CORS_ORIGINS" in os.environ:
                    del os.environ["CORS_ORIGINS"]
    
    def test_mongodb_uri_validation(self):
        """測試 MongoDB URI 驗證。"""
        print("🔍 測試 MongoDB URI 驗證...")
        
        test_cases = [
            ("有效 mongodb://", "mongodb://localhost:27017", True),
            ("有效 mongodb+srv://", "mongodb+srv://cluster.mongodb.net", True),
            ("無效協議", "http://localhost:27017", False),
            ("空字串", "", False),
        ]
        
        for test_name, mongodb_uri, should_pass in test_cases:
            try:
                original_uri = os.environ.get("MONGODB_URI")
                os.environ["MONGODB_URI"] = mongodb_uri
                
                settings = Settings()
                if should_pass:
                    self.test_results.append({
                        "test": f"MongoDB URI - {test_name}",
                        "status": "pass",
                        "message": "驗證通過"
                    })
                    print(f"   ✅ {test_name}: 驗證通過")
                else:
                    self.test_results.append({
                        "test": f"MongoDB URI - {test_name}",
                        "status": "fail",
                        "message": "應該失敗但通過了"
                    })
                    print(f"   ❌ {test_name}: 應該失敗但通過了")
                
                if original_uri:
                    os.environ["MONGODB_URI"] = original_uri
                elif "MONGODB_URI" in os.environ:
                    del os.environ["MONGODB_URI"]
                    
            except ValidationError as e:
                if not should_pass:
                    self.test_results.append({
                        "test": f"MongoDB URI - {test_name}",
                        "status": "pass",
                        "message": f"正確捕獲錯誤：{e}"
                    })
                    print(f"   ✅ {test_name}: 正確捕獲錯誤")
                else:
                    self.test_results.append({
                        "test": f"MongoDB URI - {test_name}",
                        "status": "fail",
                        "message": f"不應該失敗：{e}"
                    })
                    print(f"   ❌ {test_name}: 不應該失敗")
                
                if original_uri:
                    os.environ["MONGODB_URI"] = original_uri
                elif "MONGODB_URI" in os.environ:
                    del os.environ["MONGODB_URI"]
    
    def test_aws_region_validation(self):
        """測試 AWS 區域驗證。"""
        print("🔍 測試 AWS 區域驗證...")
        
        test_cases = [
            ("有效區域", "ap-northeast-1", True),
            ("有效區域", "us-east-1", True),
            ("無效格式", "invalid-region", False),
            ("空字串", "", False),
        ]
        
        for test_name, aws_region, should_pass in test_cases:
            try:
                original_region = os.environ.get("AWS_REGION")
                os.environ["AWS_REGION"] = aws_region
                
                settings = Settings()
                if should_pass:
                    self.test_results.append({
                        "test": f"AWS 區域 - {test_name}",
                        "status": "pass",
                        "message": "驗證通過"
                    })
                    print(f"   ✅ {test_name}: 驗證通過")
                else:
                    self.test_results.append({
                        "test": f"AWS 區域 - {test_name}",
                        "status": "fail",
                        "message": "應該失敗但通過了"
                    })
                    print(f"   ❌ {test_name}: 應該失敗但通過了")
                
                if original_region:
                    os.environ["AWS_REGION"] = original_region
                elif "AWS_REGION" in os.environ:
                    del os.environ["AWS_REGION"]
                    
            except ValidationError as e:
                if not should_pass:
                    self.test_results.append({
                        "test": f"AWS 區域 - {test_name}",
                        "status": "pass",
                        "message": f"正確捕獲錯誤：{e}"
                    })
                    print(f"   ✅ {test_name}: 正確捕獲錯誤")
                else:
                    self.test_results.append({
                        "test": f"AWS 區域 - {test_name}",
                        "status": "fail",
                        "message": f"不應該失敗：{e}"
                    })
                    print(f"   ❌ {test_name}: 不應該失敗")
                
                if original_region:
                    os.environ["AWS_REGION"] = original_region
                elif "AWS_REGION" in os.environ:
                    del os.environ["AWS_REGION"]
    
    def test_redis_db_validation(self):
        """測試 Redis 資料庫編號驗證。"""
        print("🔍 測試 Redis 資料庫編號驗證...")
        
        test_cases = [
            ("有效編號", 0, True),
            ("有效編號", 15, True),
            ("超出範圍", 16, False),
            ("負數", -1, False),
        ]
        
        for test_name, redis_db, should_pass in test_cases:
            try:
                original_db = os.environ.get("REDIS_DB")
                os.environ["REDIS_DB"] = str(redis_db)
                
                settings = Settings()
                if should_pass:
                    self.test_results.append({
                        "test": f"Redis DB - {test_name}",
                        "status": "pass",
                        "message": "驗證通過"
                    })
                    print(f"   ✅ {test_name}: 驗證通過")
                else:
                    self.test_results.append({
                        "test": f"Redis DB - {test_name}",
                        "status": "fail",
                        "message": "應該失敗但通過了"
                    })
                    print(f"   ❌ {test_name}: 應該失敗但通過了")
                
                if original_db:
                    os.environ["REDIS_DB"] = original_db
                elif "REDIS_DB" in os.environ:
                    del os.environ["REDIS_DB"]
                    
            except ValidationError as e:
                if not should_pass:
                    self.test_results.append({
                        "test": f"Redis DB - {test_name}",
                        "status": "pass",
                        "message": f"正確捕獲錯誤：{e}"
                    })
                    print(f"   ✅ {test_name}: 正確捕獲錯誤")
                else:
                    self.test_results.append({
                        "test": f"Redis DB - {test_name}",
                        "status": "fail",
                        "message": f"不應該失敗：{e}"
                    })
                    print(f"   ❌ {test_name}: 不應該失敗")
                
                if original_db:
                    os.environ["REDIS_DB"] = original_db
                elif "REDIS_DB" in os.environ:
                    del os.environ["REDIS_DB"]
    
    def test_mysql_charset_validation(self):
        """測試 MySQL 字符集驗證。"""
        print("🔍 測試 MySQL 字符集驗證...")
        
        test_cases = [
            ("有效字符集", "utf8mb4", True),
            ("有效字符集", "utf8", True),
            ("無效字符集", "invalid-charset", False),
            ("空字串", "", False),
        ]
        
        for test_name, mysql_charset, should_pass in test_cases:
            try:
                original_charset = os.environ.get("MYSQL_CHARSET")
                os.environ["MYSQL_CHARSET"] = mysql_charset
                
                settings = Settings()
                if should_pass:
                    self.test_results.append({
                        "test": f"MySQL 字符集 - {test_name}",
                        "status": "pass",
                        "message": "驗證通過"
                    })
                    print(f"   ✅ {test_name}: 驗證通過")
                else:
                    self.test_results.append({
                        "test": f"MySQL 字符集 - {test_name}",
                        "status": "fail",
                        "message": "應該失敗但通過了"
                    })
                    print(f"   ❌ {test_name}: 應該失敗但通過了")
                
                if original_charset:
                    os.environ["MYSQL_CHARSET"] = original_charset
                elif "MYSQL_CHARSET" in os.environ:
                    del os.environ["MYSQL_CHARSET"]
                    
            except ValidationError as e:
                if not should_pass:
                    self.test_results.append({
                        "test": f"MySQL 字符集 - {test_name}",
                        "status": "pass",
                        "message": f"正確捕獲錯誤：{e}"
                    })
                    print(f"   ✅ {test_name}: 正確捕獲錯誤")
                else:
                    self.test_results.append({
                        "test": f"MySQL 字符集 - {test_name}",
                        "status": "fail",
                        "message": f"不應該失敗：{e}"
                    })
                    print(f"   ❌ {test_name}: 不應該失敗")
                
                if original_charset:
                    os.environ["MYSQL_CHARSET"] = original_charset
                elif "MYSQL_CHARSET" in os.environ:
                    del os.environ["MYSQL_CHARSET"]
    
    def run_all_tests(self):
        """執行所有測試。"""
        print("🚀 Settings 驗證器測試")
        print("=" * 60)
        
        self.test_valid_config()
        self.test_cors_origins_validation()
        self.test_mongodb_uri_validation()
        self.test_aws_region_validation()
        self.test_redis_db_validation()
        self.test_mysql_charset_validation()
        
        # 總結
        print(f"\n📊 測試總結：")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "pass")
        failed_tests = total_tests - passed_tests
        
        print(f"✅ 通過：{passed_tests}/{total_tests}")
        print(f"❌ 失敗：{failed_tests}/{total_tests}")
        
        if failed_tests > 0:
            print(f"\n❌ 失敗的測試：")
            for result in self.test_results:
                if result["status"] == "fail":
                    print(f"  • {result['test']}: {result['message']}")
        
        return failed_tests == 0


def main():
    """主函數。"""
    tester = SettingsValidatorTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main() 