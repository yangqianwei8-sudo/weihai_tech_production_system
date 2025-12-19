#!/bin/bash

# 使用GitHub Token推送脚本
# 使用方法: ./push_with_token.sh <your_github_token>

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}错误: 请提供GitHub Personal Access Token${NC}"
    echo -e "${YELLOW}使用方法: ./push_with_token.sh <your_token>${NC}"
    echo -e "${YELLOW}或者设置环境变量: export GITHUB_TOKEN=your_token${NC}"
    exit 1
fi

TOKEN=$1
REMOTE_URL=$(git remote get-url origin)

# 提取仓库路径
if [[ "$REMOTE_URL" == https://github.com/* ]]; then
    REPO_PATH=$(echo "$REMOTE_URL" | sed 's|https://github.com/||' | sed 's|\.git$||')
    TOKEN_URL="https://${TOKEN}@github.com/${REPO_PATH}.git"
    
    echo -e "${YELLOW}正在推送到 GitHub...${NC}"
    echo -e "${YELLOW}仓库: ${REPO_PATH}${NC}"
    
    # 临时设置远程URL为带token的URL
    ORIGINAL_URL=$(git remote get-url origin)
    git remote set-url origin "$TOKEN_URL"
    
    # 推送
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    git push origin "$BRANCH"
    PUSH_STATUS=$?
    
    # 恢复原始URL（移除token）
    git remote set-url origin "$ORIGINAL_URL"
    
    if [ $PUSH_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ 推送成功！${NC}"
        exit 0
    else
        echo -e "${RED}✗ 推送失败${NC}"
        exit 1
    fi
else
    echo -e "${RED}错误: 不支持的远程仓库格式${NC}"
    exit 1
fi


