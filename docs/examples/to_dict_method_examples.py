"""
to_dict 方法實作範例

本檔案展示了不同版本的 to_dict 方法實作，從基本到進階，
供開發者參考和學習使用。

版本說明：
- 版本 1：基本改進版 - 簡單的錯誤處理
- 版本 2：完整改進版 - 包含關聯資料選項
- 版本 3：高效能版本 - 避免 N+1 查詢問題（推薦）
- 版本 4：安全版本 - 檢查屬性是否已加載

使用方式：
1. 複製需要的版本到您的模型類別中
2. 根據實際需求調整欄位和邏輯
3. 測試確保功能正常

注意事項：
- 需要根據實際的模型結構調整欄位名稱
- 關聯資料的處理需要考慮效能影響
- 建議在生產環境中使用版本 3 或版本 4
"""

from typing import Any, Dict, Optional

# 假設的導入（在實際使用時需要根據您的專案結構調整）
try:
    from sqlalchemy.orm import Session

    from app.models.user import User
except ImportError:
    # 如果無法導入，定義一個假設的類別用於範例
    class User:
        pass

    class Session:
        pass


# ===== 版本 1：基本改進版 =====
def to_dict_basic(self) -> Dict[str, Any]:
    """基本改進版本"""
    try:
        # 安全取得 updated_by_user 資訊
        updated_by_user_name = None
        if self.updated_by_user:
            updated_by_user_name = self.updated_by_user.name
    except Exception:
        # 如果無法取得關聯資料，設為 None
        updated_by_user_name = None

    return {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        "updated_by": self.updated_by,
        "updated_by_user": updated_by_user_name,
        "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
    }


# ===== 版本 2：完整改進版 =====
def to_dict_enhanced(self, include_relations: bool = True) -> Dict[str, Any]:
    """
    完整改進版本

    Args:
        include_relations: 是否包含關聯資料
    """
    result = {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        "updated_by": self.updated_by,
        "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        "is_deleted": self.deleted_at is not None,  # 額外的便利欄位
    }

    # 只有需要時才加載關聯資料
    if include_relations:
        try:
            if self.updated_by_user:
                result["updated_by_user"] = {
                    "id": self.updated_by_user.id,
                    "name": self.updated_by_user.name,
                    "email": self.updated_by_user.email,
                }
            else:
                result["updated_by_user"] = None
        except Exception:
            result["updated_by_user"] = None

    return result


# ===== 版本 3：高效能版本（推薦） =====
def to_dict_optimized(self, db_session: Optional[Session] = None) -> Dict[str, Any]:
    """
    高效能版本 - 避免 N+1 查詢問題

    Args:
        db_session: 資料庫會話，用於明確查詢關聯資料
    """
    result = {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        "updated_by": self.updated_by,
        "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
    }

    # 高效能的關聯資料查詢
    if self.updated_by and db_session:
        try:
            updated_by_user = db_session.get(User, self.updated_by)
            if updated_by_user:
                result["updated_by_user"] = {
                    "id": updated_by_user.id,
                    "name": updated_by_user.name,
                }
            else:
                result["updated_by_user"] = None
        except Exception:
            result["updated_by_user"] = None
    else:
        result["updated_by_user"] = None

    return result


# ===== 版本 4：使用屬性檢查版本 =====
def to_dict_safe(self) -> Dict[str, Any]:
    """安全版本 - 檢查屬性是否已加載"""
    from sqlalchemy import inspect

    result = {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        "updated_by": self.updated_by,
        "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
    }

    # 檢查關聯是否已加載
    inspector = inspect(self)
    if (
        'updated_by_user' in inspector.attrs
        and not inspector.attrs.updated_by_user.history.added
    ):
        try:
            if self.updated_by_user:
                result["updated_by_user"] = self.updated_by_user.name
            else:
                result["updated_by_user"] = None
        except Exception:
            result["updated_by_user"] = None
    else:
        # 關聯未加載，只返回基本資訊
        result["updated_by_user"] = None

    return result
