#!/usr/bin/env python3
"""
CORS 安全性檢查腳本。

檢查 CORS 設定是否符合安全性最佳實踐，並提供改進建議。
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re


def check_cors_origins(origins: List[str]) -> Dict[str, Any]:
    """
    檢查 CORS 來源設定的安全性。
    
    Args:
        origins: CORS 來源列表
        
    Returns:
        Dict: 檢查結果和建議
    """
    print("🔍 檢查 CORS 來源設定...")
    
    issues = []
    warnings = []
    recommendations = []
    
    # 檢查是否使用萬用字元
    if "*" in origins:
        issues.append("❌ 發現安全風險：使用了 '*' 作為 CORS 來源")
        recommendations.append("✅ 建議：明確指定允許的來源，避免使用 '*'")
    
    # 檢查空字串
    if "" in origins or any(not origin.strip() for origin in origins):
        issues.append("❌ 發現問題：CORS 來源包含空字串")
        recommendations.append("✅ 建議：移除空字串來源")
    
    # 檢查 HTTP vs HTTPS
    http_origins = [origin for origin in origins if origin.startswith("http://")]
    if http_origins:
        warnings.append("⚠️  警告：發現 HTTP 來源，生產環境建議使用 HTTPS")
        recommendations.append("✅ 建議：生產環境只使用 HTTPS 來源")
    
    # 檢查本地開發來源
    local_origins = [origin for origin in origins if "localhost" in origin or "127.0.0.1" in origin]
    if local_origins:
        print(f"ℹ️  發現本地開發來源：{local_origins}")
    
    # 檢查域名格式
    for origin in origins:
        if not re.match(r'^https?://[a-zA-Z0-9.-]+(:\d+)?$', origin):
            warnings.append(f"⚠️  警告：來源格式可能不正確：{origin}")
    
    return {
        "issues": issues,
        "warnings": warnings,
        "recommendations": recommendations,
        "total_origins": len(origins),
        "http_origins": len(http_origins),
        "https_origins": len([o for o in origins if o.startswith("https://")]),
        "local_origins": len(local_origins)
    }


def check_cors_methods(methods: List[str]) -> Dict[str, Any]:
    """
    檢查 CORS 方法設定的安全性。
    
    Args:
        methods: 允許的 HTTP 方法列表
        
    Returns:
        Dict: 檢查結果和建議
    """
    print("🔍 檢查 CORS 方法設定...")
    
    issues = []
    warnings = []
    recommendations = []
    
    # 檢查是否使用萬用字元
    if "*" in methods:
        issues.append("❌ 發現安全風險：使用了 '*' 作為允許的方法")
        recommendations.append("✅ 建議：明確指定需要的 HTTP 方法")
    
    # 檢查必要的方法
    required_methods = ["GET", "OPTIONS"]
    for method in required_methods:
        if method not in methods:
            warnings.append(f"⚠️  警告：缺少必要的方法：{method}")
    
    # 檢查危險方法
    dangerous_methods = ["DELETE", "PUT", "PATCH"]
    for method in dangerous_methods:
        if method in methods:
            print(f"ℹ️  發現需要驗證的方法：{method}")
            recommendations.append(f"✅ 建議：確保 {method} 方法有適當的權限驗證")
    
    return {
        "issues": issues,
        "warnings": warnings,
        "recommendations": recommendations,
        "total_methods": len(methods),
        "dangerous_methods": len([m for m in methods if m in dangerous_methods])
    }


def check_cors_headers(headers: List[str]) -> Dict[str, Any]:
    """
    檢查 CORS 標頭設定的安全性。
    
    Args:
        headers: 允許的標頭列表
        
    Returns:
        Dict: 檢查結果和建議
    """
    print("🔍 檢查 CORS 標頭設定...")
    
    issues = []
    warnings = []
    recommendations = []
    
    # 檢查是否使用萬用字元
    if "*" in headers:
        issues.append("❌ 發現安全風險：使用了 '*' 作為允許的標頭")
        recommendations.append("✅ 建議：明確指定需要的標頭")
    
    # 檢查必要的標頭
    required_headers = ["Content-Type"]
    for header in required_headers:
        if header not in headers:
            warnings.append(f"⚠️  警告：缺少必要的標頭：{header}")
    
    # 檢查安全相關標頭
    security_headers = ["Authorization", "X-CSRF-Token", "X-Requested-With"]
    for header in security_headers:
        if header in headers:
            print(f"ℹ️  發現安全標頭：{header}")
    
    return {
        "issues": issues,
        "warnings": warnings,
        "recommendations": recommendations,
        "total_headers": len(headers),
        "security_headers": len([h for h in headers if h in security_headers])
    }


def check_environment_settings() -> Dict[str, Any]:
    """
    檢查環境變數中的 CORS 設定。
    
    Returns:
        Dict: 檢查結果
    """
    print("🔍 檢查環境變數設定...")
    
    cors_origins = os.getenv("CORS_ORIGINS", "")
    
    if not cors_origins:
        return {
            "status": "warning",
            "message": "⚠️  未設定 CORS_ORIGINS 環境變數",
            "recommendation": "建議在 .env 檔案中設定 CORS_ORIGINS"
        }
    
    origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    return check_cors_origins(origins)


def main():
    """
    主函數：執行 CORS 安全性檢查。
    """
    print("🚀 開始 CORS 安全性檢查...")
    print("=" * 50)
    
    # 檢查環境變數
    env_check = check_environment_settings()
    
    # 模擬檢查（實際使用時會從應用程式設定中讀取）
    print("\n📋 模擬檢查結果：")
    
    # 檢查來源
    origins_result = check_cors_origins([
        "http://localhost:3000",
        "http://localhost:8000",
        "https://www.104.com.tw"
    ])
    
    # 檢查方法
    methods_result = check_cors_methods([
        "GET", "POST", "PUT", "DELETE", "OPTIONS"
    ])
    
    # 檢查標頭
    headers_result = check_cors_headers([
        "Content-Type", "Authorization", "X-Requested-With"
    ])
    
    # 輸出結果
    print("\n" + "=" * 50)
    print("📊 檢查結果摘要：")
    print(f"• 來源數量：{origins_result['total_origins']}")
    print(f"• 方法數量：{methods_result['total_methods']}")
    print(f"• 標頭數量：{headers_result['total_headers']}")
    
    # 輸出問題
    all_issues = (
        origins_result['issues'] + 
        methods_result['issues'] + 
        headers_result['issues']
    )
    
    if all_issues:
        print("\n❌ 發現的問題：")
        for issue in all_issues:
            print(f"  {issue}")
    
    # 輸出警告
    all_warnings = (
        origins_result['warnings'] + 
        methods_result['warnings'] + 
        headers_result['warnings']
    )
    
    if all_warnings:
        print("\n⚠️  警告：")
        for warning in all_warnings:
            print(f"  {warning}")
    
    # 輸出建議
    all_recommendations = (
        origins_result['recommendations'] + 
        methods_result['recommendations'] + 
        headers_result['recommendations']
    )
    
    if all_recommendations:
        print("\n✅ 改進建議：")
        for recommendation in all_recommendations:
            print(f"  {recommendation}")
    
    print("\n" + "=" * 50)
    print("🎉 CORS 安全性檢查完成！")


if __name__ == "__main__":
    main() 