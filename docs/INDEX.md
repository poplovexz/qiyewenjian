# 文档索引

本文档提供系统所有文档的快速导航。

## 📚 文档分类

### 🚀 快速开始

| 文档 | 说明 |
|------|------|
| [README.md](../README.md) | 项目主文档，包含技术栈、快速开始、功能概览 |
| [快速启动指南.md](../快速启动指南.md) | 中文快速启动指南 |
| [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md) | 英文快速启动指南 |
| [一键启动脚本说明.md](../一键启动脚本说明.md) | 一键启动脚本详细说明 |

---

### 📖 功能使用指南

#### 审核工作流
| 文档 | 说明 |
|------|------|
| [审核规则设置指南.md](../审核规则设置指南.md) | 审核规则配置详解 |
| [AUDIT_WORKFLOW_QUICK_START.md](../AUDIT_WORKFLOW_QUICK_START.md) | 审核工作流快速开始 |

#### 银行汇款
| 文档 | 说明 |
|------|------|
| [BANK_PAYMENT_SETUP_GUIDE.md](../BANK_PAYMENT_SETUP_GUIDE.md) | 银行汇款功能设置 |
| [BANK_PAYMENT_AUDIT_SETUP_GUIDE.md](../BANK_PAYMENT_AUDIT_SETUP_GUIDE.md) | 银行汇款审核设置 |
| [BANK_TRANSFER_AUDIT_CONFIGURATION_GUIDE.md](../BANK_TRANSFER_AUDIT_CONFIGURATION_GUIDE.md) | 银行转账审核配置 |

#### 合同管理
| 文档 | 说明 |
|------|------|
| [合同模板管理使用指南.md](../合同模板管理使用指南.md) | 合同模板使用详解 |

#### 权限管理
| 文档 | 说明 |
|------|------|
| [USER_PERMISSION_MANAGEMENT_GUIDE.md](../USER_PERMISSION_MANAGEMENT_GUIDE.md) | 用户权限管理指南 |

#### 客户管理
| 文档 | 说明 |
|------|------|
| [客户管理访问指南.md](../客户管理访问指南.md) | 客户管理功能使用 |

#### 代理记账
| 文档 | 说明 |
|------|------|
| [DAILI_JIZHANG_LIMIT_QUICK_GUIDE.md](../DAILI_JIZHANG_LIMIT_QUICK_GUIDE.md) | 代理记账服务限制指南 |

#### 线索管理
| 文档 | 说明 |
|------|------|
| [XIANSUO_AUTO_STATUS_FLOW.md](../XIANSUO_AUTO_STATUS_FLOW.md) | 线索状态自动流转说明 |

---

### 🛠 技术文档

| 文档 | 说明 |
|------|------|
| [FEATURES.md](./FEATURES.md) | 功能实现详细文档（整合） |
| [BUGFIXES.md](./BUGFIXES.md) | Bug修复记录（整合） |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | 部署完整指南（整合） |
| [test-config.md](../test-config.md) | 测试配置说明 |
| [BACKEND_SCRIPTS_README.md](../BACKEND_SCRIPTS_README.md) | 后端脚本使用说明 |

---

### 🔐 认证与安全

| 文档 | 说明 |
|------|------|
| [AUTHENTICATION_BEST_PRACTICES.md](./AUTHENTICATION_BEST_PRACTICES.md) | 认证最佳实践 |
| [AUTHENTICATION_ISSUE_RESOLUTION.md](./AUTHENTICATION_ISSUE_RESOLUTION.md) | 认证问题解决方案 |

---

### 🐛 问题修复

| 文档 | 说明 |
|------|------|
| [DEADLOCK_FIX.md](./DEADLOCK_FIX.md) | 死锁问题修复 |
| [DIALOG_CLOSE_FIX.md](./DIALOG_CLOSE_FIX.md) | 对话框关闭问题修复 |

---

### 🤖 开发者工具

| 文档 | 说明 |
|------|------|
| [AGENTS.md](../AGENTS.md) | AI助手开发规则 |

---

## 📂 文档结构

```
/var/www/
├── README.md                                    # 项目主文档 ⭐
├── 快速启动指南.md                              # 中文快速指南
├── QUICK_START_GUIDE.md                        # 英文快速指南
├── 一键启动脚本说明.md                          # 启动脚本说明
│
├── 审核规则设置指南.md                          # 审核规则配置
├── AUDIT_WORKFLOW_QUICK_START.md               # 审核快速开始
│
├── BANK_PAYMENT_SETUP_GUIDE.md                 # 银行汇款设置
├── BANK_PAYMENT_AUDIT_SETUP_GUIDE.md           # 银行汇款审核
├── BANK_TRANSFER_AUDIT_CONFIGURATION_GUIDE.md  # 银行转账审核
│
├── 合同模板管理使用指南.md                      # 合同模板使用
├── USER_PERMISSION_MANAGEMENT_GUIDE.md         # 权限管理
├── 客户管理访问指南.md                          # 客户管理
├── DAILI_JIZHANG_LIMIT_QUICK_GUIDE.md          # 代理记账限制
├── XIANSUO_AUTO_STATUS_FLOW.md                 # 线索状态流转
│
├── test-config.md                              # 测试配置
├── BACKEND_SCRIPTS_README.md                   # 后端脚本
├── AGENTS.md                                   # AI助手规则
│
└── docs/                                       # 技术文档目录
    ├── INDEX.md                                # 本文档索引 ⭐
    ├── FEATURES.md                             # 功能实现文档 ⭐
    ├── BUGFIXES.md                             # Bug修复记录 ⭐
    ├── DEPLOYMENT.md                           # 部署指南 ⭐
    ├── AUTHENTICATION_BEST_PRACTICES.md        # 认证最佳实践
    ├── AUTHENTICATION_ISSUE_RESOLUTION.md      # 认证问题解决
    ├── DEADLOCK_FIX.md                         # 死锁修复
    └── DIALOG_CLOSE_FIX.md                     # 对话框修复
```

---

## 🎯 快速查找

### 我想...

#### 快速启动系统
→ [快速启动指南.md](../快速启动指南.md) 或 [一键启动脚本说明.md](../一键启动脚本说明.md)

#### 配置审核流程
→ [审核规则设置指南.md](../审核规则设置指南.md)

#### 设置银行汇款
→ [BANK_PAYMENT_SETUP_GUIDE.md](../BANK_PAYMENT_SETUP_GUIDE.md)

#### 管理合同模板
→ [合同模板管理使用指南.md](../合同模板管理使用指南.md)

#### 配置用户权限
→ [USER_PERMISSION_MANAGEMENT_GUIDE.md](../USER_PERMISSION_MANAGEMENT_GUIDE.md)

#### 部署到生产环境
→ [docs/DEPLOYMENT.md](./DEPLOYMENT.md)

#### 查看功能实现细节
→ [docs/FEATURES.md](./FEATURES.md)

#### 解决Bug或问题
→ [docs/BUGFIXES.md](./BUGFIXES.md)

#### 运行测试
→ [test-config.md](../test-config.md)

#### 使用后端脚本
→ [BACKEND_SCRIPTS_README.md](../BACKEND_SCRIPTS_README.md)

---

## 📝 文档更新记录

### 2024-10-31
- ✅ 整合了130+个分散文档
- ✅ 创建了3个核心技术文档（FEATURES.md, BUGFIXES.md, DEPLOYMENT.md）
- ✅ 删除了过期和重复的文档
- ✅ 更新了主README文档
- ✅ 创建了文档索引（本文档）
- ✅ 保留了17个有用的使用指南

### 文档整理原则
1. **整合优先**：将相关内容整合到统一文档
2. **保留有用**：保留实用的使用指南和配置说明
3. **删除过期**：删除已过时或重复的文档
4. **清晰导航**：提供清晰的文档索引和导航

---

## 💡 文档使用建议

1. **新用户**：从 [README.md](../README.md) 和 [快速启动指南.md](../快速启动指南.md) 开始
2. **开发者**：查看 [docs/FEATURES.md](./FEATURES.md) 了解功能实现
3. **运维人员**：参考 [docs/DEPLOYMENT.md](./DEPLOYMENT.md) 进行部署
4. **遇到问题**：先查看 [docs/BUGFIXES.md](./BUGFIXES.md) 寻找解决方案
5. **功能配置**：查看对应的使用指南文档

---

## 🔄 文档维护

### 添加新文档
1. 确定文档类型（使用指南/技术文档/修复记录）
2. 放置在合适的位置（根目录/docs目录）
3. 更新本索引文档
4. 在README.md中添加链接（如需要）

### 更新现有文档
1. 直接编辑对应文档
2. 更新文档更新记录
3. 如有重大变更，通知相关人员

### 删除文档
1. 确认文档已过期或内容已整合
2. 从本索引中移除
3. 从README.md中移除链接
4. 删除文件

---

**最后更新**: 2024-10-31

