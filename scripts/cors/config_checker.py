"""
CORS 配置檢查器。

專門用於檢查專案中的 CORS 配置，與應用程式設定整合。
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings
from app.middleware.cors import get_cors_config_summary
from .security_checker import CORSecurityChecker


class CORSConfigChecker:
    """
    CORS 配置檢查器類別。
    
    專門用於檢查專案中的 CORS 配置，與應用程式設定整合。
    """
    
    def __init__(self):
        """初始化配置檢查器。"""
        self.security_checker = CORSecurityChecker()
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        取得目前的 CORS 配置。
        
        Returns:
            Dict: 目前的 CORS 配置
        """
        try:
            return get_cors_config_summary(settings)
        except Exception as e:
            return {
                "error": f"無法取得 CORS 配置：{e}",
                "environment": "unknown",
                "total_origins": 0,
                "origins": [],
                "methods": [],
                "headers": [],
                "max_age": 0,
                "allow_credentials": False
            }
    
    def check_environment_variables(self) -> Dict[str, Any]:
        """
        檢查環境變數設定。
        
        Returns:
            Dict: 環境變數檢查結果
        """
        cors_origins = os.getenv("CORS_ORIGINS", "")
        app_env = os.getenv("APP_ENV", "development")
        debug = os.getenv("DEBUG", "false")
        
        result = {
            "cors_origins_set": bool(cors_origins),
            "cors_origins_value": cors_origins,
            "app_env": app_env,
            "debug": debug,
            "origins_parsed": []
        }
        
        if cors_origins:
            origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
            result["origins_parsed"] = origins
            result["total_parsed_origins"] = len(origins)
        
        return result
    
    def comprehensive_check(self) -> Dict[str, Any]:
        """
        執行全面的配置檢查。
        
        Returns:
            Dict: 完整的檢查結果
        """
        # 取得目前配置
        current_config = self.get_current_config()
        
        if "error" in current_config:
            return {
                "success": False,
                "error": current_config["error"],
                "config": current_config
            }
        
        # 執行安全性檢查
        security_result = self.security_checker.comprehensive_check(
            origins=current_config["origins"],
            methods=current_config["methods"],
            headers=current_config["headers"],
            environment=current_config["environment"]
        )
        
        # 檢查環境變數
        env_check = self.check_environment_variables()
        
        return {
            "success": True,
            "config": current_config,
            "security": security_result,
            "environment": env_check,
            "overall_score": security_result["overall_score"]
        }
    
    def print_config_report(self, detailed: bool = True) -> None:
        """
        印出配置報告。
        
        Args:
            detailed: 是否顯示詳細資訊
        """
        result = self.comprehensive_check()
        
        if not result["success"]:
            print(f"❌ 配置檢查失敗：{result['error']}")
            return
        
        config = result["config"]
        security = result["security"]
        env_check = result["environment"]
        
        print("🚀 CORS 配置檢查報告")
        print("=" * 60)
        
        # 基本配置資訊
        print(f"📋 環境：{config['environment']}")
        print(f"🔗 來源數量：{config['total_origins']}")
        print(f"📝 允許的方法：{len(config['methods'])} 個")
        print(f"📋 允許的標頭：{len(config['headers'])} 個")
        print(f"⏱️  預檢快取時間：{config['max_age']} 秒")
        print(f"🔐 允許憑證：{config['allow_credentials']}")
        
        if detailed:
            # 詳細來源列表
            print(f"\n🌐 允許的來源：")
            for i, origin in enumerate(config['origins'], 1):
                protocol = "🔒 HTTPS" if origin.startswith("https://") else "⚠️  HTTP"
                print(f"  {i}. {origin} ({protocol})")
            
            # 詳細方法列表
            print(f"\n📡 允許的 HTTP 方法：")
            for method in config['methods']:
                if method in ["DELETE", "PUT", "PATCH"]:
                    print(f"  ⚠️  {method} (需要權限驗證)")
                else:
                    print(f"  ✅ {method}")
            
            # 詳細標頭列表
            print(f"\n📋 允許的標頭：")
            for header in config['headers']:
                if header in ["Authorization", "X-CSRF-Token"]:
                    print(f"  🔒 {header} (安全標頭)")
                else:
                    print(f"  📝 {header}")
        
        # 安全性評估
        print(f"\n🔍 安全性評估：")
        print(f"📊 總體安全性評分：{security['overall_score']}/100")
        
        if security['overall_score'] >= 90:
            print("🎉 安全性優秀！")
        elif security['overall_score'] >= 70:
            print("✅ 安全性良好")
        elif security['overall_score'] >= 50:
            print("⚠️  安全性中等，建議改進")
        else:
            print("❌ 安全性較差，需要立即改進")
        
        # 問題和警告
        if security['issues']:
            print(f"\n❌ 發現的問題：")
            for issue in security['issues']:
                print(f"  {issue}")
        
        if security['warnings']:
            print(f"\n⚠️  警告：")
            for warning in security['warnings']:
                print(f"  {warning}")
        
        # 改進建議
        if security['recommendations']:
            print(f"\n💡 改進建議：")
            for recommendation in security['recommendations']:
                print(f"  {recommendation}")
        
        # 環境變數檢查
        print(f"\n🔧 環境變數檢查：")
        if env_check['cors_origins_set']:
            print(f"✅ CORS_ORIGINS 已設定：{env_check['cors_origins_value']}")
            print(f"  解析出 {env_check['total_parsed_origins']} 個來源")
        else:
            print("⚠️  CORS_ORIGINS 未設定，使用預設值")
        
        print(f"✅ APP_ENV：{env_check['app_env']}")
        print(f"✅ DEBUG：{env_check['debug']}")
    
    def export_report(self, format: str = "json") -> str:
        """
        匯出檢查報告。
        
        Args:
            format: 報告格式 ("json", "yaml")
            
        Returns:
            str: 報告內容
        """
        result = self.comprehensive_check()
        
        if format == "json":
            import json
            return json.dumps(result, indent=2, ensure_ascii=False)
        elif format == "yaml":
            import yaml
            return yaml.dump(result, default_flow_style=False, allow_unicode=True)
        else:
            return str(result) 