import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from typing import Optional, Dict, Any

class LoggerConfig:
    """日誌配置類別"""
    
    def __init__(self, name: str = __name__, log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """設定日誌器"""
        # 建立日誌目錄
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 日誌格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 建立日誌器
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重複添加處理器
        if not self.logger.handlers:
            # 檔案處理器
            file_handler = RotatingFileHandler(
                f'{self.log_dir}/app.log',
                maxBytes=1024*1024,  # 1MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(logging.Formatter(log_format, date_format))
            
            # 控制台處理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format, date_format))
            
            # 添加處理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """記錄一般資訊"""
        if extra:
            self.logger.info(f"{message} | {extra}")
        else:
            self.logger.info(message)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """記錄除錯資訊"""
        if extra:
            self.logger.debug(f"{message} | {extra}")
        else:
            self.logger.debug(message)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """記錄警告"""
        if extra:
            self.logger.warning(f"{message} | {extra}")
        else:
            self.logger.warning(message)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """記錄錯誤"""
        if extra:
            self.logger.error(f"{message} | {extra}")
        else:
            self.logger.error(message)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """記錄嚴重錯誤"""
        if extra:
            self.logger.critical(f"{message} | {extra}")
        else:
            self.logger.critical(message)
    
    def log_request(self, method: str, url: str, status_code: int, duration: float):
        """記錄請求資訊"""
        self.info("HTTP Request", {
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2)
        })
    
    def log_database_operation(self, operation: str, table: str, record_id: Optional[int] = None):
        """記錄資料庫操作"""
        extra = {"operation": operation, "table": table}
        if record_id:
            extra["record_id"] = record_id
        self.info("Database Operation", extra)
    
    def log_user_action(self, user_id: Optional[int], action: str, details: Optional[Dict] = None):
        """記錄用戶操作"""
        extra = {"action": action}
        if user_id:
            extra["user_id"] = user_id
        if details:
            extra.update(details)
        self.info("User Action", extra)

# 全域日誌器實例
app_logger = LoggerConfig("resume_clinic_scheduler")

# 便利函數
def get_logger(name: str = __name__) -> LoggerConfig:
    """取得日誌器實例"""
    return LoggerConfig(name)

def log_performance(func):
    """效能監控裝飾器"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            app_logger.info(f"Function {func.__name__} completed", {
                "duration_seconds": round(duration, 3),
                "status": "success"
            })
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            app_logger.error(f"Function {func.__name__} failed", {
                "duration_seconds": round(duration, 3),
                "error": str(e),
                "status": "error"
            })
            raise
    return wrapper 