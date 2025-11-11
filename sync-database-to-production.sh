#!/bin/bash

# 生产环境数据库同步脚本
# 将开发环境的数据同步到生产环境

set -e

echo "========================================="
echo "生产环境数据库同步脚本"
echo "========================================="

# 配置
PROD_SERVER="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"
DB_NAME="proxy_db"
DB_USER="postgres"
DB_PASS="Pop781216"
DEV_DB_PASS="password"

# 临时文件
BACKUP_FILE="/tmp/prod_db_backup_$(date +%Y%m%d_%H%M%S).sql"
DATA_EXPORT="/tmp/dev_full_data_export.sql"

echo ""
echo "步骤 1/5: 导出开发环境数据..."
PGPASSWORD=$DEV_DB_PASS pg_dump -h localhost -U $DB_USER -d $DB_NAME \
    --data-only --inserts > $DATA_EXPORT

if [ ! -s "$DATA_EXPORT" ]; then
    echo "❌ 错误：数据导出失败或文件为空"
    exit 1
fi

echo "✅ 开发环境数据导出成功: $(wc -l < $DATA_EXPORT) 行"

echo ""
echo "步骤 2/5: 备份生产环境数据库..."
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER \
    "echo '$PROD_PASS' | sudo -S -u postgres pg_dump -d $DB_NAME > $BACKUP_FILE"

echo "✅ 生产环境数据库已备份到: $BACKUP_FILE"

echo ""
echo "步骤 3/5: 上传数据文件到生产服务器..."
sshpass -p "$PROD_PASS" scp -o StrictHostKeyChecking=no $DATA_EXPORT \
    $PROD_USER@$PROD_SERVER:/tmp/dev_data.sql

echo "✅ 数据文件已上传"

echo ""
echo "步骤 4/5: 清空生产环境数据库并导入新数据..."
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER << 'ENDSSH'
echo "清空数据库表..."
echo 'Pop781216' | sudo -S -u postgres psql -d proxy_db << 'ENDSQL'
-- 禁用外键约束
SET session_replication_role = 'replica';

-- 清空所有表数据
TRUNCATE TABLE 
    zhifu_tongzhi,
    tixing_jilu,
    yonghu_jiaose,
    jiaose_quanxian,
    renwu,
    pingzheng,
    kehu_heguishixiang,
    kaipiao_shenqing,
    heguishixiang_tixing,
    heguishixiang_shili,
    fuwu_gongdan,
    chengben_jilu,
    quanxian,
    jiaose,
    yonghu,
    kehu,
    heguishixiang,
    tongzhi
CASCADE;

-- 重新启用外键约束
SET session_replication_role = 'origin';

\echo '✅ 数据库表已清空'
ENDSQL

echo "导入新数据..."
echo 'Pop781216' | sudo -S -u postgres psql -d proxy_db < /tmp/dev_data.sql

echo "✅ 数据导入完成"
ENDSSH

echo ""
echo "步骤 5/5: 重启生产环境后端服务..."
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER \
    "pkill -9 -f 'uvicorn.*main:app' && sleep 3 && cd /home/saas/proxy-system/packages/backend && source venv/bin/activate && cd src && nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > /home/saas/proxy-system/logs/backend.log 2>&1 &"

echo "等待后端服务启动..."
sleep 15

# 验证服务
echo ""
echo "验证服务状态..."
HEALTH_STATUS=$(sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_SERVER \
    "curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo 'error'")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务状态: $HEALTH_STATUS"
fi

echo ""
echo "========================================="
echo "✅ 数据库同步完成！"
echo "========================================="
echo ""
echo "生产环境访问地址:"
echo "  - 前端: http://172.16.2.221"
echo "  - 移动端: http://172.16.2.221:81"
echo "  - API文档: http://172.16.2.221/docs"
echo ""
echo "生产数据库备份位置:"
echo "  - $BACKUP_FILE"
echo ""

