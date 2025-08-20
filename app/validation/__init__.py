"""
驗證器模組。

提供各種驗證器，包括基本型別驗證、業務邏輯驗證等。
"""

from .base import BaseValidator, ValidationError
from .parameter import (  # 類別驗證器
    DateValidator,
    EnumValidator,
    ListValidator,
    OptionalPositiveIntValidator,
    OptionalStringValidator,
    ParameterValidator,
    PositiveIntValidator,
    StringValidator,
    TimeValidator,
    TypeValidators,
    validate_parameters,
)
from .schedule import (
    ScheduleValidators,
    validate_business_hours,
    validate_note,
    validate_schedule_data_basic,
    validate_schedule_data_complete,
    validate_schedule_date,
    validate_schedule_time_range,
    validate_time_format,
)
from .users import UserValidators

__all__ = [
    "BaseValidator",
    "ValidationError",
    "ParameterValidator",
    "validate_parameters",
    "TypeValidators",
    # 類別驗證器
    "PositiveIntValidator",
    "OptionalPositiveIntValidator",
    "StringValidator",
    "OptionalStringValidator",
    "DateValidator",
    "TimeValidator",
    "EnumValidator",
    "ListValidator",
    "UserValidators",
    "ScheduleValidators",
    "validate_schedule_date",
    "validate_time_format",
    "validate_schedule_time_range",
    "validate_business_hours",
    "validate_note",
    "validate_schedule_data_basic",
    "validate_schedule_data_complete",
]
