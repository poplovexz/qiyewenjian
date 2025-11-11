# 审核规则测试代理配置修复 - 最终版本

## 🎯 问题总结

审核规则测试功能返回404错误的根本原因是**前端缺少API代理配置**。

## ✅ 最终修复方案

**文件**: `packages/frontend/vite.config.ts`

### 完整的代理配置

```typescript
server: {
  port: 5174,
  host: true,  // 改为 true 以支持所有网络接口
  strictPort: true,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',  // 使用 127.0.0.1 而不是 localhost
      changeOrigin: true,
      secure: false,
      ws: true,  // 支持 WebSocket
      configure: (proxy, _options) => {
        // 添加调试日志
        proxy.on('error', (err, _req, _res) => {
          console.log('proxy error', err);
        });
        proxy.on('proxyReq', (proxyReq, req, _res) => {
          console.log('Sending Request to the Target:', req.method, req.url);
        });
        proxy.on('proxyRes', (proxyRes, req, _res) => {
          console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
        });
      },
    }
  }
},
```

### 关键修改点

1. **`host: true`** - 改为 `true` 而不是 `'0.0.0.0'`，以支持所有网络接口
2. **`target: 'http://127.0.0.1:8000'`** - 使用 `127.0.0.1` 而不是 `localhost`，避免DNS解析问题
3. **`ws: true`** - 支持 WebSocket 连接
4. **`configure`** - 添加调试日志，方便排查问题

## 🧪 验证结果

### 代理工作正常

```bash
$ curl -s -X POST "http://localhost:5174/api/v1/audit-rules/test/single" \
  -H "Content-Type: application/json" \
  -d '{"rule_id": "test", "test_data": {}}'

{"detail":"Not authenticated"}
```

**说明**:
- ✅ 返回 "Not authenticated" 而不是404
- ✅ 说明请求已成功通过代理到达后端
- ✅ 代理配置正常工作

### 前端日志确认

```
Sending Request to the Target: POST /api/v1/audit-rules/test/single
Received Response from the Target: 401 /api/v1/audit-rules/test/single
```

**说明**:
- ✅ 代理正在转发请求
- ✅ 后端返回401（未认证）而不是404
- ✅ 端点存在且可访问

## 📊 修改清单

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `packages/frontend/vite.config.ts` | 添加并优化 API 代理配置 | ✅ 已完成 |
| `AUDIT_RULE_TEST_404_FIX.md` | 初始修复文档 | ✅ 已完成 |
| `AUDIT_RULE_TEST_PROXY_FIX_FINAL.md` | 最终修复文档 | ✅ 已完成 |

## 🎯 当前状态

- ✅ **代理配置已添加并优化**
- ✅ **前端服务已重启**
- ✅ **代理工作正常**（通过日志和测试确认）
- ⏳ **待用户测试**（需要登录后测试）

## 🔍 下一步：用户测试

### 测试步骤

1. **确保已登录系统**
   - 访问 http://localhost:5174
   - 使用有效的用户名和密码登录

2. **访问审核规则配置页面**
   ```
   http://localhost:5174/audit/rule-config
   ```

3. **选择一个规则并点击"测试"**
   - 找到任意一条审核规则
   - 点击"测试"按钮

4. **填写测试数据**
   - 在测试对话框中填写必要的测试数据
   - 点击"运行测试"按钮

5. **预期结果**
   - ✅ 没有404错误
   - ✅ 如果未登录，显示"未认证"错误
   - ✅ 如果已登录，返回测试结果

### 检查代理日志

打开浏览器开发者工具（F12）→ Console 标签页，应该看到：

```
Sending Request to the Target: POST /api/v1/audit-rules/test/single
Received Response from the Target: 200 /api/v1/audit-rules/test/single
```

## 🔧 故障排除

### 如果仍然出现404错误

1. **检查前端服务是否已重启**
   ```bash
   ps aux | grep vite
   ```

2. **检查代理配置是否正确**
   ```bash
   cat /var/www/packages/frontend/vite.config.ts | grep -A 20 "proxy"
   ```

3. **检查后端服务是否正常**
   ```bash
   curl http://localhost:8000/health
   ```

4. **查看前端日志**
   ```bash
   tail -f /tmp/frontend_final.log
   ```

### 如果出现认证错误

1. **确保已登录**
   - 检查 localStorage 中是否有 token
   - 在浏览器控制台运行: `localStorage.getItem('token')`

2. **检查 token 是否有效**
   - Token 可能已过期
   - 尝试重新登录

3. **检查请求头**
   - 打开 Network 标签页
   - 查看请求的 Authorization 头是否正确

## 📝 技术说明

### 为什么使用 127.0.0.1 而不是 localhost？

- `localhost` 需要 DNS 解析，可能解析到 IPv6 地址 `::1`
- `127.0.0.1` 直接使用 IPv4 地址，避免解析问题
- 在某些环境中，IPv6 可能导致连接问题

### 为什么 host 设置为 true？

- `host: true` 等同于 `host: '0.0.0.0'`，但更简洁
- 允许从任何网络接口访问开发服务器
- 支持通过 IP 地址访问（如 `http://172.22.61.135:5174`）

### configure 函数的作用

- 提供对底层 http-proxy 实例的访问
- 可以添加事件监听器进行调试
- 可以修改代理请求和响应

## ✅ 完成标准

- [x] 代理配置已添加
- [x] 代理配置已优化
- [x] 前端服务已重启
- [x] 代理工作正常（已验证）
- [ ] 用户登录后测试通过 ⏳

## 🎉 总结

**问题**: 前端缺少 API 代理配置，导致所有 API 请求返回404

**解决方案**: 
1. 在 `vite.config.ts` 中添加代理配置
2. 使用 `127.0.0.1` 而不是 `localhost`
3. 添加调试日志方便排查问题
4. 重启前端服务应用配置

**当前状态**: 
- ✅ 代理配置正常工作
- ✅ 请求可以到达后端
- ⏳ 需要用户登录后测试完整功能

---

**修复时间**: 2025-10-14  
**修复人员**: AI Assistant  
**测试状态**: ✅ 代理工作正常，待用户登录后完整测试  
**优先级**: 🔴 高（核心功能）  
**影响范围**: 所有前端 API 请求

