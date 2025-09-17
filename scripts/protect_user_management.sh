#!/bin/bash

# 用户管理模块保护脚本
# 用于设置和解除用户管理模块的只读保护

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 用户管理相关文件列表
USER_MANAGEMENT_FILES=(
    # 后端模型文件
    "packages/backend/src/models/yonghu_guanli/"
    "packages/backend/src/schemas/yonghu_guanli/"
    "packages/backend/src/services/yonghu_guanli/"
    "packages/backend/src/api/api_v1/endpoints/yonghu.py"
    "packages/backend/src/api/api_v1/endpoints/yonghu_guanli/"
    "packages/backend/src/api/api_v1/endpoints/auth.py"
    
    # 前端文件
    "packages/frontend/src/types/user.ts"
    "packages/frontend/src/api/modules/user.ts"
    "packages/frontend/src/api/auth.ts"
    "packages/frontend/src/stores/user.ts"
    "packages/frontend/src/stores/modules/auth.ts"
    "packages/frontend/src/composables/useAuth.ts"
    "packages/frontend/src/views/user/UserList.vue"
    "packages/frontend/src/components/user/"
    "packages/frontend/src/tests/user.test.ts"
)

# 显示帮助信息
show_help() {
    echo -e "${BLUE}用户管理模块保护脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  protect     设置用户管理模块为只读保护"
    echo "  unprotect   解除用户管理模块的只读保护"
    echo "  status      查看用户管理模块的保护状态"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 protect    # 启用保护"
    echo "  $0 unprotect  # 解除保护"
    echo "  $0 status     # 查看状态"
}

# 设置文件为只读
protect_files() {
    echo -e "${YELLOW}正在设置用户管理模块为只读保护...${NC}"
    
    for file_path in "${USER_MANAGEMENT_FILES[@]}"; do
        if [ -e "$file_path" ]; then
            if [ -d "$file_path" ]; then
                echo -e "${BLUE}保护目录: $file_path${NC}"
                chmod -R 444 "$file_path"
                find "$file_path" -type d -exec chmod 555 {} \;
            else
                echo -e "${BLUE}保护文件: $file_path${NC}"
                chmod 444 "$file_path"
            fi
        else
            echo -e "${YELLOW}警告: 文件不存在 $file_path${NC}"
        fi
    done
    
    echo -e "${GREEN}✅ 用户管理模块已设置为只读保护${NC}"
    echo -e "${YELLOW}📝 保护详情已记录在 USER_MANAGEMENT_READONLY.md${NC}"
}

# 解除只读保护
unprotect_files() {
    echo -e "${YELLOW}正在解除用户管理模块的只读保护...${NC}"
    
    read -p "确定要解除用户管理模块的只读保护吗？(y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo -e "${BLUE}操作已取消${NC}"
        return
    fi
    
    for file_path in "${USER_MANAGEMENT_FILES[@]}"; do
        if [ -e "$file_path" ]; then
            if [ -d "$file_path" ]; then
                echo -e "${BLUE}解除目录保护: $file_path${NC}"
                chmod -R 644 "$file_path"
                find "$file_path" -type d -exec chmod 755 {} \;
            else
                echo -e "${BLUE}解除文件保护: $file_path${NC}"
                chmod 644 "$file_path"
            fi
        fi
    done
    
    echo -e "${GREEN}✅ 用户管理模块的只读保护已解除${NC}"
    echo -e "${RED}⚠️  请谨慎修改，修改完成后建议重新启用保护${NC}"
}

# 查看保护状态
check_status() {
    echo -e "${BLUE}用户管理模块保护状态:${NC}"
    echo ""
    
    protected_count=0
    total_count=0
    
    for file_path in "${USER_MANAGEMENT_FILES[@]}"; do
        if [ -e "$file_path" ]; then
            if [ -d "$file_path" ]; then
                # 检查目录中的文件
                while IFS= read -r -d '' file; do
                    total_count=$((total_count + 1))
                    perms=$(stat -c "%a" "$file")
                    if [[ "$perms" == "444" ]] || [[ "$perms" == "555" ]]; then
                        protected_count=$((protected_count + 1))
                        echo -e "${GREEN}✓${NC} $file (只读)"
                    else
                        echo -e "${RED}✗${NC} $file (可写)"
                    fi
                done < <(find "$file_path" -type f -print0)
            else
                total_count=$((total_count + 1))
                perms=$(stat -c "%a" "$file_path")
                if [[ "$perms" == "444" ]]; then
                    protected_count=$((protected_count + 1))
                    echo -e "${GREEN}✓${NC} $file_path (只读)"
                else
                    echo -e "${RED}✗${NC} $file_path (可写)"
                fi
            fi
        fi
    done
    
    echo ""
    echo -e "${BLUE}统计信息:${NC}"
    echo -e "  总文件数: $total_count"
    echo -e "  受保护文件数: $protected_count"
    echo -e "  保护率: $(( protected_count * 100 / total_count ))%"
    
    if [ $protected_count -eq $total_count ]; then
        echo -e "${GREEN}✅ 用户管理模块完全受保护${NC}"
    elif [ $protected_count -gt 0 ]; then
        echo -e "${YELLOW}⚠️  用户管理模块部分受保护${NC}"
    else
        echo -e "${RED}❌ 用户管理模块未受保护${NC}"
    fi
}

# 主函数
main() {
    case "${1:-help}" in
        "protect")
            protect_files
            ;;
        "unprotect")
            unprotect_files
            ;;
        "status")
            check_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 检查是否在正确的目录中运行
if [ ! -f "packages/backend/src/models/yonghu_guanli/yonghu.py" ]; then
    echo -e "${RED}错误: 请在项目根目录中运行此脚本${NC}"
    exit 1
fi

# 运行主函数
main "$@"
