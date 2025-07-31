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
from app.core import settings, get_project_version # 應用程式配置
from app.factory import create_app, create_templates, create_static_files  # 應用程式工廠
from app.routers.main import router as main_router  # 主要路由
from app.routers.health import router as health_router  # 健康檢查路由


# ===== 應用程式初始化 =====
# 建立應用程式實例
app = create_app(settings)

# 建立模板引擎實例
templates = create_templates(settings)

# 將 templates 設定到應用程式狀態中，用依賴注入解決循環匯入問題
app.state.templates = templates

# 註冊路由
app.include_router(main_router)
app.include_router(health_router)