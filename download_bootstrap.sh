#!/bin/bash
# 下载 Bootstrap 5.3.0 到本地 static 目录

cd /home/devbox/project/vihhi/weihai_tech_production_system/backend/static

# 创建目录
mkdir -p css js

# 下载 Bootstrap CSS
echo "下载 Bootstrap CSS..."
curl -L -o css/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css || \
curl -L -o css/bootstrap.min.css https://unpkg.com/bootstrap@5.3.0/dist/css/bootstrap.min.css || \
echo "CSS 下载失败，请手动下载"

# 下载 Bootstrap Icons CSS
echo "下载 Bootstrap Icons CSS..."
curl -L -o css/bootstrap-icons.min.css https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css || \
curl -L -o css/bootstrap-icons.min.css https://unpkg.com/bootstrap-icons@1.11.0/font/bootstrap-icons.css || \
echo "Icons CSS 下载失败，请手动下载"

# 下载 Bootstrap JS
echo "下载 Bootstrap JS..."
curl -L -o js/bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js || \
curl -L -o js/bootstrap.bundle.min.js https://unpkg.com/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js || \
echo "JS 下载失败，请手动下载"

echo "完成！如果下载成功，Bootstrap 资源已保存到 static 目录"
