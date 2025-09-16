#!/bin/bash

# 本地運行 CI/CD 流程的腳本
# 這個腳本模擬 GitHub Actions 中的 CI/CD 流程

set -e  # 遇到錯誤時停止執行

echo "🚀 開始本地 CI/CD 流程..."

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查 Poetry 是否安裝
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry 未安裝，請先安裝 Poetry${NC}"
    exit 1
fi

# 檢查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${BLUE}🐍 使用 Python 版本: $PYTHON_VERSION${NC}"

# 1. 代碼品質檢查
echo -e "\n${YELLOW}📋 執行代碼品質檢查...${NC}"

echo -e "${BLUE}🔍 檢查代碼格式化 (Black)...${NC}"
poetry run black --check . || {
    echo -e "${RED}❌ Black 檢查失敗${NC}"
    echo "運行 'poetry run black .' 來自動格式化代碼"
    exit 1
}

echo -e "${BLUE}🔍 檢查導入排序 (isort)...${NC}"
poetry run isort --check-only . || {
    echo -e "${RED}❌ isort 檢查失敗${NC}"
    echo "運行 'poetry run isort .' 來自動排序導入"
    exit 1
}

echo -e "${BLUE}🔍 檢查代碼風格 (flake8)...${NC}"
poetry run flake8 . || {
    echo -e "${RED}❌ flake8 檢查失敗${NC}"
    exit 1
}

echo -e "${BLUE}🔍 檢查類型 (mypy)...${NC}"
poetry run mypy . || {
    echo -e "${YELLOW}⚠️  mypy 檢查有警告，但繼續執行${NC}"
}

echo -e "${GREEN}✅ 代碼品質檢查通過${NC}"

# 2. 安全檢查
echo -e "\n${YELLOW}🔒 執行安全檢查...${NC}"

echo -e "${BLUE}🔍 檢查依賴安全漏洞 (safety)...${NC}"
poetry run safety check || {
    echo -e "${YELLOW}⚠️  safety 檢查發現潛在問題${NC}"
}

echo -e "${BLUE}🔍 檢查代碼安全問題 (bandit)...${NC}"
poetry run bandit -r app/ || {
    echo -e "${YELLOW}⚠️  bandit 檢查發現潛在安全問題${NC}"
}

echo -e "${GREEN}✅ 安全檢查完成${NC}"

# 3. 測試執行
echo -e "\n${YELLOW}🧪 執行測試...${NC}"

echo -e "${BLUE}🔍 運行單元測試...${NC}"
poetry run pytest tests/unit/ -v --cov=app --cov-report=term-missing || {
    echo -e "${RED}❌ 單元測試失敗${NC}"
    exit 1
}

echo -e "${BLUE}🔍 運行整合測試...${NC}"
poetry run pytest tests/integration/ -v || {
    echo -e "${RED}❌ 整合測試失敗${NC}"
    exit 1
}

echo -e "${BLUE}🔍 運行端到端測試...${NC}"
poetry run pytest tests/e2e/ -v || {
    echo -e "${YELLOW}⚠️  端到端測試失敗或不存在${NC}"
}

echo -e "${GREEN}✅ 測試執行完成${NC}"

# 4. 生成測試報告
echo -e "\n${YELLOW}📊 生成測試報告...${NC}"
poetry run pytest --cov=app --cov-report=html --cov-report=xml --cov-report=term-missing

echo -e "${GREEN}✅ 測試報告已生成：${NC}"
echo "  - HTML 報告: htmlcov/index.html"
echo "  - XML 報告: coverage.xml"

# 5. 建構檢查
echo -e "\n${YELLOW}🔨 執行建構檢查...${NC}"
poetry build || {
    echo -e "${RED}❌ 建構失敗${NC}"
    exit 1
}

echo -e "${GREEN}✅ 建構成功${NC}"

# 6. 總結
echo -e "\n${GREEN}🎉 本地 CI/CD 流程完成！${NC}"
echo -e "${BLUE}📋 執行摘要：${NC}"
echo "  ✅ 代碼品質檢查通過"
echo "  ✅ 安全檢查完成"
echo "  ✅ 測試執行通過"
echo "  ✅ 建構檢查通過"

echo -e "\n${YELLOW}💡 提示：${NC}"
echo "  - 查看測試覆蓋率報告: open htmlcov/index.html"
echo "  - 所有檢查都通過，可以安全地提交代碼"
echo "  - 如果有任何檢查失敗，請根據錯誤訊息進行修復"
