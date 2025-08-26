"""
Giver 資料模組。

提供 Giver 相關的資料和常數定義。
"""

# ===== 標準函式庫 =====
from typing import Any

MOCK_GIVERS = [
    {
        "id": 1,
        "image": "https://randomuser.me/api/portraits/women/1.jpg",
        "name": "王零一",
        "title": "Python 工程師",
        "company": "王零一-資訊科技公司",
        "consulted": "106",
        "average_responding_time": "2",
        "experience": "4",
        "giverCard__topic": [
            "履歷健診",
            "模擬面試",
            "職涯諮詢",
            "職業/產業經驗分享",
            "英文履歷健診",
            "英文履歷面試",
        ],
        "industry": "農林漁牧水電資源業",
        "school": "東海大學",
        "tag": ["軟體開發"],
        "introduction": "從實務出發，結合理論，助您突破職涯瓶頸。",
    },
    {
        "id": 2,
        "image": "https://randomuser.me/api/portraits/women/2.jpg",
        "name": "王零二",
        "title": "前端工程師",
        "company": "王零二-資訊科技公司",
        "consulted": "95",
        "average_responding_time": "3",
        "experience": "3",
        "giverCard__topic": ["履歷健診", "模擬面試"],
        "industry": "政治宗教及社福相關業",
        "school": "中央大學",
        "tag": ["市場策略", "企業管理"],
        "introduction": "以人為本，以終為始，助您規劃清晰職涯路徑。",
    },
    {
        "id": 3,
        "image": "https://randomuser.me/api/portraits/women/3.jpg",
        "name": "王零三",
        "title": "後端工程師",
        "company": "王零三-資訊科技公司",
        "consulted": "88",
        "average_responding_time": "4",
        "experience": "5",
        "giverCard__topic": ["職涯諮詢", "英文履歷健診"],
        "industry": "法律／會計／顧問／研發／設計業",
        "school": "交通大學",
        "tag": ["使用者體驗"],
        "introduction": "技術專精，樂於傳授知識，解決您的技術困惑。",
    },
    {
        "id": 4,
        "image": "https://randomuser.me/api/portraits/women/4.jpg",
        "name": "王零四",
        "title": "資料分析師",
        "company": "王零四-資訊科技公司",
        "consulted": "132",
        "average_responding_time": "1",
        "experience": "6",
        "giverCard__topic": ["履歷健診", "模擬面試", "職涯諮詢"],
        "industry": "住宿／餐飲服務業",
        "school": "東吳大學",
        "tag": ["數據分析", "區塊鏈", "人工智能"],
        "introduction": "擁有跨領域背景，提供多元視角和創新思維。",
    },
    {
        "id": 5,
        "image": "https://randomuser.me/api/portraits/men/5.jpg",
        "name": "王零五",
        "title": "AI 工程師",
        "company": "王零五-資訊科技公司",
        "consulted": "77",
        "average_responding_time": "2",
        "experience": "2",
        "giverCard__topic": ["英文履歷健診"],
        "industry": "金融投顧及保險業",
        "school": "臺灣大學",
        "tag": ["工業互聯網", "產品規劃", "使用者體驗"],
        "introduction": "擁有跨領域背景，提供多元視角和創新思維。",
    },
    {
        "id": 6,
        "image": "https://randomuser.me/api/portraits/men/6.jpg",
        "name": "王零六",
        "title": "DevOps 工程師",
        "company": "王零六-資訊科技公司",
        "consulted": "60",
        "average_responding_time": "3",
        "experience": "4",
        "giverCard__topic": ["模擬面試", "職涯諮詢"],
        "industry": "運輸物流及倉儲業",
        "school": "中山大學",
        "tag": ["企業管理", "數位轉型"],
        "introduction": "溝通表達能力強，善於傾聽並給予精準回饋。",
    },
    {
        "id": 7,
        "image": "https://randomuser.me/api/portraits/men/7.jpg",
        "name": "王零七",
        "title": "全端工程師",
        "company": "王零七-資訊科技公司",
        "consulted": "110",
        "average_responding_time": "1",
        "experience": "7",
        "giverCard__topic": ["履歷健診", "模擬面試", "英文履歷健診"],
        "industry": "文教相關業",
        "school": "中正大學",
        "tag": ["敏捷開發", "工業互聯網", "產品規劃"],
        "introduction": "以人為本，以終為始，助您規劃清晰職涯路徑。",
    },
    {
        "id": 8,
        "image": "https://randomuser.me/api/portraits/men/8.jpg",
        "name": "王零八",
        "title": "資安工程師",
        "company": "王零八-資訊科技公司",
        "consulted": "48",
        "average_responding_time": "4",
        "experience": "5",
        "giverCard__topic": ["職涯諮詢"],
        "industry": "電子資訊／軟體／半導體相關業",
        "school": "逢甲大學",
        "tag": ["數位轉型"],
        "introduction": "經驗豐富，熱衷於幫助他人實現目標。",
    },
    {
        "id": 9,
        "image": "https://randomuser.me/api/portraits/men/9.jpg",
        "name": "王零九",
        "title": "UX 設計師",
        "company": "王零九-資訊科技公司",
        "consulted": "68",
        "average_responding_time": "3",
        "experience": "3",
        "giverCard__topic": ["履歷健診", "職涯諮詢"],
        "industry": "醫療保健及環境衛生業",
        "school": "世新大學",
        "tag": ["數據分析", "雲端技術", "產品規劃"],
        "introduction": (
            "上善若水 水善利萬物而不爭，處眾人之所惡，故幾於道。居，善地；心，善淵；"
            "與，善仁；言，善信；政，善治；事，善能；動，善時。夫唯不爭，故無尤。"
            "～共勉之～"
        ),
    },
    {
        "id": 10,
        "image": "https://randomuser.me/api/portraits/men/10.jpg",
        "name": "王拾",
        "title": "專案經理",
        "company": "王拾-資訊科技公司",
        "consulted": "120",
        "average_responding_time": "2",
        "experience": "8",
        "giverCard__topic": ["模擬面試", "職涯諮詢"],
        "industry": "大眾傳播相關業",
        "school": "中原大學",
        "tag": ["顧問諮詢"],
        "introduction": "溝通表達能力強，善於傾聽並給予精準回饋。",
    },
    {
        "id": 11,
        "image": "https://randomuser.me/api/portraits/men/11.jpg",
        "name": "王拾一",
        "title": "產品經理",
        "company": "王拾一-資訊科技公司",
        "consulted": "92",
        "average_responding_time": "3",
        "experience": "6",
        "giverCard__topic": ["履歷健診", "英文履歷健診"],
        "industry": "醫療保健及環境衛生業",
        "school": "東吳大學",
        "tag": ["人工智能", "數位轉型"],
        "introduction": "技術專精，樂於傳授知識，解決您的技術困惑。",
    },
    {
        "id": 12,
        "image": "https://randomuser.me/api/portraits/men/12.jpg",
        "name": "王拾二",
        "title": "資料科學家",
        "company": "王拾二-資訊科技公司",
        "consulted": "105",
        "average_responding_time": "1",
        "experience": "5",
        "giverCard__topic": ["職涯諮詢", "英文履歷健診"],
        "industry": "建築營造及不動產相關業",
        "school": "清華大學",
        "tag": ["雲端技術", "市場策略"],
        "introduction": (
            "上善若水 水善利萬物而不爭，處眾人之所惡，故幾於道。居，善地；心，善淵；"
            "與，善仁；言，善信；政，善治；事，善能；動，善時。夫唯不爭，故無尤。"
            "～共勉之～"
        ),
    },
    {
        "id": 13,
        "image": "https://randomuser.me/api/portraits/men/13.jpg",
        "name": "王拾三",
        "title": "系統分析師",
        "company": "王拾三-資訊科技公司",
        "consulted": "84",
        "average_responding_time": "2",
        "experience": "4",
        "giverCard__topic": ["模擬面試", "職涯諮詢", "履歷健診"],
        "industry": "旅遊／休閒／運動業",
        "school": "輔仁大學",
        "tag": ["產品規劃", "人工智能", "軟體開發"],
        "introduction": "持續學習，樂於分享，期待與您共同成長。",
    },
    {
        "id": 14,
        "image": "https://randomuser.me/api/portraits/men/14.jpg",
        "name": "王拾四",
        "title": "資料分析師",
        "company": "王拾四-資訊科技公司",
        "consulted": "24",
        "average_responding_time": "3",
        "experience": "5",
        "giverCard__topic": ["模擬面試", "職涯諮詢", "履歷健診", "英文履歷健診"],
        "industry": "住宿／餐飲服務業",
        "school": "東吳大學",
        "tag": ["數據分析", "區塊鏈", "人工智能"],
        "introduction": "持續學習，樂於分享，期待與您共同成長。",
    },
]


def get_all_givers() -> list[dict[str, Any]]:
    """
    取得所有 Giver 資料。

    Returns:
        list: Giver 資料列表
    """
    return MOCK_GIVERS


def get_giver_by_id(giver_id: int) -> dict[str, Any] | None:
    """
    根據 ID 取得特定 Giver 資料。

    Args:
        giver_id: Giver ID

    Returns:
        dict: Giver 資料，如果找不到則返回 None
    """
    for giver in MOCK_GIVERS:
        if giver["id"] == giver_id:
            return giver
    return None
