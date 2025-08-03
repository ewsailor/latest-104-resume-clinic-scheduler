"""
CORS 中間件模組。

負責設定和管理 FastAPI 應用程式的 CORS（跨來源資源共用）策略。
提供環境感知的 CORS 設定，確保安全性和最佳實踐。
"""

# ===== 標準函式庫 =====
import logging
from typing import List  # 型別註解支援

# ===== 第三方套件 =====
from fastapi import FastAPI  # Web 框架核心
from fastapi.middleware.cors import CORSMiddleware  # CORS 中間件

# ===== 本地模組 =====
from app.core.settings import Settings  # 應用程式設定

# 設定日誌
logger = logging.getLogger(__name__)


def get_cors_origins_by_environment(settings: Settings) -> List[str]:
    """
    根據環境動態取得 CORS 來源列表。

    Args:
        settings: 應用程式設定物件

    Returns:
        List[str]: CORS 來源列表
    """
    logger.info(f"設定 CORS 來源，環境：{settings.app_env}")

    # 根據環境設定預設的 CORS 來源
    if settings.is_development:
        # 開發環境：允許本地開發伺服器
        cors_origins = [
            "http://localhost:3000",  # React 開發伺服器
            "http://localhost:8000",  # FastAPI 開發伺服器
            "http://127.0.0.1:3000",  # React 開發伺服器 (IP)
            "http://127.0.0.1:8000",  # FastAPI 開發伺服器 (IP)
        ]
        logger.info("使用開發環境 CORS 來源")

    elif settings.is_staging:
        # 測試環境：允許測試域名
        cors_origins = [
            "https://staging.104.com.tw",
            "https://staging-api.104.com.tw",
        ]
        logger.info("使用測試環境 CORS 來源")

    elif settings.is_production:
        # 生產環境：只允許正式域名
        cors_origins = [
            "https://www.104.com.tw",
            "https://api.104.com.tw",
        ]
        logger.info("使用生產環境 CORS 來源")

    else:
        # 預設環境：使用基本設定
        cors_origins = ["http://localhost:8000"]
        logger.warning(f"未知環境 {settings.app_env}，使用預設 CORS 來源")

    # 如果設定檔中有自定義 CORS 來源，則使用設定檔的值
    if settings.cors_origins and settings.cors_origins != "http://localhost:8000":
        cors_origins = settings.cors_origins_list
        logger.info(f"使用自定義 CORS 來源：{cors_origins}")

    return cors_origins


def validate_cors_origins(origins: List[str]) -> List[str]:
    """
    驗證和清理 CORS 來源列表。

    Args:
        origins: 原始 CORS 來源列表

    Returns:
        List[str]: 驗證後的 CORS 來源列表
    """
    logger.info("驗證 CORS 來源設定")

    validated_origins = []
    issues = []

    for origin in origins:
        origin = origin.strip()

        # 跳過空字串
        if not origin:
            issues.append("發現空字串來源，已跳過")
            continue

        # 檢查協議
        if not (origin.startswith("http://") or origin.startswith("https://")):
            issues.append(f"來源 {origin} 協議格式不正確，已跳過")
            continue

        # 檢查重複
        if origin in validated_origins:
            issues.append(f"發現重複來源 {origin}，已跳過")
            continue

        validated_origins.append(origin)

    # 記錄問題
    if issues:
        for issue in issues:
            logger.warning(issue)

    logger.info(f"CORS 來源驗證完成，有效來源：{len(validated_origins)} 個")
    return validated_origins


def get_cors_methods() -> List[str]:
    """
    取得允許的 HTTP 方法列表。

    Returns:
        List[str]: 允許的 HTTP 方法列表
    """
    return [
        "GET",  # 讀取資料
        "POST",  # 建立資料
        "PUT",  # 更新資料
        "PATCH",  # 部分更新
        "DELETE",  # 刪除資料
        "OPTIONS",  # 預檢請求
    ]


def get_cors_headers() -> List[str]:
    """
    取得允許的標頭列表。

    Returns:
        List[str]: 允許的標頭列表
    """
    return [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
    ]


def setup_cors_middleware(app: FastAPI, settings: Settings) -> None:
    """
    設定 CORS 中間件。

    Args:
        app: FastAPI 應用程式實例
        settings: 應用程式設定物件
    """
    logger.info("開始設定 CORS 中間件")

    try:
        # 取得 CORS 來源
        cors_origins = get_cors_origins_by_environment(settings)

        # 驗證 CORS 來源
        validated_origins = validate_cors_origins(cors_origins)

        if not validated_origins:
            logger.error("沒有有效的 CORS 來源，CORS 中間件設定失敗")
            return

        # 取得允許的方法和標頭
        cors_methods = get_cors_methods()
        cors_headers = get_cors_headers()

        # 添加 CORS 中間件
        app.add_middleware(
            CORSMiddleware,
            # ✅ 安全：明確指定允許的來源，避免使用 "*"、避免可能包含空字串
            allow_origins=validated_origins,
            # ✅ 安全：根據需求設定 credentials
            allow_credentials=True,
            # ✅ 安全：明確指定允許的 HTTP 方法，避免使用 "*"
            allow_methods=cors_methods,
            # ✅ 安全：明確指定允許的標頭，避免使用 "*"
            allow_headers=cors_headers,
            # ✅ 安全：設定預檢請求快取時間
            max_age=3600,  # 1 小時
        )

        logger.info("CORS 中間件設定成功")
        logger.info(f"允許的來源：{validated_origins}")
        logger.info(f"允許的方法：{cors_methods}")
        logger.info(f"允許的標頭：{cors_headers}")

    except Exception as e:
        logger.error(f"CORS 中間件設定失敗：{e}")
        raise


def get_cors_config_summary(settings: Settings) -> dict:
    """
    取得 CORS 配置摘要，用於除錯和監控。

    Args:
        settings: 應用程式設定物件

    Returns:
        dict: CORS 配置摘要
    """
    cors_origins = get_cors_origins_by_environment(settings)
    validated_origins = validate_cors_origins(cors_origins)

    return {
        "environment": settings.app_env,
        "total_origins": len(validated_origins),
        "origins": validated_origins,
        "methods": get_cors_methods(),
        "headers": get_cors_headers(),
        "max_age": 3600,
        "allow_credentials": True,
    }
