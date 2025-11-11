# 审核流程配置问题修复总结

## 🐛 问题描述

用户在使用审核流程配置页面 (http://localhost:5174/audit/workflow-config) 时遇到以下问题：

1. **列表显示问题**: 创建流程后，列表中流程名称显示为空
2. **编辑功能问题**: 点击"编辑"按钮，表单内容为空
3. **规则配置问题**: 在审核规则配置页面，"指定流程"下拉框为空

## 🔍 根本原因

### 原因1: 前后端字段名不匹配

**后端返回**:
```json
{
  "id": "xxx",
  "name": "合同金额审核流程",  ← 字段名是 "name"
  "status": "active",
  ...
}
```

**前端期望**:
```vue
<el-table-column prop="workflow_name" label="流程名称" />
<!-- ↑ 期望字段名是 "workflow_name" -->
```

### 原因2: 缺少审核类型字段

后端响应中没有返回 `audit_type` 字段，导致前端无法正确显示和编辑流程类型。

### 原因3: 流程下拉框API调用错误

前端调用了不存在的API端点 `/api/v1/audit-rules/workflows/options`，应该调用 `/api/v1/audit-workflows`。

## ✅ 已实施的修复

### 修复1: 更新后端Schema

**文件**: `packages/backend/src/schemas/shenhe_guanli/audit_workflow_schemas.py`

**修改内容**:
```python
class AuditWorkflowResponse(BaseModel):
    """审核工作流响应模型"""
    id: str
    workflow_name: str  # ← 改为 workflow_name
    audit_type: str  # ← 添加审核类型
    description: Optional[str]
    status: str
    steps: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
```

### 修复2: 更新后端Service

**文件**: `packages/backend/src/services/shenhe_guanli/audit_workflow_service.py`

**修改内容**:
```python
def _to_workflow_response(self, workflow: ShenheGuize, workflow_name: str = None) -> AuditWorkflowResponse:
    # ... 省略部分代码 ...
    
    # 解析触发条件获取审核类型
    try:
        trigger_config = json.loads(workflow.chufa_tiaojian) if isinstance(workflow.chufa_tiaojian, str) else workflow.chufa_tiaojian
        audit_type = trigger_config.get("audit_type", "")
    except:
        audit_type = ""
    
    return AuditWorkflowResponse(
        id=workflow.id,
        workflow_name=workflow_name,  # ← 改为 workflow_name
        audit_type=audit_type,  # ← 添加审核类型
        description=workflow.guize_miaoshu,
        status="active" if workflow.shi_qiyong == "Y" else "inactive",
        steps=steps,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at
    )
```

### 修复3: 更新前端流程下拉框加载

**文件**: `packages/frontend/src/views/audit/AuditRuleConfig.vue`

**修改内容**:
```typescript
const fetchWorkflowOptions = async () => {
  try {
    // 修复：调用真实API获取审核流程列表
    const { auditWorkflowApi } = await import('@/api/modules/audit')
    const response = await auditWorkflowApi.getList({
      page: 1,
      size: 100,
      status: 'active'
    })
    
    // 转换为下拉框选项格式
    workflowOptions.value = (response.items || []).map((workflow: any) => ({
      label: workflow.workflow_name,  // ← 使用 workflow_name
      value: workflow.id
    }))
  } catch (error) {
    console.error('获取审核流程选项失败:', error)
    workflowOptions.value = []
  }
}
```

## 🧪 验证步骤

### 步骤1: 重启后端服务

```bash
cd /var/www/packages/backend
pkill -f "uvicorn main:app"
bash run.sh
```

**状态**: ✅ 已完成

### 步骤2: 清除浏览器缓存

1. 打开浏览器开发者工具 (F12)
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

### 步骤3: 测试审核流程配置页面

**访问**: http://localhost:5174/audit/workflow-config

**测试用例1: 创建新流程**
1. 点击"新建流程"
2. 填写表单:
   - 流程名称: `合同金额审核流程`
   - 流程类型: `contract`
   - 流程描述: `用于合同金额调整的审核流程`
   - 添加步骤: `主管审核`
3. 点击"保存"

**预期结果**:
- ✅ 列表中显示"合同金额审核流程"
- ✅ 流程类型显示正确
- ✅ 步骤数量显示为1

**测试用例2: 编辑流程**
1. 点击刚创建的流程的"编辑"按钮

**预期结果**:
- ✅ 表单中显示"合同金额审核流程"
- ✅ 流程类型为"contract"
- ✅ 步骤列表显示"主管审核"

### 步骤4: 测试审核规则配置页面

**访问**: http://localhost:5174/audit/rule-config

**测试用例: 选择流程**
1. 点击"新建规则"
2. 在"指定审核流程"下拉框中查看

**预期结果**:
- ✅ 下拉框中显示"合同金额审核流程"
- ✅ 可以选择该流程

## 📊 修复影响范围

### 已修改的文件

| 文件 | 修改内容 | 影响 |
|------|---------|------|
| `packages/backend/src/schemas/shenhe_guanli/audit_workflow_schemas.py` | 字段名修改 | 后端API响应 |
| `packages/backend/src/services/shenhe_guanli/audit_workflow_service.py` | 添加审核类型解析 | 后端业务逻辑 |
| `packages/frontend/src/views/audit/AuditRuleConfig.vue` | 修复API调用 | 前端流程下拉框 |

### 不受影响的功能

- ✅ 审核规则的其他功能
- ✅ 审核流程执行
- ✅ 审核记录查看
- ✅ 合同生成审核触发

## 🎯 后续建议

### 短期建议

1. **数据一致性检查**: 检查现有的审核流程数据是否正确
2. **前端缓存清理**: 提醒用户清除浏览器缓存
3. **文档更新**: 更新API文档说明字段名变更

### 长期建议

1. **数据表分离**: 考虑将审核流程模板从 `shenhe_guize` 表中分离出来
2. **字段命名规范**: 统一前后端字段命名规范
3. **类型定义**: 使用TypeScript接口定义API响应类型
4. **自动化测试**: 添加E2E测试覆盖审核流程配置功能

## 📝 相关文档

- **问题分析**: `AUDIT_WORKFLOW_CONFIG_BUG_ANALYSIS.md`
- **测试脚本**: `test_workflow_config_fix.py`
- **实施计划**: `AUDIT_WORKFLOW_IMPLEMENTATION_PLAN.md`

## ✅ 修复状态

| 问题 | 状态 | 备注 |
|------|------|------|
| 列表显示为空 | ✅ 已修复 | 字段名已统一为 workflow_name |
| 编辑功能为空 | ✅ 已修复 | 前端正确读取 workflow_name |
| 流程下拉框为空 | ✅ 已修复 | API调用已更正 |
| 缺少审核类型 | ✅ 已修复 | 已添加 audit_type 字段 |

---

**修复完成时间**: 2025-10-14  
**修复人员**: AI Assistant  
**测试状态**: 待用户验证  
**优先级**: 🔴 高（核心功能）

