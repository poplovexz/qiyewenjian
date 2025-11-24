#!/bin/bash

# 快速部署脚本 - 一键部署到生产环境
# 使用方法: ./quick-deploy.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   生产环境一键部署脚本                ║${NC}"
echo -e "${BLUE}║   目标: ${PROD_USER}@${PROD_HOST}        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查 sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}安装 sshpass...${NC}"
    sudo apt-get install -y sshpass || {
        echo -e "${RED}无法安装 sshpass，请手动运行 deploy.sh${NC}"
        exit 1
    }
fi

# 1. 构建前端
echo -e "${YELLOW}[1/9] 构建前端...${NC}"
cd packages/frontend
npm run build:prod || {
    echo -e "${RED}前端构建失败${NC}"
    exit 1
}
cd ../..
echo -e "${GREEN}✓ 前端构建完成${NC}"

# 2. 构建移动端
echo -e "${YELLOW}[2/9] 构建移动端...${NC}"
cd packages/mobile
npm run build || {
    echo -e "${RED}移动端构建失败${NC}"
    exit 1
}
cd ../..
echo -e "${GREEN}✓ 移动端构建完成${NC}"

# 3. 打包项目
echo -e "${YELLOW}[3/9] 打包项目...${NC}"
tar -czf deploy-package.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='*.log' \
    packages/backend \
    packages/frontend/dist \
    packages/mobile/dist \
    deploy-scripts

echo -e "${GREEN}✓ 打包完成 ($(du -h deploy-package.tar.gz | cut -f1))${NC}"

# 4. 上传文件
echo -e "${YELLOW}[4/9] 上传到生产服务器...${NC}"
sshpass -p "$PROD_PASS" scp -o StrictHostKeyChecking=no \
    deploy-package.tar.gz ${PROD_USER}@${PROD_HOST}:/tmp/ || {
    echo -e "${RED}上传失败${NC}"
    exit 1
}
echo -e "${GREEN}✓ 上传完成${NC}"

# 5. 部署到服务器
echo -e "${YELLOW}[5/9] 在服务器上部署...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
set -e

# 创建目录
mkdir -p /home/saas/proxy-system
mkdir -p /home/saas/proxy-system/logs
mkdir -p /home/saas/proxy-system/uploads

cd /home/saas/proxy-system

# 备份
if [ -d "packages" ]; then
    BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p $BACKUP_DIR
    cp -r packages $BACKUP_DIR/ 2>/dev/null || true
    echo "✓ 已备份到: $BACKUP_DIR"

    # 保存.env文件
    if [ -f "packages/backend/.env" ]; then
        cp packages/backend/.env /tmp/.env.backup
    fi

    # 修复权限后删除旧文件
    chmod -R u+w packages/ 2>/dev/null || true
    rm -rf packages
fi

# 解压
tar -xzf /tmp/deploy-package.tar.gz
rm /tmp/deploy-package.tar.gz

# 恢复.env文件
if [ -f "/tmp/.env.backup" ]; then
    cp /tmp/.env.backup packages/backend/.env
    rm /tmp/.env.backup
    echo "✓ 已恢复配置文件"
fi

# 安装依赖
cd packages/backend

# 删除旧的虚拟环境，确保依赖完整
if [ -d "venv" ]; then
    echo "删除旧的虚拟环境..."
    rm -rf venv
fi

echo "创建新的虚拟环境..."
python3 -m venv venv

source venv/bin/activate
echo "升级pip..."
pip install --upgrade pip -q

echo "安装项目依赖..."
if [ -f "requirements-production.txt" ]; then
    echo "使用 requirements-production.txt"
    pip install -r requirements-production.txt -q
else
    echo "使用默认依赖列表"
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic \
        python-jose PyJWT passlib bcrypt python-multipart redis pydantic-settings \
        "wechatpayv3>=2.0.0" python-alipay-sdk cryptography -q
fi

echo "✓ 服务器部署完成"
ENDSSH

echo -e "${GREEN}✓ 服务器部署完成${NC}"

# 6. 检查配置
echo -e "${YELLOW}[6/9] 检查配置...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
if [ ! -f "/home/saas/proxy-system/packages/backend/.env" ]; then
    echo "⚠ 警告: .env 文件不存在"
    echo "请创建配置文件: /home/saas/proxy-system/packages/backend/.env"
    exit 1
fi
echo "✓ 配置文件存在"
ENDSSH

# 7. 运行数据库迁移
echo -e "${YELLOW}[7/9] 运行数据库迁移...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate

# 运行所有SQL迁移脚本
echo "运行数据库迁移脚本..."
cd /home/saas/proxy-system/packages/backend

# 按顺序执行迁移脚本
MIGRATIONS=(
    "migrations/create_bangong_guanli_tables.sql"
    "migrations/create_payment_tables.sql"
    "migrations/create_payment_api_tables.sql"
    "migrations/add_payment_order_fields.sql"
    "migrations/add_contract_sign_payment_fields.sql"
    "migrations/add_offline_payment_types.sql"
    "migrations/refactor_hetong_zhifu_fangshi_to_use_payment_config.sql"
    "migrations/add_remark_to_zhifu_peizhi.sql"
    "migrations/add_remark_to_zhifu_tuikuan.sql"
)

for migration in "${MIGRATIONS[@]}"; do
    if [ -f "$migration" ]; then
        echo "执行迁移: $migration"
        PGPASSWORD=proxy_password_123 psql -h localhost -U proxy_user -d proxy_db -f "$migration" 2>&1 | grep -v "already exists" || true
    fi
done

cd src

# 检查并运行必要的数据库迁移脚本
echo "检查数据库表..."

# 检查办公管理表是否存在
python3 << 'PYEOF'
import sys
from core.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('baoxiao_shenqing', 'qingjia_shenqing', 'caigou_shenqing')
        """))
        count = result.scalar()

        if count < 3:
            print("NEED_OFFICE_TABLES")
            sys.exit(1)
        else:
            print("办公管理表已存在")
            sys.exit(0)
except Exception as e:
    print(f"检查失败: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 1 ]; then
    echo "创建办公管理表..."
    python3 scripts/create_bangong_guanli_tables.py
    python3 scripts/init_office_permissions.py
    echo "✓ 办公管理表创建完成"
fi

# 确保admin用户拥有所有权限（每次部署都运行）
echo "确保admin用户权限..."
python3 scripts/ensure_admin_permissions.py || echo "⚠️  admin权限配置可能失败"

echo "✓ 数据库迁移完成"
ENDSSH

echo -e "${GREEN}✓ 数据库迁移完成${NC}"

# 8. 重启服务
echo -e "${YELLOW}[8/9] 重启服务...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
# 停止旧进程
pkill -f "uvicorn.*main:app" || true
sleep 2

# 启动新进程
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
nohup uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000 --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &

sleep 3
echo "✓ 服务已重启"
ENDSSH

echo -e "${GREEN}✓ 服务重启完成${NC}"

# 9. 验证部署
echo -e "${YELLOW}[9/9] 验证部署...${NC}"
sleep 2

# 检查健康状态
if sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "curl -s http://localhost:8000/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务可能未正常启动${NC}"
    echo -e "${YELLOW}请检查日志: ssh ${PROD_USER}@${PROD_HOST} 'tail -50 /home/saas/proxy-system/logs/backend.log'${NC}"
fi

# 验证关键数据库表
echo -e "${YELLOW}验证数据库表...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
cd src

python3 << 'PYEOF'
from core.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # 检查关键表
        tables_to_check = [
            'yonghu', 'jiaose', 'quanxian',  # 用户管理
            'baoxiao_shenqing', 'qingjia_shenqing', 'caigou_shenqing',  # 办公管理
            'deploy_history', 'deploy_config'  # 部署管理
        ]

        for table in tables_to_check:
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = '{table}'
                )
            """))
            exists = result.scalar()
            status = "✓" if exists else "✗"
            print(f"  {status} {table}")

except Exception as e:
    print(f"验证失败: {e}")
PYEOF
ENDSSH

# 验证前端和移动端文件
echo -e "${YELLOW}验证前端和移动端文件...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
echo "检查前端文件:"
if [ -f "/home/saas/proxy-system/packages/frontend/dist/index.html" ]; then
    echo "  ✓ 前端 index.html 存在"
else
    echo "  ✗ 前端 index.html 不存在"
fi

echo "检查移动端文件:"
if [ -f "/home/saas/proxy-system/packages/mobile/dist/index.html" ]; then
    echo "  ✓ 移动端 index.html 存在"
else
    echo "  ✗ 移动端 index.html 不存在"
fi
ENDSSH

# 清理
rm -f deploy-package.tar.gz

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          部署完成！                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}访问地址:${NC}"
echo -e "  前端PC端: ${BLUE}http://${PROD_HOST}${NC}"
echo -e "  移动端:   ${BLUE}http://${PROD_HOST}:81${NC}"
echo -e "  API文档:  ${BLUE}http://${PROD_HOST}:8000/docs${NC}"
echo ""
echo -e "${YELLOW}查看日志:${NC}"
echo -e "  ssh ${PROD_USER}@${PROD_HOST} 'tail -f /home/saas/proxy-system/logs/backend.log'"
echo ""
echo -e "${YELLOW}管理服务:${NC}"
echo -e "  重启: ssh ${PROD_USER}@${PROD_HOST} 'pkill -f uvicorn && cd /home/saas/proxy-system/packages/backend && source venv/bin/activate && nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 > /home/saas/proxy-system/logs/backend.log 2>&1 &'"
echo ""

