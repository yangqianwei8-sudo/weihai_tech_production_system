#!/bin/bash
# 检查开发服务器状态脚本

BACKEND_PORT=8001
FRONTEND_PORT=8080

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "   开发服务器状态检查"
echo "=========================================="
echo ""

# 检查后端
echo "后端服务 (端口 $BACKEND_PORT):"
BACKEND_PID=$(pgrep -f "manage.py runserver.*$BACKEND_PORT" 2>/dev/null)
if [ -n "$BACKEND_PID" ]; then
    echo -e "  ${GREEN}✓ 进程运行中 (PID: $BACKEND_PID)${NC}"
    
    # 检查端口
    if command -v netstat >/dev/null 2>&1; then
        PORT_STATUS=$(netstat -tlnp 2>/dev/null | grep ":$BACKEND_PORT ")
    elif command -v ss >/dev/null 2>&1; then
        PORT_STATUS=$(ss -tlnp 2>/dev/null | grep ":$BACKEND_PORT ")
    fi
    
    if [ -n "$PORT_STATUS" ]; then
        echo -e "  ${GREEN}✓ 端口正在监听${NC}"
        # 测试 HTTP 连接
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/ 2>/dev/null)
        if [ "$HTTP_CODE" != "000" ]; then
            echo -e "  ${GREEN}✓ HTTP 响应正常 (状态码: $HTTP_CODE)${NC}"
        else
            echo -e "  ${YELLOW}⚠ HTTP 连接失败${NC}"
        fi
    else
        echo -e "  ${RED}✗ 端口未监听${NC}"
    fi
    
    echo "  最新日志 (最后5行):"
    tail -5 /tmp/django_dev.log 2>/dev/null | sed 's/^/    /'
else
    echo -e "  ${RED}✗ 进程未运行${NC}"
fi

echo ""

# 检查前端
echo "前端服务 (端口 $FRONTEND_PORT):"
FRONTEND_PID=$(pgrep -f "vue-cli-service serve" 2>/dev/null)
if [ -n "$FRONTEND_PID" ]; then
    echo -e "  ${GREEN}✓ 进程运行中 (PID: $FRONTEND_PID)${NC}"
    
    # 检查端口
    if command -v netstat >/dev/null 2>&1; then
        PORT_STATUS=$(netstat -tlnp 2>/dev/null | grep ":$FRONTEND_PORT ")
    elif command -v ss >/dev/null 2>&1; then
        PORT_STATUS=$(ss -tlnp 2>/dev/null | grep ":$FRONTEND_PORT ")
    fi
    
    if [ -n "$PORT_STATUS" ]; then
        echo -e "  ${GREEN}✓ 端口正在监听${NC}"
        # 测试 HTTP 连接
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT/ 2>/dev/null)
        if [ "$HTTP_CODE" != "000" ]; then
            echo -e "  ${GREEN}✓ HTTP 响应正常 (状态码: $HTTP_CODE)${NC}"
        else
            echo -e "  ${YELLOW}⚠ HTTP 连接失败${NC}"
        fi
    else
        echo -e "  ${RED}✗ 端口未监听${NC}"
    fi
    
    echo "  最新日志 (最后5行):"
    tail -5 /tmp/vue_dev.log 2>/dev/null | sed 's/^/    /'
else
    echo -e "  ${RED}✗ 进程未运行${NC}"
fi

echo ""
echo "=========================================="
echo "访问地址:"
echo "  - 前端: http://localhost:$FRONTEND_PORT"
echo "  - 后端: http://localhost:$BACKEND_PORT"
echo ""
echo "查看完整日志:"
echo "  - 后端: tail -f /tmp/django_dev.log"
echo "  - 前端: tail -f /tmp/vue_dev.log"
echo "=========================================="

