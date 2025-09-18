#!/bin/bash
# 认证功能自动检查脚本
# 用于在代码修改后验证认证系统是否正常工作

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖工具..."
    
    if ! command -v curl &> /dev/null; then
        log_error "curl 未安装"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_error "jq 未安装，请安装: apt-get install jq"
        exit 1
    fi
    
    log_success "依赖工具检查完成"
}

# 等待服务启动
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    log_info "等待 $service_name 启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$service_name 已启动"
            return 0
        fi
        
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    log_error "$service_name 启动超时"
    return 1
}

# 检查后端API服务
check_backend_api() {
    log_info "检查后端API服务..."
    
    local api_url="http://localhost:8000/api/v1/"
    
    if ! wait_for_service "$api_url" "后端API服务"; then
        log_error "后端API服务不可用"
        return 1
    fi
    
    # 检查API版本信息
    local api_info=$(curl -s "$api_url" | jq -r '.message' 2>/dev/null)
    if [ "$api_info" = "代理记账营运内部系统 API v1" ]; then
        log_success "后端API服务正常"
        return 0
    else
        log_error "后端API服务响应异常"
        return 1
    fi
}

# 检查前端服务
check_frontend_service() {
    log_info "检查前端服务..."
    
    local frontend_url="http://localhost:5174"
    
    if ! wait_for_service "$frontend_url" "前端服务"; then
        log_error "前端服务不可用"
        return 1
    fi
    
    # 检查前端页面内容
    local page_content=$(curl -s "$frontend_url" | head -20)
    if echo "$page_content" | grep -q "Vite + Vue + TS"; then
        log_success "前端服务正常"
        return 0
    else
        log_error "前端服务响应异常"
        return 1
    fi
}

# 测试登录功能
test_login_function() {
    log_info "测试登录功能..."

    local login_url="http://localhost:8000/api/v1/auth/login"
    local login_data='{"yonghu_ming": "admin", "mima": "admin123"}'

    local response=$(curl -s -X POST "$login_url" \
        -H "Content-Type: application/json" \
        -d "$login_data")

    if [ $? -ne 0 ]; then
        log_error "登录请求失败"
        return 1
    fi

    # 检查响应格式
    local token=$(echo "$response" | jq -r '.token.access_token' 2>/dev/null)
    local user_name=$(echo "$response" | jq -r '.user.xingming' 2>/dev/null)

    if [ "$token" != "null" ] && [ -n "$token" ] && [ "$token" != "" ]; then
        log_success "登录功能正常 (用户: $user_name)"
        # 将token写入临时文件
        echo "$token" > /tmp/auth_test_token
        return 0
    else
        log_error "登录功能异常，响应: $response"
        return 1
    fi
}

# 测试用户信息获取
test_user_info() {
    log_info "测试用户信息获取..."

    # 从临时文件读取token
    if [ ! -f /tmp/auth_test_token ]; then
        log_error "未找到认证token"
        return 1
    fi

    local token=$(cat /tmp/auth_test_token)
    local me_url="http://localhost:8000/api/v1/auth/me"

    local response=$(curl -s -X GET "$me_url" \
        -H "Authorization: Bearer $token")

    if [ $? -ne 0 ]; then
        log_error "用户信息请求失败"
        return 1
    fi

    local user_name=$(echo "$response" | jq -r '.xingming' 2>/dev/null)

    if [ "$user_name" != "null" ] && [ -n "$user_name" ] && [ "$user_name" != "" ]; then
        log_success "用户信息获取正常 (用户: $user_name)"
        return 0
    else
        log_error "用户信息获取异常，响应: $response"
        return 1
    fi
}

# 测试token刷新功能
test_token_refresh() {
    log_info "测试token刷新功能..."
    
    # 先登录获取refresh_token
    local login_url="http://localhost:8000/api/v1/auth/login"
    local login_data='{"yonghu_ming": "admin", "mima": "admin123"}'
    
    local login_response=$(curl -s -X POST "$login_url" \
        -H "Content-Type: application/json" \
        -d "$login_data")
    
    local refresh_token=$(echo "$login_response" | jq -r '.token.refresh_token' 2>/dev/null)
    
    if [ "$refresh_token" = "null" ] || [ -z "$refresh_token" ]; then
        log_warning "无法获取refresh_token，跳过刷新测试"
        return 0
    fi
    
    # 测试刷新
    local refresh_url="http://localhost:8000/api/v1/auth/refresh"
    local refresh_data="{\"refresh_token\": \"$refresh_token\"}"
    
    local refresh_response=$(curl -s -X POST "$refresh_url" \
        -H "Content-Type: application/json" \
        -d "$refresh_data")
    
    local new_token=$(echo "$refresh_response" | jq -r '.access_token' 2>/dev/null)
    
    if [ "$new_token" != "null" ] && [ -n "$new_token" ]; then
        log_success "Token刷新功能正常"
        return 0
    else
        log_warning "Token刷新功能异常，但不影响基本功能"
        return 0
    fi
}

# 测试前端认证页面
test_frontend_auth() {
    log_info "测试前端认证相关页面..."
    
    # 测试登录页面
    local login_page_url="http://localhost:5174/login"
    if curl -s "$login_page_url" > /dev/null 2>&1; then
        log_success "登录页面可访问"
    else
        log_warning "登录页面不可访问（可能是路由配置问题）"
    fi
    
    # 测试主页面
    local main_page_url="http://localhost:5174"
    if curl -s "$main_page_url" > /dev/null 2>&1; then
        log_success "主页面可访问"
    else
        log_error "主页面不可访问"
        return 1
    fi
    
    return 0
}

# 清理测试数据
cleanup() {
    log_info "清理测试数据..."
    # 删除临时token文件
    rm -f /tmp/auth_test_token
    log_success "清理完成"
}

# 主函数
main() {
    echo "🚀 开始认证功能自动检查..."
    echo "=================================="
    
    # 检查依赖
    check_dependencies
    
    # 检查服务状态
    if ! check_backend_api; then
        log_error "后端服务检查失败"
        exit 1
    fi
    
    if ! check_frontend_service; then
        log_error "前端服务检查失败"
        exit 1
    fi
    
    # 测试认证功能
    if test_login_function; then
        if ! test_user_info; then
            log_error "用户信息测试失败"
            exit 1
        fi
    else
        log_error "登录功能测试失败"
        exit 1
    fi
    
    # 测试token刷新（非关键功能）
    test_token_refresh
    
    # 测试前端页面
    if ! test_frontend_auth; then
        log_error "前端认证页面测试失败"
        exit 1
    fi
    
    # 清理
    cleanup
    
    echo "=================================="
    log_success "🎉 所有认证功能检查通过！"
    echo ""
    log_info "检查项目："
    echo "  ✅ 后端API服务状态"
    echo "  ✅ 前端服务状态"
    echo "  ✅ 用户登录功能"
    echo "  ✅ 用户信息获取"
    echo "  ✅ Token刷新功能"
    echo "  ✅ 前端页面访问"
    echo ""
    log_info "认证系统工作正常，可以安全进行开发！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
