# 办公管理模块开发文档

## 模块概述

办公管理模块是代理记账营运内部系统的重要组成部分，提供了5个核心子功能：

1. **申请报销** - 员工提交报销申请
2. **请假** - 员工提交请假申请
3. **申请对外付款** - 提交对外付款申请
4. **申请采购** - 提交采购申请
5. **交接单** - 工作交接单管理

## 技术架构

### 后端技术栈
- **框架**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy
- **数据库**: PostgreSQL
- **数据验证**: Pydantic

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI组件**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia

## 数据库设计

### 1. 报销申请表 (baoxiao_shenqing)
```sql
- id: UUID主键
- shenqing_bianhao: 申请编号 (BX202411110001)
- shenqing_ren_id: 申请人ID
- baoxiao_leixing: 报销类型
- baoxiao_jine: 报销金额
- baoxiao_shijian: 报销事项发生时间
- baoxiao_yuanyin: 报销原因说明
- fujian_lujing: 附件路径
- shenhe_zhuangtai: 审核状态 (daishehe/shenhezhong/tongguo/jujue)
- shenhe_liucheng_id: 审核流程ID
```

### 2. 请假申请表 (qingjia_shenqing)
```sql
- id: UUID主键
- shenqing_bianhao: 申请编号 (QJ202411110001)
- shenqing_ren_id: 申请人ID
- qingjia_leixing: 请假类型
- kaishi_shijian: 开始时间
- jieshu_shijian: 结束时间
- qingjia_tianshu: 请假天数
- qingjia_yuanyin: 请假原因
- shenhe_zhuangtai: 审核状态
```

### 3. 对外付款申请表 (duiwai_fukuan_shenqing)
```sql
- id: UUID主键
- shenqing_bianhao: 申请编号 (FK202411110001)
- fukuan_duixiang: 付款对象
- fukuan_jine: 付款金额
- fukuan_yuanyin: 付款原因
- fukuan_fangshi: 付款方式
- shoukuan_zhanghu: 收款账户信息
- fukuan_zhuangtai: 付款状态
```

### 4. 采购申请表 (caigou_shenqing)
```sql
- id: UUID主键
- shenqing_bianhao: 申请编号 (CG202411110001)
- caigou_mingcheng: 采购物品名称
- caigou_shuliang: 采购数量
- yugu_jine: 预估金额
- shiji_jine: 实际金额
- caigou_zhuangtai: 采购状态
```

### 5. 工作交接单表 (gongzuo_jiaojie)
```sql
- id: UUID主键
- jiaojie_bianhao: 交接编号 (JJ202411110001)
- jiaojie_ren_id: 交接人ID
- jieshou_ren_id: 接收人ID
- jiaojie_neirong: 交接内容 (JSONB)
- wenjian_qingdan: 文件清单 (JSONB)
- shebei_qingdan: 设备清单 (JSONB)
- jiaojie_zhuangtai: 交接状态
```

## 后端实现

### 目录结构
```
packages/backend/src/
├── models/bangong_guanli/          # 数据模型
│   ├── __init__.py
│   ├── baoxiao_shenqing.py
│   ├── qingjia_shenqing.py
│   ├── duiwai_fukuan_shenqing.py
│   ├── caigou_shenqing.py
│   └── gongzuo_jiaojie.py
├── schemas/bangong_guanli/         # 数据验证模式
│   ├── __init__.py
│   ├── baoxiao_schemas.py
│   ├── qingjia_schemas.py
│   ├── duiwai_fukuan_schemas.py
│   ├── caigou_schemas.py
│   └── gongzuo_jiaojie_schemas.py
├── services/bangong_guanli/        # 业务逻辑层
│   ├── __init__.py
│   ├── baoxiao_service.py
│   ├── qingjia_service.py
│   ├── duiwai_fukuan_service.py
│   ├── caigou_service.py
│   └── gongzuo_jiaojie_service.py
└── api/api_v1/endpoints/bangong_guanli/  # API端点
    ├── __init__.py
    ├── baoxiao.py
    ├── qingjia.py
    ├── duiwai_fukuan.py
    ├── caigou.py
    └── gongzuo_jiaojie.py
```

### API端点

#### 报销申请
- `POST /api/v1/office/reimbursement` - 创建报销申请
- `GET /api/v1/office/reimbursement` - 获取报销申请列表
- `GET /api/v1/office/reimbursement/my` - 获取我的报销申请
- `GET /api/v1/office/reimbursement/{id}` - 获取报销申请详情
- `PUT /api/v1/office/reimbursement/{id}` - 更新报销申请
- `DELETE /api/v1/office/reimbursement/{id}` - 删除报销申请
- `POST /api/v1/office/reimbursement/{id}/submit` - 提交审批

#### 请假申请
- `POST /api/v1/office/leave` - 创建请假申请
- `GET /api/v1/office/leave` - 获取请假申请列表
- `GET /api/v1/office/leave/{id}` - 获取请假申请详情
- `PUT /api/v1/office/leave/{id}` - 更新请假申请
- `DELETE /api/v1/office/leave/{id}` - 删除请假申请

#### 对外付款申请
- `POST /api/v1/office/payment` - 创建付款申请
- `GET /api/v1/office/payment` - 获取付款申请列表
- `GET /api/v1/office/payment/{id}` - 获取付款申请详情
- `PUT /api/v1/office/payment/{id}` - 更新付款申请
- `DELETE /api/v1/office/payment/{id}` - 删除付款申请

#### 采购申请
- `POST /api/v1/office/procurement` - 创建采购申请
- `GET /api/v1/office/procurement` - 获取采购申请列表
- `GET /api/v1/office/procurement/{id}` - 获取采购申请详情
- `PUT /api/v1/office/procurement/{id}` - 更新采购申请
- `DELETE /api/v1/office/procurement/{id}` - 删除采购申请

#### 工作交接单
- `POST /api/v1/office/handover` - 创建交接单
- `GET /api/v1/office/handover` - 获取交接单列表
- `GET /api/v1/office/handover/{id}` - 获取交接单详情
- `PUT /api/v1/office/handover/{id}` - 更新交接单
- `DELETE /api/v1/office/handover/{id}` - 删除交接单

## 前端实现

### 目录结构
```
packages/frontend/src/
├── api/office/                     # API接口封装
│   ├── index.ts
│   ├── reimbursement.ts
│   └── leave.ts
└── views/office/                   # 页面组件
    ├── ReimbursementList.vue
    ├── LeaveList.vue
    ├── PaymentApplicationList.vue
    ├── ProcurementList.vue
    └── HandoverList.vue
```

### 路由配置
```typescript
{
  path: '/office',
  children: [
    { path: 'reimbursement', component: ReimbursementList },
    { path: 'leave', component: LeaveList },
    { path: 'payment', component: PaymentApplicationList },
    { path: 'procurement', component: ProcurementList },
    { path: 'handover', component: HandoverList }
  ]
}
```

### 菜单配置
在MainLayout.vue中添加了"办公管理"主菜单，包含5个子菜单项。

## 权限配置

每个模块需要配置以下权限：
- `office:baoxiao:menu` - 报销菜单访问权限
- `office:baoxiao:read` - 查看报销申请
- `office:baoxiao:create` - 创建报销申请
- `office:baoxiao:update` - 修改报销申请
- `office:baoxiao:delete` - 删除报销申请
- `office:baoxiao:approve` - 审批报销申请

（其他模块类似）

## 数据库迁移

迁移脚本位于: `packages/backend/migrations/create_bangong_guanli_tables.sql`

执行迁移:
```bash
cd packages/backend
PGPASSWORD=postgres psql -h localhost -U postgres -d dailijizhang -f migrations/create_bangong_guanli_tables.sql
```

## 后续开发建议

1. **完善表单页面**: 为每个模块创建完整的新建/编辑表单页面
2. **详情页面**: 创建详情页面，显示申请详情和审批流程
3. **审批流程集成**: 集成现有的审批流程引擎
4. **文件上传**: 实现附件上传功能
5. **通知功能**: 审批通过/拒绝时发送通知
6. **数据统计**: 添加统计报表功能
7. **移动端适配**: 开发移动端页面
8. **单元测试**: 编写单元测试和集成测试

## 注意事项

1. 所有申请编号自动生成，格式为：前缀 + 日期 + 4位序号
2. 审核状态流转：daishehe → shenhezhong → tongguo/jujue
3. 只有待审核状态的申请才能修改和删除
4. 所有金额字段使用Decimal类型，精度为15,2
5. 使用软删除机制，is_deleted字段标记删除状态

## 开发完成情况

✅ 数据库设计
✅ 后端数据模型
✅ 后端Schema定义
✅ 后端Service层
✅ 后端API端点
✅ 前端菜单配置
✅ 前端路由配置
✅ 前端API封装
✅ 前端页面（报销申请列表页完整实现，其他页面占位）
✅ 数据库迁移脚本

## 联系方式

如有问题，请联系开发团队。

