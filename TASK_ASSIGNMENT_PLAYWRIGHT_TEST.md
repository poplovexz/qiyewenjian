# 工单任务项分配功能 - Playwright 自动化测试

## 🎯 测试概述

已创建完整的 Playwright 端到端测试，用于验证工单任务项分配功能的前端UI交互流程。

---

## 📁 已创建的文件

### **1. 测试脚本**
- **文件**: `tests/e2e/test_task_item_assignment.spec.ts`
- **说明**: 完整的 Playwright 测试脚本，包含10个测试步骤
- **功能**: 
  - 自动登录系统
  - 导航到工单详情页
  - 分配任务项给执行人
  - 验证分配结果
  - 测试重新分配功能
  - 自动截图保存

### **2. Playwright 配置**
- **文件**: `playwright.config.ts`
- **说明**: Playwright 测试配置文件
- **配置**:
  - 测试目录: `./tests/e2e`
  - 超时时间: 60秒
  - 浏览器: Chromium
  - 视口大小: 1920x1080
  - 失败时自动截图和录像

### **3. 测试文档**
- **文件**: `tests/e2e/README.md`
- **说明**: 详细的测试说明文档
- **内容**:
  - 测试流程说明
  - 运行方法
  - 截图说明
  - 故障排查指南
  - 预期结果示例

### **4. 运行脚本**
- **文件**: `run-task-assignment-test.sh`
- **说明**: 一键运行测试的 Shell 脚本
- **功能**:
  - 自动检查 Playwright 安装
  - 检查后端服务状态
  - 检查前端服务状态
  - 创建截图目录
  - 运行测试
  - 显示测试结果

---

## 🚀 快速开始

### **第一步：安装 Playwright**

```bash
npm install -D @playwright/test
npx playwright install chromium
```

### **第二步：启动服务**

**启动后端**（新终端窗口）：
```bash
cd packages/backend
source venv/bin/activate
python src/main.py
```

**启动前端**（新终端窗口）：
```bash
cd packages/frontend
npm run dev
```

### **第三步：运行测试**

**方式1：使用运行脚本（推荐）**
```bash
# 无头模式运行
./run-task-assignment-test.sh

# UI模式运行（可视化界面）
./run-task-assignment-test.sh --ui

# 显示浏览器窗口运行
./run-task-assignment-test.sh --headed

# 调试模式运行
./run-task-assignment-test.sh --debug
```

**方式2：直接使用 Playwright**
```bash
# 运行测试
npx playwright test tests/e2e/test_task_item_assignment.spec.ts

# UI模式（推荐）
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --ui

# 显示浏览器
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --headed

# 调试模式
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --debug
```

### **第四步：查看结果**

```bash
# 查看HTML报告
npx playwright show-report

# 查看截图
ls -la screenshots/
```

---

## 📝 测试流程详解

### **完整测试步骤（10步）**

1. **登录系统**
   - 访问登录页面
   - 输入用户名和密码
   - 验证登录成功

2. **导航到服务工单列表**
   - 访问工单列表页面
   - 验证页面加载成功

3. **打开工单详情**
   - 点击第一个工单的"查看"按钮
   - 验证详情页面打开

4. **查看任务项列表**
   - 读取所有任务项信息
   - 显示任务项名称和当前执行人

5. **打开分配对话框**
   - 点击第一个任务项的"分配"按钮
   - 验证对话框打开

6. **选择执行人**
   - 打开执行人下拉框
   - 选择第一个执行人
   - 验证选择成功

7. **确认分配**
   - 点击"确定"按钮
   - 验证成功提示显示
   - 验证对话框关闭

8. **验证分配结果**
   - 检查任务项列表
   - 验证执行人已更新

9. **验证操作日志**
   - 滚动到日志区域
   - 验证存在任务分配日志

10. **测试重新分配**
    - 点击"重新分配"按钮
    - 选择不同的执行人
    - 验证重新分配成功

---

## 📸 自动截图

测试过程中会自动保存以下截图到 `screenshots/` 目录：

| 截图文件 | 说明 |
|---------|------|
| `01-login-success.png` | 登录成功 |
| `02-service-orders-list.png` | 服务工单列表 |
| `03-service-order-detail.png` | 工单详情页面 |
| `04-task-items-list.png` | 任务项列表 |
| `05-assign-dialog-opened.png` | 分配对话框打开 |
| `06-executor-selected.png` | 执行人已选择 |
| `07-assignment-success.png` | 分配成功 |
| `08-assignment-verified.png` | 分配结果验证 |
| `09-operation-logs.png` | 操作日志 |
| `10-reassignment-success.png` | 重新分配成功 |

---

## ✅ 验证点

### **UI验证**
- ✅ 任务项表格显示"执行人"列
- ✅ 任务项表格显示"分配"/"重新分配"按钮
- ✅ 分配对话框正确打开和关闭
- ✅ 执行人下拉框显示所有可选用户
- ✅ 分配成功后显示成功提示

### **数据验证**
- ✅ 分配后执行人信息正确显示
- ✅ 重新分配后执行人信息更新
- ✅ 操作日志记录分配操作

### **交互验证**
- ✅ 点击分配按钮打开对话框
- ✅ 选择执行人后可以确认
- ✅ 确认后对话框关闭
- ✅ 页面自动刷新显示最新数据

---

## 🐛 故障排查

### **常见问题**

**1. 测试失败：服务未运行**
```bash
# 检查后端服务
curl http://localhost:8000/api/v1/health

# 检查前端服务
curl http://localhost:5174
```

**2. 测试失败：数据库未迁移**
```bash
# 检查数据库字段
PGPASSWORD=password psql -h localhost -U postgres -d proxy_db -c "
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'fuwu_gongdan_xiangmu' 
  AND column_name = 'zhixing_ren_id';
"
```

**3. 测试失败：没有工单数据**
```bash
# 检查工单数量
PGPASSWORD=password psql -h localhost -U postgres -d proxy_db -c "
SELECT COUNT(*) FROM fuwu_gongdan WHERE is_deleted = 'N';
"
```

**4. 元素定位失败**
```bash
# 以调试模式运行，逐步检查
npx playwright test --debug
```

### **调试技巧**

```bash
# 1. UI模式 - 可视化调试（推荐）
npx playwright test --ui

# 2. 显示浏览器窗口
npx playwright test --headed

# 3. 调试模式 - 逐步执行
npx playwright test --debug

# 4. 录制操作 - 生成代码
npx playwright codegen http://localhost:5174
```

---

## 📊 预期输出

### **成功运行示例**

```
================================================================================
开始测试：工单任务项分配功能
================================================================================

【步骤1】登录系统...
✅ 登录成功

【步骤2】导航到服务工单列表...
✅ 成功打开服务工单列表页面

【步骤3】查找并打开一个工单...
✅ 找到 5 个工单
✅ 成功打开工单详情页面

【步骤4】查看任务项列表...
✅ 找到 5 个任务项

任务项列表：
   1. 建账设置 - 执行人: 未分配
   2. 凭证录入 - 执行人: 未分配
   3. 账务处理 - 执行人: 未分配
   4. 报表编制 - 执行人: 未分配
   5. 纳税申报 - 执行人: 未分配

【步骤5】分配第一个任务项...
✅ 找到 5 个分配按钮
✅ 分配对话框已打开

【步骤6】选择执行人...
✅ 找到 5 个可选执行人

可选执行人：
   1. 财务张三 (caiwu001)
   2. 业务李四 (yewu001)
   3. 系统管理员 (admin)
   4. 张业务 (salesperson1)
   5. 李财务 (finance1)

✅ 已选择执行人: 财务张三 (caiwu001)

【步骤7】确认分配...
✅ 分配成功提示已显示
✅ 分配对话框已关闭

【步骤8】验证分配结果...

更新后的任务项列表：
   1. 建账设置 - 执行人: 财务张三
   2. 凭证录入 - 执行人: 未分配
   3. 账务处理 - 执行人: 未分配
   4. 报表编制 - 执行人: 未分配
   5. 纳税申报 - 执行人: 未分配

✅ 第一个任务项已成功分配给: 财务张三

【步骤9】验证操作日志...
✅ 找到 1 条任务分配日志
   最新日志: 任务项「建账设置」分配给「财务张三」

【步骤10】测试重新分配功能...
✅ 找到"重新分配"按钮
✅ 重新分配对话框已打开
✅ 已选择新的执行人: 业务李四 (yewu001)
✅ 重新分配成功

================================================================================
✅ 测试完成！所有步骤执行成功
================================================================================

测试总结：
  ✅ 登录系统
  ✅ 打开服务工单列表
  ✅ 打开工单详情
  ✅ 查看任务项列表
  ✅ 分配任务项
  ✅ 验证分配结果
  ✅ 验证操作日志
  ✅ 测试重新分配

截图已保存到 screenshots/ 目录
================================================================================
```

---

## 🎯 总结

### **已完成**

✅ **Playwright 测试脚本**: 完整的10步测试流程  
✅ **配置文件**: Playwright 配置和测试设置  
✅ **测试文档**: 详细的使用说明和故障排查  
✅ **运行脚本**: 一键运行测试的便捷脚本  
✅ **自动截图**: 每个关键步骤自动保存截图  

### **测试覆盖**

- ✅ 用户登录流程
- ✅ 页面导航和加载
- ✅ 任务项列表显示
- ✅ 分配对话框交互
- ✅ 执行人选择
- ✅ 分配确认
- ✅ 结果验证
- ✅ 日志记录
- ✅ 重新分配功能

### **下一步**

1. **运行测试**：使用 `./run-task-assignment-test.sh --ui` 运行测试
2. **查看结果**：检查截图和HTML报告
3. **验收功能**：确认所有功能正常工作
4. **部署上线**：功能验收通过后可以部署

---

**测试创建时间**: 2025年11月5日  
**测试工具**: Playwright  
**测试类型**: 端到端UI自动化测试  
**测试状态**: ✅ 已完成，可以运行

