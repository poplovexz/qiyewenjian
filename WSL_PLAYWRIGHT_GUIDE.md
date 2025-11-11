# WSL/Linux 环境下运行 Playwright 测试指南

## ⚠️ 问题说明

在 WSL/Linux 环境下，`--ui` 模式无法显示窗口，因为：
- WSL 默认没有图形界面（X11）
- UI 模式需要图形界面才能显示

---

## ✅ **推荐方案：无头模式 + HTML 报告**

这是在 WSL/Linux 环境下最实用的方案。

### **步骤1：运行测试（无头模式）**

```bash
# 运行完整流程测试
./run-task-assignment-test.sh --complete
```

测试会在后台运行，自动：
- 创建线索
- 创建报价
- 创建合同
- 创建工单
- 分配任务项
- 保存12张截图

### **步骤2：查看截图**

```bash
# 查看所有截图
ls -la screenshots/

# 查看具体截图（使用图片查看器）
# 如果安装了 eog (Eye of GNOME)
eog screenshots/01-login-success.png

# 或者复制到 Windows 桌面查看
cp -r screenshots /mnt/c/Users/YourUsername/Desktop/
```

### **步骤3：查看 HTML 报告**

```bash
# 生成并打开 HTML 报告
npx playwright show-report
```

这会启动一个 Web 服务器，通常在 `http://localhost:9323`

**在 Windows 浏览器中打开**：
- 打开 Chrome/Edge
- 访问：`http://localhost:9323`

**HTML 报告包含**：
- ✅ 测试通过/失败状态
- ⏱️ 每个步骤的执行时间
- 📸 所有截图
- 📹 测试录像（如果启用）
- 📝 详细的错误信息
- 🔍 可以点击查看每个步骤的详情

---

## 🎨 **方案2：在 Windows 上运行（最佳体验）**

如果您想看到可视化的测试过程，建议在 Windows 环境下运行。

### **步骤1：在 Windows 中打开项目**

```cmd
# 在 Windows PowerShell 或 CMD 中
cd \\wsl$\Ubuntu\var\www

# 或者如果项目在 Windows 目录
cd C:\path\to\your\project
```

### **步骤2：安装依赖**

```cmd
# 安装 Playwright（如果还没安装）
npm install -D @playwright/test

# 安装浏览器
npx playwright install chromium
```

### **步骤3：运行测试（UI 模式）**

```cmd
# UI 模式 - 可视化界面
npx playwright test tests/e2e/test_complete_workflow.spec.ts --ui

# 或者显示浏览器模式 - 看到真实浏览器操作
npx playwright test tests/e2e/test_complete_workflow.spec.ts --headed
```

**UI 模式的优势**：
- 📊 可视化测试进度
- 🔍 可以暂停和单步执行
- 🐛 方便调试
- 📸 实时查看浏览器操作

---

## 🔧 **方案3：配置 WSL 的 X11 转发（高级）**

如果您一定要在 WSL 中显示图形界面：

### **步骤1：在 Windows 上安装 X Server**

下载并安装以下之一：
- **VcXsrv**: https://sourceforge.net/projects/vcxsrv/
- **X410**: Microsoft Store（付费）
- **MobaXterm**: https://mobaxterm.mobatek.net/

### **步骤2：启动 X Server**

**VcXsrv 配置**：
1. 启动 XLaunch
2. 选择 "Multiple windows"
3. 选择 "Start no client"
4. **勾选** "Disable access control"
5. 完成

### **步骤3：配置 WSL**

```bash
# 在 WSL 中设置 DISPLAY 环境变量
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# 添加到 ~/.bashrc 使其永久生效
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '"'"'{print $2}'"'"'):0' >> ~/.bashrc
source ~/.bashrc
```

### **步骤4：测试 X11**

```bash
# 安装测试工具
sudo apt-get update
sudo apt-get install x11-apps

# 测试 X11 是否工作
xclock
```

如果看到一个时钟窗口，说明 X11 配置成功。

### **步骤5：运行 Playwright UI 模式**

```bash
./run-task-assignment-test.sh --complete --ui
```

---

## 📊 **各方案对比**

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **无头模式 + HTML 报告** | ✅ 简单<br>✅ 无需配置<br>✅ 详细报告 | ❌ 看不到实时操作 | ⭐⭐⭐⭐⭐ |
| **Windows 运行** | ✅ 完整 UI<br>✅ 实时查看<br>✅ 易调试 | ❌ 需要在 Windows 环境 | ⭐⭐⭐⭐ |
| **WSL + X11** | ✅ 在 WSL 中运行<br>✅ 有图形界面 | ❌ 配置复杂<br>❌ 可能不稳定 | ⭐⭐ |

---

## 🚀 **快速开始（推荐流程）**

### **在 WSL/Linux 中**

```bash
# 1. 运行完整流程测试
./run-task-assignment-test.sh --complete

# 2. 查看截图
ls -la screenshots/

# 3. 查看 HTML 报告
npx playwright show-report
```

### **在 Windows 浏览器中**

打开：`http://localhost:9323`

查看详细的测试报告，包括：
- 所有截图
- 每个步骤的详情
- 执行时间
- 错误信息（如果有）

---

## 📸 **查看测试截图**

### **方法1：在 WSL 中查看**

```bash
# 如果安装了图片查看器
eog screenshots/01-login-success.png

# 或使用 feh
feh screenshots/
```

### **方法2：复制到 Windows**

```bash
# 复制到 Windows 桌面
cp -r screenshots /mnt/c/Users/YourUsername/Desktop/

# 或复制到 Windows 下载文件夹
cp -r screenshots /mnt/c/Users/YourUsername/Downloads/
```

然后在 Windows 文件资源管理器中打开查看。

### **方法3：通过 HTML 报告查看**

```bash
npx playwright show-report
```

在浏览器中打开 `http://localhost:9323`，点击测试用例，可以看到所有截图。

---

## 🐛 **故障排查**

### **问题1：UI 模式窗口最小化后打不开**

**原因**：WSL 没有图形界面

**解决**：
1. 使用无头模式：`./run-task-assignment-test.sh --complete`
2. 或在 Windows 上运行
3. 或配置 X11（见方案3）

### **问题2：HTML 报告打不开**

**症状**：`npx playwright show-report` 后浏览器没反应

**解决**：
1. 手动在浏览器中打开：`http://localhost:9323`
2. 检查端口是否被占用：`netstat -tuln | grep 9323`
3. 指定其他端口：`npx playwright show-report --port 8080`

### **问题3：截图保存失败**

**症状**：`screenshots/` 目录为空

**解决**：
1. 检查目录权限：`ls -la screenshots/`
2. 手动创建目录：`mkdir -p screenshots`
3. 检查测试是否真的运行了

### **问题4：X11 转发不工作**

**症状**：`xclock` 报错 "cannot open display"

**解决**：
1. 检查 X Server 是否启动
2. 检查 DISPLAY 变量：`echo $DISPLAY`
3. 检查防火墙设置
4. 重启 X Server 并禁用访问控制

---

## 💡 **最佳实践**

### **开发和调试**

在 Windows 上使用 UI 模式：
```cmd
npx playwright test tests/e2e/test_complete_workflow.spec.ts --ui
```

### **CI/CD 和自动化**

在 Linux 上使用无头模式：
```bash
./run-task-assignment-test.sh --complete
```

### **演示和培训**

在 Windows 上使用显示浏览器模式：
```cmd
npx playwright test tests/e2e/test_complete_workflow.spec.ts --headed
```

---

## 📚 **相关文档**

1. **完整流程测试**: `COMPLETE_WORKFLOW_TEST.md`
2. **快速启动**: `QUICK_START_WINDOWS.md`
3. **测试脚本**: `tests/e2e/test_complete_workflow.spec.ts`
4. **Playwright 官方文档**: https://playwright.dev/

---

## ✨ **总结**

### **在 WSL/Linux 环境下**

✅ **推荐使用无头模式**：
```bash
./run-task-assignment-test.sh --complete
npx playwright show-report
```

### **想要可视化体验**

✅ **在 Windows 上运行**：
```cmd
npx playwright test tests/e2e/test_complete_workflow.spec.ts --ui
```

### **查看测试结果**

✅ **HTML 报告最详细**：
- 在浏览器中打开 `http://localhost:9323`
- 包含所有截图、时间线、错误信息

---

**文档创建时间**: 2025年11月5日  
**适用环境**: WSL/Linux  
**推荐方案**: 无头模式 + HTML 报告

