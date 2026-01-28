#!/bin/bash
# 启动开发服务器脚本

PROJECT_DIR="/home/devbox/project/vihhi/weihai_tech_production_system"
VENV_DIR="/home/devbox/project/.venv"
BACKEND_PORT=8001
FRONTEND_PORT=8080

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "   启动开发服务器"
echo "=========================================="
echo ""

# 检查项目目录是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}✗ 错误: 项目目录不存在: $PROJECT_DIR${NC}"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}✗ 错误: 虚拟环境不存在: $VENV_DIR${NC}"
    echo "请先创建虚拟环境: python3 -m venv $VENV_DIR"
    exit 1
fi

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
            echo -e "${YELLOW}⚠ 警告: 端口 $port 已被占用${NC}"
            netstat -tlnp 2>/dev/null | grep ":$port " | head -1
            return 1
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tlnp 2>/dev/null | grep -q ":$port "; then
            echo -e "${YELLOW}⚠ 警告: 端口 $port 已被占用${NC}"
            ss -tlnp 2>/dev/null | grep ":$port " | head -1
            return 1
        fi
    fi
    return 0
}

# 停止占用端口的进程
stop_port_process() {
    local port=$1
    local service_name=$2
    
    # 通过端口查找进程
    local pids=""
    if command -v lsof >/dev/null 2>&1; then
        pids=$(lsof -ti :$port 2>/dev/null)
    elif command -v ss >/dev/null 2>&1; then
        pids=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oP 'pid=\K[0-9]+' | sort -u)
    fi
    
    # 也通过进程名查找
    if [ "$service_name" = "backend" ]; then
        pids="$pids $(pgrep -f "manage.py runserver.*$port" 2>/dev/null)"
    elif [ "$service_name" = "frontend" ]; then
        pids="$pids $(pgrep -f "vue-cli-service serve" 2>/dev/null)"
    fi
    
    # 去重并停止进程
    if [ -n "$pids" ]; then
        for pid in $(echo $pids | tr ' ' '\n' | sort -u); do
            if ps -p $pid > /dev/null 2>&1; then
                echo "  停止占用端口 $port 的进程 (PID: $pid)..."
                kill $pid 2>/dev/null
            fi
        done
    fi
}

# 检查并停止旧服务
echo "检查并停止旧服务..."

# 停止后端相关进程
stop_port_process $BACKEND_PORT "backend"
OLD_BACKEND=$(pgrep -f "manage.py runserver.*$BACKEND_PORT" 2>/dev/null)
if [ -n "$OLD_BACKEND" ]; then
    for pid in $OLD_BACKEND; do
        echo "  停止旧的后端服务 (PID: $pid)..."
        kill $pid 2>/dev/null
    done
fi

# 停止前端相关进程
stop_port_process $FRONTEND_PORT "frontend"
OLD_FRONTEND=$(pgrep -f "vue-cli-service serve" 2>/dev/null)
if [ -n "$OLD_FRONTEND" ]; then
    for pid in $OLD_FRONTEND; do
        echo "  停止旧的前端服务 (PID: $pid)..."
        kill $pid 2>/dev/null
    done
fi

# 等待进程完全退出
echo "  等待进程退出..."
for i in {1..5}; do
    BACKEND_STILL_RUNNING=$(pgrep -f "manage.py runserver.*$BACKEND_PORT" 2>/dev/null)
    FRONTEND_STILL_RUNNING=$(pgrep -f "vue-cli-service serve" 2>/dev/null)
    
    if [ -z "$BACKEND_STILL_RUNNING" ] && [ -z "$FRONTEND_STILL_RUNNING" ]; then
        break
    fi
    
    if [ $i -lt 5 ]; then
        sleep 1
    else
        # 如果还有进程在运行，强制杀死
        echo "  强制停止残留进程..."
        [ -n "$BACKEND_STILL_RUNNING" ] && kill -9 $BACKEND_STILL_RUNNING 2>/dev/null
        [ -n "$FRONTEND_STILL_RUNNING" ] && kill -9 $FRONTEND_STILL_RUNNING 2>/dev/null
        sleep 1
    fi
done

# 再次检查端口，确保已释放
echo "  检查端口是否已释放..."
if check_port $BACKEND_PORT "后端"; then
    echo -e "  ${GREEN}✓ 后端端口 $BACKEND_PORT 已释放${NC}"
else
    echo -e "  ${YELLOW}⚠ 后端端口 $BACKEND_PORT 仍被占用，尝试强制清理...${NC}"
    stop_port_process $BACKEND_PORT "backend"
    sleep 1
fi

if check_port $FRONTEND_PORT "前端"; then
    echo -e "  ${GREEN}✓ 前端端口 $FRONTEND_PORT 已释放${NC}"
else
    echo -e "  ${YELLOW}⚠ 前端端口 $FRONTEND_PORT 仍被占用，尝试强制清理...${NC}"
    stop_port_process $FRONTEND_PORT "frontend"
    sleep 1
fi

# 检查并启动 cron 服务
echo ""
echo "检查 cron 定时任务服务..."
if ! ps aux | grep -E "[c]ron|[/]usr/sbin/cron" > /dev/null 2>&1; then
    echo "  启动 cron 服务..."
    if sudo service cron start > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Cron 服务已启动${NC}"
    else
        echo -e "  ${YELLOW}⚠ Cron 服务启动失败（可能需要手动启动）${NC}"
    fi
else
    echo -e "  ${GREEN}✓ Cron 服务已在运行${NC}"
fi

# 启动后端
echo ""
echo "启动后端 Django 开发服务器..."
cd "$PROJECT_DIR" || {
    echo -e "${RED}✗ 错误: 无法进入项目目录${NC}"
    exit 1
}

if [ ! -f "manage.py" ]; then
    echo -e "${RED}✗ 错误: 找不到 manage.py 文件${NC}"
    exit 1
fi

source "$VENV_DIR/bin/activate" || {
    echo -e "${RED}✗ 错误: 无法激活虚拟环境${NC}"
    exit 1
}

# 检查 Python 和 Django
if ! command -v python >/dev/null 2>&1; then
    echo -e "${RED}✗ 错误: 找不到 python 命令${NC}"
    exit 1
fi

# 运行 Django 检查
echo "  运行 Django 系统检查..."
python manage.py check > /tmp/django_check.log 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ 警告: Django 系统检查发现问题${NC}"
    cat /tmp/django_check.log
fi

python manage.py runserver 0.0.0.0:$BACKEND_PORT > /tmp/django_dev.log 2>&1 &
BACKEND_PID=$!
echo "  后端进程 ID: $BACKEND_PID"
echo "  后端日志: tail -f /tmp/django_dev.log"

# 等待后端服务启动（Django runserver 会 fork 子进程，需要更多时间）
echo "  等待后端服务启动..."
sleep 5

# 检查后端是否启动成功（通过端口监听状态，因为 Django 会 fork 子进程）
BACKEND_ACTUAL_PID=""
if command -v lsof >/dev/null 2>&1; then
    BACKEND_ACTUAL_PID=$(lsof -ti :$BACKEND_PORT 2>/dev/null | head -1)
elif command -v ss >/dev/null 2>&1; then
    BACKEND_ACTUAL_PID=$(ss -tlnp 2>/dev/null | grep ":$BACKEND_PORT " | grep -oP 'pid=\K[0-9]+' | head -1)
fi

if [ -z "$BACKEND_ACTUAL_PID" ]; then
    # 如果端口未监听，检查父进程是否还在
    if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${RED}✗ 后端服务启动失败${NC}"
        echo "  查看日志: tail -20 /tmp/django_dev.log"
        echo ""
        tail -20 /tmp/django_dev.log
        exit 1
    else
        # 父进程存在但端口未监听，可能是启动中，再等待一下
        echo "  后端进程存在，等待端口监听..."
        sleep 3
        if command -v lsof >/dev/null 2>&1; then
            BACKEND_ACTUAL_PID=$(lsof -ti :$BACKEND_PORT 2>/dev/null | head -1)
        elif command -v ss >/dev/null 2>&1; then
            BACKEND_ACTUAL_PID=$(ss -tlnp 2>/dev/null | grep ":$BACKEND_PORT " | grep -oP 'pid=\K[0-9]+' | head -1)
        fi
        if [ -z "$BACKEND_ACTUAL_PID" ]; then
            echo -e "${YELLOW}⚠ 警告: 后端进程存在但端口仍未监听，请检查日志${NC}"
        fi
    fi
fi

# 启动前端
echo ""
echo "启动前端 Vue 开发服务器..."
cd "$PROJECT_DIR/frontend" || {
    echo -e "${RED}✗ 错误: 无法进入前端目录${NC}"
    exit 1
}

if [ ! -f "package.json" ]; then
    echo -e "${RED}✗ 错误: 找不到 package.json 文件${NC}"
    exit 1
fi

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠ 警告: node_modules 不存在，正在安装依赖...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 错误: npm install 失败${NC}"
        exit 1
    fi
fi

npm run dev > /tmp/vue_dev.log 2>&1 &
FRONTEND_PID=$!
echo "  前端进程 ID: $FRONTEND_PID"
echo "  前端日志: tail -f /tmp/vue_dev.log"

sleep 5

# 检查服务状态
echo ""
echo "检查服务状态..."

BACKEND_RUNNING=false
FRONTEND_RUNNING=false

# 检查后端服务（优先通过端口监听状态判断，因为 Django 会 fork 子进程）
BACKEND_ACTUAL_PID=""
if command -v lsof >/dev/null 2>&1; then
    BACKEND_ACTUAL_PID=$(lsof -ti :$BACKEND_PORT 2>/dev/null | head -1)
elif command -v ss >/dev/null 2>&1; then
    BACKEND_ACTUAL_PID=$(ss -tlnp 2>/dev/null | grep ":$BACKEND_PORT " | grep -oP 'pid=\K[0-9]+' | head -1)
fi

if [ -n "$BACKEND_ACTUAL_PID" ]; then
    # 端口在监听，服务正常运行
    echo -e "${GREEN}✓ 后端服务运行中 (PID: $BACKEND_ACTUAL_PID, 端口: $BACKEND_PORT)${NC}"
    BACKEND_RUNNING=true
elif ps -p $BACKEND_PID > /dev/null 2>&1; then
    # 父进程存在但端口未监听
    echo -e "${YELLOW}⚠ 后端进程存在但端口未监听（可能正在启动中）${NC}"
    echo "  查看日志: tail -20 /tmp/django_dev.log"
else
    # 进程不存在，启动失败
    echo -e "${RED}✗ 后端服务启动失败${NC}"
    echo "  查看日志: tail -20 /tmp/django_dev.log"
    echo ""
    tail -20 /tmp/django_dev.log
fi

if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    # 检查端口是否真的在监听
    if (command -v netstat >/dev/null 2>&1 && netstat -tlnp 2>/dev/null | grep -q ":$FRONTEND_PORT ") || \
       (command -v ss >/dev/null 2>&1 && ss -tlnp 2>/dev/null | grep -q ":$FRONTEND_PORT "); then
        echo -e "${GREEN}✓ 前端服务运行中 (PID: $FRONTEND_PID, 端口: $FRONTEND_PORT)${NC}"
        FRONTEND_RUNNING=true
    else
        echo -e "${YELLOW}⚠ 前端进程存在但端口未监听${NC}"
    fi
else
    echo -e "${RED}✗ 前端服务启动失败${NC}"
    echo "  查看日志: tail -20 /tmp/vue_dev.log"
    echo ""
    tail -20 /tmp/vue_dev.log
fi

echo ""
echo "=========================================="
if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
    echo -e "   ${GREEN}开发服务器已启动${NC}"
else
    echo -e "   ${YELLOW}开发服务器部分启动（请检查上述错误）${NC}"
fi
echo "=========================================="
echo "访问地址:"
echo "  - 前端: http://localhost:$FRONTEND_PORT"
echo "  - 后端: http://localhost:$BACKEND_PORT"
echo ""
echo "查看实时日志:"
echo "  - 后端: tail -f /tmp/django_dev.log"
echo "  - 前端: tail -f /tmp/vue_dev.log"
echo ""
echo "定时任务服务:"
if ps aux | grep -E "[c]ron|[/]usr/sbin/cron" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Cron 服务运行中${NC}"
    echo "  - 查看定时任务: crontab -l"
    echo "  - 查看定时任务日志: tail -f /home/devbox/project/logs/*.log"
else
    echo -e "  ${YELLOW}⚠ Cron 服务未运行${NC}"
    echo "  - 启动命令: sudo service cron start"
fi
echo ""
echo "停止服务:"
echo "  - pkill -f 'manage.py runserver.*$BACKEND_PORT'"
echo "  - pkill -f 'vue-cli-service serve'"
echo "=========================================="




