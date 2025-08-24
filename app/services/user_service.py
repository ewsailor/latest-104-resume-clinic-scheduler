"""
使用者服務層模組。

提供使用者相關的業務邏輯處理，包括使用者管理、驗證等。
"""

import logging

from sqlalchemy.orm import Session

from app.crud.user import UserCRUD
from app.models.user import User
from app.schemas import UserCreate
from app.utils.decorators import (
    handle_crud_errors_with_rollback,
    log_operation,
)


class UserService:
    """使用者服務類別。"""

    def __init__(self):
        """初始化服務實例。"""
        self.logger = logging.getLogger(__name__)
        self.user_crud = UserCRUD()

    @handle_crud_errors_with_rollback("建立使用者")
    @log_operation("建立使用者")
    def create_user(
        self,
        db: Session,
        user_data: UserCreate,
    ) -> User:
        """
        建立使用者（業務邏輯層）。

        Args:
            db: 資料庫會話
            user_data: 使用者資料

        Returns:
            User: 建立成功的使用者物件

        Raises:
            ValueError: 當 email 已存在時
        """
        # 記錄建立操作
        self.logger.info(f"正在建立使用者: {user_data.name} ({user_data.email})")

        # 使用 CRUD 層建立使用者
        user = self.user_crud.create_user(db, user_data)

        self.logger.info(f"使用者建立成功: ID={user.id}, 名稱={user.name}")
        return user

    @handle_crud_errors_with_rollback("查詢使用者列表")
    @log_operation("查詢使用者列表")
    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        查詢使用者列表（業務邏輯層）。

        Args:
            db: 資料庫會話
            skip: 跳過的記錄數（用於分頁）
            limit: 限制返回的記錄數（用於分頁）

        Returns:
            list[User]: 使用者列表

        Raises:
            DatabaseError: 當資料庫操作失敗時
        """
        # 記錄查詢操作
        self.logger.info(f"查詢使用者列表: skip={skip}, limit={limit}")

        # 使用 CRUD 層查詢使用者
        users = self.user_crud.get_users(db, skip, limit)

        self.logger.info(f"查詢完成，找到 {len(users)} 個使用者")
        return users

    @handle_crud_errors_with_rollback("查詢單一使用者")
    @log_operation("查詢單一使用者")
    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        """
        根據 ID 查詢使用者（業務邏輯層）。

        Args:
            db: 資料庫會話
            user_id: 使用者 ID

        Returns:
            User | None: 找到的使用者物件，如果不存在則返回 None

        Raises:
            DatabaseError: 當資料庫操作失敗時
        """
        # 記錄查詢操作
        self.logger.info(f"查詢使用者: user_id={user_id}")

        # 使用 CRUD 層查詢使用者
        user = self.user_crud.get_user_by_id(db, user_id)

        if user:
            self.logger.info(f"使用者 {user_id} 查詢成功")
        else:
            self.logger.info(f"使用者 {user_id} 不存在")

        return user

    @handle_crud_errors_with_rollback("查詢使用者數量")
    @log_operation("查詢使用者數量")
    def get_users_count(self, db: Session) -> int:
        """
        查詢使用者總數（業務邏輯層）。

        Args:
            db: 資料庫會話

        Returns:
            int: 使用者總數

        Raises:
            DatabaseError: 當資料庫操作失敗時
        """
        # 記錄查詢操作
        self.logger.info("查詢使用者總數")

        # 使用 CRUD 層查詢使用者數量
        count = self.user_crud.get_users_count(db)

        self.logger.info(f"使用者總數: {count}")
        return count


# 建立服務實例
user_service = UserService()
