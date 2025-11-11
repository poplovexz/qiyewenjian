# 登录指南

## 问题修复说明

已修复以下问题：

1. **端口配置错误**：
   - 修改 `packages/mobile/vite.config.ts` 中的端口从 5175 改为 5174
   - 修改 `packages/mobile/.env.development` 中的端口从 5175 改为 5174
   - 修改 `packages/mobile/package.json` 中的 dev 脚本端口从 5175 改为 5174

2. **登录响应数据结构错误**：
   - 后端返回的数据结构是 `{ message, user, token: { access_token, ... } }`
   - 前端之前错误地使用 `res.access_token`，已修改为 `res.token.access_token`
   - 直接使用后端返回的用户信息，不再额外调用 `/users/me` 接口

3. **DOM警告修复**：
   - 为用户名输入框添加 `autocomplete="username"` 属性
   - 为密码输入框添加 `autocomplete="current-password"` 属性

## 登录信息

### 测试账号

- **用户名**: admin
- **密码**: 123456

### 其他可用账号

- caiwu001 (财务张三)
- yewu001 (业务李四)
- salesperson1 (张业务)
- finance1 (李财务)

注意：所有账号的密码都需要在数据库中查询确认。

## 访问地址

- **Mobile端**: http://localhost:5174
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 启动服务

### 启动后端
```bash
cd packages/backend/src
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 启动Mobile前端
```bash
cd packages/mobile
npm run dev
```

## 验证登录

1. 打开浏览器访问 http://localhost:5174
2. 输入用户名: admin
3. 输入密码: 123456
4. 点击登录按钮
5. 登录成功后会跳转到首页

## API测试

使用curl测试登录接口：

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"yonghu_ming":"admin","mima":"123456"}'
```

成功响应示例：
```json
{
  "message": "登录成功",
  "user": {
    "id": "55ee6a3a-ae14-4c52-b5ca-fd4506b97068",
    "yonghu_ming": "admin",
    "youxiang": "admin@example.com",
    "xingming": "系统管理员",
    "shouji": "13800138000",
    "zhuangtai": "active",
    "zuihou_denglu": "2025-11-06T14:14:28.367484",
    "denglu_cishu": "133",
    "roles": ["admin"],
    "permissions": []
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 2592000
  }
}
```

