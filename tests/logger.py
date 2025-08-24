"""
測試專用日誌管理模組。

提供統一的日誌記錄功能，用於測試檔案中的日誌輸出。
支援不同級別的日誌記錄，並可根據環境配置控制輸出。
"""

import logging
import os


class TestLogger:
    """測試專用日誌記錄器"""

    _instance = None
    _logger: logging.Logger | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        """設定日誌記錄器"""
        self._logger = logging.getLogger('test_logger')

        # 避免重複添加 handler
        if not self._logger.handlers:
            # 設定日誌級別
            log_level = os.getenv('TEST_LOG_LEVEL', 'INFO').upper()
            self._logger.setLevel(getattr(logging, log_level, logging.INFO))

            # 建立 console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 設定格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S',
            )
            console_handler.setFormatter(formatter)

            # 添加 handler
            self._logger.addHandler(console_handler)

    def info(self, message: str):
        """記錄資訊日誌"""
        self._logger.info(message)

    def debug(self, message: str):
        """記錄除錯日誌"""
        self._logger.debug(message)

    def warning(self, message: str):
        """記錄警告日誌"""
        self._logger.warning(message)

    def error(self, message: str):
        """記錄錯誤日誌"""
        self._logger.error(message)

    def critical(self, message: str):
        """記錄嚴重錯誤日誌"""
        self._logger.critical(message)


# 全域日誌實例
test_logger = TestLogger()


def log_test_info(message: str):
    """記錄測試資訊的便捷函數"""
    test_logger.info(message)


def log_test_debug(message: str):
    """記錄測試除錯資訊的便捷函數"""
    test_logger.debug(message)


def log_test_warning(message: str):
    """記錄測試警告的便捷函數"""
    test_logger.warning(message)


def log_test_error(message: str):
    """記錄測試錯誤的便捷函數"""
    test_logger.error(message)
