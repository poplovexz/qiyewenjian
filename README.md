# 代理记账营运内部系统

基于 FastAPI 和 Vue 3 的全栈 Web 应用，实现了代理记账系统的完整功能。

## 📚 目录

- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [核心功能](#核心功能)
- [文档导航](#文档导航)
- [开发指南](#开发指南)
- [部署指南](#部署指南)

---

## 🛠 技术栈

- **后端**: FastAPI (Python 3.11) + PostgreSQL + SQLAlchemy ORM
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia
- **认证**: JWT + RBAC权限系统
- **缓存**: Redis
- **包管理**: Poetry (后端), PNPM (前端)
- **测试**: Pytest (后端), Vitest (前端)

---

## 🚀 快速开始

### 一键启动（推荐）

```bash
# 启动所有服务（前端 + 后端）
./start_all.sh

# 停止所有服务
./stop_all.sh
```

详细说明：[一键启动脚本说明.md](./一键启动脚本说明.md) 或 [快速启动指南.md](./快速启动指南.md)

### 手动启动

#### 后端设置

```bash
cd packages/backend
poetry install
poetry run python src/init_db.py
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端设置

```bash
cd packages/frontend
pnpm install
pnpm dev
```

#### 环境要求

- **Node.js**: >= 18.0.0
- **Python**: >= 3.11
- **PostgreSQL**: >= 14
- **Redis**: >= 6.0
- **pnpm**: >= 8.0.0

#### 端口配置

⚠️ **重要**：系统使用固定端口，请勿修改

- **后端服务**: 8000
- **前端服务**: 5174

---

## 📁 项目结构

```
/var/www/
├── packages/
│   ├── backend/              # FastAPI 后端
│   │   ├── src/
│   │   │   ├── api/         # API路由
│   │   │   ├── models/      # 数据模型
│   │   │   ├── services/    # 业务逻辑
│   │   │   ├── schemas/     # Pydantic模型
│   │   │   └── core/        # 核心配置
│   │   └── tests/           # 后端测试
│   └── frontend/            # Vue 3 前端
│       ├── src/
│       │   ├── api/         # API调用
│       │   ├── views/       # 页面组件
│       │   ├── components/  # 通用组件
│       │   ├── stores/      # Pinia状态管理
│       │   └── router/      # 路由配置
│       └── tests/           # 前端测试
├── docs/                    # 文档目录
│   ├── FEATURES.md         # 功能实现文档
│   ├── BUGFIXES.md         # Bug修复记录
│   └── DEPLOYMENT.md       # 部署指南
├── scripts/                 # 工具脚本
├── README.md               # 本文件
└── test-config.md          # 测试配置
```

---

## ✨ 核心功能

### 用户与权限管理
- ✅ 基于RBAC的权限系统
- ✅ 用户、角色、权限管理
- ✅ 权限自动识别与代码生成
- ✅ 菜单和按钮级别权限控制

### 线索管理
- ✅ 线索创建与跟进
- ✅ 线索来源管理
- ✅ 线索状态自动流转
- ✅ 线索转化跟踪（报价、合同）

### 客户管理
- ✅ 客户信息管理
- ✅ 客户状态跟踪
- ✅ 服务记录管理
- ✅ 客户自动创建（从线索）

### 合同管理
- ✅ 合同模板管理
- ✅ 合同自动生成
- ✅ 合同变量替换
- ✅ 电子签署
- ✅ 合同审核流程

### 审核工作流
- ✅ 多级审核流程
- ✅ 审核规则自动匹配
- ✅ 审核任务分配与通知
- ✅ 审核历史记录

### 银行汇款
- ✅ 汇款单据管理
- ✅ 汇款通知发送
- ✅ 汇款审核流程
- ✅ 汇款状态跟踪

### 产品管理
- ✅ 产品创建与编辑
- ✅ 产品分类管理
- ✅ 产品定价配置

### 代理记账
- ✅ 代理记账服务限制
- ✅ 服务包配置
- ✅ 服务状态跟踪

---

## 📖 文档导航

### 快速指南
- [快速启动指南.md](./快速启动指南.md) - 系统快速启动
- [一键启动脚本说明.md](./一键启动脚本说明.md) - 启动脚本详解
- [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) - 英文快速指南

### 功能使用指南
- [审核规则设置指南.md](./审核规则设置指南.md) - 审核规则配置
- [AUDIT_WORKFLOW_QUICK_START.md](./AUDIT_WORKFLOW_QUICK_START.md) - 审核工作流快速开始
- [合同模板管理使用指南.md](./合同模板管理使用指南.md) - 合同模板使用
- [USER_PERMISSION_MANAGEMENT_GUIDE.md](./USER_PERMISSION_MANAGEMENT_GUIDE.md) - 权限管理指南
- [客户管理访问指南.md](./客户管理访问指南.md) - 客户管理使用
- [DAILI_JIZHANG_LIMIT_QUICK_GUIDE.md](./DAILI_JIZHANG_LIMIT_QUICK_GUIDE.md) - 代理记账限制指南

### 设置指南
- [BANK_PAYMENT_SETUP_GUIDE.md](./BANK_PAYMENT_SETUP_GUIDE.md) - 银行汇款设置
- [BANK_PAYMENT_AUDIT_SETUP_GUIDE.md](./BANK_PAYMENT_AUDIT_SETUP_GUIDE.md) - 银行汇款审核设置
- [BANK_TRANSFER_AUDIT_CONFIGURATION_GUIDE.md](./BANK_TRANSFER_AUDIT_CONFIGURATION_GUIDE.md) - 银行转账审核配置

### 技术文档
- [docs/FEATURES.md](./docs/FEATURES.md) - 功能实现详细文档
- [docs/BUGFIXES.md](./docs/BUGFIXES.md) - Bug修复记录
- [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) - 部署完整指南
- [test-config.md](./test-config.md) - 测试配置说明
- [BACKEND_SCRIPTS_README.md](./BACKEND_SCRIPTS_README.md) - 后端脚本说明
- [XIANSUO_AUTO_STATUS_FLOW.md](./XIANSUO_AUTO_STATUS_FLOW.md) - 线索状态流转

### 开发者文档
- [AGENTS.md](./AGENTS.md) - AI助手规则
- [docs/AUTHENTICATION_BEST_PRACTICES.md](./docs/AUTHENTICATION_BEST_PRACTICES.md) - 认证最佳实践
- [docs/AUTHENTICATION_ISSUE_RESOLUTION.md](./docs/AUTHENTICATION_ISSUE_RESOLUTION.md) - 认证问题解决

---

## 💻 开发指南

### 测试

```bash
# 运行所有测试
pnpm test

# 后端测试
cd packages/backend
poetry run pytest

# 前端测试
cd packages/frontend
pnpm test

# 测试覆盖率
pnpm test:coverage
```

详细测试配置：[test-config.md](./test-config.md)

### 代码规范

```bash
# 代码检查
pnpm lint

# 自动修复
pnpm lint:fix

# 代码格式化
pnpm format
```

### 提交规范

格式：`类型(范围): 描述`

类型：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例：`feat(backend): 添加客户管理路由`

---

## 🚢 部署指南

### 快速部署

```bash
# 快速部署脚本
./quick-deploy.sh

# 企业部署脚本
./enterprise-deploy.sh
```

### 详细部署文档

参考：[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)

包含：
- ✅ 开发环境配置
- ✅ 生产环境部署
- ✅ Nginx配置
- ✅ Systemd服务配置
- ✅ 部署检查清单
- ✅ 常见问题解决
- ✅ 回滚方案

---

## 🔧 常用脚本

### 后端脚本

```bash
# 创建管理员用户
cd packages/backend
poetry run python create_admin_user.py

# 初始化审核规则
poetry run python create_audit_rule.py

# 初始化银行汇款工作流
poetry run python init_bank_payment_workflow.py
```

详细说明：[BACKEND_SCRIPTS_README.md](./BACKEND_SCRIPTS_README.md)

### 服务管理

```bash
# 启动所有服务
./start_all.sh

# 启动后端
./start_backend.sh

# 启动前端
./start_frontend.sh

# 停止所有服务
./stop_all.sh

# 查看后端状态
./status_backend.sh
```

---

## 📝 更新日志

### 2024-10
- ✅ 完成审核工作流系统
- ✅ 完成银行汇款功能
- ✅ 完成合同管理增强
- ✅ 完成权限自动识别
- ✅ 完成线索自动状态流转
- ✅ 修复大量Bug（详见 [docs/BUGFIXES.md](./docs/BUGFIXES.md)）
- ✅ 文档整理与优化

---

## 📞 支持

如有问题，请查看：
1. [docs/BUGFIXES.md](./docs/BUGFIXES.md) - 常见问题解决方案
2. [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) - 部署相关问题
3. 相关功能使用指南

---

## 📄 许可证

本项目为内部系统，仅供公司内部使用。
