# 银行转账支付审批流程 - 快速开始指南

## ✅ 当前状态检查

### 数据库状态
- ✅ 合同支付表已创建
- ✅ 银行汇款单据表已创建
- ✅ 审批流程步骤表已创建

### 用户状态
- ✅ 测试用户已创建：
  - salesperson1 (张业务) - 密码: 123456
  - finance1 (李财务) - 密码: 123456

### 需要配置
- ⏳ 创建2个角色
- ⏳ 分配角色给用户
- ⏳ 配置审批流程

---

## 🚀 3步快速配置（预计10分钟）

### 第1步：创建角色（3分钟）

**访问**：http://localhost:5174/roles

**操作**：点击"新建角色"按钮，创建以下两个角色

#### 角色1：业务员
```
角色名称：业务员
角色编码：salesperson
角色描述：负责客户对接和汇款单据上传
状态：启用
```

#### 角色2：财务
```
角色名称：财务
角色编码：finance
角色描述：负责审核汇款单据和确认到账
状态：启用
```

---

### 第2步：分配角色（2分钟）

**访问**：http://localhost:5174/users

**操作**：为每个用户分配对应的角色

#### 用户1：张业务 (salesperson1)
1. 在用户列表中找到"张业务"
2. 点击"编辑"或"分配角色"
3. 选择角色：**业务员**
4. 保存

#### 用户2：李财务 (finance1)
1. 在用户列表中找到"李财务"
2. 点击"编辑"或"分配角色"
3. 选择角色：**财务**
4. 保存

---

### 第3步：配置审批流程（5分钟）

**访问**：http://localhost:5174/audit/workflow-config

**操作**：创建审批流程和步骤

#### 3.1 创建流程
点击"新建流程"，填写以下信息：

```
流程名称：银行转账支付审批
流程编码：bank_payment_approval
流程描述：客户选择银行转账后，业务员上传汇款单据，财务审核确认
适用范围：payment
流程状态：启用
```

#### 3.2 添加步骤1
在流程详情页，点击"添加步骤"：

```
步骤名称：业务员上传汇款单据
步骤顺序：1
审核角色：业务员
步骤类型：upload
步骤状态：启用
```

#### 3.3 添加步骤2
继续点击"添加步骤"：

```
步骤名称：财务审核确认
步骤顺序：2
审核角色：财务
步骤类型：approval
步骤状态：启用
```

---

## ✅ 配置验证

配置完成后，请验证以下内容：

### 验证角色
访问：http://localhost:5174/roles

应该看到：
- [ ] 业务员 (salesperson)
- [ ] 财务 (finance)

### 验证用户角色
访问：http://localhost:5174/users

应该看到：
- [ ] 张业务 - 角色：业务员
- [ ] 李财务 - 角色：财务

### 验证审批流程
访问：http://localhost:5174/audit/workflow-config

应该看到：
- [ ] 银行转账支付审批 (bank_payment_approval)
  - [ ] 步骤1：业务员上传汇款单据
  - [ ] 步骤2：财务审核确认

---

## 🧪 测试流程（预计5分钟）

### 准备工作
1. 获取一个合同的签署链接
2. 准备一张汇款凭证图片（可以用任意图片代替）

### 测试步骤

#### 1. 客户提交（2分钟）
1. 打开签署链接：http://localhost:5174/contract-sign/{token}
2. 完成前面的步骤（查看合同、签名）
3. 在支付步骤选择：**银行转账**
4. 查看银行账户信息
5. 上传汇款凭证
6. 填写汇款信息并提交

#### 2. 业务员审核（1分钟）
1. 登录：salesperson1 / 123456
2. 进入待审核页面
3. 查看汇款凭证
4. 确认并提交给财务

#### 3. 财务审核（2分钟）
1. 登录：finance1 / 123456
2. 进入待审核页面
3. 查看汇款凭证
4. 审核通过
5. 查看合同支付状态是否更新为"已支付"

---

## 📊 数据库验证命令

如果需要通过数据库验证配置是否正确：

### 检查角色
```bash
psql postgresql://postgres:password@localhost:5432/proxy_db -c "
SELECT jiaose_ming, jiaose_bianma, zhuangtai 
FROM jiaose 
WHERE is_deleted = 'N' 
ORDER BY jiaose_bianma;
"
```

预期输出：
```
 jiaose_ming | jiaose_bianma | zhuangtai 
-------------+---------------+-----------
 财务        | finance       | active
 业务员      | salesperson   | active
```

### 检查用户角色
```bash
psql postgresql://postgres:password@localhost:5432/proxy_db -c "
SELECT y.xingming, y.yonghu_ming, j.jiaose_ming
FROM yonghu y
JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id
JOIN jiaose j ON yj.jiaose_id = j.id
WHERE y.is_deleted = 'N' AND yj.is_deleted = 'N' AND j.is_deleted = 'N'
  AND y.yonghu_ming IN ('salesperson1', 'finance1')
ORDER BY y.yonghu_ming;
"
```

预期输出：
```
 xingming | yonghu_ming  | jiaose_ming 
----------+--------------+-------------
 李财务   | finance1     | 财务
 张业务   | salesperson1 | 业务员
```

---

## 🎯 完成后的下一步

配置完成并测试通过后，可以进行：

1. **前端开发**
   - 修改客户签署页面，添加银行转账UI
   - 创建业务员审核页面
   - 创建财务审核页面

2. **后端开发**
   - 实现银行转账提交API
   - 实现审核流程API
   - 实现支付状态更新逻辑

3. **集成测试**
   - 完整流程端到端测试
   - 异常情况测试
   - 性能测试

---

## 📞 常见问题

### Q1: 找不到角色管理页面？
A: 访问 http://localhost:5174/roles

### Q2: 找不到用户管理页面？
A: 访问 http://localhost:5174/users

### Q3: 找不到审批流程配置页面？
A: 访问 http://localhost:5174/audit/workflow-config

### Q4: 用户已存在但没有角色？
A: 在用户管理页面编辑用户，分配对应的角色

### Q5: 如何重置测试数据？
A: 运行清理脚本：
```bash
psql postgresql://postgres:password@localhost:5432/proxy_db < cleanup_duplicates.sql
```

---

## 📝 配置检查清单

完成配置后，请勾选以下项目：

**角色配置**
- [ ] 角色"业务员"已创建（编码：salesperson）
- [ ] 角色"财务"已创建（编码：finance）

**用户配置**
- [ ] 用户 salesperson1 已分配"业务员"角色
- [ ] 用户 finance1 已分配"财务"角色

**流程配置**
- [ ] 审批流程"银行转账支付审批"已创建
- [ ] 流程编码为：bank_payment_approval
- [ ] 流程状态为：启用
- [ ] 步骤1：业务员上传汇款单据（顺序1，角色：业务员）
- [ ] 步骤2：财务审核确认（顺序2，角色：财务）

**测试验证**
- [ ] 可以用 salesperson1 登录
- [ ] 可以用 finance1 登录
- [ ] 审批流程在配置页面可见
- [ ] 流程步骤显示正确

---

**预计总时间**：15分钟（配置10分钟 + 测试5分钟）

现在开始配置吧！🚀

