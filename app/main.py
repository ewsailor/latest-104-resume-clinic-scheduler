"""
FastAPI 應用程式主入口。

【MVP】104 履歷診療室 - 站內諮詢時間媒合系統：讓 Giver、Taker 在平台內，方便地設定可面談時間，並完成配對媒合。
"""

# ===== 標準函式庫 =====
from typing import Dict, Any  # 型別註解支援

# ===== 第三方套件 =====
from fastapi import FastAPI, Request  # Web 框架核心
from fastapi.responses import HTMLResponse  # HTML 回應類型

# ===== 本地模組 =====
from app.config import config, get_project_version  # 應用程式配置
from app.factory import create_app, create_templates, create_static_files  # 應用程式工廠


# ===== 應用程式初始化 =====
# 建立應用程式實例
app = create_app(config)

# 建立模板引擎實例
templates = create_templates(config)


# ===== 路由定義 =====
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """
    首頁路由 - 顯示履歷診療室主頁面。
    
    Args:
        request: FastAPI 請求物件。
        
    Returns:
        HTMLResponse: 渲染後的 HTML 頁面。
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康檢查端點。
    
    Returns:
        Dict[str, Any]: 應用程式狀態資訊。
    """
    return {
        "status": "healthy",
        "app_name": config.app_name,
        "version": get_project_version(),
    }