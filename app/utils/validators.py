"""
參數驗證工具模組。

提供統一的參數驗證功能，減少重複的驗證程式碼。
"""

import logging
from datetime import date, time
from typing import Any, Callable, Type, TypeVar, Union

from app.utils.error_handler import ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ParameterValidator:
    """參數驗證器類別。"""

    @staticmethod
    def validate_required(
        value: Any,
        param_name: str,
        expected_type: Type[T],
        min_value: Union[int, float] | None = None,
        max_value: Union[int, float] | None = None,
    ) -> T:
        """
        驗證必需的參數。

        Args:
            value: 要驗證的值
            param_name: 參數名稱
            expected_type: 期望的型別
            min_value: 最小值（僅適用於數字型別）
            max_value: 最大值（僅適用於數字型別）

        Returns:
            驗證後的值

        Raises:
            ValidationError: 當驗證失敗時
        """
        # 型別驗證
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"無效的 {param_name} 類型: {type(value).__name__}, 期望 {expected_type.__name__}"
            )

        # 數值範圍驗證（僅適用於數字型別）
        if min_value is not None and isinstance(value, (int, float)):
            if value < min_value:  # type: ignore
                raise ValidationError(f"{param_name} 不能小於 {min_value}: {value}")

        if max_value is not None and isinstance(value, (int, float)):
            if value > max_value:  # type: ignore
                raise ValidationError(f"{param_name} 不能大於 {max_value}: {value}")

        return value

    @staticmethod
    def validate_optional(
        value: Any,
        param_name: str,
        expected_type: Type[T],
        min_value: Union[int, float] | None = None,
        max_value: Union[int, float] | None = None,
    ) -> T | None:
        """
        驗證可選的參數。

        Args:
            value: 要驗證的值
            param_name: 參數名稱
            expected_type: 期望的型別
            min_value: 最小值（僅適用於數字型別）
            max_value: 最大值（僅適用於數字型別）

        Returns:
            驗證後的值，如果為 None 則返回 None

        Raises:
            ValidationError: 當驗證失敗時
        """
        if value is None:
            return None

        return ParameterValidator.validate_required(
            value, param_name, expected_type, min_value, max_value
        )

    @staticmethod
    def validate_positive_int(value: Any, param_name: str) -> int:
        """
        驗證正整數。

        Args:
            value: 要驗證的值
            param_name: 參數名稱

        Returns:
            驗證後的正整數

        Raises:
            ValidationError: 當驗證失敗時
        """
        return ParameterValidator.validate_required(value, param_name, int, min_value=1)

    @staticmethod
    def validate_optional_positive_int(value: Any, param_name: str) -> int | None:
        """
        驗證可選的正整數。

        Args:
            value: 要驗證的值
            param_name: 參數名稱

        Returns:
            驗證後的正整數，如果為 None 則返回 None

        Raises:
            ValidationError: 當驗證失敗時
        """
        return ParameterValidator.validate_optional(value, param_name, int, min_value=1)

    @staticmethod
    def validate_string(value: Any, param_name: str, min_length: int = 0) -> str:
        """
        驗證字串。

        Args:
            value: 要驗證的值
            param_name: 參數名稱
            min_length: 最小長度

        Returns:
            驗證後的字串

        Raises:
            ValidationError: 當驗證失敗時
        """
        result = ParameterValidator.validate_required(value, param_name, str)

        if len(result) < min_length:
            raise ValidationError(
                f"{param_name} 長度不能小於 {min_length}: {len(result)}"
            )

        return result

    @staticmethod
    def validate_optional_string(
        value: Any, param_name: str, min_length: int = 0
    ) -> str | None:
        """
        驗證可選的字串。

        Args:
            value: 要驗證的值
            param_name: 參數名稱
            min_length: 最小長度

        Returns:
            驗證後的字串，如果為 None 則返回 None

        Raises:
            ValidationError: 當驗證失敗時
        """
        if value is None:
            return None

        return ParameterValidator.validate_string(value, param_name, min_length)

    @staticmethod
    def validate_list(
        value: Any, param_name: str, element_type: Type[T] | None = None
    ) -> list[T]:
        """
        驗證列表。

        Args:
            value: 要驗證的值
            param_name: 參數名稱
            element_type: 元素型別（可選）

        Returns:
            驗證後的列表

        Raises:
            ValidationError: 當驗證失敗時
        """
        result = ParameterValidator.validate_required(value, param_name, list)

        if element_type is not None:
            for i, element in enumerate(result):
                if not isinstance(element, element_type):
                    raise ValidationError(
                        f"{param_name}[{i}] 類型錯誤: {type(element).__name__}, 期望 {element_type.__name__}"
                    )

        return result

    @staticmethod
    def validate_optional_list(
        value: Any, param_name: str, element_type: Type[T] | None = None
    ) -> list[T] | None:
        """
        驗證可選的列表。

        Args:
            value: 要驗證的值
            param_name: 參數名稱
            element_type: 元素型別（可選）

        Returns:
            驗證後的列表，如果為 None 則返回 None

        Raises:
            ValidationError: 當驗證失敗時
        """
        if value is None:
            return None

        return ParameterValidator.validate_list(value, param_name, element_type)

    @staticmethod
    def validate_date(value: Any, param_name: str) -> date:
        """
        驗證日期。

        Args:
            value: 要驗證的值
            param_name: 參數名稱

        Returns:
            驗證後的日期

        Raises:
            ValidationError: 當驗證失敗時
        """
        return ParameterValidator.validate_required(value, param_name, date)

    @staticmethod
    def validate_time(value: Any, param_name: str) -> time:
        """
        驗證時間。

        Args:
            value: 要驗證的值
            param_name: 參數名稱

        Returns:
            驗證後的時間

        Raises:
            ValidationError: 當驗證失敗時
        """
        return ParameterValidator.validate_required(value, param_name, time)

    @staticmethod
    def validate_time_range(
        start_time: time,
        end_time: time,
        start_param: str = "start_time",
        end_param: str = "end_time",
    ) -> None:
        """
        驗證時間範圍。

        Args:
            start_time: 開始時間
            end_time: 結束時間
            start_param: 開始時間參數名稱
            end_param: 結束時間參數名稱

        Raises:
            ValidationError: 當時間範圍無效時
        """
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
        """
        驗證枚舉值。

        Args:
            value: 要驗證的值
            param_name: 參數名稱
            enum_class: 枚舉類別
            valid_values: 有效值列表（可選）

        Returns:
            驗證後的枚舉值

        Raises:
            ValidationError: 當驗證失敗時
        """
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
    """
    參數驗證裝飾器。

    用於驗證函數參數的有效性。

    Args:
        **validations: 驗證規則字典

    Returns:
        裝飾器函數

    Example:
        @validate_parameters(
            user_id=dict(type=int, min_value=1),
            name=dict(type=str, min_length=1),
            age=dict(type=int, min_value=0, optional=True)
        )
        def create_user(user_id: int, name: str, age: int | None = None):
            pass
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 取得函數參數名稱
            import inspect

            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            # 跳過 self 參數（如果是實例方法）
            # 檢查第一個參數是否為 self（實例方法）
            start_idx = 0
            if args and len(param_names) > 0:
                # 如果第一個參數名稱是 'self'，則跳過
                if param_names[0] == 'self':
                    start_idx = 1

            # 建立參數字典
            params = {}
            for i, param_name in enumerate(param_names[start_idx:], start=start_idx):
                if i < len(args):
                    params[param_name] = args[i]

            # 合併關鍵字參數
            params.update(kwargs)

            # 執行驗證
            for param_name, validation_rules in validations.items():
                if param_name in params:
                    value = params[param_name]

                    # 取得驗證規則
                    expected_type = validation_rules.get('type')
                    min_value = validation_rules.get('min_value')
                    max_value = validation_rules.get('max_value')
                    min_length = validation_rules.get('min_length', 0)
                    optional = validation_rules.get('optional', False)
                    enum_class = validation_rules.get('enum_class')
                    valid_values = validation_rules.get('valid_values')

                    # 執行驗證
                    if optional:
                        if expected_type == int and min_value == 1:
                            ParameterValidator.validate_optional_positive_int(
                                value, param_name
                            )
                        elif expected_type == str:
                            ParameterValidator.validate_optional_string(
                                value, param_name, min_length
                            )
                        elif expected_type == list:
                            element_type = validation_rules.get('element_type')
                            ParameterValidator.validate_optional_list(
                                value, param_name, element_type
                            )
                        else:
                            ParameterValidator.validate_optional(
                                value, param_name, expected_type, min_value, max_value
                            )
                    else:
                        if expected_type == int and min_value == 1:
                            ParameterValidator.validate_positive_int(value, param_name)
                        elif expected_type == str:
                            ParameterValidator.validate_string(
                                value, param_name, min_length
                            )
                        elif expected_type == list:
                            element_type = validation_rules.get('element_type')
                            ParameterValidator.validate_list(
                                value, param_name, element_type
                            )
                        elif expected_type == date:
                            ParameterValidator.validate_date(value, param_name)
                        elif expected_type == time:
                            ParameterValidator.validate_time(value, param_name)
                        elif enum_class is not None:
                            ParameterValidator.validate_enum_value(
                                value, param_name, enum_class, valid_values
                            )
                        else:
                            ParameterValidator.validate_required(
                                value, param_name, expected_type, min_value, max_value
                            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


# 建立全域驗證器實例
validator = ParameterValidator()
