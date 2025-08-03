# """
# 時段相關的資料驗證 schema。
# """

# # ===== 標準函式庫 =====
# from datetime import date as date_type, time as time_type  # 日期和時間處理
# from typing import Optional, List  # 可選型別和列表型別

# # ===== 第三方套件 =====
# from pydantic import BaseModel, Field, field_validator  # 資料驗證


# class ScheduleCreate(BaseModel):
#     """
#     建立行程的請求資料模型。
#     """
#     date: date_type = Field(..., description="日期 (YYYY-MM-DD)")
#     start_time: time_type = Field(..., description="開始時間 (HH:MM)")
#     end_time: time_type = Field(..., description="結束時間 (HH:MM)")
#     role: str = Field("GIVER", description="角色 (GIVER/TAKER)")
#     giver_id: int = Field(..., description="Giver ID")
#     taker_id: Optional[int] = Field(None, description="Taker ID")
#     status: str = Field("AVAILABLE", description="狀態")
#     note: Optional[str] = Field(None, description="備註")

#     @field_validator('end_time')
#     @classmethod
#     def validate_end_time(cls, v, info):
#         """驗證結束時間必須晚於開始時間。"""
#         if 'start_time' in info.data and v <= info.data['start_time']:
#             raise ValueError('結束時間必須晚於開始時間')
#         return v

#     @field_validator('date')
#     @classmethod
#     def validate_date(cls, v):
#         """驗證日期不能是過去日期。"""
#         from datetime import date as date_today
#         if v < date_today.today():
#             raise ValueError('日期不能是過去日期')
#         return v


# class ScheduleResponse(BaseModel):
#     """
#     行程回應資料模型。
#     """
#     id: int = Field(..., description="行程 ID")
#     role: str = Field(..., description="角色")
#     status: str = Field(..., description="狀態")
#     giver_id: int = Field(..., description="Giver ID")
#     taker_id: Optional[int] = Field(None, description="Taker ID")
#     date: date_type = Field(..., description="日期")
#     start_time: time_type = Field(..., description="開始時間")
#     end_time: time_type = Field(..., description="結束時間")
#     note: Optional[str] = Field(None, description="備註")
#     created_at: str = Field(..., description="建立時間")

#     model_config = {
#         "from_attributes": True  # 允許從 ORM 物件建立
#     }


# class ScheduleListResponse(BaseModel):
#     """
#     行程列表回應資料模型。
#     """
#     schedules: List[ScheduleResponse] = Field(..., description="行程列表")
#     total: int = Field(..., description="總數量")
