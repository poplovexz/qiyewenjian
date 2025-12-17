#!/bin/bash
# 检查生产环境状态

PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"

echo "正在连接生产服务器..."

sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
echo "=== 生产环境状态 ==="
echo ""

# 检查目录
if [ -d "/home/saas/proxy-system" ]; then
    echo "✓ 项目目录存在"
    cd /home/saas/proxy-system
    
    # 检查文件
    echo ""
    echo "=== 当前部署的文件 ==="
    find packages -type f -name "*.py" -o -name "*.vue" -o -name "*.ts" | head -20
    
    # 检查服务状态
    echo ""
    echo "=== 服务状态 ==="
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        echo "✓ 后端服务运行中"
        ps aux | grep "uvicorn.*main:app" | grep -v grep
    else
        echo "✗ 后端服务未运行"
    fi
    
    # 检查备份
    echo ""
    echo "=== 备份历史 ==="
    if [ -d "backups" ]; then
        ls -lht backups/ | head -5
    else
        echo "无备份"
    fi
    
    # 检查日志
    echo ""
    echo "=== 最近日志 ==="
    if [ -f "logs/backend.log" ]; then
        tail -5 logs/backend.log
    fi
else
    echo "✗ 项目目录不存在"
fi
ENDSSH
