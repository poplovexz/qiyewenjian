---
type: "agent_requested"
description: "Example description"
---

# 代理记账营运内部系统

## 项目概述
本项目为基于 FastAPI 和 Vue 3 的全栈 Web 应用，实现了代理记账系统的核心功能。当前版本 v0.1.1 已完成用户权限管理、产品管理和代理记账套餐等核心模块。

## 技术栈

### 后端技术
- **框架**: FastAPI (Python 3.11)
- **数据库**: PostgreSQL + SQLAlchemy ORM
- **认证**: JWT + RBAC 权限控制
- **包管理**: Poetry
- **测试**: Pytest
- **端口**: 8000（固定端口，不可更改）

### 前端技术
- **框架**: Vue 3 + TypeScript
- **状态管理**: Pinia
- **UI组件**: Element Plus
- **构建工具**: Vite
- **包管理**: PNPM
- **测试**: Vitest
- **端口**: 5174（固定端口，不可更改）

## 项目结构

```
proxy-accounting-system/
├── packages/
│   ├── backend/                 # FastAPI 后端
│   │   ├── src/
│   │   │   ├── api/            # API 路由层
│   │   │   ├── models/         # 数据模型层
│   │   │   ├── schemas/        # Pydantic 模式
│   │   │   ├── services/       # 业务逻辑层
│   │   │   ├── core/           # 核心配置
│   │   │   └── scripts/        # 初始化脚本
│   │   └── tests/              # 后端测试
│   └── frontend/               # Vue 3 前端
│       ├── src/
│       │   ├── api/            # API 调用层
│       │   ├── components/     # 可复用组件
│       │   ├── views/          # 页面组件
│       │   ├── stores/         # Pinia 状态管理
│       │   ├── types/          # TypeScript 类型定义
│       │   └── utils/          # 工具函数
│       └── tests/              # 前端测试
├── scripts/                    # 项目脚本
└── README.md
```

## 安装与运行

### 环境要求
- Node.js >= 18.0.0
- Python >= 3.11
- PostgreSQL >= 13
- PNPM >= 8.0.0

### 后端设置
```bash
cd packages/backend
poetry install
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 DATABASE_URL 和 JWT_SECRET
poetry run python src/init_db.py
poetry run uvicorn src.main:app --reload --port 8000
```

### 前端设置
```bash
cd packages/frontend
pnpm install
pnpm dev  # 自动使用 5174 端口
```

### 环境变量配置
**后端 (.env)**:
```env
DATABASE_URL=postgresql://username:password@localhost/proxy_db
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

**数据库准备**:
```sql
CREATE DATABASE proxy_db;
```

## 已实现功能模块

### 1. 用户权限管理模块 ✅
**数据模型**: `yonghu`, `jiaose`, `quanxian`, `yonghu_jiaose`, `jiaose_quanxian`
**功能特性**:
- 用户管理：用户注册、登录、信息维护
- 角色管理：角色创建、编辑、权限分配、状态管理
- 权限管理：权限树结构、动态权限控制
- JWT认证：安全的token认证机制
- RBAC权限：基于角色的访问控制

**API端点**:
- `/api/v1/auth/*` - 认证相关接口
- `/api/v1/users/*` - 用户管理接口
- `/api/v1/user-management/roles/*` - 角色管理接口
- `/api/v1/user-management/permissions/*` - 权限管理接口

**前端页面**:
- 用户列表页面 (`UserList.vue`)
- 角色管理页面 (`RoleListSimple.vue`)
- 权限管理页面 (`PermissionList.vue`, `PermissionListSimple.vue`)
- 用户组件 (`PermissionForm.vue`, `RolePermissionDialog.vue`)

### 2. 产品管理模块 ✅
**数据模型**: `chanpin_fenlei`, `chanpin_xiangmu`, `chanpin_buzou`
**功能特性**:
- 产品分类：分类创建、编辑、层级管理
- 产品项目：项目管理、报价设置、业务配置
- 产品步骤：步骤定义、流程管理、时间控制
- 完整的CRUD操作和业务逻辑

**API端点**:
- `/api/v1/product-management/categories/*` - 产品分类管理
- `/api/v1/product-management/products/*` - 产品项目管理
- `/api/v1/product-management/*` - 产品步骤管理

**前端页面**:
- 产品管理主页 (`ProductManagement.vue`)
- 产品列表页面 (`ProductList.vue`)
- 分类列表页面 (`CategoryList.vue`)
- 代理记账套餐页面 (`BookkeepingPackages.vue`)
- 产品组件 (`CategoryForm.vue`, `ProductForm.vue`, `ProductStepsDialog.vue`)

### 3. 客户管理模块 ✅
**数据模型**: `kehu`, `fuwu_jilu`
**功能特性**:
- 客户信息管理：基本信息、联系方式、状态管理
- 服务记录：服务历史、跟踪记录

**API端点**:
- `/api/v1/customers/*` - 客户管理接口
- `/api/v1/service-records/*` - 服务记录管理

**前端页面**:
- 客户列表页面 (`CustomerList.vue`)
- 客户详情页面 (`CustomerDetail.vue`)

### 4. 基础框架模块 ✅
**核心功能**:
- 数据库连接和ORM配置
- JWT安全认证机制
- API路由聚合和版本管理
- 统一的响应格式和错误处理
- 基础模型类和审计字段
- 软删除机制

**前端基础**:
- 主布局组件 (`MainLayout.vue`)
- 路由配置和权限守卫
- API请求封装和拦截器
- 状态管理和数据持久化
- 工具函数和类型定义

## 规划中的功能模块

### 5. 合同管理模块 🚧
**数据模型**: `hetong_moban`, `hetong`
**计划功能**:
- 合同模板库管理
- 合同生成和编辑
- 电子签章集成
- 合同归档和查询

### 6. 订单收费模块 🚧
**数据模型**: `dingdan`, `fapiao`
**计划功能**:
- 订单创建和管理
- 套餐选择和定价
- 发票管理和开具
- 支付集成

### 7. 任务管理模块 🚧
**数据模型**: `renwu`
**计划功能**:
- 任务分配和跟踪
- 工作流程管理
- 进度监控和提醒
- 绩效统计

### 8. 财务账务模块 🚧
**数据模型**: `pingzheng`, `zhangbu`
**计划功能**:
- 凭证管理和录入
- 账簿生成和维护
- 财务报表生成
- 税务申报支持

## 开发规范

### 命名规范
- **数据库表名**: 中文拼音小写，下划线分隔 (如: `yonghu`, `chanpin_fenlei`)
- **字段名**: 中文拼音小写，下划线分隔 (如: `yonghu_ming`, `xiangmu_mingcheng`)
- **API路由**: 英文小写，连字符分隔 (如: `/user-management`, `/product-management`)
- **前端组件**: PascalCase (如: `UserList.vue`, `ProductForm.vue`)
- **前端文件**: camelCase (如: `userService.ts`, `productTypes.ts`)

### 代码结构规范
- **后端**: 分层架构 (API -> Service -> Model)
- **前端**: 组件化开发 (Views -> Components -> API)
- **数据库**: 统一使用UUID主键，软删除机制
- **API**: RESTful设计，统一响应格式

### 测试规范
```bash
# 后端测试
cd packages/backend
poetry run pytest

# 前端测试
cd packages/frontend
pnpm test

# 端到端测试
pnpm test:e2e
```

### Git提交规范
**格式**: `类型(范围): 描述`

**类型说明**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例**:
- `feat(backend): 添加产品管理API接口`
- `fix(frontend): 修复用户权限显示问题`
- `docs(readme): 更新安装说明`

## 当前版本状态

**版本**: v0.1.1
**提交哈希**: 4a64ea9abb664d9498ae7d93203c9b9e5c23c125
**完成度**:
- ✅ 用户权限管理 (100%)
- ✅ 产品管理 (100%)
- ✅ 客户管理 (100%)
- ✅ 基础框架 (100%)
- 🚧 合同管理 (0%)
- 🚧 订单收费 (0%)
- 🚧 任务管理 (0%)
- 🚧 财务账务 (0%)

**统计数据**:
- 后端文件: 68个Python文件
- 前端页面: 23个Vue组件
- 数据表: 13个核心业务表
- API接口: 30+个RESTful接口

## 下一步开发计划

1. **合同管理模块开发**
   - 设计合同模板数据结构
   - 实现合同生成和编辑功能
   - 开发合同管理前端界面

2. **订单收费模块开发**
   - 完善订单流程设计
   - 集成支付接口
   - 实现发票管理功能

3. **系统优化**
   - 性能优化和缓存策略
   - 安全加固和权限细化
   - 用户体验改进

## 注意事项

⚠️ **重要约束**:
- 后端服务固定使用 **8000端口**
- 前端服务固定使用 **5174端口**
- 不得使用其他端口配置

⚠️ **开发要求**:
- 所有前端功能必须完整验收，确保按钮和交互正常工作
- 遵循现有的命名规范和代码结构
- 提交前必须通过测试验证
