"""
資料模組。

提供應用程式所需的資料和常數定義，包括：
- 模擬 Giver 資料
- Giver 查詢和篩選功能
- 產業和主題分類資料
"""

from .givers import (
    MOCK_GIVERS,
    get_all_givers,
    get_giver_by_id,
    get_givers_by_industry,
    get_givers_by_topic,
    get_givers_count,
)

__all__ = [
    'MOCK_GIVERS',
    'get_all_givers',
    'get_giver_by_id',
    'get_givers_by_topic',
    'get_givers_by_industry',
    'get_givers_count',
]
