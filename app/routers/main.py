"""
主要路由模組。

包含首頁、健康檢查等基礎路由。
"""

# ===== 標準函式庫 =====
from typing import Dict, Any  # 型別註解支援
import time  # 時間處理

# ===== 第三方套件 =====
from fastapi import APIRouter, Request  # 路由和請求物件
from fastapi.responses import HTMLResponse  # HTML 回應類型

# ===== 本地模組 =====
from app.core import settings, get_project_version  # 應用程式配置


# 建立路由器
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """
    首頁路由 - 顯示履歷診療室主頁面。
    
    Args:
        request: FastAPI 請求物件。
        
    Returns:
        HTMLResponse: 渲染後的 HTML 頁面。
    """
    # 從請求狀態中取得 templates
    templates = request.app.state.templates
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康檢查端點。
    
    提供應用程式狀態、版本、環境等資訊，用於監控和診斷。
    
    Returns:
        Dict[str, Any]: 應用程式狀態資訊。
    """
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "app_name": settings.app_name,
        "version": get_project_version(),
        "environment": settings.app_env,
        "debug": settings.debug,
        "uptime": "running",  # 可以進一步實作實際的運行時間計算
    }


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    簡易連線測試端點。
    
    提供最基本的連線測試，回應速度快，適合負載平衡器健康檢查。
    
    Returns:
        Dict[str, str]: 簡易回應。
    """
    return {"message": "pong"} 