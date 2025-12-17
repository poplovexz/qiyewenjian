# Windows 环境下运行 Playwright 测试指南

## 🎯 快速开始

### **第一步：安装 Node.js**

如果还没有安装 Node.js，请先安装：

1. 访问 [Node.js 官网](https://nodejs.org/)
2. 下载并安装 LTS 版本（推荐 v18 或更高版本）
3. 安装完成后，打开命令提示符验证：
   ```cmd
   node --version
   npm --version
   ```

---

### **第二步：安装 Playwright**

在项目根目录打开命令提示符（CMD 或 PowerShell），运行：

```cmd
npm install -D @playwright/test
npx playwright install chromium
```

---

### **第三步：启动后端服务**

**打开第一个命令提示符窗口**：

```cmd
cd packages\backend
venv\Scripts\activate
python src\main.py
```

保持这个窗口运行，不要关闭。

**验证后端服务**：
- 打开浏览器访问：http://localhost:8000/api/v1/health
- 应该看到健康检查响应

---

### **第四步：启动前端服务**

**打开第二个命令提示符窗口**：

```cmd
cd packages\frontend
npm run dev
```

保持这个窗口运行，不要关闭。

**验证前端服务**：
- 打开浏览器访问：http://localhost:5174
- 应该看到登录页面

---

### **第五步：运行 Playwright 测试**

**打开第三个命令提示符窗口**，在项目根目录运行：

#### **方式1：使用批处理脚本（推荐）**

```cmd
REM UI模式 - 可视化界面（最推荐）
run-task-assignment-test.bat --ui

REM 显示浏览器窗口运行
run-task-assignment-test.bat --headed

REM 调试模式
run-task-assignment-test.bat --debug

REM 无头模式（后台运行）
run-task-assignment-test.bat
```

#### **方式2：直接使用 npx 命令**

```cmd
REM UI模式 - 可视化界面（最推荐）
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --ui

REM 显示浏览器窗口运行
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --headed

REM 调试模式
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --debug

REM 无头模式
npx playwright test tests/e2e/test_task_item_assignment.spec.ts
```

---

## 🎨 **推荐：使用 UI 模式**

UI 模式提供了最好的可视化体验，强烈推荐！

```cmd
run-task-assignment-test.bat --ui
```

或者：

```cmd
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --ui
```

**UI 模式的优势**：
- ✅ 可视化界面，可以看到每一步操作
- ✅ 可以暂停、继续、单步执行
- ✅ 可以查看每个步骤的截图
- ✅ 可以查看网络请求
- ✅ 可以查看控制台日志
- ✅ 可以重新运行失败的测试

---

## 📸 **查看测试结果**

### **1. 查看截图**

测试运行后，截图会保存在 `screenshots\` 目录：

```cmd
REM 在文件资源管理器中打开截图目录
explorer screenshots
```

截图文件：
- `01-login-success.png` - 登录成功
- `02-service-orders-list.png` - 工单列表
- `03-service-order-detail.png` - 工单详情
- `04-task-items-list.png` - 任务项列表
- `05-assign-dialog-opened.png` - 分配对话框
- `06-executor-selected.png` - 执行人选择
- `07-assignment-success.png` - 分配成功
- `08-assignment-verified.png` - 结果验证
- `09-operation-logs.png` - 操作日志
- `10-reassignment-success.png` - 重新分配

### **2. 查看 HTML 报告**

```cmd
npx playwright show-report
```

这会在浏览器中打开详细的测试报告，包括：
- 测试执行时间
- 每个步骤的详细信息
- 失败的测试截图
- 网络请求记录
- 控制台日志

### **3. 查看视频录像**（如果测试失败）

失败的测试会自动录制视频，保存在 `test-results\` 目录：

```cmd
explorer test-results
```

---

## 🎬 **使用 Playwright Inspector（调试模式）**

调试模式可以让您逐步执行测试，非常适合开发和调试：

```cmd
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --debug
```

**调试模式功能**：
- ⏸️ 暂停执行
- ▶️ 继续执行
- ⏭️ 单步执行
- 🔍 检查元素
- 📝 查看代码
- 🖼️ 查看截图

---

## 🖥️ **使用 PowerShell**

如果您更喜欢使用 PowerShell，可以直接运行：

```powershell
# UI模式
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --ui

# 显示浏览器
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --headed

# 调试模式
npx playwright test tests/e2e/test_task_item_assignment.spec.ts --debug
```

---

## 🎥 **录制新的测试（Codegen）**

Playwright 提供了代码生成器，可以录制您的操作并生成测试代码：

```cmd
npx playwright codegen http://localhost:5174
```

**使用方法**：
1. 运行上面的命令
2. 浏览器会自动打开
3. 在浏览器中执行您想要测试的操作
4. Playwright Inspector 会自动生成对应的测试代码
5. 复制生成的代码到您的测试文件

---

## 🐛 **故障排查**

### **问题1：找不到 npx 命令**

**原因**：Node.js 未安装或未添加到 PATH

**解决方法**：
1. 重新安装 Node.js
2. 安装时勾选"Add to PATH"选项
3. 重启命令提示符

### **问题2：后端服务未运行**

**检查方法**：
```cmd
curl http://localhost:8000/api/v1/health
```

**解决方法**：
```cmd
cd packages\backend
venv\Scripts\activate
python src\main.py
```

### **问题3：前端服务未运行**

**检查方法**：
```cmd
curl http://localhost:5174
```

**解决方法**：
```cmd
cd packages\frontend
npm run dev
```

### **问题4：数据库字段未添加**

**检查方法**：
```cmd
psql -h localhost -U postgres -d proxy_db -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'fuwu_gongdan_xiangmu' AND column_name = 'zhixing_ren_id';"
```

**解决方法**：
参考 `docs/task-item-assignment-feature.md` 中的数据库迁移部分

### **问题5：测试超时**

**原因**：网络慢或页面加载慢

**解决方法**：
在 `playwright.config.ts` 中增加超时时间：
```typescript
timeout: 120000, // 增加到120秒
```

---

## 📝 **完整的测试流程示例**

### **步骤1：打开3个命令提示符窗口**

**窗口1 - 后端服务**：
```cmd
cd C:\path\to\your\project
cd packages\backend
venv\Scripts\activate
python src\main.py
```

**窗口2 - 前端服务**：
```cmd
cd C:\path\to\your\project
cd packages\frontend
npm run dev
```

**窗口3 - 运行测试**：
```cmd
cd C:\path\to\your\project
run-task-assignment-test.bat --ui
```

### **步骤2：观察测试执行**

在 UI 模式下，您会看到：
1. 浏览器自动打开
2. 自动登录系统
3. 自动导航到工单列表
4. 自动打开工单详情
5. 自动点击分配按钮
6. 自动选择执行人
7. 自动确认分配
8. 验证分配结果

### **步骤3：查看结果**

测试完成后：
1. 查看控制台输出的测试日志
2. 打开 `screenshots\` 目录查看截图
3. 运行 `npx playwright show-report` 查看详细报告

---

## 🎯 **推荐的工作流程**

### **开发阶段**

使用 UI 模式或调试模式：
```cmd
npx playwright test --ui
```

### **验收阶段**

使用显示浏览器模式：
```cmd
run-task-assignment-test.bat --headed
```

### **CI/CD 阶段**

使用无头模式：
```cmd
run-task-assignment-test.bat
```

---

## 📚 **相关资源**

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright 中文文档](https://playwright.dev/docs/intro)
- [测试脚本源码](tests/e2e/test_task_item_assignment.spec.ts)
- [功能实施文档](docs/task-item-assignment-feature.md)

---

## ✨ **总结**

在 Windows 下运行 Playwright 测试非常简单：

1. ✅ 安装 Node.js 和 Playwright
2. ✅ 启动后端和前端服务
3. ✅ 运行 `run-task-assignment-test.bat --ui`
4. ✅ 观察测试执行过程
5. ✅ 查看截图和报告

**最推荐的方式**：使用 UI 模式（`--ui`），可以清楚地看到每一步操作！

---

**文档创建时间**: 2025年11月5日  
**适用系统**: Windows 10/11  
**测试工具**: Playwright  
**测试状态**: ✅ 可以运行

