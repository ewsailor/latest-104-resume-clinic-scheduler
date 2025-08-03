"""
中間件套件。

包含所有 FastAPI 應用程式的中間件，如 CORS、認證、日誌等。
"""

from .cors import setup_cors_middleware

__all__ = ["setup_cors_middleware"]
