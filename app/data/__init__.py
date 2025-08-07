"""
資料模組。

提供應用程式所需的資料和常數定義。
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
