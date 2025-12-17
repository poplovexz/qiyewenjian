# 移动端H5应用 - 需求分析报告

**生成时间**: 2025-11-06  
**项目**: 服务人员任务管理移动端应用

---

## 📋 目录

1. [现有后端API清单](#1-现有后端api清单)
2. [现有数据库表结构](#2-现有数据库表结构)
3. [现有前端功能清单](#3-现有前端功能清单)
4. [功能缺口分析](#4-功能缺口分析)
5. [需要新增的API列表](#5-需要新增的api列表)
6. [需要修改的数据库表](#6-需要修改的数据库表)
7. [移动端项目技术架构建议](#7-移动端项目技术架构建议)
8. [开发步骤建议](#8-开发步骤建议)

---

## 1. 现有后端API清单

### 1.1 服务工单管理API

**基础路径**: `/api/v1/service-orders`

| 端点 | 方法 | 功能 | 参数 | 响应 |
|------|------|------|------|------|
| `/` | POST | 创建服务工单 | FuwuGongdanCreate | FuwuGongdanDetailResponse |
| `/from-contract/{hetong_id}` | POST | 基于合同创建工单 | hetong_id | FuwuGongdanDetailResponse |
| `/` | GET | 获取工单列表 | page, size, 筛选条件 | FuwuGongdanListResponse |
| `/{gongdan_id}` | GET | 获取工单详情 | gongdan_id | FuwuGongdanDetailResponse |
| `/{gongdan_id}` | PUT | 更新工单 | gongdan_id, FuwuGongdanUpdate | FuwuGongdanDetailResponse |
| `/{gongdan_id}/assign` | POST | 分配工单 | gongdan_id, zhixing_ren_id | FuwuGongdanDetailResponse |
| `/{gongdan_id}/start` | POST | 开始工单 | gongdan_id | FuwuGongdanDetailResponse |
| `/{gongdan_id}/complete` | POST | 完成工单 | gongdan_id, wancheng_qingkuang | FuwuGongdanDetailResponse |
| `/{gongdan_id}/cancel` | POST | 取消工单 | gongdan_id, cancel_reason | FuwuGongdanDetailResponse |
| `/{gongdan_id}/comments` | POST | 添加工单评论 | gongdan_id, FuwuGongdanRizhiCreate | FuwuGongdanRizhiResponse |
| `/statistics/overview` | GET | 获取工单统计 | kehu_id?, zhixing_ren_id? | FuwuGongdanStatistics |
| `/{gongdan_id}/items/{item_id}/assign` | POST | 分配任务项 | gongdan_id, item_id, zhixing_ren_id | FuwuGongdanXiangmuResponse |

### 1.2 工单列表查询参数

```typescript
{
  page: number              // 页码
  size: number              // 每页数量
  gongdan_bianhao?: string  // 工单编号
  gongdan_biaoti?: string   // 工单标题
  fuwu_leixing?: string     // 服务类型
  gongdan_zhuangtai?: string // 工单状态
  youxian_ji?: string       // 优先级
  zhixing_ren_id?: string   // 执行人ID ✅ 支持按执行人查询
  kehu_id?: string          // 客户ID
  hetong_id?: string        // 合同ID
  is_overdue?: boolean      // 是否逾期
}
```

### 1.3 工单状态枚举

```python
gongdan_zhuangtai:
  - created: 已创建
  - assigned: 已分配
  - in_progress: 进行中
  - pending_review: 待审核
  - completed: 已完成
  - cancelled: 已取消
```

### 1.4 任务项状态枚举

```python
xiangmu_zhuangtai:
  - pending: 待处理
  - in_progress: 进行中
  - completed: 已完成
  - skipped: 已跳过
```

---

## 2. 现有数据库表结构

### 2.1 服务工单表 (fuwu_gongdan)

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | String(36) | 主键 | UUID |
| hetong_id | String(36) | 关联合同ID | 外键 |
| kehu_id | String(36) | 客户ID | 外键 |
| zhixing_ren_id | String(36) | 执行人ID | 外键，可为空 |
| gongdan_bianhao | String(50) | 工单编号 | 唯一 |
| gongdan_biaoti | String(200) | 工单标题 | 必填 |
| gongdan_miaoshu | Text | 工单描述 | 可为空 |
| fuwu_leixing | String(50) | 服务类型 | 必填 |
| youxian_ji | String(20) | 优先级 | 默认medium |
| gongdan_zhuangtai | String(20) | 工单状态 | 默认created |
| jihua_kaishi_shijian | DateTime | 计划开始时间 | 可为空 |
| jihua_jieshu_shijian | DateTime | 计划结束时间 | 必填 |
| shiji_kaishi_shijian | DateTime | 实际开始时间 | 可为空 |
| shiji_jieshu_shijian | DateTime | 实际结束时间 | 可为空 |
| fenpei_shijian | DateTime | 分配时间 | 可为空 |
| fenpei_ren_id | String(36) | 分配人ID | 可为空 |
| fenpei_beizhu | String(500) | 分配备注 | 可为空 |
| wancheng_qingkuang | Text | 完成情况说明 | 可为空 |
| jiaofei_wenjian | Text | 交付文件列表(JSON) | 可为空 |
| kehu_queren_shijian | DateTime | 客户确认时间 | 可为空 |
| kehu_pingjia | String(20) | 客户评价 | 可为空 |
| kehu_pingjia_neirong | Text | 客户评价内容 | 可为空 |

### 2.2 服务工单任务项表 (fuwu_gongdan_xiangmu)

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | String(36) | 主键 | UUID |
| gongdan_id | String(36) | 工单ID | 外键 |
| xiangmu_mingcheng | String(200) | 项目名称 | 必填 |
| xiangmu_miaoshu | Text | 项目描述 | 可为空 |
| xiangmu_zhuangtai | String(20) | 项目状态 | 默认pending |
| paixu | Integer | 排序 | 默认0 |
| jihua_gongshi | Numeric(5,2) | 计划工时 | 可为空 |
| shiji_gongshi | Numeric(5,2) | 实际工时 | 可为空 |
| kaishi_shijian | DateTime | 开始时间 | 可为空 |
| jieshu_shijian | DateTime | 结束时间 | 可为空 |
| beizhu | Text | 备注 | 可为空 |
| **zhixing_ren_id** | **String(36)** | **执行人ID** | **✅ 已支持** |

**关联关系**:
- `zhixing_ren`: relationship("Yonghu", foreign_keys=[zhixing_ren_id])

### 2.3 服务工单日志表 (fuwu_gongdan_rizhi)

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | String(36) | 主键 | UUID |
| gongdan_id | String(36) | 工单ID | 外键 |
| caozuo_leixing | String(50) | 操作类型 | 必填 |
| caozuo_neirong | Text | 操作内容 | 必填 |
| caozuo_ren_id | String(36) | 操作人ID | 必填 |
| fujian_lujing | String(500) | 附件路径 | 可为空 |

**操作类型枚举**:
- created: 创建
- assigned: 分配
- started: 开始
- paused: 暂停
- completed: 完成
- cancelled: 取消
- commented: 评论

---

## 3. 现有前端功能清单

### 3.1 PC端工单管理功能

**文件**: `packages/frontend/src/views/service-orders/ServiceOrderDetail.vue`

✅ **已实现功能**:
1. 工单详情展示
2. 工单基本信息显示
3. 任务项列表展示
4. 任务项执行人显示
5. 任务项分配功能
6. 工单状态管理（分配、开始、完成、取消）
7. 操作日志展示
8. 工单评论功能

### 3.2 任务项分配对话框

**文件**: `packages/frontend/src/views/service-orders/components/AssignTaskItemDialog.vue`

✅ **已实现功能**:
1. 选择执行人
2. 显示任务项信息
3. 调用分配API

### 3.3 Store管理

**文件**: `packages/frontend/src/stores/modules/serviceOrderManagement.ts`

✅ **已实现功能**:
1. 工单列表管理
2. 工单详情管理
3. 工单状态更新
4. 任务项分配
5. 统计信息获取

---

## 4. 功能缺口分析

### 4.1 ✅ 已支持的功能

| 功能 | 后端API | 数据库 | 前端PC |
|------|---------|--------|--------|
| 按执行人查询工单 | ✅ | ✅ | ✅ |
| 按执行人查询任务项 | ❌ | ✅ | ❌ |
| 任务项状态更新 | ❌ | ✅ | ❌ |
| 任务项实际工时记录 | ❌ | ✅ | ❌ |
| 任务项反馈记录 | ❌ | ✅ (beizhu字段) | ❌ |
| 任务项附件上传 | ❌ | ❌ | ❌ |
| 任务项开始/完成 | ❌ | ✅ | ❌ |

### 4.2 ❌ 需要新增的功能

#### 4.2.1 移动端核心功能

1. **按执行人查询任务项列表**
   - 后端API: ❌ 需要新增
   - 数据库: ✅ 已支持 (zhixing_ren_id字段)
   - 说明: 需要新增API端点，支持按执行人ID查询所有分配给该用户的任务项

2. **任务项状态更新**
   - 后端API: ❌ 需要新增
   - 数据库: ✅ 已支持 (xiangmu_zhuangtai字段)
   - 说明: 需要新增API端点，支持更新任务项状态（开始、完成、暂停等）

3. **任务项实际工时记录**
   - 后端API: ❌ 需要新增
   - 数据库: ✅ 已支持 (shiji_gongshi字段)
   - 说明: 需要新增API端点，支持记录任务项的实际工时

4. **任务项反馈记录**
   - 后端API: ❌ 需要新增
   - 数据库: ⚠️ 部分支持 (beizhu字段可用，但建议新增专门的反馈表)
   - 说明: 建议新增任务项反馈表，记录详细的任务执行反馈

5. **任务项附件上传**
   - 后端API: ❌ 需要新增
   - 数据库: ❌ 需要新增字段或关联表
   - 说明: 需要支持任务项附件上传功能

#### 4.2.2 管理端监控功能

1. **任务进度实时查看**
   - 后端API: ✅ 已支持 (通过工单详情API)
   - 前端PC: ✅ 已支持
   - 说明: 无需新增

2. **任务反馈查看**
   - 后端API: ❌ 需要新增 (如果新增反馈表)
   - 前端PC: ❌ 需要新增UI
   - 说明: 需要在工单详情页面显示任务反馈

3. **实际工时与计划工时对比**
   - 后端API: ✅ 已支持 (数据已在响应中)
   - 前端PC: ⚠️ 部分支持 (显示但无对比分析)
   - 说明: 需要增强前端显示，添加对比分析

---

## 5. 需要新增的API列表

### 5.1 任务项查询API

#### 5.1.1 按执行人查询任务项列表

```python
@router.get("/task-items/my-tasks", response_model=FuwuGongdanXiangmuListResponse)
def get_my_task_items(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    xiangmu_zhuangtai: Optional[str] = Query(None),
    gongdan_zhuangtai: Optional[str] = Query(None),
    fuwu_leixing: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取当前用户的任务项列表"""
```

**请求参数**:
```typescript
{
  page: number                    // 页码
  size: number                    // 每页数量
  xiangmu_zhuangtai?: string      // 任务项状态筛选
  gongdan_zhuangtai?: string      // 工单状态筛选
  fuwu_leixing?: string           // 服务类型筛选
}
```

**响应格式**:
```typescript
{
  items: Array<{
    id: string
    gongdan_id: string
    gongdan_bianhao: string
    gongdan_biaoti: string
    kehu_mingcheng: string
    xiangmu_mingcheng: string
    xiangmu_miaoshu: string
    xiangmu_zhuangtai: string
    jihua_gongshi: number
    shiji_gongshi: number
    kaishi_shijian: string
    jieshu_shijian: string
    beizhu: string
  }>
  total: number
  page: number
  size: number
}
```

### 5.2 任务项状态更新API

#### 5.2.1 开始任务项

```python
@router.post("/task-items/{item_id}/start", response_model=FuwuGongdanXiangmuResponse)
def start_task_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """开始执行任务项"""
```

#### 5.2.2 完成任务项

```python
@router.post("/task-items/{item_id}/complete", response_model=FuwuGongdanXiangmuResponse)
def complete_task_item(
    item_id: str,
    shiji_gongshi: Decimal = Query(...),
    beizhu: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """完成任务项"""
```

#### 5.2.3 暂停任务项

```python
@router.post("/task-items/{item_id}/pause", response_model=FuwuGongdanXiangmuResponse)
def pause_task_item(
    item_id: str,
    beizhu: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """暂停任务项"""
```

### 5.3 任务项反馈API (可选)

#### 5.3.1 添加任务项反馈

```python
@router.post("/task-items/{item_id}/feedback", response_model=TaskItemFeedbackResponse)
def add_task_item_feedback(
    item_id: str,
    feedback_data: TaskItemFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """添加任务项反馈"""
```

**请求体**:
```typescript
{
  fankui_neirong: string          // 反馈内容
  fankui_leixing: string          // 反馈类型: progress/issue/question
  fujian_list?: string[]          // 附件列表
}
```

### 5.4 任务项统计API

```python
@router.get("/task-items/statistics", response_model=TaskItemStatistics)
def get_task_item_statistics(
    zhixing_ren_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取任务项统计信息"""
```

**响应格式**:
```typescript
{
  total_count: number
  pending_count: number
  in_progress_count: number
  completed_count: number
  skipped_count: number
  total_jihua_gongshi: number
  total_shiji_gongshi: number
  avg_completion_rate: number
}
```

---

## 6. 需要修改的数据库表

### 6.1 建议新增：任务项反馈表 (fuwu_gongdan_xiangmu_fankui)

```sql
CREATE TABLE fuwu_gongdan_xiangmu_fankui (
    id VARCHAR(36) PRIMARY KEY,
    xiangmu_id VARCHAR(36) NOT NULL,
    fankui_leixing VARCHAR(20) NOT NULL COMMENT '反馈类型: progress/issue/question',
    fankui_neirong TEXT NOT NULL COMMENT '反馈内容',
    fujian_list TEXT COMMENT '附件列表(JSON)',
    fankui_ren_id VARCHAR(36) NOT NULL COMMENT '反馈人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    is_deleted CHAR(1) DEFAULT 'N',
    FOREIGN KEY (xiangmu_id) REFERENCES fuwu_gongdan_xiangmu(id),
    FOREIGN KEY (fankui_ren_id) REFERENCES yonghu(id)
) COMMENT='服务工单任务项反馈表';
```

### 6.2 可选：任务项附件表 (fuwu_gongdan_xiangmu_fujian)

```sql
CREATE TABLE fuwu_gongdan_xiangmu_fujian (
    id VARCHAR(36) PRIMARY KEY,
    xiangmu_id VARCHAR(36) NOT NULL,
    fujian_mingcheng VARCHAR(200) NOT NULL,
    fujian_lujing VARCHAR(500) NOT NULL,
    fujian_daxiao BIGINT COMMENT '文件大小(字节)',
    fujian_leixing VARCHAR(50) COMMENT '文件类型',
    shangchuan_ren_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    is_deleted CHAR(1) DEFAULT 'N',
    FOREIGN KEY (xiangmu_id) REFERENCES fuwu_gongdan_xiangmu(id),
    FOREIGN KEY (shangchuan_ren_id) REFERENCES yonghu(id)
) COMMENT='服务工单任务项附件表';
```

### 6.3 现有表无需修改

✅ `fuwu_gongdan_xiangmu` 表已包含所有必要字段:
- zhixing_ren_id: 执行人ID
- xiangmu_zhuangtai: 任务状态
- shiji_gongshi: 实际工时
- kaishi_shijian: 开始时间
- jieshu_shijian: 结束时间
- beizhu: 备注（可用于简单反馈）

---

## 7. 移动端项目技术架构建议

### 7.1 项目结构

```
packages/
├── backend/          # 现有后端
├── frontend/         # 现有PC前端
└── mobile/           # 新建移动端 ✨
    ├── public/
    ├── src/
    │   ├── api/          # API接口
    │   ├── assets/       # 静态资源
    │   ├── components/   # 公共组件
    │   ├── router/       # 路由配置
    │   ├── stores/       # Pinia状态管理
    │   ├── utils/        # 工具函数
    │   ├── views/        # 页面组件
    │   ├── App.vue
    │   └── main.ts
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

### 7.2 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.x | 前端框架 |
| TypeScript | 5.x | 类型系统 |
| Vite | 5.x | 构建工具 |
| Vant | 4.x | 移动端UI组件库 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| Axios | 1.x | HTTP客户端 |
| Day.js | 1.x | 日期处理 |

### 7.3 核心页面结构

```
views/
├── login/            # 登录页
│   └── index.vue
├── home/             # 首页（任务概览）
│   └── index.vue
├── tasks/            # 任务列表
│   ├── index.vue     # 任务列表页
│   └── detail.vue    # 任务详情页
├── orders/           # 工单列表
│   ├── index.vue     # 工单列表页
│   └── detail.vue    # 工单详情页
└── profile/          # 个人中心
    └── index.vue
```

### 7.4 移动端特性

1. **响应式设计**: 适配不同屏幕尺寸
2. **触摸优化**: 优化触摸交互体验
3. **离线支持**: 使用Service Worker实现离线访问
4. **推送通知**: 支持任务提醒推送
5. **扫码功能**: 支持扫码快速查看工单/任务
6. **拍照上传**: 支持拍照上传任务附件

---

## 8. 开发步骤建议

### 阶段一：后端API开发 (3-5天)

#### Step 1: 创建任务项Service层方法
- [ ] `get_my_task_items()` - 获取我的任务项列表
- [ ] `start_task_item()` - 开始任务项
- [ ] `complete_task_item()` - 完成任务项
- [ ] `pause_task_item()` - 暂停任务项
- [ ] `get_task_item_statistics()` - 获取任务项统计

#### Step 2: 创建Schema定义
- [ ] `TaskItemListResponse` - 任务项列表响应
- [ ] `TaskItemStatistics` - 任务项统计
- [ ] `TaskItemFeedbackCreate` - 任务项反馈创建(可选)
- [ ] `TaskItemFeedbackResponse` - 任务项反馈响应(可选)

#### Step 3: 创建API端点
- [ ] `GET /api/v1/task-items/my-tasks` - 获取我的任务
- [ ] `POST /api/v1/task-items/{item_id}/start` - 开始任务
- [ ] `POST /api/v1/task-items/{item_id}/complete` - 完成任务
- [ ] `POST /api/v1/task-items/{item_id}/pause` - 暂停任务
- [ ] `GET /api/v1/task-items/statistics` - 获取统计

#### Step 4: 数据库迁移(可选)
- [ ] 创建任务项反馈表
- [ ] 创建任务项附件表

#### Step 5: API测试
- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] Postman测试

### 阶段二：移动端项目初始化 (2-3天)

#### Step 1: 创建项目
```bash
cd /var/www/packages
pnpm create vite mobile --template vue-ts
cd mobile
pnpm install
```

#### Step 2: 安装依赖
```bash
pnpm add vant
pnpm add vue-router pinia
pnpm add axios dayjs
pnpm add -D @types/node
pnpm add -D postcss-pxtorem
pnpm add -D autoprefixer
```

#### Step 3: 配置Vite
- [ ] 配置路径别名
- [ ] 配置代理
- [ ] 配置移动端适配
- [ ] 配置环境变量

#### Step 4: 配置路由
- [ ] 创建路由配置
- [ ] 配置路由守卫
- [ ] 配置页面过渡动画

#### Step 5: 配置Pinia
- [ ] 创建Store结构
- [ ] 配置持久化插件

### 阶段三：移动端核心功能开发 (5-7天)

#### Step 1: 用户认证
- [ ] 登录页面
- [ ] Token管理
- [ ] 自动登录

#### Step 2: 任务列表
- [ ] 任务列表页面
- [ ] 任务筛选
- [ ] 下拉刷新
- [ ] 上拉加载

#### Step 3: 任务详情
- [ ] 任务详情页面
- [ ] 任务状态更新
- [ ] 工时记录
- [ ] 反馈提交

#### Step 4: 工单查看
- [ ] 工单列表页面
- [ ] 工单详情页面
- [ ] 任务项列表

#### Step 5: 个人中心
- [ ] 个人信息展示
- [ ] 统计数据展示
- [ ] 退出登录

### 阶段四：PC端功能增强 (2-3天)

#### Step 1: 工单详情页增强
- [ ] 显示任务项反馈
- [ ] 显示实际工时对比
- [ ] 显示任务项附件

#### Step 2: 任务监控面板
- [ ] 创建任务监控页面
- [ ] 实时任务进度展示
- [ ] 任务统计图表

### 阶段五：测试与优化 (3-5天)

#### Step 1: 功能测试
- [ ] 移动端功能测试
- [ ] PC端功能测试
- [ ] 接口测试

#### Step 2: 性能优化
- [ ] 移动端性能优化
- [ ] 图片懒加载
- [ ] 代码分割

#### Step 3: 兼容性测试
- [ ] iOS测试
- [ ] Android测试
- [ ] 不同浏览器测试

#### Step 4: 部署
- [ ] 配置生产环境
- [ ] 部署移动端应用
- [ ] 配置Nginx

---

## 📊 总结

### ✅ 现有基础良好

1. **数据库表结构完善**: `fuwu_gongdan_xiangmu` 表已包含执行人字段和所有必要字段
2. **后端API基础扎实**: 工单管理API已完善，任务项分配功能已实现
3. **前端PC功能完整**: 工单详情、任务项分配等功能已实现

### ⚠️ 需要补充的功能

1. **后端API**: 需要新增5-6个任务项相关API端点
2. **数据库**: 可选新增2个表（反馈表、附件表）
3. **移动端**: 需要从零开始创建移动端项目

### 📅 预估工期

- **后端开发**: 3-5天
- **移动端开发**: 7-10天
- **PC端增强**: 2-3天
- **测试优化**: 3-5天
- **总计**: 15-23天

### 🎯 建议优先级

1. **P0 (必须)**: 后端任务项API + 移动端核心功能
2. **P1 (重要)**: PC端任务监控增强
3. **P2 (可选)**: 任务项反馈表 + 附件功能

---

**报告完成，等待您的确认后开始开发。**

