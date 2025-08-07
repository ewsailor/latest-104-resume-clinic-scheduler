"""
測試模組初始化。

設定 Python 路徑以確保測試可以正確導入 app 模組。
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
