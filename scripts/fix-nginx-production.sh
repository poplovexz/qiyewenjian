#!/bin/bash

# 修复生产环境Nginx配置脚本
# 解决 ERR_CONNECTION_RESET 和 ERR_NETWORK_CHANGED 问题

set -e

echo "========================================="
echo "修复生产环境Nginx配置"
echo "========================================="

# 配置变量
REMOTE_HOST="172.16.2.221"
REMOTE_USER="saas"
REMOTE_PASSWORD="Pop781216"
NGINX_CONFIG_FILE="/etc/nginx/sites-enabled/proxy-system"
BACKUP_FILE="/etc/nginx/sites-enabled/proxy-system.backup.$(date +%Y%m%d_%H%M%S)"

echo ""
echo "[步骤 1/5] 上传优化的Nginx配置到服务器..."
sshpass -p "$REMOTE_PASSWORD" scp nginx-proxy-system-optimized.conf ${REMOTE_USER}@${REMOTE_HOST}:/tmp/

echo ""
echo "[步骤 2/5] 备份当前Nginx配置..."
sshpass -p "$REMOTE_PASSWORD" ssh ${REMOTE_USER}@${REMOTE_HOST} "echo '$REMOTE_PASSWORD' | sudo -S cp $NGINX_CONFIG_FILE $BACKUP_FILE"
echo "✓ 备份完成: $BACKUP_FILE"

echo ""
echo "[步骤 3/5] 应用新的Nginx配置..."
sshpass -p "$REMOTE_PASSWORD" ssh ${REMOTE_USER}@${REMOTE_HOST} "echo '$REMOTE_PASSWORD' | sudo -S cp /tmp/nginx-proxy-system-optimized.conf $NGINX_CONFIG_FILE"

echo ""
echo "[步骤 4/5] 测试Nginx配置..."
sshpass -p "$REMOTE_PASSWORD" ssh ${REMOTE_USER}@${REMOTE_HOST} "echo '$REMOTE_PASSWORD' | sudo -S nginx -t"

echo ""
echo "[步骤 5/5] 重新加载Nginx..."
sshpass -p "$REMOTE_PASSWORD" ssh ${REMOTE_USER}@${REMOTE_HOST} "echo '$REMOTE_PASSWORD' | sudo -S systemctl reload nginx"

echo ""
echo "========================================="
echo "✓ Nginx配置修复完成！"
echo "========================================="
echo ""
echo "优化内容："
echo "  ✓ 增加客户端缓冲区大小"
echo "  ✓ 增加代理缓冲区大小"
echo "  ✓ 启用gzip压缩"
echo "  ✓ 优化连接超时设置"
echo ""
echo "现在可以访问 http://172.16.2.221 测试"
echo "如果还有问题，可以恢复备份："
echo "  ssh saas@172.16.2.221"
echo "  sudo cp $BACKUP_FILE $NGINX_CONFIG_FILE"
echo "  sudo systemctl reload nginx"
echo ""

