#!/bin/bash

#############################################
# 全栈应用一键停止脚本
# 功能：停止前端和后端所有服务
#############################################

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

# 打印分隔线
print_separator() {
    echo -e "${BLUE}=========================================${NC}"
}

# 停止后端服务
stop_backend() {
    log_info "停止后端服务 (端口 8000)..."
    
    local pids=$(lsof -ti:8000 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -15 2>/dev/null || true
        sleep 2
        
        # 如果还在运行，强制杀死
        pids=$(lsof -ti:8000 2>/dev/null || true)
        if [ -n "$pids" ]; then
            log_warning "进程未响应，强制终止..."
            echo "$pids" | xargs kill -9 2>/dev/null || true
        fi
        
        log_success "后端服务已停止"
    else
        log_info "后端服务未运行"
    fi
    
    # 清理 uvicorn 进程
    pkill -15 -f "uvicorn.*main:app" 2>/dev/null || true
    sleep 1
    pkill -9 -f "uvicorn.*main:app" 2>/dev/null || true
}

# 停止前端服务
stop_frontend() {
    log_info "停止前端服务 (端口 5174)..."
    
    local pids=$(lsof -ti:5174 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -15 2>/dev/null || true
        sleep 2
        
        # 如果还在运行，强制杀死
        pids=$(lsof -ti:5174 2>/dev/null || true)
        if [ -n "$pids" ]; then
            log_warning "进程未响应，强制终止..."
            echo "$pids" | xargs kill -9 2>/dev/null || true
        fi
        
        log_success "前端服务已停止"
    else
        log_info "前端服务未运行"
    fi
    
    # 清理 vite 进程
    pkill -15 -f "vite.*5174" 2>/dev/null || true
    sleep 1
    pkill -9 -f "vite.*5174" 2>/dev/null || true
}

# 主函数
main() {
    print_separator
    echo -e "${YELLOW}全栈应用一键停止脚本${NC}"
    print_separator
    echo ""
    
    stop_backend
    echo ""
    
    stop_frontend
    echo ""
    
    log_success "所有服务已停止！"
    echo ""
    
    # 显示状态
    log_info "端口状态检查:"
    
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "  端口 8000 仍被占用"
    else
        log_success "  端口 8000 已释放"
    fi
    
    if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "  端口 5174 仍被占用"
    else
        log_success "  端口 5174 已释放"
    fi
    
    print_separator
}

# 执行主函数
main

