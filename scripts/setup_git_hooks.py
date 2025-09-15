#!/usr/bin/env python3
"""設定 Git hooks 自動匯出到 Postman。

這個腳本會設定 Git hooks，在提交或推送時自動匯出 OpenAPI JSON。
"""

# ===== 標準函式庫 =====
import os
from pathlib import Path
import sys


def create_pre_commit_hook(project_root: Path) -> str:
    """建立 pre-commit hook。

    Args:
        project_root: 專案根目錄

    Returns:
        hook 檔案內容
    """
    return f"""#!/bin/bash
# Pre-commit hook: 自動匯出 OpenAPI JSON

echo "🔄 正在匯出 OpenAPI JSON..."

# 切換到專案根目錄
cd "{project_root}"

# 執行匯出腳本
python scripts/export_to_postman.py

# 檢查匯出是否成功
if [ $? -eq 0 ]; then
    echo "✅ OpenAPI JSON 匯出成功"
    exit 0
else
    echo "❌ OpenAPI JSON 匯出失敗"
    exit 1
fi
"""


def create_post_commit_hook(project_root: Path) -> str:
    """建立 post-commit hook。

    Args:
        project_root: 專案根目錄

    Returns:
        hook 檔案內容
    """
    return f"""#!/bin/bash
# Post-commit hook: 自動更新 Postman 集合

echo "🔄 正在更新 Postman 集合..."

# 切換到專案根目錄
cd "{project_root}"

# 檢查是否有 Postman API 金鑰
if [ -z "$POSTMAN_API_KEY" ]; then
    echo "⚠️  未設定 POSTMAN_API_KEY，跳過 Postman 更新"
    exit 0
fi

# 執行匯出腳本
python scripts/export_to_postman.py

# 檢查匯出是否成功
if [ $? -eq 0 ]; then
    echo "✅ Postman 集合更新成功"
else
    echo "❌ Postman 集合更新失敗"
fi
"""


def create_pre_push_hook(project_root: Path) -> str:
    """建立 pre-push hook。

    Args:
        project_root: 專案根目錄

    Returns:
        hook 檔案內容
    """
    return f"""#!/bin/bash
# Pre-push hook: 確保 Postman 集合是最新的

echo "🔄 檢查 Postman 集合是否為最新..."

# 切換到專案根目錄
cd "{project_root}"

# 檢查是否有 Postman API 金鑰
if [ -z "$POSTMAN_API_KEY" ]; then
    echo "⚠️  未設定 POSTMAN_API_KEY，跳過 Postman 檢查"
    exit 0
fi

# 執行匯出腳本
python scripts/export_to_postman.py

# 檢查匯出是否成功
if [ $? -eq 0 ]; then
    echo "✅ Postman 集合已更新，可以推送"
    exit 0
else
    echo "❌ Postman 集合更新失敗，請檢查後再推送"
    exit 1
fi
"""


def setup_git_hooks(project_root: Path):
    """設定 Git hooks。

    Args:
        project_root: 專案根目錄
    """
    git_hooks_dir = project_root / ".git" / "hooks"

    if not git_hooks_dir.exists():
        print("❌ 找不到 .git/hooks 目錄，請確認這是一個 Git 倉庫")
        return False

    hooks = {
        "pre-commit": create_pre_commit_hook(project_root),
        "post-commit": create_post_commit_hook(project_root),
        "pre-push": create_pre_push_hook(project_root),
    }

    for hook_name, hook_content in hooks.items():
        hook_file = git_hooks_dir / hook_name

        # 寫入 hook 檔案
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)

        # 設定執行權限
        os.chmod(hook_file, 0o755)

        print(f"✅ 已設定 {hook_name} hook: {hook_file}")

    return True


def create_env_template(project_root: Path):
    """建立環境變數範本檔案。

    Args:
        project_root: 專案根目錄
    """
    env_template = """# Postman 自動匯出設定
# 從 https://web.postman.co/settings/me/api-keys 取得 API 金鑰
POSTMAN_API_KEY=your_postman_api_key_here

# 可選: 指定要更新的集合 ID（如果不設定會建立新集合）
# POSTMAN_COLLECTION_ID=your_collection_id_here
"""

    env_file = project_root / ".env.postman"

    if not env_file.exists():
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)

        print(f"✅ 已建立環境變數範本: {env_file}")
        print("💡 請編輯此檔案並設定您的 Postman API 金鑰")
    else:
        print(f"⚠️  環境變數檔案已存在: {env_file}")


def main():
    """主函式。"""
    print("🚀 設定 Git hooks 自動匯出到 Postman...")

    # 取得專案根目錄
    project_root = Path(__file__).parent.parent

    # 設定 Git hooks
    if setup_git_hooks(project_root):
        print("✅ Git hooks 設定完成")
    else:
        print("❌ Git hooks 設定失敗")
        sys.exit(1)

    # 建立環境變數範本
    create_env_template(project_root)

    print("\n📋 設定完成！")
    print("\n📝 使用說明:")
    print("1. 編輯 .env.postman 檔案，設定您的 Postman API 金鑰")
    print("2. 在終端中執行: source .env.postman")
    print("3. 現在每次提交或推送時都會自動更新 Postman 集合")
    print("\n🔧 手動匯出:")
    print("python scripts/export_to_postman.py")
    print("\n👀 監控模式:")
    print("python scripts/watch_and_export.py")


if __name__ == "__main__":
    main()
