#!/usr/bin/env python3
"""
配置驗證測試腳本

用於驗證所有環境變數和配置是否正確載入。
支援多種測試模式：完整測試、快速測試、特定服務測試。

使用方法:
    python scripts/test_config.py          # 完整測試
    python scripts/test_config.py --quick  # 快速測試
    python scripts/test_config.py --db     # 只測試資料庫配置
    python scripts/test_config.py --api    # 只測試 API 配置
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core import settings


class Colors:
    """終端機顏色定義"""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ConfigTester:
    """配置測試器"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_count = 0

    def log_success(self, message: str):
        """記錄成功訊息"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
        self.success_count += 1
        self.total_count += 1

    def log_warning(self, message: str):
        """記錄警告訊息"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
        self.warnings.append(message)
        self.total_count += 1

    def log_error(self, message: str):
        """記錄錯誤訊息"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
        self.errors.append(message)
        self.total_count += 1

    def log_info(self, message: str):
        """記錄資訊訊息"""
        print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

    def test_basic_config(self):
        """測試基本配置"""
        print(f"{Colors.HEADER}🔧 基本配置測試{Colors.ENDC}")

        # 應用程式基本資訊
        self.log_info(f"應用程式名稱: {settings.app_name}")
        self.log_info(f"應用程式版本: {settings.app_version}")
        self.log_info(f"應用程式環境: {settings.app_env}")
        self.log_info(f"除錯模式: {settings.debug}")

        # 驗證環境設定
        if settings.app_env in ["development", "staging", "production"]:
            self.log_success(f"應用程式環境設定正確: {settings.app_env}")
        else:
            self.log_error(f"應用程式環境設定錯誤: {settings.app_env}")

        # 驗證除錯模式
        if settings.is_development and settings.debug:
            self.log_success("開發環境除錯模式已啟用")
        elif settings.is_production and not settings.debug:
            self.log_success("生產環境除錯模式已關閉")
        else:
            self.log_warning("除錯模式設定可能需要調整")

        print()

    def test_security_config(self):
        """測試安全配置"""
        print(f"{Colors.HEADER}🔒 安全配置測試{Colors.ENDC}")

        # SECRET_KEY 測試
        if settings.secret_key:
            secret_value = settings.secret_key.get_secret_value()
            if len(secret_value) >= 32:
                self.log_success(
                    f"SECRET_KEY 已設定且長度足夠 ({len(secret_value)} 字元)"
                )
                self.log_info(f"SECRET_KEY 預覽: {secret_value[:8]}...")
            else:
                self.log_error(f"SECRET_KEY 長度不足: {len(secret_value)} 字元")
        else:
            self.log_error("SECRET_KEY 未設定")

        # SESSION_SECRET 測試
        if settings.session_secret:
            session_value = settings.session_secret.get_secret_value()
            if len(session_value) >= 32:
                self.log_success(
                    f"SESSION_SECRET 已設定且長度足夠 ({len(session_value)} 字元)"
                )
                self.log_info(f"SESSION_SECRET 預覽: {session_value[:8]}...")
            else:
                self.log_error(f"SESSION_SECRET 長度不足: {len(session_value)} 字元")
        else:
            self.log_error("SESSION_SECRET 未設定")

        print()

    def test_database_config(self):
        """測試資料庫配置"""
        print(f"{Colors.HEADER}🗄️ 資料庫配置測試{Colors.ENDC}")

        # MySQL 配置
        self.log_info(f"MySQL 主機: {settings.mysql_host}")
        self.log_info(f"MySQL 連接埠: {settings.mysql_port}")
        self.log_info(f"MySQL 資料庫: {settings.mysql_database}")
        self.log_info(f"MySQL 字符集: {settings.mysql_charset}")

        # MySQL 使用者驗證
        if settings.mysql_user:
            if settings.mysql_user.lower() != "root":
                self.log_success(f"MySQL 使用者設定正確: {settings.mysql_user}")
            else:
                self.log_error("MySQL 使用者不應為 root")
        else:
            self.log_error("MySQL 使用者未設定")

        # MySQL 密碼驗證
        if settings.mysql_password:
            password_value = settings.mysql_password.get_secret_value()
            if password_value:
                self.log_success("MySQL 密碼已設定")
            else:
                self.log_error("MySQL 密碼為空")
        else:
            self.log_error("MySQL 密碼未設定")

        # 連接字串測試
        try:
            connection_string = settings.mysql_connection_string
            self.log_success("MySQL 連接字串生成成功")
            self.log_info(f"連接字串: {connection_string}")
        except Exception as e:
            self.log_error(f"MySQL 連接字串錯誤: {e}")

        print()

    def test_redis_config(self):
        """測試 Redis 配置"""
        print(f"{Colors.HEADER}📦 Redis 配置測試{Colors.ENDC}")

        self.log_info(f"Redis 主機: {settings.redis_host}")
        self.log_info(f"Redis 連接埠: {settings.redis_port}")
        self.log_info(f"Redis 資料庫: {settings.redis_db}")

        # Redis 密碼（可選）
        if settings.redis_password:
            self.log_success("Redis 密碼已設定")
        else:
            self.log_warning("Redis 密碼未設定（開發環境可接受）")

        # 連接字串測試
        try:
            connection_string = settings.redis_connection_string
            self.log_success("Redis 連接字串生成成功")
            self.log_info(f"連接字串: {connection_string}")
        except Exception as e:
            self.log_error(f"Redis 連接字串錯誤: {e}")

        print()

    def test_api_config(self):
        """測試 API 配置"""
        print(f"{Colors.HEADER}🌐 API 配置測試{Colors.ENDC}")

        # API 超時配置
        self.log_info(f"API 總超時: {settings.api_timeout} 秒")
        self.log_info(f"API 連接超時: {settings.api_connect_timeout} 秒")
        self.log_info(f"API 讀取超時: {settings.api_read_timeout} 秒")

        # 驗證超時設定
        if 0 < settings.api_timeout <= 300:
            self.log_success("API 總超時設定合理")
        else:
            self.log_error(f"API 總超時設定不合理: {settings.api_timeout} 秒")

        if 0 < settings.api_connect_timeout <= 60:
            self.log_success("API 連接超時設定合理")
        else:
            self.log_error(f"API 連接超時設定不合理: {settings.api_connect_timeout} 秒")

        # 104 API 配置（可選）
        if settings.api_104_base_url:
            self.log_info(f"104 API 基礎 URL: {settings.api_104_base_url}")
        else:
            self.log_warning("104 API 基礎 URL 未設定")

        if settings.api_104_client_id:
            self.log_info("104 API 客戶端 ID 已設定")
        else:
            self.log_warning("104 API 客戶端 ID 未設定")

        if settings.api_104_client_secret:
            self.log_success("104 API 密鑰已設定")
        else:
            self.log_warning("104 API 密鑰未設定")

        print()

    def test_cors_config(self):
        """測試 CORS 配置"""
        print(f"{Colors.HEADER}🌍 CORS 配置測試{Colors.ENDC}")

        self.log_info(f"CORS 來源: {settings.cors_origins}")
        self.log_info(f"CORS 來源列表: {settings.cors_origins_list}")

        if settings.cors_origins_list:
            self.log_success("CORS 配置已設定")
        else:
            self.log_error("CORS 配置為空")

        print()

    def test_optional_services(self):
        """測試可選服務配置"""
        print(f"{Colors.HEADER}🔧 可選服務配置測試{Colors.ENDC}")

        # SMTP 配置
        if settings.has_smtp_config:
            self.log_success("SMTP 配置完整")
            smtp_config = settings.get_smtp_config()
            self.log_info(f"SMTP 主機: {smtp_config.get('host')}")
            self.log_info(f"SMTP 連接埠: {smtp_config.get('port')}")
        else:
            self.log_warning("SMTP 配置不完整（開發環境可接受）")

        # AWS 配置
        if settings.has_aws_config:
            self.log_success("AWS 配置完整")
        else:
            self.log_warning("AWS 配置不完整（開發環境可接受）")

        # 104 API 配置
        if settings.has_104_api_config:
            self.log_success("104 API 配置完整")
        else:
            self.log_warning("104 API 配置不完整（開發環境可接受）")

        print()

    def test_paths(self):
        """測試路徑配置"""
        print(f"{Colors.HEADER}📁 路徑配置測試{Colors.ENDC}")

        paths_to_check = [
            ("專案根目錄", settings.project_root),
            ("應用程式目錄", settings.app_dir),
            ("靜態檔案目錄", settings.static_dir),
            ("模板目錄", settings.templates_dir),
        ]

        for name, path in paths_to_check:
            if path.exists():
                self.log_success(f"{name}存在: {path}")
            else:
                self.log_warning(f"{name}不存在: {path}")

        print()

    def run_quick_test(self):
        """執行快速測試"""
        print(f"{Colors.BOLD}🚀 快速配置檢查{Colors.ENDC}")
        print("=" * 50)

        self.test_basic_config()
        self.test_security_config()
        self.test_database_config()

    def run_full_test(self):
        """執行完整測試"""
        print(f"{Colors.BOLD}🚀 完整配置驗證測試{Colors.ENDC}")
        print("=" * 50)

        self.test_basic_config()
        self.test_security_config()
        self.test_database_config()
        self.test_redis_config()
        self.test_api_config()
        self.test_cors_config()
        self.test_optional_services()
        self.test_paths()

    def print_summary(self):
        """印出測試摘要"""
        print(f"{Colors.BOLD}📊 測試摘要{Colors.ENDC}")
        print("=" * 50)
        print(f"總測試項目: {self.total_count}")
        print(f"成功: {self.success_count}")
        print(f"警告: {len(self.warnings)}")
        print(f"錯誤: {len(self.errors)}")

        if self.errors:
            print(f"\n{Colors.FAIL}❌ 錯誤項目:{Colors.ENDC}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n{Colors.WARNING}⚠️ 警告項目:{Colors.ENDC}")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors:
            print(f"\n{Colors.OKGREEN}✅ 所有關鍵配置都正確！{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}❌ 請修正上述錯誤後重新測試{Colors.ENDC}")


def main():
    """主函式"""
    parser = argparse.ArgumentParser(description="配置驗證測試腳本")
    parser.add_argument("--quick", action="store_true", help="執行快速測試")
    parser.add_argument("--db", action="store_true", help="只測試資料庫配置")
    parser.add_argument("--api", action="store_true", help="只測試 API 配置")

    args = parser.parse_args()

    tester = ConfigTester()

    try:
        if args.quick:
            tester.run_quick_test()
        elif args.db:
            print(f"{Colors.BOLD}🗄️ 資料庫配置測試{Colors.ENDC}")
            tester.test_database_config()
        elif args.api:
            print(f"{Colors.BOLD}🌐 API 配置測試{Colors.ENDC}")
            tester.test_api_config()
        else:
            tester.run_full_test()

        tester.print_summary()

        # 如果有錯誤，返回非零退出碼
        if tester.errors:
            sys.exit(1)

    except Exception as e:
        print(f"{Colors.FAIL}❌ 測試執行失敗: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
