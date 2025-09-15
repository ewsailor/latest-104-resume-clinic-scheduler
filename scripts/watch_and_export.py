#!/usr/bin/env python3
"""監控檔案變更並自動匯出到 Postman。

這個腳本會監控路由和 schema 檔案的變更，
當偵測到變更時自動匯出 OpenAPI JSON 並更新 Postman。
"""

# ===== 標準函式庫 =====
import os
from pathlib import Path
import time

# ===== 本地模組 =====
from export_to_postman import PostmanExporter
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class APIChangeHandler(FileSystemEventHandler):
    """API 變更處理器。"""

    def __init__(self, exporter: PostmanExporter, debounce_time: float = 2.0):
        """初始化處理器。

        Args:
            exporter: Postman 匯出器
            debounce_time: 防抖時間（秒）
        """
        self.exporter = exporter
        self.debounce_time = debounce_time
        self.last_export_time = 0
        self.watched_extensions = {'.py'}
        self.watched_dirs = {
            'app/routers',
            'app/schemas',
            'app/models',
            'app/main.py',
            'app/factory.py',
        }

    def should_export(self, file_path: str) -> bool:
        """判斷是否應該觸發匯出。

        Args:
            file_path: 檔案路徑

        Returns:
            是否應該匯出
        """
        path = Path(file_path)

        # 檢查副檔名
        if path.suffix not in self.watched_extensions:
            return False

        # 檢查是否在監控目錄中
        for watched_dir in self.watched_dirs:
            if watched_dir in str(path):
                return True

        return False

    def on_modified(self, event):
        """檔案修改事件處理。"""
        if event.is_directory:
            return

        if not self.should_export(event.src_path):
            return

        # 防抖處理
        current_time = time.time()
        if current_time - self.last_export_time < self.debounce_time:
            return

        self.last_export_time = current_time

        print(f"📝 偵測到變更: {event.src_path}")
        self.export_after_change()

    def on_created(self, event):
        """檔案建立事件處理。"""
        if event.is_directory:
            return

        if not self.should_export(event.src_path):
            return

        print(f"📄 偵測到新檔案: {event.src_path}")
        self.export_after_change()

    def export_after_change(self):
        """變更後執行匯出。"""
        try:
            print("🔄 開始自動匯出...")

            # 等待一下確保檔案寫入完成
            time.sleep(1)

            # 匯出 OpenAPI JSON
            openapi_data = self.exporter.export_openapi_json(
                "exports/openapi_latest.json"
            )

            # 如果有 Postman API 金鑰，則更新 Postman 集合
            postman_api_key = os.getenv("POSTMAN_API_KEY")
            if postman_api_key:
                collection_id = os.getenv("POSTMAN_COLLECTION_ID")
                success = self.exporter.update_postman_collection(
                    openapi_data, postman_api_key, collection_id
                )
                if success:
                    print("🎉 Postman 集合已自動更新！")
                else:
                    print("⚠️  Postman 集合更新失敗")
            else:
                print("⚠️  未設定 POSTMAN_API_KEY，僅匯出檔案")

            print("✅ 自動匯出完成！")

        except Exception as e:
            print(f"❌ 自動匯出失敗: {e}")


def setup_watcher(project_root: Path) -> Observer:
    """設定檔案監控器。

    Args:
        project_root: 專案根目錄

    Returns:
        監控器實例
    """
    exporter = PostmanExporter()
    event_handler = APIChangeHandler(exporter)

    observer = Observer()

    # 監控特定目錄
    watch_dirs = [
        project_root / "app" / "routers",
        project_root / "app" / "schemas",
        project_root / "app" / "models",
    ]

    for watch_dir in watch_dirs:
        if watch_dir.exists():
            observer.schedule(event_handler, str(watch_dir), recursive=True)
            print(f"👀 監控目錄: {watch_dir}")

    # 監控特定檔案
    watch_files = [
        project_root / "app" / "main.py",
        project_root / "app" / "factory.py",
    ]

    for watch_file in watch_files:
        if watch_file.exists():
            observer.schedule(event_handler, str(watch_file.parent), recursive=False)
            print(f"👀 監控檔案: {watch_file}")

    return observer


def main():
    """主函式。"""
    print("🚀 啟動 API 變更監控器...")

    # 取得專案根目錄
    project_root = Path(__file__).parent.parent

    # 建立匯出目錄
    exports_dir = project_root / "exports"
    exports_dir.mkdir(exist_ok=True)

    # 設定監控器
    observer = setup_watcher(project_root)

    try:
        # 啟動監控
        observer.start()
        print("✅ 監控器已啟動，等待檔案變更...")
        print("💡 提示: 按 Ctrl+C 停止監控")

        # 初始匯出
        print("🔄 執行初始匯出...")
        exporter = PostmanExporter()
        exporter.export_openapi_json("exports/openapi_latest.json")
        print("✅ 初始匯出完成")

        # 保持運行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 停止監控器...")
        observer.stop()
        print("✅ 監控器已停止")

    observer.join()


if __name__ == "__main__":
    main()
