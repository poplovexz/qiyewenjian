# 故障排除指南

## 🔧 当前问题：后端服务响应超时

### 问题描述
移动端登录时出现超时错误：
```
AxiosError {message: 'timeout of 15000ms exceeded'}
```

### 根本原因
后端服务的Redis连接阻塞导致请求响应缓慢（超过15秒）。

---

## ✅ 解决方案

### 方案1：重启后端服务（推荐）

1. **停止当前后端服务**
```bash
pkill -f "python.*main.py"
```

2. **重新启动后端服务**
```bash
cd /var/www/packages/backend
python3 main.py
```

3. **等待后端完全启动**（约10-30秒）
   - 看到 "Application startup complete" 表示启动成功

4. **测试后端API**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"yonghu_ming":"admin","mima":"admin123"}'
```

如果返回JSON数据（包含access_token），说明后端正常。

---

### 方案2：检查Redis服务

后端启动慢通常是因为Redis连接问题。

1. **检查Redis是否运行**
```bash
redis-cli ping
```

应该返回 `PONG`

2. **如果Redis未运行，启动Redis**
```bash
sudo service redis-server start
# 或
redis-server
```

3. **重启后端服务**
```bash
cd /var/www/packages/backend
python3 main.py
```

---

### 方案3：增加移动端超时时间（临时方案）

如果后端启动慢但最终能响应，可以增加移动端的超时时间：

编辑 `packages/mobile/src/utils/request.ts`：

```typescript
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || '/api/v1',
  timeout: 60000, // 从15000改为60000（60秒）
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})
```

然后刷新移动端页面。

---

## 📊 验证服务状态

### 检查所有服务是否运行

```bash
# 检查后端（应该显示python3进程）
lsof -i :8000

# 检查前端（应该显示node进程）
lsof -i :5174

# 检查移动端（应该显示node进程）
lsof -i :5175
```

### 测试后端API

```bash
# 测试登录API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"yonghu_ming":"admin","mima":"admin123"}'

# 应该返回类似这样的JSON：
# {"access_token":"eyJ...","token_type":"bearer"}
```

### 测试移动端

1. 打开浏览器访问 http://localhost:5175
2. 打开Chrome DevTools（F12）
3. 切换到Network标签
4. 尝试登录
5. 查看 `/api/v1/auth/login` 请求的状态

---

## 🚀 快速重启所有服务

### 使用提供的脚本

```bash
# 停止所有服务
./stop-all.sh

# 启动所有服务
./start-all.sh
```

### 手动启动

```bash
# 1. 启动后端
cd /var/www/packages/backend
python3 main.py &

# 2. 启动前端
cd /var/www/packages/frontend
pnpm dev &

# 3. 启动移动端
cd /var/www/packages/mobile
pnpm dev &
```

---

## 📝 查看日志

### 后端日志
```bash
# 如果使用脚本启动
tail -f /tmp/backend.log

# 如果手动启动，查看终端输出
```

### 前端日志
```bash
# 如果使用脚本启动
tail -f /tmp/frontend.log

# 如果手动启动，查看终端输出
```

### 移动端日志
查看启动移动端的终端输出

---

## 🔍 常见问题

### Q1: 后端启动很慢（超过30秒）
**A**: 这是Redis连接问题。检查Redis服务是否运行：
```bash
redis-cli ping
```

### Q2: 移动端登录一直超时
**A**: 
1. 确认后端服务正常运行（端口8000）
2. 测试后端API是否响应
3. 检查浏览器控制台的Network标签，查看请求详情

### Q3: 移动端页面空白
**A**: 
1. 检查移动端服务是否运行（端口5175）
2. 打开浏览器控制台查看错误信息
3. 确认Vite配置文件没有错误

### Q4: API请求404错误
**A**: 
1. 确认后端服务运行在8000端口
2. 检查Vite代理配置（`packages/mobile/vite.config.ts`）
3. 确认API路径正确（`/api/v1/...`）

---

## 💡 最佳实践

1. **启动顺序**: 先启动后端，再启动前端和移动端
2. **等待时间**: 后端启动后等待10-30秒再测试
3. **日志监控**: 使用 `tail -f` 实时查看日志
4. **端口检查**: 确保端口8000、5174、5175没有被其他程序占用

---

## 📞 需要帮助？

如果以上方案都无法解决问题，请提供以下信息：

1. 后端日志（`/tmp/backend.log` 或终端输出）
2. 浏览器控制台错误信息
3. Network标签中的请求详情
4. Redis服务状态（`redis-cli ping`）

---

**提示**: 根据记忆，后端main.py中已经有try-catch来处理Redis连接失败，所以即使Redis未运行，后端也应该能启动（只是会有警告）。如果后端启动超过1分钟，可能需要检查数据库连接或其他配置。

