# 104-resume-clinic-scheduler/tests/test_main.py

from httpx import AsyncClient
import pytest

# 從您的應用程式中導入 FastAPI 實例
from app.main import app

@pytest.mark.asyncio
async def test_read_root():
    """
    測試根路徑是否正常返回 HTML 頁面。
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    # 根路徑返回 HTML 頁面，不是 JSON
    assert "text/html" in response.headers.get("content-type", "")

@pytest.mark.asyncio
async def test_health_check():
    """
    測試健康檢查端點是否正常返回。
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data

# 更多測試案例...
# async def test_get_givers():
# async def test_schedule_appointment():
# async def test_create_user_success():
# async def test_create_user_duplicate_email():