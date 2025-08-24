"""
使用者管理 API 路由模組。

提供使用者相關的 API 端點，包括建立、查詢、更新和刪除使用者。
"""

from typing import Any

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, Query, status  # 路由和錯誤處理
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.crud import user_crud  # CRUD 操作
from app.errors import (
    APIError,
    create_http_exception_from_api_error,
)
from app.models.database import get_db  # 資料庫連接
from app.schemas import UserCreate  # 資料模型
from app.services import user_service  # SERVICE 層

# 建立路由器
router = APIRouter(prefix="/api/v1", tags=["Users"])


# ===== API 端點 =====


@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1, description="頁碼"),
    per_page: int = Query(10, ge=1, le=100, description="每頁數量"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    取得使用者列表。

    Args:
        page: 頁碼（從 1 開始）
        per_page: 每頁數量
        db: 資料庫會話依賴注入

    Returns:
        dict: 包含使用者列表和分頁資訊的回應
    """
    try:
        # 使用 SERVICE 層取得使用者列表
        users = user_service.get_users(db, skip=(page - 1) * per_page, limit=per_page)
        total = user_service.get_users_count(db)

        return {
            "results": [user.to_dict() for user in users],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    except APIError as e:
        # 處理自定義 API 錯誤
        raise create_http_exception_from_api_error(e)
    except Exception as e:
        # 處理其他未預期的錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得使用者列表失敗: {str(e)}",
        )


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    建立使用者。

    Args:
        user: 使用者資料
        db: 資料庫會話依賴注入

    Returns:
        dict: 建立成功的使用者資訊
    """
    try:
        # 使用 SERVICE 層建立使用者
        new_user = user_service.create_user(db, user)
        return {"message": "使用者建立成功", "user": new_user.to_dict()}

    except APIError as e:
        # 處理自定義 API 錯誤
        raise create_http_exception_from_api_error(e)
    except ValueError as e:
        # 處理驗證錯誤
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        # 處理其他未預期的錯誤
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立使用者時發生內部錯誤: {str(e)}",
        )
