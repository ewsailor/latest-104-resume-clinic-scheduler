"""
FastAPI 應用程式主入口。

【MVP】104 履歷診療室 - 站內諮詢時間媒合系統：讓 Giver、Taker 在平台內，方便地設定可面談時間，並完成配對媒合。
"""

# ===== 本地模組 =====
from app.core import settings  # 應用程式配置
from app.factory import create_app, create_templates  # 應用程式工廠
from app.routers.health import router as health_router  # 健康檢查路由
from app.routers.main import router as main_router  # 主要路由

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
