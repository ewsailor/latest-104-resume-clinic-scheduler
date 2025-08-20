"""
基礎驗證器模組。

定義驗證器的基礎介面和通用驗證錯誤。
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar('T')


class ValidationError(Exception):
    """驗證錯誤例外。"""

    def __init__(self, message: str, field_name: str | None = None, value: Any = None):
        self.message = message
        self.field_name = field_name
        self.value = value
        super().__init__(message)


class BaseValidator(ABC, Generic[T]):
    """基礎驗證器抽象類別。"""

    @abstractmethod
    def validate(self, value: Any, field_name: str = "value") -> T:
        """
        驗證值。

        Args:
            value: 要驗證的值
            field_name: 欄位名稱（用於錯誤訊息）

        Returns:
            驗證後的值

        Raises:
            ValidationError: 當驗證失敗時
        """
        pass

    def __call__(self, value: Any, field_name: str = "value") -> T:
        """讓驗證器可以像函式一樣被調用。"""
        return self.validate(value, field_name)
