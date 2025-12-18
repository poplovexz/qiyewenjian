---
type: "always_apply"
---

# AI 代码规范 (Augment Agent 自律准则)

> 此规范用于约束 AI 在本项目中生成的代码质量，避免产生 DeepSource 等静态分析工具报告的问题。

## 一、Python 代码规范

### 1.1 异常处理 (FLK-E722)

```python
# ❌ 错误：裸 except
try:
    do_something()
except:
    pass

# ✅ 正确：指定异常类型
try:
    do_something()
except (ValueError, TypeError, KeyError) as e:
    logger.error(f"操作失败: {e}")
```

### 1.2 生成器默认值 (PTC-W0063)

```python
# ❌ 错误：next() 无默认值
db = next(get_db())

# ✅ 正确：添加默认值并检查
db = next(get_db(), None)
if db is None:
    raise RuntimeError("无法获取数据库连接")
```

### 1.3 导入规范 (PYL-W0404)

```python
# ❌ 错误：重复导入
from sqlalchemy import Column, String, String

# ✅ 正确：检查后再导入，不重复
from sqlalchemy import Column, String
```

### 1.4 subprocess 调用 (PYL-W1510)

```python
# ❌ 错误：缺少 check 参数
subprocess.run(["ls", "-la"])

# ✅ 正确：明确指定 check 参数
subprocess.run(["ls", "-la"], check=False, capture_output=True)
```

### 1.5 退出函数 (PYL-R1722)

```python
# ❌ 错误：使用 exit()
exit(1)

# ✅ 正确：使用 sys.exit()
import sys
sys.exit(1)
```

### 1.6 循环变量命名 (FLK-F402)

```python
# ❌ 错误：循环变量覆盖导入
from fastapi import status
for status in statuses:  # 覆盖了 status 导入
    pass

# ✅ 正确：使用不同的变量名
for item_status in statuses:
    pass
```

### 1.7 受保护成员 (PYL-W0212)

```python
# ❌ 错误：外部访问受保护方法
result = service._internal_method()

# ✅ 正确：将方法改为公共或创建公共包装器
result = service.public_method()
```

## 二、JavaScript/Vue 代码规范

### 2.1 console 调用 (JS-0002)

```javascript
// ❌ 错误：生产代码中使用 console
console.log("调试信息");

// ✅ 正确：使用日志服务或移除
logger.debug("调试信息");
// 或者在开发环境中条件输出
if (import.meta.env.DEV) console.log("调试信息");
```

### 2.2 XSS 防护 (JS-0693)

```vue
<!-- ❌ 错误：直接使用 v-html -->
<div v-html="userContent"></div>

<!-- ✅ 正确：使用 DOMPurify 清理 -->
<div v-html="sanitizeHtml(userContent)"></div>

<script>
import DOMPurify from "dompurify";
const sanitizeHtml = (html) => DOMPurify.sanitize(html);
</script>
```

### 2.3 Props 默认值 (JS-0682)

```javascript
// ❌ 错误：Props 无默认值
defineProps({
  title: String,
  count: Number,
});

// ✅ 正确：提供默认值
defineProps({
  title: { type: String, default: "" },
  count: { type: Number, default: 0 },
});
```

## 三、安全规范

### 3.1 路径验证 (PTC-W6004)

```python
# ❌ 错误：直接使用用户输入的路径
file_path = user_input
open(file_path)

# ✅ 正确：验证路径在允许范围内
import os
base_dir = "/var/www/uploads"
file_path = os.path.normpath(os.path.join(base_dir, user_input))
if not file_path.startswith(base_dir):
    raise ValueError("非法路径")
```

### 3.2 XML 解析 (BAN-B314)

```python
# ❌ 错误：使用不安全的 XML 解析
from xml.etree import ElementTree

# ✅ 正确：使用 defusedxml
from defusedxml.ElementTree import parse, fromstring
```

### 3.3 Shell 命令 (BAN-B602)

```python
# ❌ 错误：shell=True
subprocess.run(command, shell=True)

# ✅ 正确：使用列表参数
subprocess.run(["git", "status"], check=False)
```

## 四、提交前检查清单

在提交代码前，AI 必须自检：

- [ ] 所有 `except` 都指定了异常类型
- [ ] 所有 `next()` 都有默认值
- [ ] 没有重复的 import 语句
- [ ] `subprocess.run` 有 `check` 参数
- [ ] 使用 `sys.exit()` 而非 `exit()`
- [ ] 循环变量不覆盖导入的模块名
- [ ] 不直接访问 `_` 开头的受保护成员
- [ ] 生产代码无 `console.log/error`
- [ ] `v-html` 内容已用 DOMPurify 清理
- [ ] Props 都有默认值
- [ ] 文件路径已验证防止遍历攻击
- [ ] XML 使用 defusedxml 解析
- [ ] 不使用 `shell=True`
