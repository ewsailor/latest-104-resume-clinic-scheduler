#!/bin/bash

# 快速測試腳本 - 用於開發期間的快速驗證

set -e

echo "🚀 快速測試開始..."

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 代碼格式化
echo -e "\n${BLUE}🔧 自動格式化代碼...${NC}"
poetry run black .
poetry run isort .

# 2. 運行單元測試
echo -e "\n${BLUE}🧪 運行單元測試...${NC}"
poetry run pytest tests/unit/ -v --tb=short

echo -e "\n${GREEN}✅ 快速測試完成！${NC}"
echo -e "${YELLOW}💡 提示：運行完整 CI 流程請使用 scripts/run-ci-locally.sh${NC}"
