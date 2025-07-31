#!/usr/bin/env python3
"""
CORS 配置檢查腳本。

用於檢查和驗證 CORS 設定，提供安全性分析和改進建議。
"""

import sys
import os
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings
from app.middleware.cors import get_cors_config_summary


def print_cors_config():
    """印出目前的 CORS 配置。"""
    print("🚀 CORS 配置檢查")
    print("=" * 60)
    
    try:
        # 取得 CORS 配置摘要
        config = get_cors_config_summary(settings)
        
        print(f"📋 環境：{config['environment']}")
        print(f"🔗 來源數量：{config['total_origins']}")
        print(f"📝 允許的方法：{len(config['methods'])} 個")
        print(f"📋 允許的標頭：{len(config['headers'])} 個")
        print(f"⏱️  預檢快取時間：{config['max_age']} 秒")
        print(f"🔐 允許憑證：{config['allow_credentials']}")
        
        print(f"\n🌐 允許的來源：")
        for i, origin in enumerate(config['origins'], 1):
            protocol = "🔒 HTTPS" if origin.startswith("https://") else "⚠️  HTTP"
            print(f"  {i}. {origin} ({protocol})")
        
        print(f"\n📡 允許的 HTTP 方法：")
        for method in config['methods']:
            if method in ["DELETE", "PUT", "PATCH"]:
                print(f"  ⚠️  {method} (需要權限驗證)")
            else:
                print(f"  ✅ {method}")
        
        print(f"\n📋 允許的標頭：")
        for header in config['headers']:
            if header in ["Authorization", "X-CSRF-Token"]:
                print(f"  🔒 {header} (安全標頭)")
            else:
                print(f"  📝 {header}")
        
        # 安全性評估
        print(f"\n🔍 安全性評估：")
        security_score = 100
        
        # 檢查 HTTP 來源
        http_origins = [o for o in config['origins'] if o.startswith("http://")]
        if http_origins and config['environment'] == 'production':
            print(f"  ❌ 生產環境發現 HTTP 來源：{http_origins}")
            security_score -= 30
        elif http_origins:
            print(f"  ⚠️  發現 HTTP 來源（開發環境可接受）：{http_origins}")
            security_score -= 10
        
        # 檢查來源數量
        if config['total_origins'] == 0:
            print(f"  ❌ 沒有設定任何 CORS 來源")
            security_score -= 50
        elif config['total_origins'] > 10:
            print(f"  ⚠️  CORS 來源過多（{config['total_origins']} 個），建議檢查")
            security_score -= 10
        
        # 檢查方法
        dangerous_methods = ["DELETE", "PUT", "PATCH"]
        if any(method in config['methods'] for method in dangerous_methods):
            print(f"  ⚠️  包含危險方法，確保有適當的權限驗證")
            security_score -= 5
        
        # 安全性評分
        print(f"\n📊 安全性評分：{max(0, security_score)}/100")
        
        if security_score >= 90:
            print("🎉 安全性優秀！")
        elif security_score >= 70:
            print("✅ 安全性良好")
        elif security_score >= 50:
            print("⚠️  安全性中等，建議改進")
        else:
            print("❌ 安全性較差，需要立即改進")
        
        # 改進建議
        print(f"\n💡 改進建議：")
        
        if http_origins and config['environment'] == 'production':
            print("  ✅ 生產環境應使用 HTTPS 來源")
        
        if config['total_origins'] == 0:
            print("  ✅ 請設定至少一個 CORS 來源")
        
        if config['total_origins'] > 10:
            print("  ✅ 考慮減少 CORS 來源數量，只保留必要的")
        
        if any(method in config['methods'] for method in dangerous_methods):
            print("  ✅ 確保危險方法有適當的權限驗證機制")
        
        print("  ✅ 定期檢查和更新 CORS 設定")
        print("  ✅ 考慮使用子域名限制，如 api.domain.com")
        
    except Exception as e:
        print(f"❌ 檢查失敗：{e}")
        return False
    
    return True


def check_environment_variables():
    """檢查環境變數設定。"""
    print(f"\n🔧 環境變數檢查：")
    print("=" * 60)
    
    # 檢查 CORS_ORIGINS
    cors_origins = os.getenv("CORS_ORIGINS", "")
    if cors_origins:
        print(f"✅ CORS_ORIGINS 已設定：{cors_origins}")
        
        # 解析並檢查
        origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
        print(f"  解析出 {len(origins)} 個來源")
        
        for i, origin in enumerate(origins, 1):
            if origin.startswith("https://"):
                print(f"  {i}. {origin} ✅ HTTPS")
            elif origin.startswith("http://"):
                print(f"  {i}. {origin} ⚠️  HTTP")
            else:
                print(f"  {i}. {origin} ❌ 格式錯誤")
    else:
        print("⚠️  CORS_ORIGINS 未設定，使用預設值")
    
    # 檢查其他相關環境變數
    app_env = os.getenv("APP_ENV", "development")
    print(f"✅ APP_ENV：{app_env}")
    
    debug = os.getenv("DEBUG", "false")
    print(f"✅ DEBUG：{debug}")


def main():
    """主函數。"""
    print("🚀 CORS 配置檢查工具")
    print("=" * 60)
    
    # 檢查 CORS 配置
    success = print_cors_config()
    
    # 檢查環境變數
    check_environment_variables()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 檢查完成！")
    else:
        print("❌ 檢查失敗！")
        sys.exit(1)


if __name__ == "__main__":
    main() 