"""
使用者 CRUD 操作模組。

提供使用者相關的資料庫操作，包括建立、查詢、更新和刪除使用者。
"""

import logging  # 日誌記錄

# ===== 標準函式庫 =====
from typing import Optional  # 型別提示

# ===== 第三方套件 =====
from sqlalchemy.orm import Session  # 資料庫會話

# ===== 本地模組 =====
from app.models.user import User  # 使用者模型
from app.schemas import UserCreate  # 資料模型


class UserCRUD:
    """使用者 CRUD 操作類別。"""

    def __init__(self):
        """初始化 CRUD 實例，設定日誌器。"""
        self.logger = logging.getLogger(__name__)

    def create_user(self, db: Session, user: UserCreate) -> User:
        """
        建立使用者。

        Args:
            db: 資料庫會話
            user: 使用者資料

        Returns:
            User: 建立的使用者物件

        Raises:
            ValueError: 當 email 已存在時
        """
        self.logger.info(f"正在建立使用者: {user.name} ({user.email})")

        # 檢查 email 是否已存在
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            error_msg = f"電子信箱已被使用: {user.email}"
            self.logger.warning(error_msg)
            raise ValueError("此電子信箱已被使用")

        try:
            # 建立新使用者
            new_user = User(name=user.name, email=user.email)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            self.logger.info(f"成功建立使用者: ID={new_user.id}, 名稱={new_user.name}")
            return new_user
        except Exception as e:
            db.rollback()
            error_msg = f"建立使用者失敗: {str(e)}"
            self.logger.error(error_msg)
            raise

    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        """
        根據 ID 查詢使用者（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            user_id: 使用者 ID

        Returns:
            User | None: 找到的使用者物件，如果不存在或已軟刪除則返回 None
        """
        return (
            db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        )

    def get_user_by_email(self, db: Session, email: str) -> User | None:
        """
        根據 email 查詢使用者（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            email: 使用者 email

        Returns:
            User | None: 找到的使用者物件，如果不存在或已軟刪除則返回 None
        """
        return (
            db.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """
        查詢使用者列表（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            skip: 跳過的記錄數（用於分頁）
            limit: 限制返回的記錄數（用於分頁）

        Returns:
            list[User]: 使用者列表（排除已軟刪除的記錄）
        """
        return (
            db.query(User)
            .filter(User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_users_count(self, db: Session) -> int:
        """
        取得使用者總數（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話

        Returns:
            int: 使用者總數
        """
        return db.query(User).filter(User.deleted_at.is_(None)).count()


# 建立全域實例
user_crud = UserCRUD()
