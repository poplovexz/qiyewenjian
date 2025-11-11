# 工单任务项分配功能 - 实施文档

## 📋 功能概述

本功能允许将服务工单的每个任务项独立分配给不同的执行人，支持多人协作完成复杂的服务流程。

### **业务价值**

- ✅ **专业分工**：不同步骤可以分配给具有相应专业技能的人员
- ✅ **责任明确**：每个步骤有明确的负责人
- ✅ **进度跟踪**：可以清晰地看到每个步骤的执行情况
- ✅ **跨部门协作**：支持不同部门的人员协作完成工单

### **适用场景**

以"公司改制（内转外/外转内）"增值服务为例，包含以下6个步骤：

1. **工商核名** - 由工商专员负责
2. **网报签字** - 由客户经理负责
3. **领取执照** - 由工商专员负责
4. **客户交接** - 由客户经理负责
5. **开立基本户** - 由财务专员负责
6. **税务登记** - 由税务专员负责

---

## 🚀 实施内容

### **第一阶段：数据库层（已完成）**

#### **1. 数据库迁移**

在 `fuwu_gongdan_xiangmu` 表添加执行人字段：

```sql
-- 添加执行人ID字段
ALTER TABLE fuwu_gongdan_xiangmu 
ADD COLUMN zhixing_ren_id VARCHAR(36);

-- 添加外键约束
ALTER TABLE fuwu_gongdan_xiangmu
ADD CONSTRAINT fk_fuwu_gongdan_xiangmu_zhixing_ren
FOREIGN KEY (zhixing_ren_id) REFERENCES yonghu(id) ON DELETE SET NULL;

-- 创建索引
CREATE INDEX idx_fuwu_gongdan_xiangmu_zhixing_ren 
ON fuwu_gongdan_xiangmu(zhixing_ren_id);

-- 添加注释
COMMENT ON COLUMN fuwu_gongdan_xiangmu.zhixing_ren_id IS '执行人ID';
```

**执行状态**: ✅ 已完成

#### **2. 数据模型更新**

文件：`packages/backend/src/models/fuwu_guanli/fuwu_gongdan.py`

```python
class FuwuGongdanXiangmu(BaseModel):
    """服务工单项目表"""
    
    # ... 现有字段 ...
    
    # 新增字段
    zhixing_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="执行人ID"
    )
    
    # 关联关系
    gongdan = relationship("FuwuGongdan", back_populates="xiangmu_list")
    zhixing_ren = relationship("Yonghu", foreign_keys=[zhixing_ren_id])
```

**执行状态**: ✅ 已完成

---

### **第二阶段：后端API层（已完成）**

#### **1. Schema更新**

文件：`packages/backend/src/schemas/fuwu_guanli/fuwu_gongdan_schemas.py`

**新增执行人信息Schema**：

```python
class ZhixingRenInfo(BaseModel):
    """执行人简要信息"""
    id: str
    yonghu_ming: str
    xingming: str
    
    class Config:
        from_attributes = True
```

**更新任务项Schema**：

```python
class FuwuGongdanXiangmuBase(BaseModel):
    # ... 现有字段 ...
    zhixing_ren_id: Optional[str] = Field(None, description="执行人ID")

class FuwuGongdanXiangmuResponse(FuwuGongdanXiangmuBase):
    id: str
    gongdan_id: str
    zhixing_ren: Optional[ZhixingRenInfo] = Field(None, description="执行人信息")
    created_at: datetime
    updated_at: datetime
```

**执行状态**: ✅ 已完成

#### **2. Service层方法**

文件：`packages/backend/src/services/fuwu_guanli/fuwu_gongdan_service.py`

**新增方法**：`assign_task_item()`

```python
def assign_task_item(
    self,
    gongdan_id: str,
    item_id: str,
    zhixing_ren_id: str,
    operator_id: str
) -> FuwuGongdanXiangmuResponse:
    """分配工单任务项给执行人"""
    # 1. 验证工单是否存在
    # 2. 验证任务项是否存在且属于该工单
    # 3. 验证执行人是否存在
    # 4. 更新任务项的执行人
    # 5. 创建操作日志
    # 6. 返回更新后的任务项信息
```

**执行状态**: ✅ 已完成

#### **3. API端点**

文件：`packages/backend/src/api/api_v1/endpoints/fuwu_guanli/fuwu_gongdan.py`

**新增端点**：

```python
@router.post(
    "/{gongdan_id}/items/{item_id}/assign",
    response_model=FuwuGongdanXiangmuResponse,
    summary="分配工单任务项"
)
def assign_task_item(
    gongdan_id: str,
    item_id: str,
    zhixing_ren_id: str = Query(..., description="执行人ID"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """分配工单任务项给执行人"""
    service = FuwuGongdanService(db)
    return service.assign_task_item(
        gongdan_id=gongdan_id,
        item_id=item_id,
        zhixing_ren_id=zhixing_ren_id,
        operator_id=current_user.id
    )
```

**API路径**: `POST /api/v1/service-orders/{gongdan_id}/items/{item_id}/assign?zhixing_ren_id={user_id}`

**执行状态**: ✅ 已完成

---

### **第三阶段：前端UI层（已完成）**

#### **1. Store更新**

文件：`packages/frontend/src/stores/modules/serviceOrderManagement.ts`

**更新接口定义**：

```typescript
export interface ZhixingRenInfo {
  id: string
  yonghu_ming: string
  xingming: string
}

export interface ServiceOrderItem {
  // ... 现有字段 ...
  zhixing_ren_id?: string
  zhixing_ren?: ZhixingRenInfo
}
```

**新增方法**：

```typescript
const assignTaskItem = async (
  gongdanId: string,
  itemId: string,
  zhixingRenId: string
) => {
  const response = await request.post(
    `/service-orders/${gongdanId}/items/${itemId}/assign`,
    null,
    { params: { zhixing_ren_id: zhixingRenId } }
  )
  ElMessage.success('分配任务项成功')
  return response
}
```

**执行状态**: ✅ 已完成

#### **2. 分配对话框组件**

文件：`packages/frontend/src/views/service-orders/components/AssignTaskItemDialog.vue`

**功能**：
- 显示任务项基本信息（名称、描述、计划工时）
- 显示当前执行人
- 选择新的执行人
- 提交分配请求

**执行状态**: ✅ 已完成

#### **3. 工单详情页更新**

文件：`packages/frontend/src/views/service-orders/ServiceOrderDetail.vue`

**更新内容**：
- 在任务项表格添加"执行人"列
- 在任务项表格添加"操作"列，包含"分配"/"重新分配"按钮
- 集成分配对话框组件
- 添加分配成功后的刷新逻辑

**执行状态**: ✅ 已完成

---

## ✅ 测试验证

### **数据库层测试**

**测试脚本**: `packages/backend/test_task_item_assignment.py`

**测试结果**: ✅ 通过

```
✅ 找到工单: WO202511041838308JW - AAA代理记账服务合同 - 服务工单
✅ 找到 5 个任务项
✅ 成功将5个任务项分配给不同的执行人
✅ 验证分配结果正确
```

---

## 📝 使用说明

### **操作步骤**

1. **打开工单详情页**
   - 导航到服务工单列表
   - 点击任意工单查看详情

2. **查看任务项**
   - 在"工单项目"卡片中查看所有任务项
   - "执行人"列显示当前分配情况

3. **分配任务项**
   - 点击任务项右侧的"分配"或"重新分配"按钮
   - 在弹出的对话框中选择执行人
   - 点击"确定"完成分配

4. **验证分配结果**
   - 分配成功后，页面自动刷新
   - "执行人"列显示新的执行人姓名
   - 工单日志中记录分配操作

---

## 🔄 后续优化建议

### **阶段2：功能完善（下周）**

1. **任务状态管理**
   - 只有被分配的执行人才能更新任务状态
   - 任务完成后自动更新工单进度

2. **通知机制**
   - 任务分配后通知执行人
   - 任务即将到期时提醒执行人

3. **权限控制**
   - 工单负责人可以分配任务
   - 执行人只能查看和更新自己的任务

### **阶段3：高级功能（本月）**

1. **任务依赖**
   - 定义任务之间的依赖关系
   - 前置任务未完成时，后续任务不能开始

2. **批量分配**
   - 根据角色自动分配任务
   - 支持批量分配多个任务

3. **工作量统计**
   - 统计每个人的任务工作量
   - 避免任务分配不均

---

## 📚 相关文件清单

### **后端文件**

- `packages/backend/src/models/fuwu_guanli/fuwu_gongdan.py` - 数据模型
- `packages/backend/src/schemas/fuwu_guanli/fuwu_gongdan_schemas.py` - Schema定义
- `packages/backend/src/services/fuwu_guanli/fuwu_gongdan_service.py` - 业务逻辑
- `packages/backend/src/api/api_v1/endpoints/fuwu_guanli/fuwu_gongdan.py` - API端点
- `packages/backend/alembic/versions/add_task_item_assignee.py` - 数据库迁移脚本

### **前端文件**

- `packages/frontend/src/stores/modules/serviceOrderManagement.ts` - Store
- `packages/frontend/src/views/service-orders/ServiceOrderDetail.vue` - 工单详情页
- `packages/frontend/src/views/service-orders/components/AssignTaskItemDialog.vue` - 分配对话框

### **测试文件**

- `packages/backend/test_task_item_assignment.py` - 数据库层测试脚本

---

## 🎯 总结

✅ **已完成**：
- 数据库迁移和模型更新
- 后端API实现
- 前端UI组件开发
- 数据库层功能测试

⏳ **待完成**：
- 前端UI功能测试（需要启动前后端服务）
- 端到端集成测试
- 用户验收测试

📅 **实施日期**: 2025年11月5日

👤 **实施人员**: AI Assistant (Augment Agent)

