# 代理记账营运内部系统

基于 FastAPI 和 Vue 3 的全栈 Web 应用，实现了代理记账系统的功能。

## 技术栈

- **后端**: FastAPI (Python 3.11) + PostgreSQL (SQLAlchemy ORM)
- **前端**: Vue 3 + TypeScript + Pinia
- **认证**: JWT + RBAC
- **包管理**: Poetry (后端), PNPM (前端)
- **测试**: Pytest (后端), Vitest (前端)

## 项目结构

```
proxy-accounting-system/
├── packages/
│   ├── backend/          # FastAPI 后端
│   └── frontend/         # Vue 3 前端
├── README.md
└── .gitignore
```

## 安装与运行

### 后端设置

```bash
cd packages/backend
poetry install
poetry run python src/init_db.py
poetry run uvicorn src.main:app --reload --port 8000
```

### 前端设置

```bash
cd packages/frontend
pnpm install
pnpm dev
```

### 环境变量

- **后端**: 复制 `packages/backend/.env.example` 到 `.env`，设置 `DATABASE_URL` 和 `JWT_SECRET`
- 确保 PostgreSQL 运行并创建 `proxy_db`

## 功能模块

- **用户管理**: 角色（管理员、会计、客服、客户）、权限控制、访问日志
- **客户管理**: 信息录入、营业执照上传、状态管理
- **合同管理**: 模板库、自动生成、电子签章、归档
- **订单与收费**: 套餐选择、阶梯计费、支付对接、发票管理
- **任务管理**: 自动分配、进度跟踪、提醒通知
- **财务与账务**: 凭证管理、账簿管理、报表生成、税务申报
- **数据分析**: 客户增长、收入趋势、会计绩效、满意度分析
- **系统设置**: 服务周期、收费参数、日志管理

## 测试

```bash
# 后端测试
cd packages/backend
poetry run pytest

# 前端测试
cd packages/frontend
pnpm test
```

## 提交规范

格式：`类型(范围): 描述`

示例：`feat(backend): 添加客户管理路由`
