"""
時段驗證器模組。

提供時段相關的驗證器，如時段重疊檢查、營業時間驗證等。
"""

from datetime import date, time
import logging

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.errors import (
    BusinessLogicError,
    ErrorCode,
    format_schedule_overlap_error_message,
)
from app.models.schedule import Schedule
from app.schemas import ScheduleData

from .base import BaseValidator, ValidationError
from .parameter import TypeValidators

# 暫時移除，避免循環導入
# from app.utils.schedule_validator import ScheduleValidator


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

        query = self.db.query(Schedule).filter(
            and_(
                Schedule.giver_id == giver_id,
                Schedule.date == schedule_date,
                Schedule.deleted_at.is_(None),
            )
        )

        if exclude_id is not None:
            query = query.filter(Schedule.id != exclude_id)

        existing_schedules = query.all()
        overlapping_schedules = []

        for existing_schedule in existing_schedules:
            if (
                start_time < existing_schedule.end_time
                and end_time > existing_schedule.start_time
            ):
                overlapping_schedules.append(existing_schedule)

        if overlapping_schedules:
            error_msg = format_schedule_overlap_error_message(
                overlapping_schedules, schedule_date, "建立"
            )
            raise BusinessLogicError(error_msg, ErrorCode.SCHEDULE_OVERLAP)


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
    """時段驗證器集合。

    提供類別驗證器的工廠方法，適合需要狀態管理的複雜驗證場景。
    """

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


# ============================================================================
# 純函數驗證器（Pure Function Validators）
# 這些函數提供簡單、可重用的驗證邏輯，無需狀態管理
# ============================================================================
def validate_schedule_date(schedule_date: date, max_months_ahead: int = 3) -> None:
    """
    驗證時段日期。

    Args:
        schedule_date: 要驗證的日期
        max_months_ahead: 最大可預約月數

    Raises:
        ValueError: 當日期無效時
    """
    today = date.today()

    # 不能新增以前的日期
    if schedule_date < today:
        raise ValueError(f"不能新增過去的日期: {schedule_date}")

    # 不能預約超過指定月數的日期
    max_date = today.replace(month=today.month + max_months_ahead)
    if schedule_date > max_date:
        raise ValueError(f"不能預約超過 {max_months_ahead} 個月的日期: {schedule_date}")


def validate_time_format(time_obj: time, field_name: str) -> None:
    """
    驗證時間格式。

    Args:
        time_obj: 要驗證的時間物件
        field_name: 欄位名稱

    Raises:
        ValueError: 當時間格式無效時
    """
    # 檢查小時範圍 (00-23)
    if not (0 <= time_obj.hour <= 23):
        raise ValueError(
            f"「{field_name}」時數「{time_obj.hour}」超過 23，請輸入00-23之間的數字"
        )

    # 檢查分鐘範圍 (00-59)
    if not (0 <= time_obj.minute <= 59):
        raise ValueError(
            f"「{field_name}」分數「{time_obj.minute}」超過 59，請輸入00-59之間的數字"
        )


def validate_schedule_time_range(start_time: time, end_time: time) -> None:
    """
    驗證時段時間範圍是否有效。

    Args:
        start_time: 開始時間
        end_time: 結束時間

    Raises:
        ValueError: 當時間範圍無效時
    """
    if end_time <= start_time:
        raise ValueError(f"結束時間 ({end_time}) 必須晚於開始時間 ({start_time})")


def validate_business_hours(
    start_time: time,
    end_time: time,
    rest_start: time = time(0, 0),
    rest_end: time = time(8, 0),
) -> None:
    """
    驗證營業時間（排除休息時間）。

    Args:
        start_time: 開始時間
        end_time: 結束時間
        rest_start: 休息開始時間
        rest_end: 休息結束時間

    Raises:
        ValueError: 當時間在休息時間內時
    """

    def is_in_rest_period(check_time: time) -> bool:
        """檢查時間是否在休息時間內。"""
        if rest_start <= rest_end:
            # 正常情況：休息時間在同一天內
            return rest_start <= check_time < rest_end
        else:
            # 跨越午夜：休息時間跨越到隔天
            return check_time >= rest_start or check_time < rest_end

    # 檢查開始時間是否在休息時間內
    if is_in_rest_period(start_time):
        raise ValueError(
            f"開始時間 ({start_time}) 在休息時間內 ({rest_start}-{rest_end})"
        )

    # 檢查結束時間是否在休息時間內
    if is_in_rest_period(end_time):
        raise ValueError(
            f"結束時間 ({end_time}) 在休息時間內 ({rest_start}-{rest_end})"
        )


def validate_note(note: str | None, max_length: int = 265) -> None:
    """
    驗證備註。

    Args:
        note: 要驗證的備註
        max_length: 最大長度

    Raises:
        ValueError: 當備註無效時
    """
    if note is not None and len(note) > max_length:
        raise ValueError(f"備註不能超過 {max_length} 個字符")


def validate_schedule_data_basic(schedule_data: ScheduleData) -> None:
    """
    驗證時段資料的基本參數。

    Args:
        schedule_data: 要驗證的時段資料

    Raises:
        ValueError: 當驗證失敗時
    """
    # 驗證 giver_id
    TypeValidators.positive_int.validate(schedule_data.giver_id, "giver_id")

    # 驗證 taker_id（如果提供）
    if schedule_data.taker_id is not None:
        TypeValidators.positive_int.validate(schedule_data.taker_id, "taker_id")


def validate_schedule_data_complete(
    schedule_data: ScheduleData,
    skip_date_validation: bool = False,
    max_months_ahead: int = 3,
    max_note_length: int = 265,
) -> None:
    """
    完整驗證時段資料。

    Args:
        schedule_data: 要驗證的時段資料
        skip_date_validation: 是否跳過日期驗證
        max_months_ahead: 最大可預約月數
        max_note_length: 備註最大長度

    Raises:
        ValueError: 當驗證失敗時
    """
    # 基本參數驗證
    validate_schedule_data_basic(schedule_data)

    # 日期驗證（可選跳過）
    if not skip_date_validation:
        validate_schedule_date(schedule_data.schedule_date, max_months_ahead)

    # 時間格式驗證
    validate_time_format(schedule_data.start_time, "start_time")
    validate_time_format(schedule_data.end_time, "end_time")

    # 時間範圍驗證
    validate_schedule_time_range(schedule_data.start_time, schedule_data.end_time)

    # 營業時間驗證
    validate_business_hours(schedule_data.start_time, schedule_data.end_time)

    # 備註驗證
    validate_note(schedule_data.note, max_note_length)
