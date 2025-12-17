# 审核流程实施快速开始指南

## 📖 文档导航

本项目包含以下详细实施文档：

| 文档 | 优先级 | 状态 | 预计时间 | 说明 |
|------|-------|------|---------|------|
| [AUDIT_WORKFLOW_IMPLEMENTATION_PLAN.md](./AUDIT_WORKFLOW_IMPLEMENTATION_PLAN.md) | ⭐⭐⭐⭐⭐ | 立即可用 | 30分钟 | 合同金额调整审核配置 |
| [AUDIT_WORKFLOW_PRIORITY2_BANK_PAYMENT.md](./AUDIT_WORKFLOW_PRIORITY2_BANK_PAYMENT.md) | ⭐⭐⭐⭐ | 需要开发 | 2-3天 | 银行转账支付审核 |
| [AUDIT_WORKFLOW_PRIORITY3_DYNAMIC_FORMS.md](./AUDIT_WORKFLOW_PRIORITY3_DYNAMIC_FORMS.md) | ⭐⭐⭐ | 需要开发 | 3-5天 | 动态表单配置 |

---

## 🚀 立即开始：合同金额调整审核（5分钟配置）

### 前提条件检查

```bash
# 1. 检查后端服务是否运行
curl http://localhost:8000/health

# 2. 检查前端服务是否运行
curl http://localhost:5174

# 3. 检查数据库连接
cd packages/backend
source venv/bin/activate
python3 -c "
from sqlalchemy import create_engine
from core.config import settings
engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()
print('✅ 数据库连接成功')
conn.close()
"
```

### 方法1: 使用前端界面配置（推荐）

**步骤1**: 访问审核规则配置页面
```
http://localhost:5174/audit/rule-config
```

**步骤2**: 点击"新建规则"按钮

**步骤3**: 填写表单
- **规则名称**: `合同金额降价审核规则`
- **规则类型**: 选择 `hetong_jine_xiuzheng`
- **规则描述**: `当合同金额低于报价金额时触发审核`
- **是否启用**: 选择"是"

**步骤4**: 配置触发条件（JSON格式）
```json
{
  "type": "amount_decrease",
  "thresholds": [
    {
      "percentage": 5,
      "approver_level": "supervisor",
      "description": "降价5%-10%需主管审核"
    },
    {
      "percentage": 10,
      "approver_level": "manager",
      "description": "降价10%-20%需经理审核"
    },
    {
      "percentage": 20,
      "approver_level": "director",
      "description": "降价超过20%需总监审核"
    }
  ]
}
```

**步骤5**: 配置审核流程（JSON格式）
```json
{
  "steps": [
    {
      "step": 1,
      "name": "主管审核",
      "role": "supervisor",
      "required": true,
      "condition": "percentage >= 5",
      "expected_time": 24
    },
    {
      "step": 2,
      "name": "经理审核",
      "role": "manager",
      "required": true,
      "condition": "percentage >= 10",
      "expected_time": 48
    },
    {
      "step": 3,
      "name": "总监审核",
      "role": "director",
      "required": true,
      "condition": "percentage >= 20",
      "expected_time": 72
    }
  ],
  "auto_assign": true,
  "notification_methods": ["system", "email"]
}
```

**步骤6**: 点击"保存"

### 方法2: 使用API配置（备选）

**步骤1**: 获取访问令牌
```bash
# 登录获取token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token',''))")

echo "Token: $TOKEN"
```

**步骤2**: 创建审核规则
```bash
curl -X POST http://localhost:8000/api/v1/audit-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "guize_mingcheng": "合同金额降价审核规则",
    "guize_leixing": "hetong_jine_xiuzheng",
    "guize_miaoshu": "当合同金额低于报价金额时触发审核",
    "chufa_tiaojian": {
      "type": "amount_decrease",
      "thresholds": [
        {"percentage": 5, "approver_level": "supervisor"},
        {"percentage": 10, "approver_level": "manager"},
        {"percentage": 20, "approver_level": "director"}
      ]
    },
    "shenhe_liucheng_peizhi": {
      "steps": [
        {
          "step": 1,
          "name": "主管审核",
          "role": "supervisor",
          "required": true,
          "condition": "percentage >= 5",
          "expected_time": 24
        },
        {
          "step": 2,
          "name": "经理审核",
          "role": "manager",
          "required": true,
          "condition": "percentage >= 10",
          "expected_time": 48
        },
        {
          "step": 3,
          "name": "总监审核",
          "role": "director",
          "required": true,
          "condition": "percentage >= 20",
          "expected_time": 72
        }
      ],
      "auto_assign": true,
      "notification_methods": ["system", "email"]
    },
    "shi_qiyong": "Y",
    "paixu": 1
  }'
```

### 验证配置

**方法1: 查看规则列表**
```bash
curl -X GET "http://localhost:8000/api/v1/audit-rules?guize_leixing=hetong_jine_xiuzheng" \
  -H "Authorization: Bearer $TOKEN"
```

**方法2: 数据库查询**
```sql
SELECT 
    guize_mingcheng,
    guize_leixing,
    shi_qiyong,
    created_at
FROM shenhe_guize 
WHERE guize_leixing = 'hetong_jine_xiuzheng'
  AND is_deleted = 'N';
```

---

## 🧪 测试审核流程

### 测试场景: 降价10%触发审核

**步骤1**: 访问线索管理页面
```
http://localhost:5174/leads
```

**步骤2**: 找到一个已接受的报价
- 例如：线索编号 `XS20251014001`
- 报价金额：`6400元`

**步骤3**: 生成合同
1. 点击"生成合同"按钮
2. 选择合同类型：代理记账
3. 设置合同金额：`5760元`（降价10%）
4. 填写价格调整原因：`客户要求优惠，竞争对手报价更低`
5. 点击"生成合同"

**预期结果**:
```
✅ 系统提示："价格调整需要审核"
✅ 创建审核流程记录
✅ 合同状态：待审核
✅ 审核步骤：主管审核 + 经理审核（共2步）
```

**验证审核流程**:
```sql
-- 查看最新的审核流程
SELECT 
    l.liucheng_bianhao,
    l.shenhe_leixing,
    l.shenhe_zhuangtai,
    l.dangqian_buzhou,
    l.zonggong_buzhou,
    l.created_at
FROM shenhe_liucheng l
WHERE l.shenhe_leixing = 'hetong_jine_xiuzheng'
  AND l.is_deleted = 'N'
ORDER BY l.created_at DESC
LIMIT 1;

-- 查看审核步骤
SELECT 
    j.buzhou_mingcheng,
    j.shenhe_ren_id,
    j.shenhe_zhuangtai,
    j.shenhe_jieguo
FROM shenhe_jilu j
JOIN shenhe_liucheng l ON j.liucheng_id = l.id
WHERE l.shenhe_leixing = 'hetong_jine_xiuzheng'
  AND l.is_deleted = 'N'
ORDER BY j.buzhou_shunxu;
```

---

## 📊 实施进度跟踪

### 优先级1: 合同金额调整审核

- [ ] 前提条件检查完成
- [ ] 审核规则创建成功
- [ ] 规则配置验证通过
- [ ] 测试场景1（降价5%）通过
- [ ] 测试场景2（降价10%）通过
- [ ] 测试场景3（降价20%）通过
- [ ] 审核通知正常发送
- [ ] 审核流程可以正常审批
- [ ] 文档记录完成

**完成时间**: ___________

### 优先级2: 银行转账支付审核

- [ ] 前端API封装完成
- [ ] 汇款单上传页面完成
- [ ] 业务员审核页面完成
- [ ] 财务审核页面完成
- [ ] 合同签署页面集成完成
- [ ] 路由配置完成
- [ ] 集成测试通过
- [ ] 文档记录完成

**完成时间**: ___________

### 优先级3: 动态表单配置

- [ ] 数据库迁移完成
- [ ] 模型和Schema更新完成
- [ ] 表单验证工具完成
- [ ] 动态表单渲染器完成
- [ ] 表单构建器完成
- [ ] 审核规则集成完成
- [ ] 集成测试通过
- [ ] 文档记录完成

**完成时间**: ___________

---

## 🔧 故障排查

### 问题1: 审核规则创建失败

**症状**: API返回400或500错误

**排查步骤**:
```bash
# 1. 检查后端日志
tail -f packages/backend/logs/app.log

# 2. 检查数据库连接
cd packages/backend
source venv/bin/activate
python3 -c "from core.database import get_db; next(get_db())"

# 3. 检查用户权限
# 确保当前用户有 audit_rule:create 权限
```

### 问题2: 审核未触发

**症状**: 生成合同时没有触发审核流程

**排查步骤**:
```bash
# 1. 检查规则是否启用
curl -X GET "http://localhost:8000/api/v1/audit-rules?shi_qiyong=Y" \
  -H "Authorization: Bearer $TOKEN"

# 2. 检查价格差异计算
# 在 hetong_generate.py 中添加日志
# 查看 price_diff 的值

# 3. 检查审核引擎日志
tail -f packages/backend/logs/app.log | grep "trigger_audit"
```

### 问题3: 前端页面无法访问

**症状**: 访问审核规则配置页面返回404

**排查步骤**:
```bash
# 1. 检查前端服务
curl http://localhost:5174

# 2. 检查路由配置
# 查看 packages/frontend/src/router/index.ts

# 3. 重启前端服务
cd packages/frontend
npm run dev
```

---

## 📞 支持和帮助

### 相关文档

- **后端API文档**: http://localhost:8000/docs
- **数据库Schema**: `packages/backend/src/models/`
- **前端组件**: `packages/frontend/src/components/`

### 日志位置

- **后端日志**: `packages/backend/logs/app.log`
- **前端控制台**: 浏览器开发者工具 Console
- **数据库日志**: PostgreSQL日志

### 常用命令

```bash
# 重启后端服务
cd packages/backend
bash run.sh

# 重启前端服务
cd packages/frontend
npm run dev

# 查看数据库
psql -U postgres -d your_database

# 运行测试
cd packages/backend
pytest tests/
```

---

## ✅ 下一步行动

1. **立即执行**: 完成优先级1（合同金额调整审核配置）
2. **本周完成**: 开始优先级2（银行转账支付审核前端开发）
3. **下周计划**: 规划优先级3（动态表单配置）的详细设计

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2025-10-14 | 1.0 | 初始版本，包含三个优先级的详细计划 |

---

**祝您实施顺利！** 🎉

