# E2E 自动化测试 - 文件索引

## 📋 快速导航

### 🚀 开始使用

- **[快速开始指南](QUICK_START.md)** - 5分钟快速上手
- **[详细文档](README.md)** - 完整的使用文档

### 📝 测试文件

- **[完整业务流程测试](tests/test_complete_workflow.spec.ts)** - 从线索到工单任务项分配
- **[任务项分配测试](tests/test_task_item_assignment.spec.ts)** - 仅测试任务项分配功能

### ⚙️ 配置文件

- **[Playwright 配置](playwright.config.ts)** - Playwright 测试配置
- **[运行脚本](run-task-assignment-test.sh)** - Linux/Mac 测试运行脚本
- **[Git 忽略配置](.gitignore)** - Git 版本控制配置

### 📚 文档

- **[完整流程测试文档](docs/COMPLETE_WORKFLOW_TEST.md)** - 详细的测试流程说明
- **[WSL 环境指南](docs/WSL_PLAYWRIGHT_GUIDE.md)** - WSL 环境下的使用指南
- **[测试数据准备](docs/prepare-test-data.md)** - 如何准备测试数据

---

## 🎯 常用命令

```bash
# 运行完整业务流程测试
./run-task-assignment-test.sh --complete

# UI 模式运行
./run-task-assignment-test.sh --complete --ui

# 查看测试报告
npx playwright show-report

# 查看截图
ls -la screenshots/
```

---

## 📁 目录结构

```
e2e-automation/
├── INDEX.md                    ← 本文件
├── QUICK_START.md              ← 快速开始
├── README.md                   ← 详细文档
├── .gitignore                  ← Git 配置
├── playwright.config.ts        ← Playwright 配置
├── run-task-assignment-test.sh ← 运行脚本
├── tests/                      ← 测试文件
│   ├── test_complete_workflow.spec.ts
│   └── test_task_item_assignment.spec.ts
├── screenshots/                ← 测试截图
├── docs/                       ← 文档目录
│   ├── COMPLETE_WORKFLOW_TEST.md
│   ├── WSL_PLAYWRIGHT_GUIDE.md
│   └── prepare-test-data.md
├── playwright-report/          ← HTML 报告（运行后生成）
└── test-results/               ← 测试结果（运行后生成）
```

---

## 🔗 相关链接

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright 中文文档](https://playwright.dev/docs/intro)
- [项目根目录](../)

---

**最后更新**：2025-11-06

