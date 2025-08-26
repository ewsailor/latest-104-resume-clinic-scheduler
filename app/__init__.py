"""
104 履歷診療室 - 站內諮詢時間媒合系統

FastAPI 應用程式主套件，讓 Giver、Taker 在平台內，
方便地設定可面談時間，並完成配對媒合。

主要組件：
- 核心配置（app/core）：應用程式設定、版本管理
- 資料庫模型（app/models）：SQLAlchemy 模型定義
- 資料驗證模式（app/schemas）：Pydantic 資料模型
- 業務邏輯服務（app/services）：業務邏輯處理層
- 資料庫操作（app/crud）：資料庫 CRUD 操作
- API 路由（app/routers）：FastAPI 路由定義
- 錯誤處理（app/errors）：統一錯誤處理機制
- 工具模組（app/utils）：共用工具函數
- 中間件（app/middleware）：FastAPI 中間件
- 資料模組（app/data）：靜態資料和常數
- 枚舉定義（app/enums）：系統枚舉類型
"""
