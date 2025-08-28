"""使用者相關的 Pydantic 資料模型。

定義使用者管理相關的請求和回應模型。
"""

# ===== 標準函式庫 =====
from datetime import datetime

# ===== 第三方套件 =====
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """建立使用者的請求模型。"""

    name: str = Field(
        ..., description="使用者姓名", min_length=1, max_length=50, example="張三"
    )
    email: EmailStr = Field(..., description="電子信箱", example="zhangsan@example.com")


class UserResponse(BaseModel):
    """使用者回應模型。"""

    id: int = Field(..., description="使用者 ID", gt=0, example=1)
    name: str = Field(..., description="使用者姓名", example="張三")
    email: EmailStr = Field(..., description="電子信箱", example="zhangsan@example.com")
    created_at: datetime = Field(
        ..., description="建立時間（本地時間）", example=datetime(2025, 9, 15, 9, 0)
    )
    updated_at: datetime = Field(
        ..., description="更新時間（本地時間）", example=datetime(2025, 9, 15, 9, 0)
    )
    deleted_at: datetime | None = Field(
        None, description="軟刪除標記（本地時間）", example=None
    )
