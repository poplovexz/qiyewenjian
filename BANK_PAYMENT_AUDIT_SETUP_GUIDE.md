# 银行汇款审核流程设置指南

## 📋 概述

本指南将帮助你设置银行汇款审核流程，使财务人员能够审核业务员上传的汇款凭证。

## 🎯 流程说明

### 完整业务流程

1. **客户确认银行转账** → 系统创建汇款单据（状态：待上传凭证）
2. **业务员上传凭证** → 状态更新为"待审核"，触发审核流程
3. **财务审核凭证** → 审核通过后，合同支付状态自动更新为"已支付"

### 审核类型

- **审核类型代码**: `yinhang_huikuan`（银行汇款审核）
- **关联对象**: 银行汇款单据（YinhangHuikuanDanju）

## 🛠️ 方案一：通过前端界面配置（推荐）

### 步骤1：访问审核流程配置页面

1. 登录系统（使用管理员账号）
2. 访问：`http://localhost:5174/audit/workflow-config`
3. 点击"新建工作流"按钮

### 步骤2：填写工作流基本信息

在弹出的表单中填写：

| 字段 | 值 | 说明 |
|------|-----|------|
| 工作流名称 | 银行汇款凭证审核 | 显示名称 |
| 审核类型 | yinhang_huikuan | **重要**：必须是这个值 |
| 工作流描述 | 业务员上传银行汇款凭证后，由财务人员审核确认 | 可选 |
| 状态 | 启用 | 选择"启用" |

### 步骤3：配置审核步骤

点击"添加步骤"，配置以下审核步骤：

#### 步骤1：财务专员审核

| 字段 | 值 |
|------|-----|
| 步骤名称 | 财务专员审核 |
| 步骤顺序 | 1 |
| 审核人 | 选择财务专员角色或具体财务人员 |
| 步骤描述 | 审核汇款凭证的真实性和金额是否正确 |
| 预计处理时间 | 24（小时） |
| 是否必需 | 是 |

#### 步骤2：财务经理审核（可选，大额汇款）

如果需要对大额汇款进行二次审核，可以添加第二步：

| 字段 | 值 |
|------|-----|
| 步骤名称 | 财务经理审核 |
| 步骤顺序 | 2 |
| 审核人 | 选择财务经理角色或具体财务经理 |
| 步骤描述 | 对大额汇款进行二次确认 |
| 预计处理时间 | 48（小时） |
| 是否必需 | 是 |

### 步骤4：保存配置

点击"确定"按钮保存配置。

## 🛠️ 方案二：通过数据库直接配置

如果前端界面还没有完全实现，可以通过数据库直接插入配置。

### SQL脚本

```sql
-- 插入银行汇款审核流程配置
INSERT INTO shenhe_guize (
    id,
    guize_mingcheng,
    guize_leixing,
    chufa_tiaojian,
    shenhe_liucheng_peizhi,
    shi_qiyong,
    paixu,
    guize_miaoshu,
    created_by,
    created_at,
    updated_at,
    is_deleted
) VALUES (
    gen_random_uuid(),
    '工作流模板-银行汇款凭证审核',
    'workflow_template',
    '{"type": "workflow_template", "audit_type": "yinhang_huikuan"}',
    '{
        "steps": [
            {
                "step": 1,
                "name": "财务专员审核",
                "approver_role": "finance_specialist",
                "description": "审核汇款凭证的真实性和金额是否正确",
                "expected_time": 24,
                "is_required": true
            }
        ]
    }',
    'Y',
    1,
    '业务员上传银行汇款凭证后，由财务人员审核确认',
    'system',
    NOW(),
    NOW(),
    'N'
);
```

### 验证配置

执行以下SQL验证配置是否成功：

```sql
SELECT 
    id,
    guize_mingcheng,
    guize_leixing,
    chufa_tiaojian,
    shenhe_liucheng_peizhi,
    shi_qiyong
FROM shenhe_guize 
WHERE guize_leixing = 'workflow_template'
AND chufa_tiaojian::jsonb->>'audit_type' = 'yinhang_huikuan'
AND is_deleted = 'N';
```

## 🛠️ 方案三：通过API配置

### 使用curl命令

```bash
# 1. 登录获取token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@example.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. 创建审核流程配置
curl -X POST http://localhost:8000/api/v1/audit-workflows/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "workflow_name": "银行汇款凭证审核",
    "audit_type": "yinhang_huikuan",
    "description": "业务员上传银行汇款凭证后，由财务人员审核确认",
    "status": "active",
    "steps": [
      {
        "step_name": "财务专员审核",
        "step_order": 1,
        "approver_role": "finance_specialist",
        "description": "审核汇款凭证的真实性和金额是否正确",
        "expected_time": 24,
        "is_required": true
      }
    ]
  }'
```

## 🔧 后端代码集成

### 修改业务员上传凭证服务

需要在业务员上传凭证后触发审核流程。

**文件**: `packages/backend/src/services/zhifu_guanli/yinhang_huikuan_danju_service.py`

在 `upload_voucher` 方法中添加触发审核的代码：

```python
def upload_voucher(self, danju_id: str, voucher_url: str, uploader_id: str, beizhu: str = None):
    """业务员上传汇款凭证"""
    # ... 现有代码 ...
    
    # 更新状态为待审核
    danju.shenhe_zhuangtai = "pending_audit"
    
    # ✅ 触发审核流程
    from services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine
    
    workflow_engine = ShenheWorkflowEngine(self.db)
    workflow_id = workflow_engine.trigger_audit(
        audit_type="yinhang_huikuan",  # 审核类型
        related_id=danju_id,  # 汇款单据ID
        trigger_data={
            "danju_bianhao": danju.danju_bianhao,
            "huikuan_jine": float(danju.huikuan_jine),
            "voucher_url": voucher_url
        },
        applicant_id=uploader_id  # 上传人ID
    )
    
    # 保存审核流程ID（可选）
    if workflow_id:
        danju.shenhe_liucheng_id = workflow_id
    
    self.db.commit()
    
    return {
        "success": True,
        "message": "凭证上传成功，已提交审核",
        "workflow_id": workflow_id
    }
```

### 修改财务审核服务

财务审核通过后，需要更新汇款单据状态和合同支付状态。

**文件**: `packages/backend/src/services/zhifu_guanli/yinhang_huikuan_danju_service.py`

```python
def audit_voucher(self, danju_id: str, approved: bool, auditor_id: str, audit_opinion: str = None):
    """财务审核汇款凭证"""
    # ... 现有代码 ...
    
    if approved:
        # 审核通过
        danju.shenhe_zhuangtai = "approved"
        
        # ✅ 更新合同支付状态为已支付
        if danju.hetong_zhifu_id:
            from models.hetong_guanli.hetong_zhifu import HetongZhifu
            
            hetong_zhifu = self.db.query(HetongZhifu).filter(
                HetongZhifu.id == danju.hetong_zhifu_id,
                HetongZhifu.is_deleted == "N"
            ).first()
            
            if hetong_zhifu:
                hetong_zhifu.zhifu_zhuangtai = "paid"  # 已支付
                hetong_zhifu.shiji_zhifu_shijian = datetime.now()
                
                # 更新合同状态为已生效
                from models.hetong_guanli.hetong import Hetong
                hetong = self.db.query(Hetong).filter(
                    Hetong.id == hetong_zhifu.hetong_id,
                    Hetong.is_deleted == "N"
                ).first()
                
                if hetong and hetong.hetong_zhuangtai == "signed":
                    hetong.hetong_zhuangtai = "active"  # 已生效
    else:
        # 审核拒绝
        danju.shenhe_zhuangtai = "rejected"
    
    danju.shenhe_ren_id = auditor_id
    danju.shenhe_shijian = datetime.now()
    danju.shenhe_yijian = audit_opinion
    
    self.db.commit()
    
    return {
        "success": True,
        "message": "审核完成"
    }
```

## 📊 测试流程

### 1. 创建测试数据

1. 访问合同签署页面：`http://localhost:5174/contract-sign/{token}`
2. 完成签名
3. 选择"银行转账"支付方式
4. 点击"确认使用银行转账"

### 2. 业务员上传凭证

1. 访问：`http://localhost:5174/finance/bank-transfers`
2. 找到"待上传凭证"的单据
3. 点击"上传凭证"
4. 上传图片并提交

### 3. 财务审核

1. 访问：`http://localhost:5174/audit/my-tasks`（待实现）
2. 查看待审核的汇款凭证
3. 点击"审核"
4. 选择"通过"或"拒绝"
5. 填写审核意见
6. 提交审核

### 4. 验证结果

- 审核通过后，汇款单据状态应该变为"已通过"
- 合同支付状态应该变为"已支付"
- 合同状态应该变为"已生效"

## ⚠️ 注意事项

1. **审核类型必须匹配**：配置中的 `audit_type` 必须是 `yinhang_huikuan`
2. **审核人权限**：确保审核人有相应的审核权限
3. **通知机制**：建议配置审核通知，及时提醒财务人员审核
4. **数据完整性**：确保审核流程配置包含完整的 `steps` 数组

## 🚧 下一步工作

1. **集成到审核任务列表** - 让财务可以在"我的审核"中看到待审核的汇款凭证
2. **添加审核详情页面** - 显示汇款凭证图片和相关信息
3. **添加通知功能** - 业务员上传后通知财务，审核完成后通知业务员
4. **添加审核历史** - 记录所有审核操作的历史记录

## 📝 常见问题

### Q1: 为什么看不到待审核的汇款凭证？

**A**: 检查以下几点：
1. 审核流程配置是否正确创建（`audit_type` 必须是 `yinhang_huikuan`）
2. 审核流程是否已启用（`shi_qiyong = 'Y'`）
3. 业务员上传凭证后是否成功触发了审核流程
4. 当前用户是否有审核权限

### Q2: 审核通过后合同状态没有更新？

**A**: 检查以下几点：
1. `audit_voucher` 方法中是否正确更新了合同支付状态
2. 合同支付记录是否存在
3. 数据库事务是否正确提交

### Q3: 如何修改审核流程？

**A**: 
1. 访问审核流程配置页面
2. 找到"银行汇款凭证审核"流程
3. 点击"编辑"按钮
4. 修改步骤配置
5. 保存

---

**文档创建时间**: 2025-10-16  
**创建人员**: AI Assistant  
**状态**: 待实施

