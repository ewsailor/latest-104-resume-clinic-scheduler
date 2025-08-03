"""
主要路由測試模組。

測試首頁、健康檢查等基礎路由功能。
"""

# ===== 標準函式庫 =====
import pytest  # 測試框架

# ===== 第三方套件 =====
from httpx import AsyncClient  # 非同步 HTTP 客戶端

# ===== 本地模組 =====
from app.main import app  # FastAPI 應用程式


@pytest.mark.asyncio
async def test_read_root():
    """
    測試首頁路由是否正常返回 HTML 頁面。
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    # 根路徑返回 HTML 頁面，不是 JSON
    assert "text/html" in response.headers.get("content-type", "")


# 更多測試案例...
# async def test_get_givers():
# async def test_schedule_appointment():
# async def test_create_user_success():
# async def test_create_user_duplicate_email():
