# 104-resume-clinic-scheduler/tests/test_main.py

from httpx import AsyncClient
import pytest

# 從您的應用程式中導入 FastAPI 實例
from app.main import app

@pytest.mark.asyncio
async def test_read_root():
    """
    測試根路徑 (Health Check) 是否正常返回。
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running smoothly!"}

@pytest.mark.asyncio
async def test_create_user_success():
    """
    測試成功創建用戶的場景。
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/users/",
            json={"email": "newuser@example.com", "password": "securepassword123"}
        )
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert response_data["email"] == "newuser@example.com"
    assert response_data["is_active"] is True
    # 測試時不應返回密碼哈希

@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    """
    測試使用重複 email 創建用戶時是否返回 400 錯誤。
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 第一次創建
        await ac.post(
            "/users/",
            json={"email": "duplicate@example.com", "password": "password1"}
        )
        # 第二次嘗試使用相同 email
        response = await ac.post(
            "/users/",
            json={"email": "duplicate@example.com", "password": "password2"}
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


# 更多測試案例...
# async def test_get_givers():
# async def test_schedule_appointment():