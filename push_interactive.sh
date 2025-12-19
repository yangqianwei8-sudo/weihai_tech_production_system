#!/bin/bash

# 交互式GitHub推送脚本
# 安全地输入token（不会显示在终端）

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}════════════════════════════════════════${NC}"
echo -e "${YELLOW}GitHub 代码推送工具${NC}"
echo -e "${YELLOW}════════════════════════════════════════${NC}"
echo ""

# 检查是否有待推送的提交
UNPUSHED=$(git log origin/main..HEAD --oneline 2>/dev/null | wc -l)
if [ "$UNPUSHED" -eq 0 ]; then
    echo -e "${YELLOW}没有待推送的提交${NC}"
    exit 0
fi

echo -e "${YELLOW}待推送的提交数: ${UNPUSHED}${NC}"
echo ""

# 安全地读取token
read -sp "请输入您的GitHub Personal Access Token: " TOKEN
echo ""

if [ -z "$TOKEN" ]; then
    echo -e "${RED}错误: Token不能为空${NC}"
    exit 1
fi

# 使用token推送
REMOTE_URL=$(git remote get-url origin)
if [[ "$REMOTE_URL" == https://github.com/* ]]; then
    REPO_PATH=$(echo "$REMOTE_URL" | sed 's|https://github.com/||' | sed 's|\.git$||')
    TOKEN_URL="https://${TOKEN}@github.com/${REPO_PATH}.git"
    
    echo ""
    echo -e "${YELLOW}正在推送到 GitHub...${NC}"
    
    ORIGINAL_URL=$(git remote get-url origin)
    git remote set-url origin "$TOKEN_URL"
    
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    git push origin "$BRANCH"
    PUSH_STATUS=$?
    
    git remote set-url origin "$ORIGINAL_URL"
    
    if [ $PUSH_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ 推送成功！${NC}"
        exit 0
    else
        echo -e "${RED}✗ 推送失败，请检查token是否正确${NC}"
        exit 1
    fi
else
    echo -e "${RED}错误: 不支持的远程仓库格式${NC}"
    exit 1
fi
