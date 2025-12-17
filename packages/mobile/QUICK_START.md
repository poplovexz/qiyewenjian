# 快速启动指南

## 📦 安装依赖

```bash
cd packages/mobile
pnpm install
```

## 🚀 启动开发服务器

```bash
pnpm dev
```

应用将在 **http://localhost:5175** 启动

## ✅ 前置条件

确保以下服务正在运行：

1. **后端服务** - http://localhost:8000
2. **数据库服务** - PostgreSQL

## 🔑 测试账号

使用系统中已有的用户账号登录，例如：
- 用户名：`admin`
- 密码：`admin123`

## 📱 测试步骤

### 1. 登录
1. 打开浏览器访问 http://localhost:5175
2. 输入用户名和密码
3. 点击"登录"按钮

### 2. 查看首页
- 查看任务统计
- 点击快捷入口

### 3. 查看任务列表
1. 点击底部导航"任务"或首页的"我的任务"
2. 查看任务列表
3. 切换不同的状态标签（全部/待处理/进行中/已完成）
4. 下拉刷新列表
5. 上拉加载更多

### 4. 管理任务
1. 点击任务卡片进入详情
2. 如果任务状态是"待处理"，点击"开始任务"
3. 如果任务状态是"进行中"，可以：
   - 点击"完成任务"，填写实际工时
   - 点击"暂停任务"

### 5. 查看个人中心
1. 点击底部导航"我的"
2. 查看个人信息和统计
3. 点击"退出登录"

## 🛠️ 开发工具

### Chrome DevTools
1. 打开Chrome浏览器
2. 按F12打开开发者工具
3. 点击"Toggle device toolbar"（Ctrl+Shift+M）
4. 选择移动设备模拟器（推荐：iPhone 6/7/8 或 iPhone X）

### Vue DevTools
安装Vue DevTools浏览器扩展，可以查看：
- 组件树
- Pinia状态
- 路由信息

## 📝 常见问题

### Q: 登录后提示401错误
A: 检查后端服务是否正常运行，Token是否正确

### Q: 任务列表为空
A: 确保数据库中有分配给当前用户的任务项

### Q: 页面样式异常
A: 清除浏览器缓存，重新加载页面

### Q: API请求失败
A: 检查Vite代理配置，确保后端服务运行在8000端口

## 🔧 调试技巧

### 查看API请求
1. 打开Chrome DevTools
2. 切换到Network标签
3. 筛选XHR请求
4. 查看请求和响应

### 查看Pinia状态
1. 安装Vue DevTools
2. 打开DevTools
3. 切换到Pinia标签
4. 查看user store的状态

### 查看Console日志
1. 打开Chrome DevTools
2. 切换到Console标签
3. 查看错误和警告信息

## 📚 相关文档

- [README.md](./README.md) - 项目说明
- [MOBILE_APP_COMPLETED.md](../../MOBILE_APP_COMPLETED.md) - 完成报告
- [MOBILE_APP_ANALYSIS_REPORT.md](../../MOBILE_APP_ANALYSIS_REPORT.md) - 需求分析

## 🎯 下一步

1. 测试所有功能
2. 根据实际需求调整UI
3. 添加更多功能（如任务反馈、附件上传等）
4. 优化性能
5. 准备生产环境部署

