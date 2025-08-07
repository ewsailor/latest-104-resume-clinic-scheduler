"""
API 路由模組集中匯入點。

匯入所有 API 相關的路由器，提供統一的 API 介面。
"""

# ===== 第三方套件 =====
from fastapi import APIRouter  # 路由物件

# ===== 本地模組 =====
from app.routers.api.schedule import router as schedule_router  # 時段 API 路由

# 建立 API 路由器
api_router = APIRouter()

# 註冊所有 API 路由
api_router.include_router(schedule_router)

# 未來可以輕鬆新增其他 API 路由
# from app.routers.api.users import router as users_router
# api_router.include_router(users_router)

# from app.routers.api.auth import router as auth_router
# api_router.include_router(auth_router)
