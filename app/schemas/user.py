"""
使用者相關的 Pydantic 資料模型。

定義使用者管理相關的請求和回應模型。
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """建立使用者的請求模型"""

    name: str = Field(..., description="使用者姓名")
    email: EmailStr = Field(..., description="電子信箱")


class UserResponse(BaseModel):
    """使用者回應模型"""

    id: int
    name: str
    email: EmailStr
    created_at: datetime = Field(description="建立時間（本地時間）")
    updated_at: datetime = Field(description="更新時間（本地時間）")
    deleted_at: datetime | None = Field(None, description="軟刪除標記（本地時間）")
