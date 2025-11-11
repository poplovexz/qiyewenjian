#!/bin/bash

#############################################
# 后端服务状态查看脚本
# 功能：查看所有后端服务的运行状态
#############################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印分隔线
print_separator() {
    echo -e "${BLUE}=========================================${NC}"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# 检查系统服务状态
check_system_service() {
    local service_name=$1
    local display_name=$2
    
    if systemctl is-active --quiet "$service_name"; then
        echo -e "  ${GREEN}✓${NC} $display_name: ${GREEN}运行中${NC}"
        
        # 显示详细信息
        local status=$(systemctl status "$service_name" 2>/dev/null | grep "Active:" | sed 's/^[[:space:]]*//')
        echo -e "    ${CYAN}状态:${NC} $status"
    else
        echo -e "  ${RED}✗${NC} $display_name: ${RED}未运行${NC}"
    fi
}

# 检查端口状态
check_port_status() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $service_name (端口 $port): ${GREEN}运行中${NC}"
        
        # 显示进程信息
        local pid=$(lsof -ti:$port 2>/dev/null | head -1)
        if [ -n "$pid" ]; then
            local cmd=$(ps -p $pid -o cmd= 2>/dev/null)
            echo -e "    ${CYAN}PID:${NC} $pid"
            echo -e "    ${CYAN}命令:${NC} ${cmd:0:80}..."
        fi
        
        # 尝试健康检查
        if [ "$port" = "8000" ]; then
            local health=$(curl -s http://localhost:8000/health 2>/dev/null)
            if [ -n "$health" ]; then
                echo -e "    ${CYAN}健康检查:${NC} ${GREEN}通过${NC}"
                # 解析 JSON 状态
                local status=$(echo "$health" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
                if [ -n "$status" ]; then
                    echo -e "    ${CYAN}服务状态:${NC} $status"
                fi
            else
                echo -e "    ${CYAN}健康检查:${NC} ${YELLOW}无响应${NC}"
            fi
        fi
    else
        echo -e "  ${RED}✗${NC} $service_name (端口 $port): ${RED}未运行${NC}"
    fi
}

# 检查数据库连接
check_database() {
    print_header "数据库连接"
    
    # 检查 PostgreSQL
    if command -v psql >/dev/null 2>&1; then
        if psql -U postgres -d proxy_db -c "SELECT 1;" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} PostgreSQL 连接: ${GREEN}正常${NC}"
            
            # 获取数据库大小
            local db_size=$(psql -U postgres -d proxy_db -t -c "SELECT pg_size_pretty(pg_database_size('proxy_db'));" 2>/dev/null | xargs)
            if [ -n "$db_size" ]; then
                echo -e "    ${CYAN}数据库大小:${NC} $db_size"
            fi
        else
            echo -e "  ${YELLOW}⚠${NC} PostgreSQL 连接: ${YELLOW}无法连接${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} psql 命令未找到"
    fi
}

# 检查 Redis 连接
check_redis() {
    print_header "Redis 连接"
    
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli ping >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} Redis 连接: ${GREEN}正常${NC}"
            
            # 获取 Redis 信息
            local redis_version=$(redis-cli INFO server 2>/dev/null | grep "redis_version:" | cut -d':' -f2 | tr -d '\r')
            local redis_keys=$(redis-cli DBSIZE 2>/dev/null | cut -d':' -f2 | xargs)
            
            if [ -n "$redis_version" ]; then
                echo -e "    ${CYAN}版本:${NC} $redis_version"
            fi
            if [ -n "$redis_keys" ]; then
                echo -e "    ${CYAN}键数量:${NC} $redis_keys"
            fi
        else
            echo -e "  ${YELLOW}⚠${NC} Redis 连接: ${YELLOW}无法连接${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} redis-cli 命令未找到"
    fi
}

# 显示日志信息
show_logs() {
    print_header "最近日志 (最后 10 行)"
    
    if [ -f "/tmp/backend_8000.log" ]; then
        echo -e "${CYAN}后端日志:${NC}"
        tail -10 /tmp/backend_8000.log 2>/dev/null | sed 's/^/  /'
    else
        echo -e "  ${YELLOW}日志文件不存在: /tmp/backend_8000.log${NC}"
    fi
}

# 显示访问地址
show_urls() {
    print_header "访问地址"
    
    echo -e "  ${CYAN}API 服务:${NC}     http://localhost:8000"
    echo -e "  ${CYAN}API 文档:${NC}     http://localhost:8000/docs"
    echo -e "  ${CYAN}健康检查:${NC}     http://localhost:8000/health"
    echo -e "  ${CYAN}OpenAPI:${NC}      http://localhost:8000/api/v1/openapi.json"
}

# 显示有用的命令
show_commands() {
    print_header "常用命令"
    
    echo -e "  ${CYAN}启动服务:${NC}     ./start_backend_all.sh"
    echo -e "  ${CYAN}停止服务:${NC}     ./stop_backend_all.sh"
    echo -e "  ${CYAN}查看日志:${NC}     tail -f /tmp/backend_8000.log"
    echo -e "  ${CYAN}重启服务:${NC}     ./stop_backend_all.sh && ./start_backend_all.sh"
}

# 主函数
main() {
    clear
    print_separator
    echo -e "${GREEN}后端服务状态总览${NC}"
    print_separator
    echo ""
    
    # 系统服务状态
    print_header "系统服务"
    check_system_service "postgresql@16-main.service" "PostgreSQL"
    check_system_service "redis-server.service" "Redis"
    echo ""
    
    # 应用服务状态
    print_header "应用服务"
    check_port_status "8000" "后端 API 服务"
    echo ""
    
    # 数据库连接
    check_database
    echo ""
    
    # Redis 连接
    check_redis
    echo ""
    
    # 访问地址
    show_urls
    echo ""
    
    # 日志信息
    show_logs
    echo ""
    
    # 常用命令
    show_commands
    echo ""
    
    print_separator
    echo -e "${GREEN}状态检查完成${NC}"
    print_separator
}

# 执行主函数
main

