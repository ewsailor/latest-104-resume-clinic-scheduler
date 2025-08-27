"""使用者服務層模組。

提供使用者相關的業務邏輯處理，包括使用者管理、驗證等。
"""

# ===== 標準函式庫 =====
import logging

# ===== 第三方套件 =====
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.crud import user_crud
from app.decorators import (
    handle_service_errors,
    log_operation,
)
from app.models.user import User
from app.schemas import UserCreate


class UserService:
    """使用者服務類別。"""

    def __init__(self) -> None:
        """初始化服務實例。"""
        self.logger = logging.getLogger(__name__)

    @handle_service_errors("建立使用者")
    @log_operation("建立使用者")
    def create_user(
        self,
        db: Session,
        user_data: UserCreate,
    ) -> User:
        """建立使用者。"""
        # 業務邏輯：檢查 email 是否已存在
        existing_user = user_crud.get_user_by_email(db, user_data.email)
        if existing_user:
            error_msg = f"電子信箱已被使用: {user_data.email}"
            self.logger.warning(error_msg)
            raise ValueError("此電子信箱已被使用")

        user = user_crud.create_user(db, user_data)

        self.logger.info(f"使用者建立成功: ID={user.id}, 名稱={user.name}")
        return user

    @handle_service_errors("查詢使用者列表")
    @log_operation("查詢使用者列表")
    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """查詢使用者列表。"""
        users = user_crud.get_users(db, skip, limit)

        self.logger.info(f"查詢完成，找到 {len(users)} 個使用者")
        return users

    @handle_service_errors("查詢單一使用者")
    @log_operation("查詢單一使用者")
    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        """根據 ID 查詢使用者。"""
        user = user_crud.get_user_by_id(db, user_id)

        if user:
            self.logger.info(f"使用者 {user_id} 查詢成功")
        else:
            self.logger.info(f"使用者 {user_id} 不存在")

        return user

    @handle_service_errors("查詢使用者數量")
    @log_operation("查詢使用者數量")
    def get_users_count(self, db: Session) -> int:
        """查詢使用者總數。"""
        count = user_crud.get_users_count(db)

        self.logger.info(f"使用者總數: {count}")
        return count


# 建立服務實例
user_service = UserService()
