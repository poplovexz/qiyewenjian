# 完整业务流程 - Playwright 自动化测试

## 🎯 测试目标

这个测试脚本会**自动化执行完整的业务流程**，无需手动创建任何数据：

1. ✅ 登录系统
2. ✅ 创建线索（不需要客户）
3. ✅ 创建报价（包含"公司改制（内转外/外转内）"产品）
4. ✅ 创建合同（关联报价）
5. ✅ 从合同创建工单
6. ✅ 验证任务项从产品步骤加载（应该有6个任务项）
7. ✅ 测试任务项分配功能
8. ✅ 验证分配结果

---

## 🚀 快速开始

### **前置条件**

1. **后端服务运行**：http://localhost:8000
2. **前端服务运行**：http://localhost:5174
3. **数据库中有**：
   - 至少1个用户（admin/123456）
   - "公司改制（内转外/外转内）"产品（产品代码：zengzhi_1_2）
   - 该产品包含6个步骤

### **运行测试**

**Linux**:
```bash
# 运行完整流程测试
./run-task-assignment-test.sh --complete

# 以 UI 模式运行（推荐）
./run-task-assignment-test.sh --complete --ui

# 以显示浏览器模式运行
./run-task-assignment-test.sh --complete --headed

# 以调试模式运行
./run-task-assignment-test.sh --complete --debug
```

**Windows**:
```cmd
REM 运行完整流程测试
npx playwright test tests/e2e/test_complete_workflow.spec.ts

REM 以 UI 模式运行（推荐）
npx playwright test tests/e2e/test_complete_workflow.spec.ts --ui

REM 以显示浏览器模式运行
npx playwright test tests/e2e/test_complete_workflow.spec.ts --headed
```

---

## 📋 测试流程详解

### **步骤1：登录系统**

- 访问登录页面
- 输入用户名：admin
- 输入密码：123456
- 点击"登 录"按钮
- 验证登录成功

### **步骤2：创建线索**

- 访问线索管理页面
- 点击"新增线索"按钮
- 选择线索来源（第一个选项）
- 填写线索标题：`测试线索_时间戳`
- 填写联系人信息（如果需要）
- 保存线索

### **步骤3：创建报价**

- 在线索列表中找到刚创建的线索
- 点击"报价"按钮
- 填写报价名称：`测试报价_时间戳`
- 设置有效期：未来30天
- **添加产品**：
  - 点击"添加产品"
  - 选择"公司改制（内转外/外转内）"产品
  - 数量：1
  - 单价：5000
- 保存报价

### **步骤4：创建合同**

- 访问合同管理页面
- 点击"新增合同"按钮
- 填写合同名称：`测试合同_时间戳`
- 填写合同金额：5000
- **关联报价**：选择刚创建的报价（重要！）
- 保存合同

### **步骤5：从合同创建工单**

- 在合同列表中找到刚创建的合同
- 点击"操作" -> "创建工单"
- 选择服务类型：增值服务
- 填写工单标题：`测试工单_公司改制_时间戳`
- 选择优先级：中
- 确认创建

### **步骤6：验证任务项从产品步骤加载**

- 导航到服务工单列表
- 找到刚创建的工单
- 点击"查看"打开工单详情
- **验证任务项数量**：应该是6个
- **验证任务项名称**：
  1. 工商核名
  2. 网报签字
  3. 领取执照
  4. 客户交接
  5. 开立基本户
  6. 税务登记

### **步骤7：测试任务项分配**

- 点击第一个任务项的"分配"按钮
- 打开分配对话框
- 选择执行人（第一个用户）
- 点击"确定"确认分配
- 等待分配成功提示

### **步骤8：验证分配结果**

- 刷新页面
- 检查执行人列是否显示分配的用户
- 验证分配成功

---

## 📸 测试截图

测试过程中会自动保存10张截图到 `screenshots/` 目录：

1. `01-login-success.png` - 登录成功
2. `02-lead-created.png` - 线索创建成功
3. `03-quote-created.png` - 报价创建成功
4. `04-contract-created.png` - 合同创建成功
5. `05-order-created.png` - 工单创建成功
6. `06-order-detail.png` - 工单详情页面
7. `07-task-items-list.png` - 任务项列表
8. `08-executor-selected.png` - 执行人选择
9. `09-assignment-success.png` - 分配成功
10. `10-assignment-verified.png` - 分配结果验证

---

## 🎨 UI 模式（推荐）

使用 UI 模式可以清楚地看到每一步操作：

```bash
./run-task-assignment-test.sh --complete --ui
```

**UI 模式的优势**：
- 📊 可视化测试进度
- 🔍 可以暂停和单步执行
- 🐛 方便调试
- 📸 实时查看浏览器操作
- 📝 查看详细的测试日志

---

## 📊 测试报告

测试完成后，查看 HTML 报告：

```bash
npx playwright show-report
```

报告包含：
- ✅ 测试通过/失败状态
- ⏱️ 每个步骤的执行时间
- 📸 失败时的截图
- 📹 测试录像（如果启用）
- 📝 详细的错误信息

---

## 🐛 故障排查

### **问题1：找不到"公司改制"产品**

**症状**：测试在步骤4失败，提示找不到产品

**解决方案**：
1. 检查数据库中是否有该产品：
   ```sql
   SELECT * FROM chanpin WHERE chanpin_daima = 'zengzhi_1_2';
   ```
2. 如果没有，创建该产品：
   - 访问 http://localhost:5174/products
   - 创建产品：公司改制（内转外/外转内）
   - 产品代码：zengzhi_1_2
   - 添加6个步骤

### **问题2：任务项数量不是6个**

**症状**：工单创建成功，但任务项数量不对

**可能原因**：
1. 产品没有步骤
2. 合同没有关联报价
3. 报价没有包含该产品

**解决方案**：
1. 检查产品步骤：
   ```sql
   SELECT * FROM chanpin_buzhou WHERE chanpin_id = (
     SELECT id FROM chanpin WHERE chanpin_daima = 'zengzhi_1_2'
   );
   ```
2. 确保合同关联了报价
3. 确保报价包含了该产品

### **问题3：分配对话框打不开**

**症状**：点击"分配"按钮没有反应

**可能原因**：
1. 前端组件未加载
2. 权限不足
3. 任务项已分配

**解决方案**：
1. 检查浏览器控制台错误
2. 确认使用 admin 账号登录
3. 检查任务项状态

### **问题4：测试超时**

**症状**：测试在某个步骤超时

**解决方案**：
1. 检查网络连接
2. 检查后端服务是否正常
3. 增加超时时间（在测试脚本中修改）
4. 使用 `--headed` 模式查看浏览器操作

---

## 🔧 自定义测试

### **修改测试数据**

编辑 `tests/e2e/test_complete_workflow.spec.ts`：

```typescript
// 修改客户名称
await page.fill('input[placeholder*="客户名称"]', '您的客户名称')

// 修改产品
await page.click('.el-select-dropdown__item:has-text("您的产品名称")')

// 修改合同金额
await page.fill('input[placeholder*="合同金额"]', '10000')
```

### **添加更多验证**

```typescript
// 验证任务项状态
const taskStatus = await page.locator('td:has-text("待处理")').count()
expect(taskStatus).toBeGreaterThan(0)

// 验证操作日志
await page.click('text=操作日志')
const logCount = await page.locator('.log-item').count()
expect(logCount).toBeGreaterThan(0)
```

---

## 📚 相关文档

1. **测试脚本**: `tests/e2e/test_complete_workflow.spec.ts`
2. **运行脚本**: `run-task-assignment-test.sh`
3. **Playwright 配置**: `playwright.config.ts`
4. **数据准备指南**: `prepare-test-data.md`
5. **状态总结**: `TEST_STATUS_SUMMARY.md`

---

## ✨ 总结

### **优势**

✅ **完全自动化**：无需手动创建任何数据  
✅ **完整流程**：覆盖从线索到工单的全流程  
✅ **真实场景**：模拟真实用户操作  
✅ **详细验证**：验证任务项从产品步骤加载  
✅ **可视化**：支持 UI 模式查看操作过程  
✅ **可重复**：每次运行都创建新的测试数据  

### **适用场景**

- ✅ 验证完整业务流程
- ✅ 回归测试
- ✅ 演示系统功能
- ✅ 培训新员工
- ✅ 调试问题

### **下一步**

1. 运行测试：`./run-task-assignment-test.sh --complete --ui`
2. 查看截图：`ls -la screenshots/`
3. 查看报告：`npx playwright show-report`

---

**文档创建时间**: 2025年11月5日  
**测试脚本**: `tests/e2e/test_complete_workflow.spec.ts`  
**运行命令**: `./run-task-assignment-test.sh --complete`

