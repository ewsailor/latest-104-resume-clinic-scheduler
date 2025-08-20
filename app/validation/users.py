"""
用戶驗證器模組。

提供用戶相關的驗證器，如用戶存在性驗證等。
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.error_handler import NotFoundError

from .base import BaseValidator


class UserExistsValidator(BaseValidator[User]):
    """使用者存在驗證器。"""

    def __init__(self, db: Session):
        self.db = db

    def validate(self, value: int, field_name: str = "使用者ID") -> User:
        user = self.db.query(User).filter(User.id == value).first()
        if not user:
            raise NotFoundError(field_name, value)
        return user


class UserValidators:
    """用戶驗證器集合。"""

    @staticmethod
    def user_exists(db: Session) -> UserExistsValidator:
        return UserExistsValidator(db)
