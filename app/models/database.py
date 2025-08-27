"""資料庫管理模組。

包含資料庫連線、會話管理等功能。
"""

# ===== 標準函式庫 =====
import logging
from typing import Generator

# ===== 第三方套件 =====
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ===== 本地模組 =====
from app.core import settings
from app.errors import create_database_error, create_service_unavailable_error
from app.errors.exceptions import APIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 建立基礎類別：所有資料表模型，都會繼承這個類別，避免重複的程式碼
Base = declarative_base()


def create_database_engine() -> tuple[create_engine, sessionmaker]:
    """建立資料庫引擎和會話工廠"""
    logger.info("create_database_engine() called: 開始建立資料庫引擎")

    DATABASE_URL = settings.mysql_connection_string

    try:
        # 建立資料庫引擎連線
        engine = create_engine(
            DATABASE_URL,  # MySQL 連接字串
            echo=False,  # 關閉 SQL 查詢日誌
            pool_pre_ping=True,  # 啟用連線檢查，確保連線有效性
            pool_size=10,  # 連線池大小
            max_overflow=10,  # 最大溢出連線數（通常是 pool_size 的 1-2 倍）
            pool_timeout=30,  # 連線超時時間（30秒）
            pool_recycle=3600,  # 連線池回收時間（1小時）
            connect_args={  # pymysql 特定參數
                "charset": "utf8mb4",  # 使用 utf8mb4 字符集
            },
        )

        # 測試連線
        with engine.connect():
            logger.info(
                f"成功建立資料庫引擎，並連結到資料庫：{settings.mysql_database}"
            )
            logger.info(f"資料庫主機：{settings.mysql_host}:{settings.mysql_port}")
            logger.info(f"使用者：{settings.mysql_user}")
            logger.info("驅動程式：pymysql")

        # 建立 session 工廠：每次呼叫 SessionLocal()，就生成一個新 Session 實例，確保每個請求，都有一個獨立的資料庫連線，避免共用連線，導致資料庫操作錯亂
        SessionLocal = sessionmaker(
            bind=engine,  # 指定 Session 連線的資料庫引擎（engine）
            autocommit=False,  # 不自動提交，手動呼叫 .commit() 才會儲存資料
            autoflush=False,  # 不自動刷新、不自動將未提交的改動同步到資料庫，需手動呼叫 flush()
        )

        logger.info("create_database_engine() success: 資料庫引擎建立成功")
        return engine, SessionLocal

    except Exception as e:
        logger.error(f"create_database_engine() error: 連結到資料庫失敗 - {str(e)}")
        raise create_service_unavailable_error(f"資料庫引擎建立失敗：{str(e)}")


# 程式啟動時，立即建立引擎和會話工廠
try:
    engine, SessionLocal = create_database_engine()
except Exception as e:
    logger.error(f"資料庫初始化失敗：{str(e)}")
    # 這裡不重新拋出，因為程式啟動失敗應該直接終止
    raise


def get_db() -> Generator[Session, None, None]:
    """
    資料庫會話依賴注入函式。

    用於 FastAPI 的依賴注入系統，為每個請求提供獨立的資料庫會話。
    使用 yield 確保無論有無錯誤，請求結束後自動關閉 session 連線，避免資源浪費、洩漏。

    Yields:
        Session: SQLAlchemy 資料庫會話實例
    """
    logger.info("get_db() called: 建立資料庫連線")
    # db 是實際的 Session 實例，用來進行 add()、query()、commit()、close() 等操作
    db = SessionLocal()
    try:
        # 設定時區為台灣時間
        db.execute(text("SET time_zone = '+08:00'"))

        # 設定 sql_mode 為嚴格模式（每個連線都會設定）
        db.execute(
            text(
                "SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'"
            )
        )

        # 驗證連線是否有效（輕量級檢查）
        db.execute(text("SELECT 1"))
        logger.info("get_db() yield: 傳遞資料庫連線給處理函式")
        yield db
    except APIError as e:
        # APIError 類型直接向上傳遞，不要包裝
        logger.error(f"get_db() error: API 錯誤 - {str(e)}")
        db.rollback()
        raise
    except HTTPException as e:
        # HTTPException 類型直接向上傳遞，不要包裝
        logger.error(f"get_db() error: HTTP 錯誤 - {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        # 其他異常包裝成 DatabaseError
        logger.error(f"get_db() error: 資料庫操作錯誤 - {str(e)}")
        db.rollback()
        raise create_database_error(f"資料庫會話建立失敗：{str(e)}")
    finally:
        logger.info("get_db() cleanup: 關閉資料庫連線")
        db.close()


def check_db_connection() -> None:
    """檢查資料庫連線狀態"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # 執行簡單的查詢來測試連線
            logger.info("check_db_connection() success: 資料庫連線正常")
    except Exception as e:
        logger.error(f"check_db_connection() error: 資料庫連線檢查失敗 - {str(e)}")
        raise create_service_unavailable_error(f"資料庫連線失敗：{str(e)}")
