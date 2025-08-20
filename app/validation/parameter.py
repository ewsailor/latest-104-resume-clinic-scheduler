"""
參數驗證工具模組。

提供統一的參數驗證功能，減少重複的驗證程式碼。
這些是純邏輯驗證，不包含業務邏輯。
"""

import inspect
import logging
from datetime import date, datetime, time
from enum import Enum
from typing import Any, Callable, List, Optional, Type, TypeVar

from app.errors import ValidationError as APIValidationError

from .base import BaseValidator, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PositiveIntValidator(BaseValidator[int]):
    """正整數驗證器。"""

    def validate(self, value: Any, field_name: str = "value") -> int:
        if not isinstance(value, int) or value <= 0:
            raise ValidationError(
                f"無效的 {field_name}: {value}，必須為正整數",
                field_name=field_name,
                value=value,
            )
        return value


class OptionalPositiveIntValidator(BaseValidator[Optional[int]]):
    """可選正整數驗證器。"""

    def __init__(self):
        self._positive_int_validator = PositiveIntValidator()

    def validate(self, value: Any, field_name: str = "value") -> Optional[int]:
        if value is None:
            return None
        return self._positive_int_validator.validate(value, field_name)


class StringValidator(BaseValidator[str]):
    """字串驗證器。"""

    def __init__(self, min_length: int = 0, max_length: Optional[int] = None):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any, field_name: str = "value") -> str:
        if not isinstance(value, str):
            raise ValidationError(
                f"無效的 {field_name} 類型: {type(value).__name__}, 期望 str",
                field_name=field_name,
                value=value,
            )

        if len(value) < self.min_length:
            raise ValidationError(
                f"{field_name} 長度不能小於 {self.min_length}: {len(value)}",
                field_name=field_name,
                value=value,
            )

        if self.max_length and len(value) > self.max_length:
            raise ValidationError(
                f"{field_name} 長度不能大於 {self.max_length}: {len(value)}",
                field_name=field_name,
                value=value,
            )

        return value


class OptionalStringValidator(BaseValidator[Optional[str]]):
    """可選字串驗證器。"""

    def __init__(self, min_length: int = 0, max_length: Optional[int] = None):
        self._string_validator = StringValidator(min_length, max_length)

    def validate(self, value: Any, field_name: str = "value") -> Optional[str]:
        if value is None:
            return None
        return self._string_validator.validate(value, field_name)


class DateValidator(BaseValidator[date]):
    """日期驗證器。"""

    def validate(self, value: Any, field_name: str = "value") -> date:
        if isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                pass

        raise ValidationError(
            f"無效的 {field_name}: {value}，必須為 date 類型或 'YYYY-MM-DD' 格式字串",
            field_name=field_name,
            value=value,
        )


class TimeValidator(BaseValidator[time]):
    """時間驗證器。"""

    def validate(self, value: Any, field_name: str = "value") -> time:
        if isinstance(value, time):
            return value

        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%H:%M:%S").time()
            except ValueError:
                try:
                    return datetime.strptime(value, "%H:%M").time()
                except ValueError:
                    pass

        raise ValidationError(
            f"無效的 {field_name}: {value}，必須為 time 類型或 'HH:MM' 格式字串",
            field_name=field_name,
            value=value,
        )


class EnumValidator(BaseValidator[T]):
    """枚舉驗證器。"""

    def __init__(self, enum_class: Type[T]):
        self.enum_class = enum_class

    def validate(self, value: Any, field_name: str = "value") -> T:
        if isinstance(value, self.enum_class):
            return value

        if isinstance(value, str):
            try:
                # 嘗試將字串轉換為枚舉值
                return self.enum_class(value)  # type: ignore
            except (ValueError, TypeError):
                pass

        # 簡化的錯誤訊息，避免複雜的枚舉值獲取
        raise ValidationError(f"無效的 {field_name}: {value}，必須為有效的枚舉值")


class ListValidator(BaseValidator[List[T]]):
    """列表驗證器。"""

    def __init__(self, element_validator: BaseValidator[T], min_length: int = 0):
        self.element_validator = element_validator
        self.min_length = min_length

    def validate(self, value: Any, field_name: str = "value") -> List[T]:
        if not isinstance(value, list):
            raise ValidationError(
                f"無效的 {field_name} 類型: {type(value).__name__}, 期望 list",
                field_name=field_name,
                value=value,
            )

        if len(value) < self.min_length:
            raise ValidationError(
                f"{field_name} 長度不能小於 {self.min_length}: {len(value)}",
                field_name=field_name,
                value=value,
            )

        validated_list = []
        for i, item in enumerate(value):
            try:
                validated_item = self.element_validator.validate(
                    item, f"{field_name}[{i}]"
                )
                validated_list.append(validated_item)
            except ValidationError as e:
                # 重新包裝錯誤，包含列表索引信息
                raise ValidationError(
                    f"{field_name}[{i}] 驗證失敗: {e.message}",
                    field_name=field_name,
                    value=value,
                )

        return validated_list


class TypeValidators:
    """型別驗證器集合，提供便捷的訪問方式。"""

    # 基本型別
    positive_int = PositiveIntValidator()
    optional_positive_int = OptionalPositiveIntValidator()

    # 字串相關
    string = StringValidator()
    optional_string = OptionalStringValidator()

    @staticmethod
    def string_with_length(
        min_length: int = 0, max_length: Optional[int] = None
    ) -> StringValidator:
        return StringValidator(min_length, max_length)

    @staticmethod
    def optional_string_with_length(
        min_length: int = 0, max_length: Optional[int] = None
    ) -> OptionalStringValidator:
        return OptionalStringValidator(min_length, max_length)

    # 日期時間
    date = DateValidator()
    time = TimeValidator()

    # 枚舉
    @staticmethod
    def enum(enum_class: Type[T]) -> EnumValidator[T]:
        return EnumValidator(enum_class)  # type: ignore

    # 列表
    @staticmethod
    def list_of(
        element_validator: BaseValidator[T], min_length: int = 0
    ) -> ListValidator[T]:
        return ListValidator(element_validator, min_length)


def validate_parameters(**validations: dict[str, Any]) -> Callable:
    """參數驗證裝飾器。"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 使用 inspect 取得函數簽名
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # 驗證每個參數
            for param_name, validation_config in validations.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    _validate_parameter(value, param_name, validation_config)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _validate_parameter(value: Any, param_name: str, config: dict[str, Any]) -> None:
    """驗證單一參數。"""
    param_type = config.get("type")
    min_value = config.get("min_value")
    max_value = config.get("max_value")
    min_length = config.get("min_length")
    max_length = config.get("max_length")

    # 型別驗證
    if param_type is not None and not isinstance(value, param_type):
        raise APIValidationError(
            f"參數 {param_name} 型別錯誤，期望 {param_type.__name__}，實際 {type(value).__name__}"
        )

    # 數值範圍驗證
    if isinstance(value, (int, float)):
        if min_value is not None and value < min_value:
            raise APIValidationError(
                f"參數 {param_name} 值 {value} 小於最小值 {min_value}"
            )
        if max_value is not None and value > max_value:
            raise APIValidationError(
                f"參數 {param_name} 值 {value} 大於最大值 {max_value}"
            )

    # 字串長度驗證
    if isinstance(value, str):
        if min_length is not None and len(value) < min_length:
            raise APIValidationError(
                f"參數 {param_name} 長度 {len(value)} 小於最小長度 {min_length}"
            )
        if max_length is not None and len(value) > max_length:
            raise APIValidationError(
                f"參數 {param_name} 長度 {len(value)} 大於最大長度 {max_length}"
            )
