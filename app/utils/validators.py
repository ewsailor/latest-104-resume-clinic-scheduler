"""
參數驗證工具模組。

提供統一的參數驗證功能，減少重複的驗證程式碼。
"""

import logging
from datetime import date, time
from typing import Any, Callable, Type, TypeVar

from app.utils.error_handler import ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ParameterValidator:
    """參數驗證器類別。"""

    @staticmethod
    def validate_positive_int(value: Any, param_name: str) -> int:
        """驗證正整數。"""
        if not isinstance(value, int) or value <= 0:
            raise ValidationError(f"無效的 {param_name}: {value}，必須為正整數")
        return value

    @staticmethod
    def validate_optional_positive_int(value: Any, param_name: str) -> int | None:
        """驗證可選的正整數。"""
        if value is None:
            return None
        return ParameterValidator.validate_positive_int(value, param_name)

    @staticmethod
    def validate_string(value: Any, param_name: str, min_length: int = 0) -> str:
        """驗證字串。"""
        if not isinstance(value, str):
            raise ValidationError(
                f"無效的 {param_name} 類型: {type(value).__name__}, 期望 str"
            )
        if len(value) < min_length:
            raise ValidationError(
                f"{param_name} 長度不能小於 {min_length}: {len(value)}"
            )
        return value

    @staticmethod
    def validate_optional_string(
        value: Any, param_name: str, min_length: int = 0
    ) -> str | None:
        """驗證可選的字串。"""
        if value is None:
            return None
        return ParameterValidator.validate_string(value, param_name, min_length)

    @staticmethod
    def validate_list(
        value: Any, param_name: str, element_type: Type[T] | None = None
    ) -> list[T]:
        """驗證列表。"""
        if not isinstance(value, list):
            raise ValidationError(
                f"無效的 {param_name} 類型: {type(value).__name__}, 期望 list"
            )

        if element_type is not None:
            for i, element in enumerate(value):
                if not isinstance(element, element_type):
                    raise ValidationError(
                        f"{param_name}[{i}] 類型錯誤: {type(element).__name__}, 期望 {element_type.__name__}"
                    )
        return value

    @staticmethod
    def validate_date(value: Any, param_name: str) -> date:
        """驗證日期。"""
        if not isinstance(value, date):
            raise ValidationError(
                f"無效的 {param_name} 類型: {type(value).__name__}, 期望 date"
            )
        return value

    @staticmethod
    def validate_time(value: Any, param_name: str) -> time:
        """驗證時間。"""
        if not isinstance(value, time):
            raise ValidationError(
                f"無效的 {param_name} 類型: {type(value).__name__}, 期望 time"
            )
        return value

    @staticmethod
    def validate_time_range(
        start_time: time,
        end_time: time,
        start_param: str = "start_time",
        end_param: str = "end_time",
    ) -> None:
        """驗證時間範圍。"""
        if start_time >= end_time:
            raise ValidationError(
                f"{start_param} 必須早於 {end_param}: {start_time} >= {end_time}"
            )

    @staticmethod
    def validate_enum_value(
        value: Any,
        param_name: str,
        enum_class: Type,
        valid_values: list[str] | None = None,
    ) -> str:
        """驗證枚舉值。"""
        result = ParameterValidator.validate_string(value, param_name)
        try:
            enum_class(result)
        except ValueError:
            if valid_values is None:
                valid_values = [e.value for e in enum_class]
            raise ValidationError(
                f"無效的 {param_name} 值: {result}，有效值為: {valid_values}"
            )
        return result


def validate_parameters(**validations: dict[str, Any]) -> Callable:
    """參數驗證裝飾器。"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            import inspect

            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            # 跳過 self 參數
            start_idx = 0
            if args and len(param_names) > 0 and param_names[0] == 'self':
                start_idx = 1

            # 建立參數字典
            params = {}
            for i, param_name in enumerate(param_names[start_idx:], start=start_idx):
                if i < len(args):
                    params[param_name] = args[i]
            params.update(kwargs)

            # 執行驗證
            for param_name, validation_rules in validations.items():
                if param_name in params:
                    value = params[param_name]
                    expected_type = validation_rules.get('type')
                    min_value = validation_rules.get('min_value')
                    min_length = validation_rules.get('min_length', 0)
                    optional = validation_rules.get('optional', False)
                    enum_class = validation_rules.get('enum_class')

                    if optional:
                        if expected_type == int and min_value == 1:
                            ParameterValidator.validate_optional_positive_int(
                                value, param_name
                            )
                        elif expected_type == str:
                            ParameterValidator.validate_optional_string(
                                value, param_name, min_length
                            )
                    else:
                        if expected_type == int and min_value == 1:
                            ParameterValidator.validate_positive_int(value, param_name)
                        elif expected_type == str:
                            ParameterValidator.validate_string(
                                value, param_name, min_length
                            )
                        elif expected_type == date:
                            ParameterValidator.validate_date(value, param_name)
                        elif expected_type == time:
                            ParameterValidator.validate_time(value, param_name)
                        elif enum_class is not None:
                            ParameterValidator.validate_enum_value(
                                value, param_name, enum_class
                            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


# 建立全域驗證器實例
validator = ParameterValidator()
