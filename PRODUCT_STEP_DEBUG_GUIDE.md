# 产品步骤保存问题调试指南

## 问题描述

在产品管理页面 `http://localhost:5174/product-management?type=zengzhi` 中，尝试保存产品步骤时可能遇到保存失败但没有错误提示的问题。

## 已修复的问题

### 1. 增强的数据验证

**修复内容：**
- 添加了预估时长必须大于0的验证
- 添加了步骤费用不能为负数的验证
- 改进了步骤名称的验证逻辑

**代码位置：** `packages/frontend/src/components/product/ProductStepsDialog.vue`

```typescript
// 验证步骤名称
if (!step.buzou_mingcheng || !step.buzou_mingcheng.trim()) {
  ElMessage.error('请输入步骤名称')
  return
}

// 验证预估时长
if (!step.yugu_shichang || step.yugu_shichang <= 0) {
  ElMessage.error('预估时长必须大于0')
  return
}

// 验证步骤费用
if (step.buzou_feiyong < 0) {
  ElMessage.error('步骤费用不能为负数')
  return
}
```

### 2. 增强的错误处理

**修复内容：**
- 添加了详细的控制台日志
- 改进了错误消息的提取和显示
- 确保所有错误都有用户友好的提示

```typescript
catch (error: any) {
  console.error('保存步骤失败:', error)
  
  // 提取详细的错误信息
  let errorMessage = '保存步骤失败'
  if (error.response?.data?.detail) {
    errorMessage = error.response.data.detail
  } else if (error.message) {
    errorMessage = error.message
  }
  
  ElMessage.error(errorMessage)
}
```

### 3. 输入控件改进

**修复内容：**
- 预估时长的最小值从 0 改为 0.1
- 添加了步进值 0.5，方便用户输入

```vue
<el-input-number
  v-if="row.editing"
  v-model="row.yugu_shichang"
  :min="0.1"
  :precision="1"
  :step="0.5"
  size="small"
  style="width: 100%"
/>
```

### 4. 数据类型转换

**修复内容：**
- 确保所有数字字段都正确转换为 Number 类型
- 确保字符串字段正确 trim() 处理

```typescript
const createData = {
  buzou_mingcheng: step.buzou_mingcheng.trim(),
  xiangmu_id: props.product!.id,
  yugu_shichang: Number(step.yugu_shichang),
  shichang_danwei: step.shichang_danwei,
  buzou_feiyong: Number(step.buzou_feiyong || 0),
  buzou_miaoshu: step.buzou_miaoshu || '',
  paixu: Number(step.paixu || 0),
  shi_bixu: step.shi_bixu,
  zhuangtai: step.zhuangtai
}
```

## 调试步骤

### 1. 打开浏览器开发者工具

按 `F12` 或右键点击页面选择"检查"

### 2. 查看控制台（Console）

在 Console 标签中查看：
- ✅ 创建步骤数据的日志
- ✅ API 响应的日志
- ❌ 任何 JavaScript 错误

### 3. 查看网络请求（Network）

在 Network 标签中：
1. 点击"保存"按钮
2. 查找 `/api/v1/product-management/steps` 的请求
3. 检查：
   - **请求方法：** POST（创建）或 PUT（更新）
   - **状态码：** 200/201（成功）或 4xx/5xx（失败）
   - **请求数据：** 查看 Payload 标签
   - **响应数据：** 查看 Response 标签

### 4. 常见错误及解决方案

#### 错误 1: 预估时长为 0 或负数

**错误信息：**
```
预估时长必须大于0
```

**解决方案：**
- 确保预估时长大于 0
- 最小值为 0.1

#### 错误 2: 步骤名称为空

**错误信息：**
```
请输入步骤名称
```

**解决方案：**
- 填写步骤名称

#### 错误 3: 后端验证错误

**错误信息：**
```
1 validation error for ChanpinBuzouCreate
yugu_shichang
  Input should be greater than 0
```

**解决方案：**
- 这是后端的 Pydantic 验证错误
- 检查所有字段是否符合要求
- 前端验证应该已经阻止了这种情况

#### 错误 4: 权限错误

**错误信息：**
```
403 Forbidden
```

**解决方案：**
- 确保当前用户有 `product:update` 权限
- 联系管理员分配权限

## 测试后端 API

运行测试脚本验证后端 API 是否正常：

```bash
cd packages/backend
poetry run python src/scripts/test_product_step_api.py
```

测试脚本会：
1. ✅ 查找"股权变更（内资）"产品
2. ✅ 查询现有步骤
3. ✅ 测试创建新步骤（包括边界情况）
4. ✅ 测试更新步骤
5. ✅ 清理测试数据

## 验证修复

### 步骤 1: 刷新页面

强制刷新浏览器页面：
- Windows/Linux: `Ctrl + F5`
- macOS: `Cmd + Shift + R`

### 步骤 2: 测试添加步骤

1. 访问 `http://localhost:5174/product-management?type=zengzhi`
2. 找到"股权变更（内资）"产品
3. 点击"管理步骤"按钮
4. 点击"添加步骤"
5. 填写步骤信息：
   - 步骤名称：测试步骤
   - 预估时长：1.5
   - 时长单位：小时
   - 步骤费用：100
   - 步骤描述：这是一个测试步骤
6. 点击"保存"按钮
7. 应该看到"步骤创建成功"的提示

### 步骤 3: 测试编辑步骤

1. 点击已有步骤的"编辑"按钮
2. 修改步骤信息
3. 点击"保存"按钮
4. 应该看到"步骤更新成功"的提示

### 步骤 4: 测试删除步骤

1. 点击步骤的"删除"按钮
2. 确认删除
3. 应该看到"步骤删除成功"的提示

## 后端日志

查看后端日志以获取更多信息：

```bash
tail -f /tmp/backend_8000.log
```

或者查看运行中的后端进程输出。

## 数据库验证

直接查询数据库验证步骤是否保存：

```bash
cd packages/backend
poetry run python -c "
import sys
sys.path.insert(0, 'src')
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chanpin_guanli import ChanpinBuzou

engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

steps = db.query(ChanpinBuzou).filter(
    and_(
        ChanpinBuzou.xiangmu_id == 'b2d35463-73c3-4727-8294-c70e0067ec82',
        ChanpinBuzou.is_deleted == 'N'
    )
).all()

print(f'步骤数量: {len(steps)}')
for step in steps:
    print(f'  - {step.buzou_mingcheng}: ¥{step.buzou_feiyong}')

db.close()
"
```

## 总结

修复内容：
- ✅ 增强了前端数据验证
- ✅ 改进了错误处理和提示
- ✅ 添加了详细的调试日志
- ✅ 修复了输入控件的最小值限制
- ✅ 确保了数据类型的正确转换

如果问题仍然存在，请：
1. 查看浏览器控制台的完整错误信息
2. 查看网络请求的详细信息
3. 运行后端测试脚本验证 API
4. 提供具体的错误信息以便进一步诊断

