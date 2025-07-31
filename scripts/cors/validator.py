"""
CORS 驗證器。

用於驗證特定的 CORS 設定字串或配置。
"""

import re
from typing import List, Dict, Any, Optional
from .security_checker import CORSecurityChecker


class CORSValidator:
    """
    CORS 驗證器類別。
    
    用於驗證特定的 CORS 設定字串或配置。
    """
    
    def __init__(self):
        """初始化驗證器。"""
        self.security_checker = CORSecurityChecker()
    
    def validate_origin_string(self, origin_string: str) -> Dict[str, Any]:
        """
        驗證 CORS 來源字串。
        
        Args:
            origin_string: CORS 來源字串，如 "http://localhost,https://api.example.com"
            
        Returns:
            Dict: 驗證結果
        """
        print(f"🔍 驗證 CORS 來源字串：{origin_string}")
        
        # 解析來源
        origins = [origin.strip() for origin in origin_string.split(",") if origin.strip()]
        
        if not origins:
            return {
                "valid": False,
                "error": "沒有找到有效的來源",
                "origins": [],
                "total_origins": 0
            }
        
        # 驗證每個來源
        valid_origins = []
        invalid_origins = []
        
        for origin in origins:
            if self._is_valid_origin(origin):
                valid_origins.append(origin)
            else:
                invalid_origins.append(origin)
        
        # 執行安全性檢查
        security_result = self.security_checker.check_origins(valid_origins)
        
        return {
            "valid": len(invalid_origins) == 0,
            "origins": valid_origins,
            "invalid_origins": invalid_origins,
            "total_origins": len(valid_origins),
            "security": security_result,
            "recommendations": self._generate_origin_recommendations(valid_origins, invalid_origins)
        }
    
    def _is_valid_origin(self, origin: str) -> bool:
        """
        檢查單個來源是否有效。
        
        Args:
            origin: 來源字串
            
        Returns:
            bool: 是否有效
        """
        # 基本格式檢查
        if not origin or not origin.strip():
            return False
        
        # 協議檢查
        if not (origin.startswith("http://") or origin.startswith("https://")):
            return False
        
        # 格式檢查
        pattern = r'^https?://[a-zA-Z0-9.-]+(:\d+)?$'
        return bool(re.match(pattern, origin))
    
    def _generate_origin_recommendations(self, valid_origins: List[str], 
                                       invalid_origins: List[str]) -> List[str]:
        """
        生成來源改進建議。
        
        Args:
            valid_origins: 有效的來源列表
            invalid_origins: 無效的來源列表
            
        Returns:
            List[str]: 改進建議列表
        """
        recommendations = []
        
        # 處理無效來源
        for origin in invalid_origins:
            if not origin.strip():
                recommendations.append(f"✅ 移除空字串來源")
            elif not (origin.startswith("http://") or origin.startswith("https://")):
                recommendations.append(f"✅ 修正來源格式：{origin} -> https://{origin}")
            else:
                recommendations.append(f"✅ 檢查來源格式：{origin}")
        
        # 處理有效來源
        http_origins = [o for o in valid_origins if o.startswith("http://")]
        if http_origins:
            recommendations.append("✅ 生產環境建議使用 HTTPS 來源")
        
        # 檢查本地開發來源
        local_origins = [o for o in valid_origins if "localhost" in o or "127.0.0.1" in o]
        for origin in local_origins:
            if ":" not in origin:
                recommendations.append(f"✅ 為 {origin} 添加埠號，如 {origin}:3000")
        
        return recommendations
    
    def validate_cors_config(self, origins: List[str], methods: List[str], 
                           headers: List[str], environment: str = "development") -> Dict[str, Any]:
        """
        驗證完整的 CORS 配置。
        
        Args:
            origins: CORS 來源列表
            methods: 允許的 HTTP 方法列表
            headers: 允許的標頭列表
            environment: 環境名稱
            
        Returns:
            Dict: 驗證結果
        """
        print(f"🔍 驗證 CORS 配置（環境：{environment}）")
        
        # 驗證來源
        origins_validation = self._validate_origins(origins, environment)
        
        # 驗證方法
        methods_validation = self._validate_methods(methods)
        
        # 驗證標頭
        headers_validation = self._validate_headers(headers)
        
        # 執行安全性檢查
        security_result = self.security_checker.comprehensive_check(
            origins, methods, headers, environment
        )
        
        # 計算總體驗證分數
        validation_score = (
            origins_validation["score"] * 0.4 +
            methods_validation["score"] * 0.3 +
            headers_validation["score"] * 0.3
        )
        
        return {
            "valid": validation_score >= 70,  # 70分以上視為有效
            "validation_score": int(validation_score),
            "security_score": security_result["overall_score"],
            "origins": origins_validation,
            "methods": methods_validation,
            "headers": headers_validation,
            "security": security_result,
            "recommendations": self._merge_recommendations([
                origins_validation["recommendations"],
                methods_validation["recommendations"],
                headers_validation["recommendations"],
                security_result["recommendations"]
            ])
        }
    
    def _validate_origins(self, origins: List[str], environment: str) -> Dict[str, Any]:
        """驗證來源設定。"""
        score = 100
        issues = []
        recommendations = []
        
        if not origins:
            score = 0
            issues.append("沒有設定任何 CORS 來源")
            recommendations.append("設定至少一個 CORS 來源")
        
        # 檢查 HTTP 來源
        http_origins = [o for o in origins if o.startswith("http://")]
        if http_origins and environment == "production":
            score -= 30
            issues.append("生產環境不應使用 HTTP 來源")
            recommendations.append("生產環境應使用 HTTPS 來源")
        
        # 檢查格式
        for origin in origins:
            if not self._is_valid_origin(origin):
                score -= 20
                issues.append(f"無效的來源格式：{origin}")
                recommendations.append(f"修正來源格式：{origin}")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "total_origins": len(origins),
            "http_origins": len(http_origins)
        }
    
    def _validate_methods(self, methods: List[str]) -> Dict[str, Any]:
        """驗證方法設定。"""
        score = 100
        issues = []
        recommendations = []
        
        if not methods:
            score = 0
            issues.append("沒有設定任何 HTTP 方法")
            recommendations.append("設定必要的 HTTP 方法")
        
        # 檢查必要方法
        required_methods = ["GET", "OPTIONS"]
        for method in required_methods:
            if method not in methods:
                score -= 10
                issues.append(f"缺少必要的方法：{method}")
                recommendations.append(f"添加必要的方法：{method}")
        
        # 檢查萬用字元
        if "*" in methods:
            score -= 30
            issues.append("不應使用 '*' 作為允許的方法")
            recommendations.append("明確指定需要的 HTTP 方法")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "total_methods": len(methods)
        }
    
    def _validate_headers(self, headers: List[str]) -> Dict[str, Any]:
        """驗證標頭設定。"""
        score = 100
        issues = []
        recommendations = []
        
        if not headers:
            score = 0
            issues.append("沒有設定任何標頭")
            recommendations.append("設定必要的標頭")
        
        # 檢查必要標頭
        required_headers = ["Content-Type"]
        for header in required_headers:
            if header not in headers:
                score -= 10
                issues.append(f"缺少必要的標頭：{header}")
                recommendations.append(f"添加必要的標頭：{header}")
        
        # 檢查萬用字元
        if "*" in headers:
            score -= 30
            issues.append("不應使用 '*' 作為允許的標頭")
            recommendations.append("明確指定需要的標頭")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "total_headers": len(headers)
        }
    
    def _merge_recommendations(self, recommendation_lists: List[List[str]]) -> List[str]:
        """合併多個建議列表。"""
        all_recommendations = []
        for recs in recommendation_lists:
            all_recommendations.extend(recs)
        
        # 去重並保持順序
        seen = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations 