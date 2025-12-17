# 审核规则测试404错误修复

## 🐛 问题描述

在审核规则配置页面点击"测试"按钮时，出现404错误：

```
Failed to load resource: the server responded with a status of 404 (Not Found)
:5174/api/v1/audit-rules/test/single:1

规则测试失败: Error: 测试请求失败
```

## 🔍 根本原因

**前端代理配置缺失**

前端 Vite 配置文件（`vite.config.ts`）中没有配置 API 代理，导致：

1. **请求发送到错误的服务器**:
   - 前端运行在 `http://localhost:5174`
   - 后端运行在 `http://localhost:8000`
   - 前端请求 `/api/v1/audit-rules/test/single` 时，没有代理配置
   - 请求被发送到 `http://localhost:5174/api/v1/audit-rules/test/single`（前端服务器）
   - 前端服务器没有这个路由，返回404

2. **正确的请求应该是**:
   - 请求应该被代理到 `http://localhost:8000/api/v1/audit-rules/test/single`（后端服务器）

## ✅ 修复方案

**文件**: `packages/frontend/vite.config.ts`

### 添加 API 代理配置

```typescript
// 修复前
server: {
  port: 5174,
  host: '0.0.0.0',
  strictPort: true
},

// 修复后
server: {
  port: 5174,
  host: '0.0.0.0',
  strictPort: true,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false
    }
  }
},
```

### 配置说明

- **`'/api'`**: 匹配所有以 `/api` 开头的请求
- **`target: 'http://localhost:8000'`**: 将请求代理到后端服务器
- **`changeOrigin: true`**: 修改请求头中的 origin 字段
- **`secure: false`**: 允许代理到 http（非 https）服务器

## 🔧 工作原理

### 修复前的请求流程

```
浏览器
  ↓
  请求: GET http://localhost:5174/api/v1/audit-rules/test/single
  ↓
前端服务器 (Vite Dev Server, 端口 5174)
  ↓
  ❌ 404 Not Found (前端服务器没有这个路由)
```

### 修复后的请求流程

```
浏览器
  ↓
  请求: GET http://localhost:5174/api/v1/audit-rules/test/single
  ↓
前端服务器 (Vite Dev Server, 端口 5174)
  ↓
  检测到 /api 前缀，触发代理
  ↓
  代理请求: GET http://localhost:8000/api/v1/audit-rules/test/single
  ↓
后端服务器 (FastAPI, 端口 8000)
  ↓
  ✅ 200 OK (返回测试结果)
```

## 📊 修改清单

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `packages/frontend/vite.config.ts` | 添加 API 代理配置 | ✅ 已完成 |
| `AUDIT_RULE_TEST_404_FIX.md` | 修复文档 | ✅ 已完成 |

## 🎯 验证步骤

### 重启前端服务（重要！）

**Vite 配置修改后需要重启前端服务才能生效**

1. **停止当前前端服务**
   - 在运行前端的终端按 `Ctrl+C`

2. **重新启动前端服务**
   ```bash
   cd /var/www/packages/frontend
   npm run dev
   ```

3. **等待服务启动**
   ```
   VITE v5.x.x  ready in xxx ms

   ➜  Local:   http://localhost:5174/
   ➜  Network: http://0.0.0.0:5174/
   ```

### 测试审核规则测试功能

1. **清除浏览器缓存**（可选但推荐）

2. **访问审核规则配置页面**
   ```
   http://localhost:5174/audit/rule-config
   ```

3. **选择一个规则并点击"测试"**
   - 找到任意一条审核规则
   - 点击"测试"按钮
   - 在测试对话框中填写测试数据
   - 点击"运行测试"

4. **预期结果**
   - ✅ 请求成功发送到后端
   - ✅ 返回测试结果
   - ✅ 没有404错误
   - ✅ 控制台显示测试结果

### 检查网络请求

打开浏览器开发者工具（F12）→ Network 标签页：

**修复前**:
```
Request URL: http://localhost:5174/api/v1/audit-rules/test/single
Status: 404 Not Found
```

**修复后**:
```
Request URL: http://localhost:5174/api/v1/audit-rules/test/single
Status: 200 OK
(实际请求被代理到 http://localhost:8000/api/v1/audit-rules/test/single)
```

## 🔍 其他可能受影响的功能

这个代理配置修复会影响所有前端发送到 `/api` 的请求，包括但不限于：

- ✅ 审核规则测试
- ✅ 审核工作流管理
- ✅ 审核记录查询
- ✅ 合同管理
- ✅ 客户管理
- ✅ 线索管理
- ✅ 所有其他 API 请求

**注意**: 如果之前有其他 API 请求也出现404错误，这个修复应该也能解决那些问题。

## 📝 相关技术文档

### Vite 代理配置

Vite 使用 [http-proxy](https://github.com/http-party/node-http-proxy) 作为代理中间件。

**常用配置选项**:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',  // 目标服务器
    changeOrigin: true,                // 修改 origin 头
    secure: false,                     // 允许 http
    rewrite: (path) => path.replace(/^\/api/, '')  // 重写路径（可选）
  }
}
```

**多个代理规则**:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  },
  '/ws': {
    target: 'ws://localhost:8000',
    ws: true  // WebSocket 代理
  }
}
```

### 为什么需要代理？

在开发环境中：
- 前端运行在 `localhost:5174`
- 后端运行在 `localhost:8000`
- 浏览器的同源策略（CORS）会阻止跨域请求
- 使用代理可以绕过 CORS 限制

在生产环境中：
- 前端和后端通常部署在同一域名下
- 或者后端配置了 CORS 允许跨域
- 不需要前端代理

## ✅ 完成标准

- [x] 代理配置已添加
- [x] 文档已更新
- [ ] 前端服务已重启 ⏳
- [ ] 用户验证通过 ⏳

## 🎉 下一步

**请您现在执行以下步骤**:

1. **重启前端服务**（必须！）
   ```bash
   # 在前端服务运行的终端按 Ctrl+C 停止
   # 然后重新运行
   cd /var/www/packages/frontend
   npm run dev
   ```

2. **等待服务启动完成**

3. **测试审核规则测试功能**
   - 访问 http://localhost:5174/audit/rule-config
   - 点击任意规则的"测试"按钮
   - 填写测试数据并运行测试

4. **验证是否成功**
   - 检查是否返回测试结果
   - 检查控制台是否还有404错误

**如果还有问题**:
- 检查前端服务是否已重启
- 检查后端服务是否正常运行
- 查看浏览器控制台的完整错误信息
- 查看 Network 标签页的请求详情

---

**修复时间**: 2025-10-14  
**修复人员**: AI Assistant  
**测试状态**: ✅ 代码修复完成，待重启前端服务和用户验证  
**优先级**: 🔴 高（核心功能无法使用）  
**影响范围**: 所有前端 API 请求

