# 银行转账支付审批流程 - 配置指南

## 📋 当前状态

### ✅ 已完成
1. **数据库表已创建**
   - hetong_zhifu (合同支付表)
   - yinhang_huikuan_danju (银行汇款单据表)
   - shenhe_liucheng_buzou (审批流程步骤表)

2. **测试用户已创建**
   - salesperson1 (张业务) - 密码: 123456
   - finance1 (李财务) - 密码: 123456

### ⏳ 需要配置

1. **创建角色**
2. **分配角色给用户**
3. **配置审批流程**

---

## 🎯 配置步骤

### 步骤1：创建角色

**访问页面**：http://localhost:5174/roles

**需要创建的角色**：

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

### 步骤2：分配角色给用户

**访问页面**：http://localhost:5174/users

**需要分配的角色**：

#### 用户1：张业务 (salesperson1)
- 找到用户：张业务 (salesperson1)
- 点击"编辑"或"分配角色"
- 选择角色：**业务员**
- 保存

#### 用户2：李财务 (finance1)
- 找到用户：李财务 (finance1)
- 点击"编辑"或"分配角色"
- 选择角色：**财务**
- 保存

---

### 步骤3：配置审批流程

**访问页面**：http://localhost:5174/audit/workflow-config

**创建审批流程**：

#### 流程基本信息
```
流程名称：银行转账支付审批
流程编码：bank_payment_approval
流程描述：客户选择银行转账后，业务员上传汇款单据，财务审核确认
适用范围：payment
流程状态：启用
```

#### 审批步骤

**步骤1：业务员上传汇款单据**
```
步骤名称：业务员上传汇款单据
步骤顺序：1
审核角色：业务员
步骤类型：upload
步骤状态：启用
```

**步骤2：财务审核确认**
```
步骤名称：财务审核确认
步骤顺序：2
审核角色：财务
步骤类型：approval
步骤状态：启用
```

---

## 🧪 测试流程

### 测试准备

1. **确认角色已创建**
   - 访问 http://localhost:5174/roles
   - 确认看到"业务员"和"财务"两个角色

2. **确认用户已分配角色**
   - 访问 http://localhost:5174/users
   - 确认 salesperson1 有"业务员"角色
   - 确认 finance1 有"财务"角色

3. **确认审批流程已配置**
   - 访问 http://localhost:5174/audit/workflow-config
   - 确认看到"银行转账支付审批"流程
   - 确认流程有2个步骤

### 完整测试流程

#### 1. 客户操作（无需登录）

访问签署链接：http://localhost:5174/contract-sign/{token}

操作步骤：
1. 查看合同内容
2. 填写签名信息并签名
3. 选择支付方式：**银行转账**
4. 查看银行账户信息：
   ```
   收款单位：代理记账服务有限公司
   开户银行：中国工商银行北京分行
   银行账号：1234 5678 9012 3456
   应付金额：¥5000.00
   ```
5. 上传汇款凭证（图片或PDF）
6. 填写汇款信息：
   - 汇款人：张三
   - 汇款日期：2025-10-13
   - 汇款银行：中国工商银行
7. 提交

#### 2. 业务员操作

登录账号：salesperson1 / 123456

操作步骤：
1. 进入"待审核汇款单据"页面
2. 查看客户提交的汇款凭证
3. 确认收到客户的汇款单据
4. 填写备注（可选）
5. 点击"确认并提交给财务"

#### 3. 财务操作

登录账号：finance1 / 123456

操作步骤：
1. 进入"待审核汇款单据"页面
2. 查看汇款凭证和业务员备注
3. 核对汇款金额：¥5000.00
4. 确认银行账户已到账
5. 选择审核结果：
   - **通过**：金额已到账，审核通过
   - **拒绝**：金额不符或其他原因
6. 填写审核意见
7. 提交审核

#### 4. 系统自动处理

审核通过后，系统自动：
1. 更新合同支付状态：pending → paid
2. 更新支付时间
3. 发送通知给相关人员（可选）

---

## 📊 数据库状态检查

### 检查角色
```sql
SELECT jiaose_ming, jiaose_bianma, zhuangtai 
FROM jiaose 
WHERE is_deleted = 'N';
```

预期结果：
```
 jiaose_ming | jiaose_bianma | zhuangtai 
-------------+---------------+-----------
 业务员      | salesperson   | active
 财务        | finance       | active
```

### 检查用户角色分配
```sql
SELECT y.xingming, y.yonghu_ming, j.jiaose_ming
FROM yonghu y
JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id
JOIN jiaose j ON yj.jiaose_id = j.id
WHERE y.is_deleted = 'N' AND yj.is_deleted = 'N'
  AND y.yonghu_ming IN ('salesperson1', 'finance1');
```

预期结果：
```
 xingming | yonghu_ming  | jiaose_ming 
----------+--------------+-------------
 张业务   | salesperson1 | 业务员
 李财务   | finance1     | 财务
```

---

## 🔧 清理重复数据（如果需要）

### 清理重复角色
```sql
-- 查看所有角色
SELECT id, jiaose_ming, jiaose_bianma, created_at 
FROM jiaose 
WHERE is_deleted = 'N' 
ORDER BY created_at;

-- 如果有重复，软删除旧的
UPDATE jiaose 
SET is_deleted = 'Y', updated_at = NOW() 
WHERE id = '旧的角色ID';
```

### 清理重复用户
```sql
-- 查看所有用户
SELECT id, xingming, yonghu_ming, created_at 
FROM yonghu 
WHERE is_deleted = 'N' 
ORDER BY created_at;

-- 如果有重复，软删除旧的
UPDATE yonghu 
SET is_deleted = 'Y', updated_at = NOW() 
WHERE id = '旧的用户ID';
```

---

## 📝 配置检查清单

配置完成后，请检查以下项目：

- [ ] 角色"业务员"已创建
- [ ] 角色"财务"已创建
- [ ] 用户 salesperson1 已分配"业务员"角色
- [ ] 用户 finance1 已分配"财务"角色
- [ ] 审批流程"银行转账支付审批"已创建
- [ ] 审批流程有2个步骤
- [ ] 步骤1：业务员上传汇款单据
- [ ] 步骤2：财务审核确认
- [ ] 流程状态为"启用"

---

## 🎯 下一步

配置完成后，可以进行以下工作：

1. **前端开发**
   - 修改客户签署页面，添加银行转账选项
   - 创建业务员审核页面
   - 创建财务审核页面

2. **后端开发**
   - 实现银行转账提交API
   - 实现业务员审核API
   - 实现财务审核API
   - 实现支付状态更新逻辑

3. **测试**
   - 端到端测试完整流程
   - 测试各种异常情况

---

## 📞 支持

如果在配置过程中遇到问题：

1. 检查数据库连接是否正常
2. 检查用户权限是否正确
3. 查看浏览器控制台错误信息
4. 查看后端日志

---

**配置时间估计**：10-15分钟  
**测试时间估计**：5-10分钟  
**总计**：15-25分钟

开始配置吧！🚀

