# 支付方式管理功能增强

## 问题描述

用户反馈：http://localhost:5174/finance/payment-methods 的支付方式管理功能对微信支付和支付宝支付没有很好的支持。

## 解决方案

### 1. 数据库模型增强

在 `hetong_zhifu_fangshi` 表中添加了以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `weixin_haoma` | VARCHAR(100) | 微信号/微信收款账号 |
| `weixin_shoukuan_ming` | VARCHAR(100) | 微信收款名 |
| `zhifubao_haoma` | VARCHAR(100) | 支付宝账号 |
| `zhifubao_shoukuan_ming` | VARCHAR(100) | 支付宝收款名 |
| `erweima_lujing` | VARCHAR(500) | 收款二维码图片路径 |

### 2. 后端API更新

#### 模型文件
- **`packages/backend/src/models/hetong_guanli/hetong_zhifu_fangshi.py`**
  - 添加微信和支付宝相关字段
  - 添加二维码路径字段

#### Schema文件
- **`packages/backend/src/schemas/hetong_guanli/hetong_zhifu_fangshi_schemas.py`**
  - 更新 `HetongZhifuFangshiBase` 添加新字段
  - 更新 `HetongZhifuFangshiUpdate` 添加新字段
  - 更新 `HetongZhifuFangshiResponse` 添加新字段

#### 数据库迁移
- **`packages/backend/src/scripts/add_payment_method_fields.py`**
  - 自动检测并添加新字段
  - 幂等性设计，可安全重复运行
  - 已在开发环境执行成功

### 3. 前端表单优化

#### 动态字段显示

根据选择的支付类型，表单会动态显示相应的字段：

**银行转账 (yinhangzhuanzhang)**
- 账户名称
- 账户号码 ✱
- 开户行 ✱
- 联行号

**微信支付 (weixin)**
- 微信号 ✱
- 微信收款名
- 收款二维码（图片上传）

**支付宝 (zhifubao)**
- 支付宝账号 ✱
- 支付宝收款名
- 收款二维码（图片上传）

**现金 (xianjin)**
- 基本信息即可

**其他 (qita)**
- 基本信息即可

✱ 表示必填字段

#### 二维码上传功能

- 支持拖拽上传
- 支持点击上传
- 图片预览功能
- 文件大小限制：5MB
- 支持格式：JPG、PNG等图片格式
- 上传成功后显示预览图

#### 表单验证增强

- 根据支付类型动态验证必填字段
- 银行转账：账户号码、开户行必填
- 微信支付：微信号必填
- 支付宝：支付宝账号必填
- 账户号码长度验证：5-50字符
- 支付方式名称长度验证：2-100字符

### 4. 前端API类型定义

更新了 `packages/frontend/src/api/modules/contract.ts` 中的类型定义：

```typescript
export interface PaymentMethod {
  // ... 其他字段
  weixin_haoma?: string
  weixin_shoukuan_ming?: string
  zhifubao_haoma?: string
  zhifubao_shoukuan_ming?: string
  erweima_lujing?: string
  // ...
}

export interface PaymentMethodCreate {
  // ... 同上
}

export interface PaymentMethodUpdate {
  // ... 同上
}
```

## 修改的文件

### 后端
1. `packages/backend/src/models/hetong_guanli/hetong_zhifu_fangshi.py` - 数据库模型
2. `packages/backend/src/schemas/hetong_guanli/hetong_zhifu_fangshi_schemas.py` - API schemas
3. `packages/backend/src/scripts/add_payment_method_fields.py` - 数据库迁移脚本（新建）

### 前端
1. `packages/frontend/src/views/contract/PaymentMethodForm.vue` - 支付方式表单
2. `packages/frontend/src/api/modules/contract.ts` - API类型定义

## 部署步骤

### 开发环境
✅ 已完成
- 数据库迁移已执行
- 代码已提交到Git

### 生产环境
需要执行以下步骤：

1. **部署代码**
   - 使用一键部署功能：http://localhost:5174/settings/deploy
   - 或使用命令：`./quick-deploy.sh`

2. **运行数据库迁移**
   ```bash
   ssh saas@172.16.2.221
   cd /home/saas/proxy-system/packages/backend
   source venv/bin/activate
   export PYTHONPATH=/home/saas/proxy-system/packages/backend/src
   python3 src/scripts/add_payment_method_fields.py
   ```

3. **验证功能**
   - 访问 http://172.16.2.221/finance/payment-methods
   - 点击"新建支付方式"
   - 选择不同的支付类型，验证字段显示是否正确
   - 测试微信和支付宝的二维码上传功能

## 使用示例

### 创建微信支付方式

1. 访问支付方式管理页面
2. 点击"新建支付方式"
3. 选择乙方主体
4. 支付方式选择"微信支付"
5. 填写：
   - 支付方式名称：如"张三微信收款"
   - 微信号：如"zhangsan123"
   - 微信收款名：如"张三"（可选）
   - 上传收款二维码（可选）
6. 设置是否默认
7. 点击"创建"

### 创建支付宝支付方式

1. 访问支付方式管理页面
2. 点击"新建支付方式"
3. 选择乙方主体
4. 支付方式选择"支付宝"
5. 填写：
   - 支付方式名称：如"李四支付宝收款"
   - 支付宝账号：如"lisi@example.com" 或 "13800138000"
   - 支付宝收款名：如"李四"（可选）
   - 上传收款二维码（可选）
6. 设置是否默认
7. 点击"创建"

### 创建银行转账方式

1. 访问支付方式管理页面
2. 点击"新建支付方式"
3. 选择乙方主体
4. 支付方式选择"银行转账"
5. 填写：
   - 支付方式名称：如"公司对公账户"
   - 账户名称：如"XX科技有限公司"
   - 账户号码：如"6222021234567890123"
   - 开户行：如"中国工商银行北京分行"
   - 联行号：如"102100099996"（可选）
6. 设置是否默认
7. 点击"创建"

## 技术亮点

1. **智能表单**：根据支付类型动态显示相关字段，避免信息冗余
2. **完善验证**：根据支付类型智能验证必填字段
3. **图片上传**：集成二维码上传功能，支持预览
4. **幂等迁移**：数据库迁移脚本可安全重复运行
5. **类型安全**：完整的TypeScript类型定义

## 后续优化建议

1. **二维码识别**：可以添加二维码识别功能，自动提取收款信息
2. **批量导入**：支持批量导入支付方式
3. **模板功能**：常用支付方式模板
4. **权限控制**：不同角色对支付方式的访问权限
5. **审计日志**：记录支付方式的创建、修改、删除操作

## 测试清单

- [ ] 创建微信支付方式
- [ ] 创建支付宝支付方式
- [ ] 创建银行转账支付方式
- [ ] 上传二维码图片
- [ ] 编辑支付方式
- [ ] 删除支付方式
- [ ] 设置默认支付方式
- [ ] 表单验证测试
- [ ] 生产环境部署测试

## Git提交

```
commit 190ef3f
增强支付方式管理：添加微信和支付宝支持

功能改进：
1. 数据库模型增强
2. 后端API更新
3. 前端表单优化
4. 用户体验提升
```

## 相关文档

- [支付方式管理API文档](packages/backend/src/api/api_v1/endpoints/hetong_guanli/README.md)
- [数据库迁移指南](packages/backend/src/scripts/README.md)
- [前端组件开发规范](packages/frontend/README.md)

