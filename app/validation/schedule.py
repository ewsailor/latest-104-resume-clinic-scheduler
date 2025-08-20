"""
時段驗證器模組。

提供時段相關的驗證器，如時段重疊檢查、營業時間驗證等。
"""

import logging
from datetime import date, time
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.schedule import Schedule
from app.schemas import ScheduleData
from app.utils.error_handler import BusinessLogicError, ErrorCode

from .base import BaseValidator, ValidationError
from .types import TypeValidators

logger = logging.getLogger(__name__)


class BusinessHoursValidator(BaseValidator[None]):
    """排除休息時間驗證器。

    排除休息時間 00:00-08:00，允許的時間為 08:00-24:00。
    """

    def __init__(self, rest_start: time = time(0, 0), rest_end: time = time(8, 0)):
        self.rest_start = rest_start  # 休息開始時間 (00:00)
        self.rest_end = rest_end  # 休息結束時間 (08:00)

    def validate(self, value: tuple[time, time], field_name: str = "時間範圍") -> None:
        start_time, end_time = value

        # 檢查開始時間是否在休息時間內
        if self._is_in_rest_period(start_time):
            raise ValidationError(
                f"開始時間 ({start_time}) 在休息時間內 ({self.rest_start}-{self.rest_end})",
                field_name=field_name,
                value=value,
            )

        # 檢查結束時間是否在休息時間內
        if self._is_in_rest_period(end_time):
            raise ValidationError(
                f"結束時間 ({end_time}) 在休息時間內 ({self.rest_start}-{self.rest_end})",
                field_name=field_name,
                value=value,
            )

    def _is_in_rest_period(self, check_time: time) -> bool:
        """檢查時間是否在休息時間內。"""
        # 休息時間跨越午夜 (例如: 22:00-06:00 或 00:00-08:00)
        if self.rest_start <= self.rest_end:
            # 正常情況：休息時間在同一天內
            return self.rest_start <= check_time < self.rest_end
        else:
            # 跨越午夜：休息時間跨越到隔天
            # 例如：22:00-06:00 表示 22:00-23:59 和 00:00-05:59
            return check_time >= self.rest_start or check_time < self.rest_end


class TimeRangeValidator(BaseValidator[None]):
    """時間範圍驗證器。"""

    def validate(self, value: tuple[time, time], field_name: str = "時間範圍") -> None:
        start_time, end_time = value

        if end_time <= start_time:
            raise ValidationError(
                f"結束時間 ({end_time}) 必須晚於開始時間 ({start_time})",
                field_name=field_name,
                value=value,
            )


class DateRangeValidator(BaseValidator[date]):
    """日期範圍驗證器。"""

    def __init__(self, max_months_ahead: int = 3):
        self.max_months_ahead = max_months_ahead

    def validate(self, value: date, field_name: str = "日期") -> date:
        today = date.today()

        # 不能是過去的日期
        if value < today:
            raise ValidationError(
                f"不能新增過去的日期: {value}", field_name=field_name, value=value
            )

        # 不能超過指定月份
        max_date = today.replace(month=today.month + self.max_months_ahead)
        if value > max_date:
            raise ValidationError(
                f"不能預約超過 {self.max_months_ahead} 個月的日期: {value}",
                field_name=field_name,
                value=value,
            )

        return value


class ScheduleOverlapValidator(BaseValidator[None]):
    """時段重疊驗證器。"""

    def __init__(self, db: Session):
        self.db = db

    def validate(
        self,
        value: tuple[int, date, time, time],
        field_name: str = "時段",
        exclude_id: int | None = None,
    ) -> None:
        """
        驗證時段是否重疊。

        Args:
            value: (giver_id, schedule_date, start_time, end_time)
            field_name: 欄位名稱
            exclude_id: 要排除的時段ID（用於更新時）
        """
        giver_id, schedule_date, start_time, end_time = value

        # 查詢同一天、同一 Giver 的時段
        query = self.db.query(Schedule).filter(
            and_(
                Schedule.giver_id == giver_id,
                Schedule.date == schedule_date,
                Schedule.deleted_at.is_(None),
            )
        )

        # 排除指定時段（用於更新時）
        if exclude_id is not None:
            query = query.filter(Schedule.id != exclude_id)

        existing_schedules = query.all()

        # 檢查重疊
        overlapping_schedules = []
        for existing_schedule in existing_schedules:
            if self._is_time_overlapping(
                start_time,
                end_time,
                existing_schedule.start_time,
                existing_schedule.end_time,
            ):
                overlapping_schedules.append(existing_schedule)

        if overlapping_schedules:
            from app.utils.error_handler import format_schedule_overlap_error_message

            error_msg = format_schedule_overlap_error_message(
                overlapping_schedules, schedule_date, "建立"
            )
            raise BusinessLogicError(error_msg, ErrorCode.SCHEDULE_OVERLAP)

    def _is_time_overlapping(
        self, start1: time, end1: time, start2: time, end2: time
    ) -> bool:
        """檢查兩個時間範圍是否重疊。"""
        return start1 < end2 and start2 < end1


class ScheduleDataValidator(BaseValidator[ScheduleData]):
    """時段資料驗證器。"""

    def __init__(
        self,
        db: Session,
        skip_date_validation: bool = False,
        max_note_length: int = 265,
    ):
        self.db = db
        self.skip_date_validation = skip_date_validation
        self.max_note_length = max_note_length

        # 初始化子驗證器
        self.business_hours_validator = BusinessHoursValidator()
        self.time_range_validator = TimeRangeValidator()
        self.date_range_validator = DateRangeValidator()
        self.schedule_overlap_validator = ScheduleOverlapValidator(db)

    def validate(
        self, value: ScheduleData, field_name: str = "時段資料"
    ) -> ScheduleData:
        logger.debug(f"開始驗證{field_name}: {value}")

        # 基本參數驗證
        TypeValidators.positive_int.validate(value.giver_id, "giver_id")

        if value.taker_id is not None:
            TypeValidators.positive_int.validate(value.taker_id, "taker_id")

        # 日期驗證（可選跳過）
        if not self.skip_date_validation:
            self.date_range_validator.validate(value.schedule_date, "時段日期")

        # 時間驗證
        self.time_range_validator.validate(
            (value.start_time, value.end_time), "時間範圍"
        )

        # 營業時間驗證
        self.business_hours_validator.validate(
            (value.start_time, value.end_time), "營業時間"
        )

        # 備註驗證
        if value.note is not None:
            TypeValidators.string_with_length(max_length=self.max_note_length).validate(
                value.note, "備註"
            )

        logger.debug(f"{field_name}驗證通過")
        return value


class ScheduleValidators:
    """時段驗證器集合。"""

    @staticmethod
    def business_hours(
        rest_start: time = time(0, 0), rest_end: time = time(8, 0)
    ) -> BusinessHoursValidator:
        return BusinessHoursValidator(rest_start, rest_end)

    @staticmethod
    def time_range() -> TimeRangeValidator:
        return TimeRangeValidator()

    @staticmethod
    def date_range(max_months_ahead: int = 3) -> DateRangeValidator:
        return DateRangeValidator(max_months_ahead)

    @staticmethod
    def schedule_overlap(db: Session) -> ScheduleOverlapValidator:
        return ScheduleOverlapValidator(db)

    @staticmethod
    def schedule_data(
        db: Session, skip_date_validation: bool = False, max_note_length: int = 265
    ) -> ScheduleDataValidator:
        return ScheduleDataValidator(db, skip_date_validation, max_note_length)
