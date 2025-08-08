"""
資料庫管理模組。

包含資料庫連線、會話管理等功能。
"""

# ===== 標準函式庫 =====
import logging  # 日誌記錄
from typing import Any, Generator, Tuple

# ===== 第三方套件 =====
from fastapi import HTTPException, status  # FastAPI 錯誤處理
from sqlalchemy import create_engine, text  # 資料庫引擎
from sqlalchemy.exc import OperationalError  # 資料庫錯誤
from sqlalchemy.orm import Session, declarative_base, sessionmaker  # 會話管理

# ===== 本地模組 =====
from app.core import settings  # 應用程式配置
from app.utils.timezone import get_utc_timestamp  # 時間戳記工具

logging.basicConfig(
    level=logging.INFO
)  # 設定日誌級別為 INFO：INFO 級別以上的訊息就會顯示
logger = logging.getLogger(
    __name__
)  # 取得 logger 實例，用於記錄日誌，讓 logger 根據不同模組來源分辨訊息來源

# 設定 SQLAlchemy 的日誌級別為 WARNING：只顯示 WARNING 級別以上的訊息
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def create_database_engine() -> Tuple[Any, Any, Any]:
    """
    建立並初始化資料庫引擎和相關組件。

    包含：
    - 建立 SQLAlchemy 引擎
    - 測試資料庫連線
    - 建立 session 工廠
    - 建立基礎類別

    Returns:
        tuple: (engine, SessionLocal, Base) 資料庫引擎、會話工廠、基礎類別

    Raises:
        Exception: 當資料庫連線失敗時拋出異常
    """
    logger.info("create_database_engine() called: 開始建立資料庫引擎")

    DATABASE_URL = settings.mysql_connection_string

    try:
        # 創建資料庫引擎
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # 關閉 SQL 查詢日誌
            pool_pre_ping=True,  # 啟用連線檢查，確保連線有效性
            pool_recycle=3600,  # 連線池回收時間（1小時）
            pool_size=10,  # 連線池大小
            max_overflow=20,  # 最大溢出連線數
            pool_timeout=30,  # 連線超時時間（30秒）
            # pymysql 特定參數
            connect_args={
                "charset": "utf8mb4",  # 使用 utf8mb4 字符集
                "autocommit": False,  # 手動提交事務
                # 嚴格模式
                "sql_mode": (
                    "STRICT_TRANS_TABLES,NO_ZERO_DATE,"
                    "NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO"
                ),
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

        # 建立 session（會話）類別工廠
        SessionLocal = sessionmaker(
            bind=engine,  # 指定 Session 連線的資料庫引擎（engine）
            autocommit=False,  # 不自動提交，手動呼叫 .commit() 才會儲存資料
            autoflush=False,  # 不自動刷新、不自動將未提交的改動同步到資料庫，需手動呼叫 flush()
        )

        # 建立基礎類別：所有資料表模型，都會繼承這個類別，避免重複的程式碼
        Base = declarative_base()

        logger.info("create_database_engine() success: 資料庫引擎建立成功")
        return engine, SessionLocal, Base

    except Exception as e:
        logger.error(f"連結到資料庫失敗：{str(e)}")
        logger.error("請檢查以下項目：")
        logger.error("   1. MySQL 服務是否正在運行")
        logger.error("   2. 資料庫連線設定是否正確")
        logger.error("   3. 使用者權限是否足夠")
        logger.error("   4. 防火牆設定是否允許連線")
        raise


# 初始化資料庫組件
try:
    engine, SessionLocal, Base = create_database_engine()
except Exception as e:
    logger.error(f"資料庫初始化失敗：{str(e)}")
    raise


# ===== 資料庫依賴和工具函式 =====


def get_db() -> Generator[Session, None, None]:
    """
    資料庫會話依賴注入函式。

    用於 FastAPI 的依賴注入系統，為每個請求提供獨立的資料庫會話。
    使用 yield 確保會話在請求結束後自動關閉，避免資源洩漏。

    Yields:
        Session: SQLAlchemy 資料庫會話實例

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    logger.info("get_db() called: 建立資料庫連線")
    db = (
        SessionLocal()
    )  # 建立資料庫連線：每次操作資料庫，會透過 SessionLocal() 建立一個 session 實例（db）來操作
    try:
        # 設定時區為台灣時間
        db.execute(text("SET time_zone = '+08:00'"))
        # 驗證連線是否有效（輕量級檢查）
        db.execute(text("SELECT 1"))
        logger.info("get_db() yield: 傳遞資料庫連線給處理函式")
        yield db  # 傳給處理請求的函式使用，執行查詢/新增/修改操作，每次請求建立一個 session，避免多個使用者共享同一個連線
    except Exception as e:
        logger.error(f"get_db() error: 資料庫操作發生錯誤 - {str(e)}")
        db.rollback()  # 發生錯誤時回滾事務
        raise
    finally:
        logger.info("get_db() cleanup: 關閉資料庫連線")
        db.close()  # 每次請求結束後，無論有沒有錯誤發生，都自動關閉 session 連線，避免資源浪費、外洩


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
