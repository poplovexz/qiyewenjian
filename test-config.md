# 测试配置指南

## 测试架构

### 后端测试 (Pytest)
- **单元测试**: 测试单个函数和类
- **集成测试**: 测试API端点和数据库交互
- **缓存测试**: 测试Redis缓存逻辑
- **权限测试**: 测试RBAC权限系统

### 前端测试 (Vitest)
- **组件测试**: 测试Vue组件
- **Store测试**: 测试Pinia状态管理
- **API测试**: 测试API调用逻辑
- **路由测试**: 测试路由守卫和权限

## 测试命令

### 开发环境
```bash
# 运行所有测试
pnpm test

# 分别运行后端和前端测试
pnpm test:backend
pnpm test:frontend

# 端到端测试
pnpm test:e2e

# CI环境测试 (生成JSON报告)
pnpm test:ci
```

### 测试覆盖率
```bash
# 后端覆盖率
cd packages/backend && poetry run pytest --cov=src --cov-report=html

# 前端覆盖率
cd packages/frontend && npm run test:coverage
```

## 关键测试用例

### 线索管理模块
1. **缓存分支测试**
   - Redis可用时的缓存命中/未命中
   - Redis不可用时的降级处理
   - 缓存失效和刷新逻辑

2. **权限断言测试**
   - 不同角色的访问权限
   - API端点的权限验证
   - 前端组件的权限显示

3. **数据一致性测试**
   - 创建/更新/删除操作
   - 并发访问处理
   - 事务回滚测试

### 认证系统测试
1. **Token管理**
   - JWT生成和验证
   - Token刷新机制
   - 过期处理

2. **权限系统**
   - RBAC权限检查
   - 动态权限更新
   - 权限继承

## 测试数据管理

### 测试数据库
- 使用独立的测试数据库
- 每次测试前重置数据
- 使用工厂模式生成测试数据

### Mock和Stub
- Redis连接Mock
- 外部API Mock
- 时间和随机数Mock

## CI/CD集成

### GitHub Actions示例
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: pnpm install
      - name: Run tests
        run: pnpm test:ci
```

## 性能测试

### 缓存性能
- 缓存命中率测试
- 响应时间对比
- 并发访问测试

### API性能
- 响应时间基准
- 吞吐量测试
- 内存使用监控

## 测试最佳实践

1. **测试隔离**: 每个测试独立运行
2. **数据清理**: 测试后清理数据
3. **Mock外部依赖**: 避免依赖外部服务
4. **覆盖率目标**: 后端>80%, 前端>70%
5. **持续集成**: 每次提交都运行测试
