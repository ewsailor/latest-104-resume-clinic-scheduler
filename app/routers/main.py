"""
主要路由模組。

包含首頁、健康檢查等基礎路由。
"""

import time  # 時間處理

# ===== 標準函式庫 =====
from typing import Any, Dict  # 型別註解支援

# ===== 第三方套件 =====
from fastapi import APIRouter, Request  # 路由和請求物件
from fastapi.responses import HTMLResponse  # HTML 回應類型

# ===== 本地模組 =====
from app.core import get_project_version, settings  # 應用程式配置

# 建立路由器
router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["Pages"])
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
