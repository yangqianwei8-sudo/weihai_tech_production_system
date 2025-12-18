#!/bin/bash

# Git自动提交和推送脚本
# 使用方法: ./auto_git_push.sh [提交信息]

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取提交信息，如果没有提供则使用默认信息
COMMIT_MSG="${1:-自动提交: $(date '+%Y-%m-%d %H:%M:%S')}"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}Git自动提交和推送${NC}"
echo -e "${YELLOW}=========================================${NC}"

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}没有需要提交的更改${NC}"
    exit 0
fi

# 显示当前状态
echo -e "${YELLOW}当前分支: $(git rev-parse --abbrev-ref HEAD)${NC}"
echo ""

# 添加所有更改
echo -e "${YELLOW}正在添加更改...${NC}"
git add -A

# 提交更改
echo -e "${YELLOW}正在提交更改...${NC}"
echo -e "${YELLOW}提交信息: $COMMIT_MSG${NC}"
git commit -m "$COMMIT_MSG"

# 检查commit是否成功
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 提交成功${NC}"
    
    # 推送到远程仓库
    echo -e "${YELLOW}正在推送到远程仓库...${NC}"
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    
    # 如果设置了GITHUB_TOKEN环境变量，使用token进行推送
    if [ -n "$GITHUB_TOKEN" ]; then
        REMOTE_URL=$(git remote get-url origin)
        # 如果URL是HTTPS格式，临时替换为带token的URL
        if [[ "$REMOTE_URL" == https://* ]]; then
            REPO_PATH=$(echo "$REMOTE_URL" | sed 's|https://github.com/||')
            git remote set-url origin "https://${GITHUB_TOKEN}@github.com/${REPO_PATH}"
            git push origin "$BRANCH"
            # 恢复原始URL（移除token）
            git remote set-url origin "$REMOTE_URL"
        else
            git push origin "$BRANCH"
        fi
    else
        git push origin "$BRANCH"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 推送成功${NC}"
        echo -e "${GREEN}=========================================${NC}"
    else
        echo -e "${RED}✗ 推送失败${NC}"
        echo -e "${YELLOW}提示: 如果使用HTTPS，可以设置GITHUB_TOKEN环境变量:${NC}"
        echo -e "${YELLOW}  export GITHUB_TOKEN=your_personal_access_token${NC}"
        echo -e "${YELLOW}或者使用SSH方式配置远程仓库${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ 提交失败${NC}"
    exit 1
fi


