#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/weihai-app
SRC_DIR="$APP_DIR/src"
VENV="$APP_DIR/venv"
LOG_FILE="$APP_DIR/deploy.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[$TIMESTAMP] === 部署开始 ==="

echo "[1/6] 更新代码"
cd "$SRC_DIR"
git fetch --all
git reset --hard origin/main

echo "[2/6] 安装依赖"
source "$VENV/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

if [ -f package.json ]; then
  echo "[2b] 安装前端依赖"
  npm install --production
  npm run build || echo "前端构建失败，可检查 npm 输出"
fi

echo "[3/6] 数据库迁移"
python manage.py migrate

echo "[4/6] 收集静态文件"
python manage.py collectstatic --noinput

echo "[5/6] 重启应用服务"
sudo systemctl restart weihai-app

if systemctl is-active --quiet nginx; then
  echo "[6/6] 重载 Nginx"
  sudo systemctl reload nginx
else
  echo "[6/6] 跳过 Nginx 重载 (未检测到 nginx 服务)"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 部署完成 ==="
