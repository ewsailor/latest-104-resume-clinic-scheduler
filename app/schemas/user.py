"""
使用者相關的 Pydantic 資料模型。

定義使用者管理相關的請求和回應模型。
"""

from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """建立使用者的請求模型"""

    name: str = Field(..., description="使用者姓名")
    email: str = Field(..., description="電子信箱")


class UserResponse(BaseModel):
    """使用者回應模型"""

    id: int
    name: str
    email: str
    role: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
