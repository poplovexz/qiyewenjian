#!/bin/bash

# ============================================
# Docker 一键启动脚本
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示帮助
show_help() {
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  dev       启动开发环境 (热重载)"
    echo "  prod      启动生产环境"
    echo "  build     构建镜像"
    echo "  stop      停止所有服务"
    echo "  logs      查看日志"
    echo "  clean     清理容器和镜像"
    echo ""
    echo "示例:"
    echo "  $0 dev              # 启动开发环境"
    echo "  $0 prod             # 启动生产环境"
    echo "  $0 logs backend     # 查看后端日志"
    echo "  $0 stop             # 停止所有服务"
}

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行，请启动 Docker"
        exit 1
    fi
}

# 检查 .env 文件
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，正在从模板创建..."
        cp .env.example .env
        log_info "已创建 .env 文件，请根据需要修改配置"
    fi
}

# 启动开发环境
start_dev() {
    log_info "启动开发环境..."
    docker compose -f docker-compose.dev.yml up -d --build
    log_success "开发环境已启动!"
    echo ""
    echo "访问地址:"
    echo "  - 前端: http://localhost:5173"
    echo "  - 后端: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
}

# 启动生产环境
start_prod() {
    log_info "启动生产环境..."
    check_env
    docker compose -f docker-compose.yml up -d --build
    log_success "生产环境已启动!"
    echo ""
    echo "访问地址:"
    echo "  - 前端: http://localhost:80"
    echo "  - 后端: http://localhost:8000"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    docker compose -f docker-compose.yml build --no-cache
    log_success "镜像构建完成!"
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    docker compose -f docker-compose.yml down 2>/dev/null || true
    docker compose -f docker-compose.dev.yml down 2>/dev/null || true
    log_success "所有服务已停止"
}

# 查看日志
view_logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        docker compose -f docker-compose.yml logs -f "$service"
    else
        docker compose -f docker-compose.yml logs -f
    fi
}

# 清理
clean_all() {
    log_warning "这将删除所有容器、镜像和数据卷，是否继续? (y/N)"
    read -r confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        stop_services
        docker compose -f docker-compose.yml down -v --rmi local 2>/dev/null || true
        docker compose -f docker-compose.dev.yml down -v --rmi local 2>/dev/null || true
        log_success "清理完成"
    else
        log_info "已取消"
    fi
}

# 主逻辑
check_docker

case "${1:-help}" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    build)
        build_images
        ;;
    stop)
        stop_services
        ;;
    logs)
        view_logs "$2"
        ;;
    clean)
        clean_all
        ;;
    *)
        show_help
        ;;
esac

