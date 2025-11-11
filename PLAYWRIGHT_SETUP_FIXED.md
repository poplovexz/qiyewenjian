# Playwright 测试环境配置问题解决方案

## 🐛 遇到的问题

### **问题1：重复安装检测**

**现象**：
```bash
./run-task-assignment-test.sh --ui
⚠️  Playwright 未安装，正在安装...
```

每次运行脚本都提示未安装，即使已经安装过。

**原因**：
脚本使用 `[ ! -d "node_modules/@playwright/test" ]` 检测，但这个目录在 pnpm 工作区中不存在。

**解决方案**：
改用 `pnpm list @playwright/test` 命令检测是否已安装。

---

### **问题2：npm 安装失败**

**现象**：
```bash
npm install -D @playwright/test
npm error code EUNSUPPORTEDPROTOCOL
npm error Unsupported URL Type "link:": link:./src/types
```

**原因**：
项目使用 pnpm 作为包管理器，node_modules 中的 vite 包含了 `link:` 协议的依赖，npm 不支持。

**解决方案**：
使用 pnpm 安装：
```bash
pnpm add -D @playwright/test -w
```

---

## ✅ 已修复的内容

### **1. 更新了检测逻辑**

**修改文件**: `run-task-assignment-test.sh`

**修改前**:
```bash
if [ ! -d "node_modules/@playwright/test" ]; then
    npm install -D @playwright/test
fi
```

**修改后**:
```bash
if ! pnpm list @playwright/test &> /dev/null; then
    pnpm add -D @playwright/test -w
fi
```

### **2. 改进了浏览器检测**

**修改前**:
```bash
if ! npx playwright --version &> /dev/null || [ ! -d "$HOME/.cache/ms-playwright/chromium-"* ]; then
    npx playwright install chromium
fi
```

**修改后**:
```bash
CHROMIUM_DIR=$(find "$HOME/.cache/ms-playwright" -maxdepth 1 -name "chromium-*" -type d 2>/dev/null | head -1)
if [ -z "$CHROMIUM_DIR" ]; then
    npx playwright install chromium
fi
```

### **3. 已安装 @playwright/test**

```bash
pnpm add -D @playwright/test -w
```

安装结果：
```
devDependencies:
+ @playwright/test ^1.56.1
```

---

## 🚀 现在如何运行测试

### **Linux 环境（服务器）**

**1. 确保服务已启动**:
```bash
# 检查后端
curl http://localhost:8000/api/v1/health

# 检查前端
curl http://localhost:5174
```

**2. 运行测试**:
```bash
# 无头模式（推荐 - 服务器环境）
./run-task-assignment-test.sh

# 显示浏览器模式（需要 X11）
./run-task-assignment-test.sh --headed

# 调试模式
./run-task-assignment-test.sh --debug
```

**3. 查看结果**:
```bash
# 查看截图
ls -la screenshots/

# 查看HTML报告
npx playwright show-report
```

---

### **Windows 环境（本地开发）**

**1. 启动服务**:

窗口1 - 后端:
```cmd
cd packages\backend
venv\Scripts\activate
python src\main.py
```

窗口2 - 前端:
```cmd
cd packages\frontend
npm run dev
```

**2. 运行测试**:

窗口3:
```cmd
REM UI模式（推荐）
run-task-assignment-test.bat --ui

REM 显示浏览器
run-task-assignment-test.bat --headed

REM 调试模式
run-task-assignment-test.bat --debug
```

**3. 查看结果**:
```cmd
REM 查看截图
explorer screenshots

REM 查看HTML报告
npx playwright show-report
```

---

## 📊 测试执行结果

### **成功运行示例**

```bash
root@server:/var/www# ./run-task-assignment-test.sh --ui
================================================================================
工单任务项分配功能 - Playwright 端到端测试
================================================================================

【检查1】检查 Playwright 是否已安装...
✅ Playwright 已安装

【检查2】检查后端服务是否运行...
✅ 后端服务正在运行 (http://localhost:8000)

【检查3】检查前端服务是否运行...
✅ 前端服务正在运行 (http://localhost:5174)

【准备】创建截图目录...
✅ 截图目录已创建

================================================================================
开始运行测试...
================================================================================

以UI模式运行...

================================================================================
✅ 测试执行成功！
================================================================================

查看测试结果：
  - 截图目录: screenshots/
  - HTML报告: npx playwright show-report
```

---

## 🎯 关键要点

### **1. 使用正确的包管理器**

- ✅ **Linux/服务器**: 使用 `pnpm`（项目配置的包管理器）
- ✅ **Windows**: 可以使用 `npm` 或 `pnpm`

### **2. 选择合适的运行模式**

- ✅ **服务器环境**: 使用无头模式（`--headed` 或不带参数）
- ✅ **本地开发**: 使用 UI 模式（`--ui`）或显示浏览器模式（`--headed`）
- ✅ **调试**: 使用调试模式（`--debug`）

### **3. 检测逻辑**

- ❌ **不要用**: 检查目录是否存在（`[ -d "node_modules/@playwright/test" ]`）
- ✅ **应该用**: 使用包管理器命令（`pnpm list @playwright/test`）

### **4. 环境差异**

| 环境 | 包管理器 | 推荐模式 | 图形界面 |
|------|---------|---------|---------|
| Linux 服务器 | pnpm | 无头模式 | ❌ |
| Linux 桌面 | pnpm | UI/Headed | ✅ |
| Windows | npm/pnpm | UI模式 | ✅ |
| macOS | npm/pnpm | UI模式 | ✅ |

---

## 📚 相关文档

- **快速启动**: `QUICK_START_WINDOWS.md` - 5分钟快速上手（已更新支持 Linux）
- **Windows 指南**: `WINDOWS_TEST_GUIDE.md` - Windows 详细指南
- **测试文档**: `tests/e2e/README.md` - 测试说明
- **功能文档**: `docs/task-item-assignment-feature.md` - 功能实施文档

---

## 🔧 故障排查

### **问题：pnpm 命令未找到**

**解决方案**:
```bash
npm install -g pnpm
```

### **问题：测试超时**

**解决方案**:
编辑 `playwright.config.ts`，增加超时时间：
```typescript
timeout: 120000, // 120秒
```

### **问题：浏览器未安装**

**解决方案**:
```bash
npx playwright install chromium
```

### **问题：服务未启动**

**解决方案**:
```bash
# 检查后端
curl http://localhost:8000/api/v1/health

# 检查前端
curl http://localhost:5174

# 如果未启动，参考 QUICK_START_WINDOWS.md 启动服务
```

---

## ✨ 总结

✅ **问题已解决**：
- 修复了重复安装检测问题
- 修复了 npm 安装失败问题
- 改进了浏览器检测逻辑
- 更新了文档支持 Linux 和 Windows

✅ **现在可以正常运行**：
```bash
# Linux
./run-task-assignment-test.sh

# Windows
run-task-assignment-test.bat --ui
```

✅ **测试已验证**：
- 脚本检测逻辑正常
- Playwright 安装成功
- 测试执行成功

---

**文档更新时间**: 2025年11月5日  
**问题状态**: ✅ 已解决  
**测试状态**: ✅ 可以正常运行

