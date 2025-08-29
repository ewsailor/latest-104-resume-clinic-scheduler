"""Giver 測試資料模組。

提供測試用的 Giver 資料。
"""

# ===== 測試資料 =====
TEST_GIVERS = [
    {
        "id": 1,
        "name": "測試 Giver 1",
        "title": "測試職位 1",
        "company": "測試公司 1",
        "consulted": 50,
        "average_responding_time": 1,
        "experience": 5,
        "image": "test/1.jpg",
        "giverCard__topic": ["測試技能 1", "測試技能 2"],
    },
    {
        "id": 2,
        "name": "測試 Giver 2",
        "title": "測試職位 2",
        "company": "測試公司 2",
        "consulted": 75,
        "average_responding_time": 2,
        "experience": 7,
        "image": "test/2.jpg",
        "giverCard__topic": ["測試技能 3", "測試技能 4"],
    },
]


def get_test_givers():
    """取得測試用的 Giver 資料。

    Returns:
        list: 測試 Giver 資料列表
    """
    return TEST_GIVERS.copy()


def get_test_giver_by_id(giver_id: int):
    """根據 ID 取得測試用的特定 Giver 資料。

    Args:
        giver_id (int): Giver ID

    Returns:
        dict: 測試 Giver 資料，如果找不到則返回 None
    """
    for giver in TEST_GIVERS:
        if giver["id"] == giver_id:
            return giver.copy()
    return None
