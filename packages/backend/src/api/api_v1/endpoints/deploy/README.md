# 部署管理系统

## 概述

这是一个基于Web界面的轻量级部署管理系统，集成在现有的CRM系统中。通过Web界面可以一键触发部署、查看部署历史、实时查看部署日志，并支持版本回滚功能。

## 功能特性

### 1. 一键部署
- 通过Web界面触发部署
- 支持选择部署环境（生产/预发布/开发）
- 支持指定Git分支
- 可选跳过构建或数据库迁移步骤
- 实时显示部署进度

### 2. 部署历史
- 查看所有历史部署记录
- 按环境和状态筛选
- 显示部署人、时间、耗时等信息
- 支持分页查询

### 3. 实时日志
- 实时查看部署日志输出
- 自动滚动到最新日志
- 支持手动刷新

### 4. 版本回滚
- 一键回滚到历史成功版本
- 自动记录回滚操作

### 5. 部署控制
- 取消正在运行的部署
- 查看部署详情

## 技术架构

### 后端

**目录结构**:
```
packages/backend/src/
├── api/api_v1/endpoints/deploy/
│   ├── __init__.py
│   └── deploy.py              # 部署管理API endpoints
├── services/deploy/
│   ├── __init__.py
│   └── deploy_service.py      # 部署服务逻辑
├── schemas/deploy/
│   ├── __init__.py
│   └── deploy_schemas.py      # 部署相关schemas
├── models/deploy/
│   ├── __init__.py
│   └── deploy_history.py      # 部署历史数据模型
└── scripts/
    └── create_deploy_history_table.py  # 数据库表创建脚本
```

**API端点**:
- `POST /api/v1/deploy/trigger` - 触发部署
- `GET /api/v1/deploy/status/{deploy_id}` - 获取部署状态
- `GET /api/v1/deploy/logs/{deploy_id}` - 获取部署日志
- `GET /api/v1/deploy/history` - 获取部署历史列表
- `GET /api/v1/deploy/history/{deploy_id}` - 获取部署详情
- `POST /api/v1/deploy/cancel/{deploy_id}` - 取消部署
- `POST /api/v1/deploy/rollback` - 回滚到指定版本

**数据库表**:
```sql
CREATE TABLE deploy_history (
    id SERIAL PRIMARY KEY,
    environment VARCHAR(50) NOT NULL DEFAULT 'production',
    branch VARCHAR(100) NOT NULL DEFAULT 'main',
    commit_hash VARCHAR(40),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    deployed_by VARCHAR(100) NOT NULL,
    description TEXT,
    logs TEXT,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted VARCHAR(1) NOT NULL DEFAULT 'N'
);
```

### 前端

**目录结构**:
```
packages/frontend/src/
├── api/modules/
│   └── deploy.ts              # 部署API客户端
└── views/settings/deploy/
    └── DeployManagement.vue   # 部署管理主页面
```

**路由配置**:
- `/settings/deploy` - 部署管理页面

## 使用指南

### 访问部署管理

1. 登录系统
2. 进入"设置" → "部署管理"
3. 只有管理员可以访问此功能

### 触发部署

1. 点击"一键部署"按钮
2. 选择部署环境（默认：生产环境）
3. 输入Git分支（默认：main）
4. 可选填写部署说明
5. 可选勾选"跳过构建步骤"或"跳过数据库迁移"
6. 点击"开始部署"

### 查看部署进度

- 部署启动后，页面顶部会显示当前部署状态
- 进度条实时更新
- 可以点击"查看日志"查看详细输出
- 可以点击"取消部署"中止正在运行的部署

### 查看部署历史

- 部署历史表格显示所有历史记录
- 可以按环境和状态筛选
- 点击"查看日志"查看历史部署的完整日志
- 对于成功的部署，可以点击"回滚"恢复到该版本

### 版本回滚

1. 在部署历史中找到要回滚的版本
2. 点击"回滚"按钮
3. 输入回滚说明（可选）
4. 确认回滚
5. 系统会自动创建一个新的部署任务

## 部署脚本

系统使用以下部署脚本：

- **生产环境**: `/var/www/quick-deploy.sh`
- **预发布环境**: `/var/www/deploy-to-staging.sh`
- **开发环境**: `/var/www/deploy-to-development.sh`

部署脚本的主要步骤：
1. 构建前端（npm run build）
2. 打包代码
3. 上传到目标服务器
4. 解压并覆盖文件
5. 运行数据库迁移
6. 重启服务
7. 健康检查

## 安全性

- 所有部署操作需要管理员权限
- 部署操作会记录操作人和时间
- 支持审计追踪
- 部署日志完整保存

## 监控和告警

- 部署状态实时更新（每3秒轮询）
- 部署成功/失败会显示通知
- 部署日志实时显示
- 支持查看错误信息

## 故障排查

### 部署失败

1. 查看部署日志，找到错误信息
2. 检查部署脚本是否正确
3. 检查目标服务器连接
4. 检查权限配置

### 日志查看

- 后端日志: `tail -f /tmp/backend_8000.log`
- 部署脚本日志: 在部署日志中查看

### 常见问题

**Q: 部署一直处于运行中状态？**
A: 检查部署脚本是否卡住，可以取消部署后重试。

**Q: 无法连接到目标服务器？**
A: 检查SSH配置和网络连接。

**Q: 回滚失败？**
A: 确保目标版本的代码仍然可用，检查Git提交是否存在。

## 未来改进

- [ ] 支持WebSocket实时推送日志（当前使用轮询）
- [ ] 支持多环境配置管理
- [ ] 支持蓝绿部署
- [ ] 支持灰度发布
- [ ] 集成自动化测试
- [ ] 支持部署通知（邮件/钉钉/企业微信）
- [ ] 支持部署审批流程
- [ ] 支持定时部署
- [ ] 支持Git webhook自动部署

## 维护

### 数据库维护

定期清理旧的部署记录：
```sql
-- 删除3个月前的部署记录
UPDATE deploy_history 
SET is_deleted = 'Y' 
WHERE created_at < NOW() - INTERVAL '3 months';
```

### 日志清理

部署日志存储在数据库中，建议定期清理：
```sql
-- 清理旧部署的日志内容
UPDATE deploy_history 
SET logs = NULL 
WHERE created_at < NOW() - INTERVAL '1 month' 
AND status IN ('success', 'failed', 'cancelled');
```

## 贡献

如需改进或添加新功能，请遵循以下步骤：

1. 在`packages/backend/src/services/deploy/`中添加服务逻辑
2. 在`packages/backend/src/api/api_v1/endpoints/deploy/`中添加API端点
3. 在`packages/frontend/src/api/modules/deploy.ts`中添加API客户端方法
4. 在`packages/frontend/src/views/settings/deploy/`中更新UI组件
5. 更新本文档

## 许可

内部系统，仅供公司内部使用。

