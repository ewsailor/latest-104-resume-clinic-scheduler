# """
# 資料庫管理模組。

# 包含資料庫連線、會話管理、軟刪除查詢等功能。
# """

# # ===== 標準函式庫 =====
# import logging  # 日誌記錄
# from typing import Optional, Any, Dict, List  # 型別註解

# # ===== 第三方套件 =====
# from sqlalchemy import create_engine, text  # 資料庫引擎
# from sqlalchemy.orm import sessionmaker, Session  # 會話管理
# from sqlalchemy.pool import QueuePool  # 連線池
# from sqlalchemy.exc import SQLAlchemyError  # 資料庫錯誤

# # ===== 本地模組 =====
# from app.core import settings  # 應用程式配置

# # 設定日誌
# logger = logging.getLogger(__name__)

# # ===== 資料庫引擎設定 =====
# def create_database_engine() -> Any:
#     """
#     建立資料庫引擎。
    
#     Returns:
#         Engine: SQLAlchemy 引擎實例。
#     """
#     try:
#         # 建立 MySQL 連線字串
#         database_url = (
#             f"mysql+pymysql://{config.mysql_user}:{config.mysql_password}"
#             f"@{config.mysql_host}:{config.mysql_port}/{config.mysql_database}"
#             f"?charset={config.mysql_charset}"
#         )
        
#         # 建立引擎
#         engine = create_engine(
#             database_url,
#             poolclass=QueuePool,
#             pool_size=10,  # 連線池大小
#             max_overflow=20,  # 最大溢出連線數
#             pool_pre_ping=True,  # 連線前檢查
#             pool_recycle=3600,  # 連線回收時間（秒）
#             echo=config.debug,  # 開發模式顯示 SQL
#         )
        
#         logger.info(f"資料庫引擎建立成功：{config.mysql_host}:{config.mysql_port}/{config.mysql_database}")
#         return engine
        
#     except Exception as e:
#         logger.error(f"資料庫引擎建立失敗：{e}")
#         raise


# # 建立引擎實例
# engine = create_database_engine()

# # 建立會話工廠
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# # ===== 資料庫會話管理 =====
# def get_db() -> Session:
#     """
#     取得資料庫會話。
    
#     Yields:
#         Session: 資料庫會話實例。
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     except SQLAlchemyError as e:
#         logger.error(f"資料庫操作錯誤：{e}")
#         db.rollback()
#         raise
#     finally:
#         db.close()


# # ===== 基礎模型類別 =====
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()


# # ===== 軟刪除查詢混入 =====
# class SoftDeleteQueryMixin:
#     """
#     軟刪除查詢混入類別。
    
#     提供軟刪除相關的查詢方法。
#     """
    
#     def filter_active(self, query):
#         """
#         過濾未刪除的記錄。
        
#         Args:
#             query: SQLAlchemy 查詢物件。
            
#         Returns:
#             Query: 過濾後的查詢物件。
#         """
#         return query.filter(self.deleted_at.is_(None))
    
#     def filter_deleted(self, query):
#         """
#         過濾已刪除的記錄。
        
#         Args:
#             query: SQLAlchemy 查詢物件。
            
#         Returns:
#             Query: 過濾後的查詢物件。
#         """
#         return query.filter(self.deleted_at.isnot(None))
    
#     def include_deleted(self, query):
#         """
#         包含已刪除的記錄。
        
#         Args:
#             query: SQLAlchemy 查詢物件。
            
#         Returns:
#             Query: 查詢物件（不過濾刪除狀態）。
#         """
#         return query


# # ===== 歷史記錄管理 =====
# class HistoryManager:
#     """
#     歷史記錄管理器。
    
#     負責記錄資料變更歷史。
#     """
    
#     def __init__(self, db: Session):
#         """
#         初始化歷史記錄管理器。
        
#         Args:
#             db: 資料庫會話。
#         """
#         self.db = db
    
#     def log_change(
#         self,
#         schedule_id: int,
#         user_id: Optional[int],
#         action: str,
#         old_status: Optional[str] = None,
#         new_status: Optional[str] = None,
#         changes: Optional[Dict[str, Any]] = None,
#         ip_address: Optional[str] = None,
#         user_agent: Optional[str] = None
#     ) -> None:
#         """
#         記錄變更歷史。
        
#         Args:
#             schedule_id: 行程 ID。
#             user_id: 操作使用者 ID。
#             action: 操作類型。
#             old_status: 舊狀態。
#             new_status: 新狀態。
#             changes: 變更內容。
#             ip_address: IP 位址。
#             user_agent: 使用者代理字串。
#         """
#         try:
#             from app.models.schedule import ScheduleHistory
            
#             history = ScheduleHistory(
#                 schedule_id=schedule_id,
#                 user_id=user_id,
#                 action=action,
#                 old_status=old_status,
#                 new_status=new_status,
#                 changes=changes,
#                 ip_address=ip_address,
#                 user_agent=user_agent
#             )
            
#             self.db.add(history)
#             self.db.commit()
            
#             logger.info(f"歷史記錄已建立：schedule_id={schedule_id}, action={action}")
            
#         except Exception as e:
#             logger.error(f"歷史記錄建立失敗：{e}")
#             self.db.rollback()
#             raise


# # ===== 資料庫健康檢查 =====
# def check_database_health() -> Dict[str, Any]:
#     """
#     檢查資料庫健康狀態。
    
#     Returns:
#         Dict[str, Any]: 健康狀態資訊。
#     """
#     try:
#         with engine.connect() as connection:
#             # 執行簡單查詢
#             result = connection.execute(text("SELECT 1"))
#             result.fetchone()
            
#             # 檢查連線池狀態
#             pool_status = {
#                 "pool_size": engine.pool.size(),
#                 "checked_in": engine.pool.checkedin(),
#                 "checked_out": engine.pool.checkedout(),
#                 "overflow": engine.pool.overflow(),
#             }
            
#             return {
#                 "status": "healthy",
#                 "message": "資料庫連線正常",
#                 "pool_status": pool_status
#             }
            
#     except Exception as e:
#         logger.error(f"資料庫健康檢查失敗：{e}")
#         return {
#             "status": "unhealthy",
#             "message": f"資料庫連線異常：{str(e)}",
#             "pool_status": {}
#         }


# # ===== 資料庫初始化 =====
# def init_database() -> None:
#     """
#     初始化資料庫。
    
#     建立所有資料表。
#     """
#     try:
#         # 匯入所有模型以確保它們被註冊
#         from app.models.schedule import User, Schedule, ScheduleHistory, NotificationSetting
        
#         # 建立所有資料表
#         Base.metadata.create_all(bind=engine)
        
#         logger.info("資料庫初始化完成")
        
#     except Exception as e:
#         logger.error(f"資料庫初始化失敗：{e}")
#         raise


# # ===== 資料庫清理 =====
# def cleanup_database() -> None:
#     """
#     清理資料庫。
    
#     刪除所有資料表（謹慎使用）。
#     """
#     try:
#         Base.metadata.drop_all(bind=engine)
#         logger.warning("資料庫已清理")
        
#     except Exception as e:
#         logger.error(f"資料庫清理失敗：{e}")
#         raise 