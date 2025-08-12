"""
CORS 安全性檢查器。

提供通用的 CORS 安全性檢查功能，可用於任何 CORS 設定。
"""

import re
from typing import Any, Dict, List


class CORSecurityChecker:
    """
    CORS 安全性檢查器類別。

    提供各種 CORS 安全性檢查功能，包括來源、方法、標頭檢查等。
    """

    def __init__(self):
        """初始化檢查器。"""
        self.logger = None  # 可以注入 logger

    def check_origins(self, origins: List[str]) -> Dict[str, Any]:
        """
        檢查 CORS 來源設定的安全性。

        Args:
            origins: CORS 來源列表

        Returns:
            Dict: 檢查結果和建議
        """
        issues = []
        warnings = []
        recommendations = []
        security_score = 100

        # 檢查是否使用萬用字元
        if "*" in origins:
            issues.append("❌ 發現安全風險：使用了 '*' 作為 CORS 來源")
            recommendations.append("✅ 建議：明確指定允許的來源，避免使用 '*'")
            security_score -= 30

        # 檢查空字串
        if "" in origins or any(not origin.strip() for origin in origins):
            issues.append("❌ 發現問題：CORS 來源包含空字串")
            recommendations.append("✅ 建議：移除空字串來源")
            security_score -= 20

        # 檢查 HTTP vs HTTPS
        http_origins = [origin for origin in origins if origin.startswith("http://")]
        if http_origins:
            warnings.append("⚠️  警告：發現 HTTP 來源，生產環境建議使用 HTTPS")
            recommendations.append("✅ 建議：生產環境只使用 HTTPS 來源")
            security_score -= 10

        # 檢查本地開發來源
        local_origins = [
            origin
            for origin in origins
            if "localhost" in origin or "127.0.0.1" in origin
        ]

        # 檢查域名格式
        for origin in origins:
            if not re.match(r'^https?://[a-zA-Z0-9.-]+(:\d+)?$', origin):
                warnings.append(f"⚠️  警告：來源格式可能不正確：{origin}")
                security_score -= 5

        # 檢查重複來源
        if len(origins) != len(set(origins)):
            issues.append("❌ 發現重複的來源")
            security_score -= 10

        return {
            "issues": issues,
            "warnings": warnings,
            "recommendations": recommendations,
            "security_score": max(0, security_score),
            "total_origins": len(origins),
            "http_origins": len(http_origins),
            "https_origins": len([o for o in origins if o.startswith("https://")]),
            "local_origins": len(local_origins),
            "local_origins_list": local_origins,
        }

    def check_methods(self, methods: List[str]) -> Dict[str, Any]:
        """
        檢查 CORS 方法設定的安全性。

        Args:
            methods: 允許的 HTTP 方法列表

        Returns:
            Dict: 檢查結果和建議
        """
        issues = []
        warnings = []
        recommendations = []
        security_score = 100

        # 檢查是否使用萬用字元
        if "*" in methods:
            issues.append("❌ 發現安全風險：使用了 '*' 作為允許的方法")
            recommendations.append("✅ 建議：明確指定需要的 HTTP 方法")
            security_score -= 30

        # 檢查必要的方法
        required_methods = ["GET", "OPTIONS"]
        for method in required_methods:
            if method not in methods:
                warnings.append(f"⚠️  警告：缺少必要的方法：{method}")
                security_score -= 5

        # 檢查危險方法
        dangerous_methods = ["DELETE", "PUT", "PATCH"]
        dangerous_found = []
        for method in dangerous_methods:
            if method in methods:
                dangerous_found.append(method)
                recommendations.append(f"✅ 建議：確保 {method} 方法有適當的權限驗證")
                security_score -= 5

        return {
            "issues": issues,
            "warnings": warnings,
            "recommendations": recommendations,
            "security_score": max(0, security_score),
            "total_methods": len(methods),
            "dangerous_methods": len(dangerous_found),
            "dangerous_methods_list": dangerous_found,
        }

    def check_headers(self, headers: List[str]) -> Dict[str, Any]:
        """
        檢查 CORS 標頭設定的安全性。

        Args:
            headers: 允許的標頭列表

        Returns:
            Dict: 檢查結果和建議
        """
        issues = []
        warnings = []
        recommendations = []
        security_score = 100

        # 檢查是否使用萬用字元
        if "*" in headers:
            issues.append("❌ 發現安全風險：使用了 '*' 作為允許的標頭")
            recommendations.append("✅ 建議：明確指定需要的標頭")
            security_score -= 30

        # 檢查必要的標頭
        required_headers = ["Content-Type"]
        for header in required_headers:
            if header not in headers:
                warnings.append(f"⚠️  警告：缺少必要的標頭：{header}")
                security_score -= 5

        # 檢查安全相關標頭
        security_headers = ["Authorization", "X-CSRF-Token", "X-Requested-With"]
        security_found = []
        for header in security_headers:
            if header in headers:
                security_found.append(header)

        return {
            "issues": issues,
            "warnings": warnings,
            "recommendations": recommendations,
            "security_score": max(0, security_score),
            "total_headers": len(headers),
            "security_headers": len(security_found),
            "security_headers_list": security_found,
        }

    def check_environment_mix(
        self, origins: List[str], environment: str
    ) -> Dict[str, Any]:
        """
        檢查環境混合問題。

        Args:
            origins: CORS 來源列表
            environment: 環境名稱

        Returns:
            Dict: 檢查結果
        """
        issues = []
        warnings = []
        recommendations = []
        security_score = 100

        has_local = any("localhost" in o or "127.0.0.1" in o for o in origins)
        has_production = any(
            "." in o and not any(local in o for local in ["localhost", "127.0.0.1"])
            for o in origins
        )

        if has_local and has_production:
            warnings.append("⚠️  混合了本地開發和生產環境來源")
            recommendations.append("✅ 建議：根據環境分離 CORS 來源設定")
            security_score -= 10

        if environment == "production" and has_local:
            issues.append("❌ 生產環境包含本地開發來源")
            security_score -= 20

        return {
            "issues": issues,
            "warnings": warnings,
            "recommendations": recommendations,
            "security_score": max(0, security_score),
            "has_local": has_local,
            "has_production": has_production,
        }

    def comprehensive_check(
        self,
        origins: List[str],
        methods: List[str],
        headers: List[str],
        environment: str = "development",
    ) -> Dict[str, Any]:
        """
        執行全面的 CORS 安全性檢查。

        Args:
            origins: CORS 來源列表
            methods: 允許的 HTTP 方法列表
            headers: 允許的標頭列表
            environment: 環境名稱

        Returns:
            Dict: 完整的檢查結果
        """
        origins_check = self.check_origins(origins)
        methods_check = self.check_methods(methods)
        headers_check = self.check_headers(headers)
        environment_check = self.check_environment_mix(origins, environment)

        # 計算總體安全性評分
        total_score = (
            origins_check["security_score"] * 0.4
            + methods_check["security_score"] * 0.3
            + headers_check["security_score"] * 0.2
            + environment_check["security_score"] * 0.1
        )

        # 合併所有問題和建議
        all_issues = (
            origins_check["issues"]
            + methods_check["issues"]
            + headers_check["issues"]
            + environment_check["issues"]
        )

        all_warnings = (
            origins_check["warnings"]
            + methods_check["warnings"]
            + headers_check["warnings"]
            + environment_check["warnings"]
        )

        all_recommendations = (
            origins_check["recommendations"]
            + methods_check["recommendations"]
            + headers_check["recommendations"]
            + environment_check["recommendations"]
        )

        return {
            "overall_score": int(total_score),
            "issues": all_issues,
            "warnings": all_warnings,
            "recommendations": all_recommendations,
            "details": {
                "origins": origins_check,
                "methods": methods_check,
                "headers": headers_check,
                "environment": environment_check,
            },
            "summary": {
                "total_origins": origins_check["total_origins"],
                "total_methods": methods_check["total_methods"],
                "total_headers": headers_check["total_headers"],
                "environment": environment,
            },
        }
