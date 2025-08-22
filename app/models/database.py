"""
資料庫管理模組。

包含資料庫連線、會話管理等功能。
"""

import logging
from typing import Generator

from fastapi import HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core import settings
from app.utils.timezone import get_utc_timestamp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# 建立基礎類別：所有資料表模型，都會繼承這個類別，避免重複的程式碼
Base = declarative_base()


def create_database_engine() -> tuple[Engine, sessionmaker]:
    """
    建立並初始化資料庫引擎和相關組件。

    包含：
    - 建立 SQLAlchemy 資料庫引擎連線
    - 測試資料庫引擎連線
    - 建立 session 工廠

    Returns:
        tuple: (engine, SessionLocal) 資料庫引擎、會話工廠

    Raises:
        Exception: 當資料庫引擎連線失敗時拋出異常
    """
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

    except OperationalError as e:
        logger.error(f"create_database_engine() error: 資料庫連線失敗 - {str(e)}")
        raise

    except Exception as e:
        logger.error(f"create_database_engine() error: 連結到資料庫失敗 - {str(e)}")
        logger.error("請檢查以下項目：")
        logger.error("   1. MySQL 服務是否正在運行")
        logger.error("   2. 資料庫連線設定是否正確")
        logger.error("   3. 使用者權限是否足夠")
        logger.error("   4. 防火牆設定是否允許連線")
        raise


# 程式啟動時，立即建立引擎和會話工廠
try:
    engine, SessionLocal = create_database_engine()
except Exception as e:
    logger.error(f"資料庫初始化失敗：{str(e)}")
    raise


def get_db() -> Generator[Session, None, None]:
    """
    資料庫會話依賴注入函式。

    用於 FastAPI 的依賴注入系統，為每個請求提供獨立的資料庫會話。
    使用 yield 確保無論有無錯誤，請求結束後自動關閉 session 連線，避免資源浪費、洩漏。

    Yields:
        Session: SQLAlchemy 資料庫會話實例

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
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
    except Exception as e:
        logger.error(f"get_db() error: 資料庫操作發生錯誤 - {str(e)}")
        db.rollback()  # 發生錯誤時回滾事務
        raise
    finally:
        logger.info("get_db() cleanup: 關閉資料庫連線")
        db.close()


def check_db_connection() -> bool:
    """
    檢查資料庫連線狀態。

    執行簡單的 SQL 查詢來驗證資料庫連線是否正常。
    用於健康檢查和監控系統。

    Returns:
        bool: True 表示連線正常，False 表示連線失敗

    Example:
        if check_db_connection():
            print("資料庫連線正常")
        else:
            print("資料庫連線失敗")
    """
    logger.info("check_db_connection() called: 檢查資料庫連線狀態")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # 執行簡單的查詢來測試連線
            logger.info("check_db_connection() success: 資料庫連線正常")
            return True
    except OperationalError as e:
        logger.error(f"check_db_connection() error: 資料庫連線失敗 - {str(e)}")
        return False
    except Exception as e:
        logger.error(
            f"check_db_connection() error: 檢查連線時發生未預期錯誤 - {str(e)}"
        )
        return False


def get_healthy_db() -> bool:
    """
    健康檢查專用的資料庫依賴。

    用於 readiness probe，如果資料庫連線失敗會拋出 HTTPException。
    這讓健康檢查端點可以專注於業務邏輯，而不需要處理連線錯誤。

    Returns:
        bool: True 表示資料庫連線正常

    Raises:
        HTTPException: 當資料庫連線失敗時拋出 503 錯誤

    Example:
        @router.get("/readyz")
        async def readiness_probe(db_healthy: bool = Depends(get_healthy_db)):
            return {"status": "healthy"}
    """
    logger.info("get_healthy_db() called: 健康檢查資料庫連線")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("get_healthy_db() success: 資料庫連線正常")
            return True
    except Exception as e:
        logger.error(f"get_healthy_db() error: 資料庫連線失敗 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "database": "disconnected",
                "message": "Database connection failed. Application is not ready.",
                "timestamp": get_utc_timestamp(),
            },
        )
