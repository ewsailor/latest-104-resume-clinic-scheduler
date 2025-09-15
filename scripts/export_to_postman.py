#!/usr/bin/env python3
"""自動從 Swagger 匯出 OpenAPI JSON 並更新 Postman 集合。

這個腳本會：
1. 從 FastAPI 應用程式匯出 OpenAPI JSON
2. 自動更新 Postman 集合
3. 支援多種匯入方式
"""

# ===== 標準函式庫 =====
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, Optional

# ===== 第三方套件 =====
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===== 本地模組 =====
# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import app


class PostmanExporter:
    """Postman 匯出器類別。"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """初始化匯出器。

        Args:
            base_url: API 基礎 URL
        """
        self.base_url = base_url
        self.openapi_url = f"{base_url}/openapi.json"
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """建立具有重試機制的 HTTP 會話。"""
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def export_openapi_json(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """從 FastAPI 應用程式匯出 OpenAPI JSON。

        Args:
            output_path: 輸出檔案路徑，如果為 None 則不儲存檔案

        Returns:
            OpenAPI JSON 資料
        """
        print("🔄 正在匯出 OpenAPI JSON...")

        try:
            # 方法 1: 直接從 FastAPI 應用程式取得
            openapi_schema = app.openapi()

            # 方法 2: 如果應用程式未運行，嘗試從 URL 取得
            if not openapi_schema:
                print("⚠️  無法從應用程式取得 schema，嘗試從 URL 取得...")
                response = self.session.get(self.openapi_url, timeout=10)
                response.raise_for_status()
                openapi_schema = response.json()

            # 儲存到檔案
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

                print(f"✅ OpenAPI JSON 已儲存到: {output_file}")

            print(f"📊 匯出完成，包含 {len(openapi_schema.get('paths', {}))} 個端點")
            return openapi_schema

        except Exception as e:
            print(f"❌ 匯出 OpenAPI JSON 失敗: {e}")
            raise

    def update_postman_collection(
        self,
        openapi_data: Dict[str, Any],
        postman_api_key: str,
        collection_id: Optional[str] = None,
        collection_name: str = "104 Resume Clinic API",
    ) -> bool:
        """更新 Postman 集合。

        Args:
            openapi_data: OpenAPI JSON 資料
            postman_api_key: Postman API 金鑰
            collection_id: 現有集合 ID，如果為 None 則建立新集合
            collection_name: 集合名稱

        Returns:
            是否成功更新
        """
        print("🔄 正在更新 Postman 集合...")

        try:
            # 轉換 OpenAPI 到 Postman 格式
            postman_collection = self._convert_to_postman_format(
                openapi_data, collection_name
            )

            if collection_id:
                # 更新現有集合
                return self._update_existing_collection(
                    collection_id, postman_collection, postman_api_key
                )
            else:
                # 建立新集合
                return self._create_new_collection(postman_collection, postman_api_key)

        except Exception as e:
            print(f"❌ 更新 Postman 集合失敗: {e}")
            return False

    def _convert_to_postman_format(
        self, openapi_data: Dict[str, Any], collection_name: str
    ) -> Dict[str, Any]:
        """將 OpenAPI 格式轉換為 Postman 格式。"""
        collection = {
            "info": {
                "name": collection_name,
                "description": openapi_data.get("info", {}).get("description", ""),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [],
            "variable": [{"key": "base_url", "value": self.base_url, "type": "string"}],
        }

        # 轉換路徑
        for path, methods in openapi_data.get("paths", {}).items():
            for method, details in methods.items():
                if method.upper() in [
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE",
                    "OPTIONS",
                ]:
                    item = self._create_postman_item(path, method.upper(), details)
                    collection["item"].append(item)

        return collection

    def _create_postman_item(
        self, path: str, method: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """建立 Postman 項目。"""
        return {
            "name": details.get("summary", f"{method} {path}"),
            "request": {
                "method": method,
                "header": [],
                "url": {
                    "raw": f"{{{{base_url}}}}{path}",
                    "host": ["{{base_url}}"],
                    "path": path.strip("/").split("/"),
                },
                "description": details.get("description", ""),
            },
            "response": [],
        }

    def _update_existing_collection(
        self, collection_id: str, collection_data: Dict[str, Any], api_key: str
    ) -> bool:
        """更新現有的 Postman 集合。"""
        url = f"https://api.getpostman.com/collections/{collection_id}"
        headers = {"X-API-Key": api_key}

        response = self.session.put(
            url, json={"collection": collection_data}, headers=headers
        )
        response.raise_for_status()

        print(f"✅ Postman 集合已更新: {collection_id}")
        return True

    def _create_new_collection(
        self, collection_data: Dict[str, Any], api_key: str
    ) -> bool:
        """建立新的 Postman 集合。"""
        url = "https://api.getpostman.com/collections"
        headers = {"X-API-Key": api_key}

        response = self.session.post(
            url, json={"collection": collection_data}, headers=headers
        )
        response.raise_for_status()

        result = response.json()
        collection_id = result["collection"]["id"]
        print(f"✅ 新 Postman 集合已建立: {collection_id}")
        return True

    def export_to_file(self, output_dir: str = "exports") -> str:
        """匯出到檔案系統。

        Args:
            output_dir: 輸出目錄

        Returns:
            輸出檔案路徑
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"openapi_{timestamp}.json"
        output_path = output_dir / filename

        openapi_data = self.export_openapi_json(str(output_path))

        # 同時建立 Postman 格式的檔案
        postman_file = output_dir / f"postman_{timestamp}.json"
        postman_data = self._convert_to_postman_format(
            openapi_data, f"104 Resume Clinic API - {timestamp}"
        )

        with open(postman_file, 'w', encoding='utf-8') as f:
            json.dump(postman_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Postman 格式檔案已儲存到: {postman_file}")

        return str(output_path)


def main():
    """主函式。"""
    print("🚀 開始自動匯出到 Postman...")

    # 從環境變數取得 Postman API 金鑰
    postman_api_key = os.getenv("POSTMAN_API_KEY")
    collection_id = os.getenv("POSTMAN_COLLECTION_ID")  # 可選

    # 建立匯出器
    exporter = PostmanExporter()

    try:
        # 匯出 OpenAPI JSON
        openapi_data = exporter.export_openapi_json("exports/openapi_latest.json")

        # 如果有 Postman API 金鑰，則更新 Postman 集合
        if postman_api_key:
            success = exporter.update_postman_collection(
                openapi_data, postman_api_key, collection_id
            )
            if success:
                print("🎉 Postman 集合更新成功！")
            else:
                print("⚠️  Postman 集合更新失敗，但檔案已匯出")
        else:
            print("⚠️  未設定 POSTMAN_API_KEY，僅匯出檔案")
            exporter.export_to_file()

        print("✅ 匯出完成！")

    except Exception as e:
        print(f"❌ 匯出失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
