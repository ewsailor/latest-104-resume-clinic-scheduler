"""
資料模組。

提供應用程式所需的資料和常數定義，包括：
- 模擬 Giver 資料
- Giver 查詢和篩選功能
"""

# ===== 本地模組 =====
from .givers import (
    MOCK_GIVERS,
    get_all_givers,
    get_giver_by_id,
)

__all__ = [
    # Giver 資料
    'MOCK_GIVERS',
    # Giver 查詢函式
    'get_all_givers',
    'get_giver_by_id',
]
