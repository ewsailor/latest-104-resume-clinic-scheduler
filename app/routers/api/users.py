"""使用者管理 API 路由模組。

提供使用者相關的 API 端點，包括建立、查詢、更新和刪除使用者。
"""

# ===== 標準函式庫 =====
from typing import Any

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.decorators import handle_api_errors

# ===== 本地模組 =====
from app.models.database import get_db
from app.schemas import UserCreate, UserResponse
from app.services import user_service

router = APIRouter(prefix="/api/v1", tags=["Users"])


# ===== API 端點 =====
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@handle_api_errors()
async def create_user(
    user: UserCreate, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """建立使用者。"""
    new_user = user_service.create_user(db, user)
    return {"message": "使用者建立成功", "user": new_user.to_dict()}


@router.get(
    "/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
@handle_api_errors()
async def get_users(
    page: int = Query(1, ge=1, description="頁碼"),
    per_page: int = Query(10, ge=1, le=100, description="每頁數量"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """取得使用者列表。"""
    users = user_service.get_users(db, skip=(page - 1) * per_page, limit=per_page)
    total = user_service.get_users_count(db)

    return {
        "results": [user.to_dict() for user in users],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }
