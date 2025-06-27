from sqlalchemy import create_engine  # 引入 create_engine 函式，用於建立資料庫連線引擎
from sqlalchemy.orm import sessionmaker, declarative_base  # 引入 sessionmaker 函式用於建立 session 實例，declarative_base 函式用於建立基礎類別
import logging  # 引入 logging 模組，用於記錄日誌

# 設定日誌級別為 INFO：INFO 級別以上的訊息就會顯示
logging.basicConfig(level=logging.INFO)  
# 取得 logger 實例，用於記錄日誌，讓 logger 根據不同模組來源分辨訊息來源
logger = logging.getLogger(__name__)  

# 設定 SQLAlchemy 的日誌級別為 WARNING：只顯示 WARNING 級別以上的訊息，避免太多日誌訊息，因為預設 SQLAlchemy 執行時會印出很多 SQL log
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)  

# MySQL 資料庫連線字串：
# DATABASE_URL = "mysql+pymysql://使用者名稱:密碼@localhost/資料庫名稱"  
# 資料庫類型為 MySQL
# 資料庫驅動程式為 pymysql
# 使用者名稱為 fastapi_user
# 密碼為 fastapi123
# 資料庫位址為 localhost
# 資料庫名稱為 scheduler_db
DATABASE_URL = "mysql+pymysql://fastapi_user:fastapi123@localhost/scheduler_db"

try:
    # 創建資料庫引擎
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # 關閉 SQL 查詢日誌
        pool_pre_ping=True  # 啟用連線檢查
    )
    
    # 測試連線
    with engine.connect() as connection:
        logger.info("Successfully connected to the database!")
        
    # SessionLocal = sessionmaker()：建立 session（會話）類別工廠，指定給變數 SessionLocal，每次操作資料庫，會透過 SessionLocal() 建立一個 session 實例來操作。
    # bind=engine：指定 Session 連線的資料庫引擎（engine）
    # autocommit=False：不自動提交，手動呼叫 .commit() 才會儲存資料
    # autoflush=False：不自動刷新、不自動將未提交的改動同步到資料庫，需手動呼叫 flush()
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)  
    # 建立基礎類別：所有資料表模型，都會繼承這個類別，避免重複的程式碼
    Base = declarative_base()  
    
except Exception as e:
    logger.error(f"Error connecting to the database: {str(e)}")
    raise