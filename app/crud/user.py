"""使用者 CRUD 操作模組。

提供使用者相關的資料庫操作，包括建立、查詢、更新和刪除使用者。
"""

# ===== 標準函式庫 =====
import logging

# ===== 第三方套件 =====
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.models.user import User
from app.schemas import UserCreate


class UserCRUD:
    """使用者 CRUD 操作類別。"""

    def __init__(self) -> None:
        """初始化 CRUD 實例，設定日誌器。"""
        self.logger = logging.getLogger(__name__)

    def create_user(
        self,
        db: Session,
        user: UserCreate,
    ) -> User:
        """建立使用者。"""
        self.logger.info(f"正在建立使用者: {user.name} ({user.email})")

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

    def get_user_by_id(
        self,
        db: Session,
        user_id: int,
    ) -> User | None:
        """根據 ID 查詢使用者，排除已軟刪除的記錄。"""
        return (
            db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        )

    def get_user_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:
        """根據 email 查詢使用者（排除已軟刪除的記錄）。"""
        return (
            db.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )

    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """查詢使用者列表（排除已軟刪除的記錄）。"""
        return (
            db.query(User)
            .filter(User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_users_count(self, db: Session) -> int:
        """取得使用者總數（排除已軟刪除的記錄）。"""
        return db.query(User).filter(User.deleted_at.is_(None)).count()


# 建立全域實例
user_crud = UserCRUD()
