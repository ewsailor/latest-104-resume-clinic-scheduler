#!/usr/bin/env python3
"""
CORS 檢查工具。

統一的 CORS 檢查命令列工具，支援多種檢查模式。
"""

import sys
import argparse
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.cors import CORSecurityChecker, CORSConfigChecker, CORSValidator


def main():
    """主函數。"""
    parser = argparse.ArgumentParser(
        description="CORS 檢查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  # 檢查專案 CORS 配置
  python scripts/cors_check.py config
  
  # 檢查專案 CORS 配置（簡潔模式）
  python scripts/cors_check.py config --simple
  
  # 驗證特定的 CORS 來源字串
  python scripts/cors_check.py validate "http://localhost,https://api.example.com"
  
  # 安全性檢查（模擬資料）
  python scripts/cors_check.py security
  
  # 匯出報告為 JSON
  python scripts/cors_check.py config --export json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="檢查專案 CORS 配置")
    config_parser.add_argument("--simple", action="store_true", help="簡潔模式")
    config_parser.add_argument("--export", choices=["json", "yaml"], help="匯出格式")
    
    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="驗證 CORS 設定")
    validate_parser.add_argument("origins", help="CORS 來源字串")
    validate_parser.add_argument("--environment", default="development", 
                               choices=["development", "staging", "production"],
                               help="環境設定")
    
    # security 命令
    security_parser = subparsers.add_parser("security", help="安全性檢查（模擬資料）")
    security_parser.add_argument("--environment", default="development",
                               choices=["development", "staging", "production"],
                               help="環境設定")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "config":
            handle_config_command(args)
        elif args.command == "validate":
            handle_validate_command(args)
        elif args.command == "security":
            handle_security_command(args)
    except Exception as e:
        print(f"❌ 執行失敗：{e}")
        sys.exit(1)


def handle_config_command(args):
    """處理 config 命令。"""
    print("🚀 CORS 配置檢查")
    print("=" * 60)
    
    checker = CORSConfigChecker()
    
    if args.export:
        # 匯出報告
        report = checker.export_report(args.export)
        print(report)
    else:
        # 顯示報告
        checker.print_config_report(detailed=not args.simple)


def handle_validate_command(args):
    """處理 validate 命令。"""
    print("🔍 CORS 設定驗證")
    print("=" * 60)
    
    validator = CORSValidator()
    
    # 驗證來源字串
    result = validator.validate_origin_string(args.origins)
    
    print(f"📋 驗證結果：{'✅ 有效' if result['valid'] else '❌ 無效'}")
    print(f"🔗 有效來源：{result['total_origins']} 個")
    
    if result['origins']:
        print(f"\n✅ 有效的來源：")
        for i, origin in enumerate(result['origins'], 1):
            protocol = "🔒 HTTPS" if origin.startswith("https://") else "⚠️  HTTP"
            print(f"  {i}. {origin} ({protocol})")
    
    if result['invalid_origins']:
        print(f"\n❌ 無效的來源：")
        for i, origin in enumerate(result['invalid_origins'], 1):
            print(f"  {i}. {origin}")
    
    # 安全性檢查
    if result['security']:
        print(f"\n🔍 安全性評估：")
        print(f"📊 安全性評分：{result['security']['security_score']}/100")
        
        if result['security']['issues']:
            print(f"\n❌ 發現的問題：")
            for issue in result['security']['issues']:
                print(f"  {issue}")
        
        if result['security']['warnings']:
            print(f"\n⚠️  警告：")
            for warning in result['security']['warnings']:
                print(f"  {warning}")
    
    # 改進建議
    if result['recommendations']:
        print(f"\n💡 改進建議：")
        for recommendation in result['recommendations']:
            print(f"  {recommendation}")


def handle_security_command(args):
    """處理 security 命令。"""
    print("🔒 CORS 安全性檢查（模擬資料）")
    print("=" * 60)
    
    # 模擬資料
    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://www.104.com.tw"
    ]
    
    methods = [
        "GET", "POST", "PUT", "DELETE", "OPTIONS"
    ]
    
    headers = [
        "Content-Type", "Authorization", "X-Requested-With"
    ]
    
    print(f"📋 檢查環境：{args.environment}")
    print(f"🔗 來源：{origins}")
    print(f"📡 方法：{methods}")
    print(f"📋 標頭：{headers}")
    print()
    
    # 執行安全性檢查
    checker = CORSecurityChecker()
    result = checker.comprehensive_check(origins, methods, headers, args.environment)
    
    print(f"📊 總體安全性評分：{result['overall_score']}/100")
    
    if result['overall_score'] >= 90:
        print("🎉 安全性優秀！")
    elif result['overall_score'] >= 70:
        print("✅ 安全性良好")
    elif result['overall_score'] >= 50:
        print("⚠️  安全性中等，建議改進")
    else:
        print("❌ 安全性較差，需要立即改進")
    
    # 詳細結果
    print(f"\n📋 詳細結果：")
    print(f"• 來源檢查：{result['details']['origins']['security_score']}/100")
    print(f"• 方法檢查：{result['details']['methods']['security_score']}/100")
    print(f"• 標頭檢查：{result['details']['headers']['security_score']}/100")
    print(f"• 環境檢查：{result['details']['environment']['security_score']}/100")
    
    # 問題和警告
    if result['issues']:
        print(f"\n❌ 發現的問題：")
        for issue in result['issues']:
            print(f"  {issue}")
    
    if result['warnings']:
        print(f"\n⚠️  警告：")
        for warning in result['warnings']:
            print(f"  {warning}")
    
    # 改進建議
    if result['recommendations']:
        print(f"\n💡 改進建議：")
        for recommendation in result['recommendations']:
            print(f"  {recommendation}")


if __name__ == "__main__":
    main() 