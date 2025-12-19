# 共享模块规范 (SHARED_MODULES.md)

> ⚠️ **本文件由 MCP (Model Context Protocol) v2.0 管理**
>
> **设计状态**: 🔒 已冻结 (FROZEN)
> **冻结时间**: 2025-12-19T16:30:00Z

---

## 🎯 核心原则

### 1. DRY 原则 (Don't Repeat Yourself)

**规则**: 任何功能在编写前，必须先检查是否已存在可复用的实现。

**执行流程**:
```
需要某功能 → 检查共享模块 → 存在？ → 直接复用
                           ↓
                         不存在？ → 检查是否通用 → 是 → 创建共享模块
                                                  ↓
                                                 否 → 写在业务模块内
```

### 2. 复用优先级

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1️⃣ | `src/core/` | 核心基础设施 |
| 2️⃣ | `src/utils/` | 工具函数 |
| 3️⃣ | 已有业务模块 | 可提取的公共逻辑 |
| 4️⃣ | 新建 | 确认不存在后才新建 |

---

## 📦 后端共享模块

### 核心基础设施 (`src/core/`)

| 模块 | 文件 | 用途 | 使用方式 |
|------|------|------|----------|
| **配置** | `config.py` | 环境变量、系统配置 | `from src.core.config import settings` |
| **数据库** | `database.py` | 数据库连接、Session | `from src.core.database import get_db` |
| **异常** | `exceptions.py` | 自定义异常类 | `from src.core.exceptions import BusinessError` |
| **日志** | `logging.py` | 统一日志 | `from src.core.logging import get_logger` |
| **缓存** | `cache_decorator.py` | Redis 缓存装饰器 | `@cache(ttl=300)` |
| **中间件** | `middleware.py` | 请求日志、异常处理 | 自动加载 |
| **事件** | `events.py` | 事件发布订阅 | `from src.core.events import event_bus` |

### 安全模块 (`src/core/security/`)

| 模块 | 文件 | 用途 | 使用方式 |
|------|------|------|----------|
| **JWT** | `jwt_handler.py` | Token 生成验证 | `from src.core.security.jwt_handler import create_token` |
| **密码** | `password_handler.py` | 密码哈希验证 | `from src.core.security.password_handler import hash_password` |
| **权限** | `permissions.py` | 权限校验依赖 | `Depends(require_permission("xxx"))` |
| **RBAC** | `rbac_handler.py` | 角色权限管理 | `from src.core.security.rbac_handler import check_permission` |
| **加密** | `encryption.py` | 数据加密解密 | `from src.core.security.encryption import encrypt` |

### 通用 Mixins (`src/core/mixins.py`)

```python
# 已有的 Mixins，新模型应继承使用
class TimestampMixin:       # 创建时间、更新时间
class SoftDeleteMixin:      # 软删除
class AuditMixin:           # 操作审计
class UUIDMixin:            # UUID 主键
```

### 基础模型 (`src/models/base.py`)

```python
# 所有模型必须继承 Base
from src.models.base import Base

class MyModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "my_table"
    ...
```

---

## 🎨 前端共享模块

### 工具函数 (`src/utils/`)

| 模块 | 文件 | 用途 | 使用方式 |
|------|------|------|----------|
| **请求** | `request.ts` | HTTP 请求封装 | `import request from '@/utils/request'` |
| **Token** | `tokenManager.ts` | Token 管理 | `import { getToken } from '@/utils/tokenManager'` |
| **权限** | `permissions.ts` | 权限检查 | `import { hasPermission } from '@/utils/permissions'` |
| **日期** | `date.ts` | 日期格式化 | `import { formatDate } from '@/utils/date'` |
| **格式化** | `format.ts` | 数据格式化 | `import { formatMoney } from '@/utils/format'` |
| **缓存** | `cache.ts` | 本地缓存 | `import { setCache, getCache } from '@/utils/cache'` |
| **安全** | `sanitize.ts` | XSS 过滤 | `import { sanitizeHtml } from '@/utils/sanitize'` |

### UI 组件 (`src/components/ui/`)

| 组件 | 文件 | 用途 |
|------|------|------|
| **ModernButton** | `ModernButton.vue` | 统一按钮样式 |
| **ModernCard** | `ModernCard.vue` | 卡片容器 |
| **ModernInput** | `ModernInput.vue` | 输入框 |
| **ModernTable** | `ModernTable.vue` | 数据表格 |
| **StatCard** | `StatCard.vue` | 统计卡片 |

### 业务组件 (`src/components/`)

| 目录 | 用途 |
|------|------|
| `audit/` | 审核相关组件 |
| `notification/` | 通知组件 |
| `payment/` | 支付组件 |
| `product/` | 产品组件 |
| `user/` | 用户组件 |
| `xiansuo/` | 线索组件 |

### Composables (`src/composables/`)

| 模块 | 文件 | 用途 |
|------|------|------|
| **useAuth** | `useAuth.ts` | 认证相关逻辑 |

---

## 🚫 禁止重复的模式

### 1. HTTP 请求

```typescript
// ❌ 禁止：直接使用 axios
import axios from 'axios'
axios.get('/api/xxx')

// ✅ 正确：使用封装的 request
import request from '@/utils/request'
request.get('/api/xxx')
```

### 2. 权限校验

```python
# ❌ 禁止：自己写权限校验逻辑
if current_user.has_permission("xxx"):
    ...

# ✅ 正确：使用依赖注入
@router.get("/")
async def get_list(
    _: bool = Depends(require_permission("xxx:view"))
):
    ...


---

## 🤖 AI 编码检查清单

### 编码前必查

在编写任何代码前，AI **必须**执行以下检查：

```
□ 1. 检查 src/core/ 是否有可复用的基础设施
□ 2. 检查 src/utils/ 是否有可复用的工具函数
□ 3. 检查 src/components/ui/ 是否有可复用的 UI 组件
□ 4. 检查相似业务模块是否有可参考的实现
□ 5. 如果需要新建共享模块，确认是否真的通用
```

### 代码复用查询命令

```bash
# 查找后端类似实现
grep -r "关键词" packages/backend/src/core/
grep -r "关键词" packages/backend/src/services/

# 查找前端类似实现
grep -r "关键词" packages/frontend/src/utils/
grep -r "关键词" packages/frontend/src/components/
```

### 复用决策树

```
要写的功能
    │
    ├─ 是基础设施？(日志/缓存/数据库/认证)
    │      └─ 必须使用 src/core/ 中已有的
    │
    ├─ 是工具函数？(格式化/验证/转换)
    │      └─ 先查 src/utils/，不存在则添加到 utils
    │
    ├─ 是 UI 组件？
    │      └─ 先查 src/components/ui/，不存在则添加
    │
    └─ 是业务逻辑？
           └─ 写在对应业务模块内，提取公共部分到 service
```

---

## 📋 共享模块注册表

### 当需要以下功能时，使用对应模块：

| 需要做什么 | 后端模块 | 前端模块 |
|-----------|---------|---------|
| 发送 HTTP 请求 | `httpx` (直接用) | `@/utils/request` |
| 日志记录 | `src/core/logging` | `console` (开发) / Sentry (生产) |
| 缓存数据 | `src/core/cache_decorator` | `@/utils/cache` |
| 密码哈希 | `src/core/security/password_handler` | - |
| Token 处理 | `src/core/security/jwt_handler` | `@/utils/tokenManager` |
| 权限校验 | `src/core/security/permissions` | `@/utils/permissions` |
| 异常处理 | `src/core/exceptions` | try/catch + ElMessage |
| 日期格式化 | `datetime` / `dateutil` | `@/utils/date` |
| 金额格式化 | `Decimal` | `@/utils/format` |
| XSS 过滤 | - | `@/utils/sanitize` |
| 数据库操作 | `src/core/database` | - |
| 配置读取 | `src/core/config` | `import.meta.env` |

---

## 🔐 DESIGN_FREEZE

```yaml
design_locked: true
frozen_at: "2025-12-19T16:30:00Z"
```

**冻结后禁止**:
- ❌ 删除现有共享模块
- ❌ 修改共享模块的接口签名
- ❌ 在业务代码中重复共享模块的功能

**冻结后允许**:
- ✅ 向共享模块添加新功能
- ✅ 修复共享模块的 bug
- ✅ 优化共享模块的性能

