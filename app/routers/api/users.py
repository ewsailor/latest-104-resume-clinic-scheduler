"""
使用者管理 API 路由模組。

提供使用者相關的 API 端點，包括建立、查詢、更新和刪除使用者。
"""

# ===== 第三方套件 =====
from fastapi import APIRouter, Depends, HTTPException, status  # 路由和錯誤處理

# ===== 本地模組 =====
from app.crud import schedule_crud  # CRUD 操作
from app.models.database import get_db  # 資料庫連接
from app.schemas import UserCreate  # 資料模型

# 建立路由器
router = APIRouter(prefix="/api", tags=["Users"])


# ===== API 端點 =====


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db=Depends(get_db)):
    """
    建立使用者。

    Args:
        user: 使用者資料
        db: 資料庫會話依賴注入

    Returns:
        dict: 建立成功的使用者資訊
    """
    try:
        # 使用 CRUD 層建立使用者
        new_user = schedule_crud.create_user(db, user)
        return {"message": "使用者建立成功", "user": new_user.to_dict()}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"建立使用者失敗: {str(e)}"
        )
