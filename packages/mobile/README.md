# 服务人员任务管理移动端

基于 Vue 3 + TypeScript + Vite + Vant 4 的移动端H5应用。

## 功能特性

- ✅ 用户登录/退出
- ✅ 任务列表查看（支持筛选、下拉刷新、上拉加载）
- ✅ 任务详情查看
- ✅ 任务状态管理（开始/完成/暂停）
- ✅ 工时记录
- ✅ 任务统计
- ✅ 个人中心

## 技术栈

- **框架**: Vue 3.4
- **语言**: TypeScript 5.3
- **构建工具**: Vite 5.0
- **UI组件库**: Vant 4.8
- **状态管理**: Pinia 2.1
- **路由**: Vue Router 4.2
- **HTTP客户端**: Axios 1.6
- **日期处理**: Day.js 1.11

## 项目结构

```
packages/mobile/
├── src/
│   ├── api/              # API接口
│   │   ├── auth.ts       # 认证相关API
│   │   └── task.ts       # 任务相关API
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # Pinia状态管理
│   │   └── user.ts       # 用户状态
│   ├── types/            # TypeScript类型定义
│   │   └── task.ts       # 任务类型
│   ├── utils/            # 工具函数
│   │   └── request.ts    # Axios封装
│   ├── views/            # 页面组件
│   │   ├── Login.vue     # 登录页
│   │   ├── Home.vue      # 首页
│   │   ├── TaskList.vue  # 任务列表
│   │   ├── TaskDetail.vue# 任务详情
│   │   ├── OrderList.vue # 工单列表
│   │   ├── OrderDetail.vue# 工单详情
│   │   └── Profile.vue   # 个人中心
│   ├── App.vue           # 根组件
│   ├── main.ts           # 入口文件
│   └── style.css         # 全局样式
├── index.html            # HTML模板
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TypeScript配置
├── package.json          # 项目配置
├── .env.development      # 开发环境变量
└── .env.production       # 生产环境变量
```

## 安装依赖

```bash
cd packages/mobile
pnpm install
```

## 开发

```bash
pnpm dev
```

应用将在 http://localhost:5175 启动

## 构建

```bash
pnpm build
```

## 预览

```bash
pnpm preview
```

## 环境变量

### 开发环境 (.env.development)
```
VITE_APP_TITLE=服务人员任务管理
VITE_APP_BASE_API=/api/v1
VITE_APP_PORT=5175
```

### 生产环境 (.env.production)
```
VITE_APP_TITLE=服务人员任务管理
VITE_APP_BASE_API=/api/v1
```

## API端点

所有API请求都会通过Vite代理转发到后端服务（http://localhost:8000）

### 认证相关
- `POST /api/v1/auth/login` - 登录
- `GET /api/v1/users/me` - 获取当前用户信息

### 任务相关
- `GET /api/v1/task-items/my-tasks` - 获取我的任务列表
- `GET /api/v1/task-items/statistics` - 获取任务统计
- `POST /api/v1/task-items/{id}/start` - 开始任务
- `POST /api/v1/task-items/{id}/complete` - 完成任务
- `POST /api/v1/task-items/{id}/pause` - 暂停任务

## 路由

- `/login` - 登录页
- `/home` - 首页
- `/tasks` - 任务列表
- `/tasks/:id` - 任务详情
- `/orders` - 工单列表
- `/orders/:id` - 工单详情
- `/profile` - 个人中心

## 注意事项

1. **端口配置**: 移动端使用5175端口，避免与前端PC端（5174）冲突
2. **Token管理**: Token存储在Pinia中并持久化到localStorage
3. **路由守卫**: 所有需要登录的页面都会检查Token，未登录会跳转到登录页
4. **移动端适配**: 使用postcss-pxtorem进行移动端适配，基准值为37.5
5. **API代理**: 开发环境下，所有/api请求会代理到http://localhost:8000

## 开发建议

1. 确保后端服务运行在8000端口
2. 使用Chrome DevTools的移动设备模拟器进行调试
3. 建议使用iPhone 6/7/8 (375x667) 或 iPhone X (375x812) 进行测试

