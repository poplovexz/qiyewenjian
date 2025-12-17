#!/bin/bash

#############################################
# 全栈应用一键启动脚本
# 功能：启动前端和后端所有服务
#############################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# 检查是否有 systemd
has_systemd() {
    if [ -d /run/systemd/system ]; then
        return 0
    else
        return 1
    fi
}

# 检查 PostgreSQL 状态
check_postgresql() {
    # 方法1: 尝试连接
    if pg_isready -q 2>/dev/null; then
        return 0
    fi
    # 方法2: 检查进程
    if pgrep -x postgres >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 检查 Redis 状态
check_redis() {
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        return 0
    fi
    return 1
}

# 检查服务状态 (兼容 systemd 和非 systemd 环境)
check_service() {
    local service_name=$1

    case "$service_name" in
        *postgresql*)
            check_postgresql
            return $?
            ;;
        *redis*)
            check_redis
            return $?
            ;;
        *)
            if has_systemd; then
                systemctl is-active --quiet "$service_name"
                return $?
            else
                return 1
            fi
            ;;
    esac
}

# 启动 PostgreSQL (兼容多种环境)
start_postgresql() {
    log_info "启动 PostgreSQL..."

    # 如果已经在运行，直接返回成功
    if check_postgresql; then
        log_success "PostgreSQL 已经在运行"
        return 0
    fi

    # 方法1: 使用 systemctl (如果有 systemd)
    if has_systemd; then
        if sudo systemctl start postgresql 2>/dev/null || sudo systemctl start postgresql@16-main 2>/dev/null; then
            sleep 2
            if check_postgresql; then
                log_success "PostgreSQL 启动成功 (systemd)"
                return 0
            fi
        fi
    fi

    # 方法2: 使用 service 命令
    if sudo service postgresql start 2>/dev/null; then
        sleep 2
        if check_postgresql; then
            log_success "PostgreSQL 启动成功 (service)"
            return 0
        fi
    fi

    # 方法3: 使用 pg_ctlcluster (Debian/Ubuntu)
    if command -v pg_ctlcluster >/dev/null 2>&1; then
        if sudo pg_ctlcluster 16 main start 2>/dev/null || sudo pg_ctlcluster 15 main start 2>/dev/null || sudo pg_ctlcluster 14 main start 2>/dev/null; then
            sleep 2
            if check_postgresql; then
                log_success "PostgreSQL 启动成功 (pg_ctlcluster)"
                return 0
            fi
        fi
    fi

    # 方法4: 直接启动 postgres (Docker/WSL)
    if command -v pg_ctl >/dev/null 2>&1; then
        local pgdata="${PGDATA:-/var/lib/postgresql/data}"
        if [ -d "$pgdata" ]; then
            sudo -u postgres pg_ctl -D "$pgdata" start 2>/dev/null &
            sleep 3
            if check_postgresql; then
                log_success "PostgreSQL 启动成功 (pg_ctl)"
                return 0
            fi
        fi
    fi

    log_error "无法启动 PostgreSQL，请手动启动"
    log_info "  尝试: sudo service postgresql start"
    log_info "  或者: sudo pg_ctlcluster 16 main start"
    return 1
}

# 启动 Redis (兼容多种环境)
start_redis() {
    log_info "启动 Redis..."

    # 如果已经在运行，直接返回成功
    if check_redis; then
        log_success "Redis 已经在运行"
        return 0
    fi

    # 方法1: 使用 systemctl (如果有 systemd)
    if has_systemd; then
        if sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null; then
            sleep 2
            if check_redis; then
                log_success "Redis 启动成功 (systemd)"
                return 0
            fi
        fi
    fi

    # 方法2: 使用 service 命令
    if sudo service redis-server start 2>/dev/null; then
        sleep 2
        if check_redis; then
            log_success "Redis 启动成功 (service)"
            return 0
        fi
    fi

    # 方法3: 直接启动 redis-server (后台运行)
    if command -v redis-server >/dev/null 2>&1; then
        redis-server --daemonize yes 2>/dev/null
        sleep 2
        if check_redis; then
            log_success "Redis 启动成功 (直接启动)"
            return 0
        fi
    fi

    log_warning "无法启动 Redis，系统将在无缓存模式下运行"
    return 1
}

# 启动系统服务 (兼容包装函数)
start_service() {
    local service_name=$1

    case "$service_name" in
        *postgresql*)
            start_postgresql
            return $?
            ;;
        *redis*)
            start_redis
            return $?
            ;;
        *)
            log_error "未知服务: $service_name"
            return 1
            ;;
    esac
}

# 清理旧进程
cleanup_processes() {
    log_info "清理旧进程..."
    
    # 清理后端进程 (端口 8000)
    local backend_pids=$(lsof -ti:8000 2>/dev/null || true)
    if [ -n "$backend_pids" ]; then
        log_warning "清理后端进程: $backend_pids"
        echo "$backend_pids" | xargs kill -9 2>/dev/null || true
    fi
    
    # 清理前端进程 (端口 5174)
    local frontend_pids=$(lsof -ti:5174 2>/dev/null || true)
    if [ -n "$frontend_pids" ]; then
        log_warning "清理前端进程: $frontend_pids"
        echo "$frontend_pids" | xargs kill -9 2>/dev/null || true
    fi
    
    # 清理 uvicorn 和 vite 进程
    pkill -9 -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -9 -f "vite.*5174" 2>/dev/null || true
    
    sleep 2
    log_success "进程清理完成"
}

# 启动后端服务
start_backend() {
    print_header "启动后端服务"
    
    local backend_dir="/var/www/packages/backend"
    
    # 检查虚拟环境
    if [ ! -d "$backend_dir/venv" ]; then
        log_error "后端虚拟环境不存在: $backend_dir/venv"
        return 1
    fi
    
    # 检查 .env 文件
    if [ ! -f "$backend_dir/.env" ]; then
        log_error "后端 .env 文件不存在"
        return 1
    fi
    
    cd "$backend_dir"
    source venv/bin/activate
    export PYTHONPATH="$backend_dir/src"
    
    log_info "启动后端服务 (端口 8000)..."
    nohup python3 -m uvicorn src.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --reload-dir src \
        > /tmp/backend_8000.log 2>&1 &
    
    local backend_pid=$!
    log_info "后端进程 PID: $backend_pid"
    
    # 等待服务启动
    sleep 5
    
    # 健康检查
    local max_retries=10
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            log_success "后端服务启动成功！"
            log_info "  - API 服务: http://localhost:8000"
            log_info "  - API 文档: http://localhost:8000/docs"
            log_info "  - 日志文件: /tmp/backend_8000.log"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_info "等待后端服务响应... ($retry_count/$max_retries)"
        sleep 2
    done
    
    log_error "后端服务启动失败或超时"
    log_info "请查看日志: tail -f /tmp/backend_8000.log"
    return 1
}

# 启动前端服务
start_frontend() {
    print_header "启动前端服务"
    
    local frontend_dir="/var/www/packages/frontend"
    
    # 检查 node_modules
    if [ ! -d "$frontend_dir/node_modules" ]; then
        log_warning "前端依赖未安装，正在安装..."
        cd "$frontend_dir"
        pnpm install || {
            log_error "前端依赖安装失败"
            return 1
        }
    fi
    
    cd "$frontend_dir"
    
    log_info "启动前端服务 (端口 5174)..."
    nohup pnpm dev --port 5174 --host 0.0.0.0 \
        > /tmp/frontend_5174.log 2>&1 &
    
    local frontend_pid=$!
    log_info "前端进程 PID: $frontend_pid"
    
    # 等待服务启动
    sleep 5
    
    # 检查服务
    local max_retries=10
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:5174 >/dev/null 2>&1; then
            log_success "前端服务启动成功！"
            log_info "  - 前端应用: http://localhost:5174"
            log_info "  - 日志文件: /tmp/frontend_5174.log"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_info "等待前端服务响应... ($retry_count/$max_retries)"
        sleep 2
    done
    
    log_error "前端服务启动失败或超时"
    log_info "请查看日志: tail -f /tmp/frontend_5174.log"
    return 1
}

# 显示服务状态
show_status() {
    print_separator
    print_header "服务状态总览"
    print_separator
    echo ""
    
    echo "系统服务:"
    check_postgresql && echo "  ✓ PostgreSQL: 运行中" || echo "  ✗ PostgreSQL: 未运行"
    check_redis && echo "  ✓ Redis: 运行中" || echo "  ✗ Redis: 未运行"
    
    echo ""
    echo "应用服务:"
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "  ✓ 后端服务 (8000): 运行中"
    else
        echo "  ✗ 后端服务 (8000): 未运行"
    fi
    
    if curl -s http://localhost:5174 >/dev/null 2>&1; then
        echo "  ✓ 前端服务 (5174): 运行中"
    else
        echo "  ✗ 前端服务 (5174): 未运行"
    fi
    
    echo ""
    echo "访问地址:"
    echo "  - 前端应用: http://localhost:5174"
    echo "  - 后端 API: http://localhost:8000"
    echo "  - API 文档: http://localhost:8000/docs"
    
    echo ""
    echo "日志文件:"
    echo "  - 后端日志: tail -f /tmp/backend_8000.log"
    echo "  - 前端日志: tail -f /tmp/frontend_5174.log"
    
    print_separator
}

# 主函数
main() {
    print_separator
    echo -e "${GREEN}全栈应用一键启动脚本${NC}"
    print_separator
    echo ""
    
    # 步骤 1: 检查并启动 PostgreSQL
    log_info "步骤 1/6: 检查 PostgreSQL 服务"
    if ! check_postgresql; then
        start_postgresql || {
            log_error "PostgreSQL 启动失败，无法继续"
            exit 1
        }
    else
        log_success "PostgreSQL 正在运行"
    fi
    echo ""

    # 步骤 2: 检查并启动 Redis
    log_info "步骤 2/6: 检查 Redis 服务"
    if ! check_redis; then
        start_redis || {
            log_warning "Redis 启动失败，系统将在无缓存模式下运行"
        }
    else
        log_success "Redis 正在运行"
    fi
    echo ""
    
    # 步骤 3: 清理旧进程
    log_info "步骤 3/6: 清理旧进程"
    cleanup_processes
    echo ""
    
    # 步骤 4: 启动后端服务
    log_info "步骤 4/6: 启动后端服务"
    start_backend || {
        log_error "后端服务启动失败"
        exit 1
    }
    echo ""
    
    # 步骤 5: 启动前端服务
    log_info "步骤 5/6: 启动前端服务"
    start_frontend || {
        log_error "前端服务启动失败"
        exit 1
    }
    echo ""
    
    # 步骤 6: 显示状态
    log_info "步骤 6/6: 显示服务状态"
    show_status
    
    log_success "所有服务启动完成！"
    echo ""
    log_info "提示: 在浏览器中打开 http://localhost:5174 访问应用"
    log_info "提示: 使用 './stop_all.sh' 停止所有服务"
}

# 执行主函数
main

