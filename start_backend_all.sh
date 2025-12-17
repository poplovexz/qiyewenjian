#!/bin/bash

#############################################
# 后端一键启动脚本
# 功能：启动所有后端依赖服务和应用
#############################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印分隔线
print_separator() {
    echo -e "${BLUE}=========================================${NC}"
}

# 检查服务状态
check_service() {
    local service_name=$1
    if systemctl is-active --quiet "$service_name"; then
        log_success "$service_name 正在运行"
        return 0
    else
        log_warning "$service_name 未运行"
        return 1
    fi
}

# 启动系统服务
start_service() {
    local service_name=$1
    log_info "启动 $service_name..."
    
    if sudo systemctl start "$service_name" 2>/dev/null; then
        sleep 2
        if check_service "$service_name"; then
            log_success "$service_name 启动成功"
            return 0
        else
            log_error "$service_name 启动失败"
            return 1
        fi
    else
        log_error "无法启动 $service_name (可能需要 sudo 权限)"
        return 1
    fi
}

# 检查端口占用
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "端口 $port 已被占用 ($service_name)"
        return 1
    else
        log_success "端口 $port 可用 ($service_name)"
        return 0
    fi
}

# 清理旧的后端进程
cleanup_backend() {
    log_info "清理旧的后端进程..."
    
    # 查找并杀死占用 8000 端口的进程
    local pids=$(lsof -ti:8000 2>/dev/null || true)
    if [ -n "$pids" ]; then
        log_warning "发现占用端口 8000 的进程: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
        log_success "已清理端口 8000"
    else
        log_info "端口 8000 未被占用"
    fi
    
    # 清理 uvicorn 进程
    pkill -9 -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -9 -f "python.*main.py" 2>/dev/null || true
    
    sleep 1
    log_success "后端进程清理完成"
}

# 检查 Python 虚拟环境
check_venv() {
    local backend_dir="/var/www/packages/backend"
    
    if [ ! -d "$backend_dir/venv" ]; then
        log_error "虚拟环境不存在: $backend_dir/venv"
        log_info "请先创建虚拟环境: cd $backend_dir && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        return 1
    fi
    
    log_success "虚拟环境检查通过"
    return 0
}

# 检查环境变量文件
check_env_file() {
    local backend_dir="/var/www/packages/backend"
    
    if [ ! -f "$backend_dir/.env" ]; then
        log_warning ".env 文件不存在"
        if [ -f "$backend_dir/.env.example" ]; then
            log_info "发现 .env.example 文件"
            read -p "是否复制 .env.example 到 .env? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cp "$backend_dir/.env.example" "$backend_dir/.env"
                log_success "已创建 .env 文件，请编辑配置"
                log_warning "请检查并修改 .env 文件中的配置，特别是数据库连接信息"
                return 1
            fi
        fi
        log_error "缺少 .env 配置文件"
        return 1
    fi
    
    log_success "环境变量文件检查通过"
    return 0
}

# 启动后端服务
start_backend() {
    local backend_dir="/var/www/packages/backend"
    
    log_info "启动后端服务 (端口 8000)..."
    
    cd "$backend_dir"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 设置环境变量
    export PYTHONPATH="$backend_dir/src"
    
    # 启动服务（后台运行）
    nohup python3 -m uvicorn src.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --reload-dir src \
        > /tmp/backend_8000.log 2>&1 &
    
    local backend_pid=$!
    log_info "后端进程 PID: $backend_pid"
    
    # 等待服务启动
    log_info "等待后端服务启动..."
    sleep 5
    
    # 检查服务健康状态
    local max_retries=10
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            log_success "后端服务启动成功！"
            log_info "健康检查: http://localhost:8000/health"
            log_info "API 文档: http://localhost:8000/docs"
            log_info "日志文件: /tmp/backend_8000.log"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_info "等待服务响应... ($retry_count/$max_retries)"
        sleep 2
    done
    
    log_error "后端服务启动失败或超时"
    log_info "请查看日志: tail -f /tmp/backend_8000.log"
    return 1
}

# 显示服务状态
show_status() {
    print_separator
    log_info "服务状态总览"
    print_separator
    
    echo ""
    echo "系统服务:"
    check_service "postgresql@16-main.service" && echo "  ✓ PostgreSQL: 运行中" || echo "  ✗ PostgreSQL: 未运行"
    check_service "redis-server.service" && echo "  ✓ Redis: 运行中" || echo "  ✗ Redis: 未运行"
    
    echo ""
    echo "应用服务:"
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "  ✓ 后端服务 (8000): 运行中"
    else
        echo "  ✗ 后端服务 (8000): 未运行"
    fi
    
    echo ""
    echo "访问地址:"
    echo "  - API 服务: http://localhost:8000"
    echo "  - API 文档: http://localhost:8000/docs"
    echo "  - 健康检查: http://localhost:8000/health"
    
    echo ""
    echo "日志文件:"
    echo "  - 后端日志: /tmp/backend_8000.log"
    
    print_separator
}

# 主函数
main() {
    print_separator
    echo -e "${GREEN}后端服务一键启动脚本${NC}"
    print_separator
    echo ""
    
    # 步骤 1: 检查并启动 PostgreSQL
    log_info "步骤 1/5: 检查 PostgreSQL 服务"
    if ! check_service "postgresql@16-main.service"; then
        start_service "postgresql@16-main.service" || {
            log_error "PostgreSQL 启动失败，无法继续"
            exit 1
        }
    fi
    echo ""
    
    # 步骤 2: 检查并启动 Redis
    log_info "步骤 2/5: 检查 Redis 服务"
    if ! check_service "redis-server.service"; then
        start_service "redis-server.service" || {
            log_warning "Redis 启动失败，系统将在无缓存模式下运行"
        }
    fi
    echo ""
    
    # 步骤 3: 检查环境
    log_info "步骤 3/5: 检查后端环境"
    check_venv || exit 1
    check_env_file || exit 1
    echo ""
    
    # 步骤 4: 清理旧进程
    log_info "步骤 4/5: 清理旧进程"
    cleanup_backend
    echo ""
    
    # 步骤 5: 启动后端服务
    log_info "步骤 5/5: 启动后端服务"
    start_backend || {
        log_error "后端服务启动失败"
        exit 1
    }
    echo ""
    
    # 显示状态
    show_status
    
    log_success "所有服务启动完成！"
    echo ""
    log_info "提示: 使用 'tail -f /tmp/backend_8000.log' 查看实时日志"
    log_info "提示: 使用 'pkill -f uvicorn' 停止后端服务"
}

# 执行主函数
main

