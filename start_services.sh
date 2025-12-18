#!/bin/bash
# 启动服务脚本（项目根目录版本）
# 此脚本会调用子目录中的实际启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_SCRIPT="$SCRIPT_DIR/vihhi/weihai_tech_production_system/start_services.sh"

if [ ! -f "$SERVICE_SCRIPT" ]; then
    echo "错误: 找不到启动脚本: $SERVICE_SCRIPT"
    exit 1
fi

# 执行实际的启动脚本
bash "$SERVICE_SCRIPT"

