@echo off
chcp 65001 >nul
REM 工单任务项分配功能 - Playwright 测试运行脚本 (Windows版本)

echo ================================================================================
echo 工单任务项分配功能 - Playwright 端到端测试
echo ================================================================================
echo.

REM 检查 Node.js 是否已安装
echo [检查1] 检查 Node.js 是否已安装...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js 未找到，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js 已安装
echo.

REM 检查 Playwright 是否已安装
echo [检查2] 检查 Playwright 是否已安装...
if not exist "node_modules\@playwright\test" (
    echo ⚠️  Playwright 未安装，正在安装...
    call npm install -D @playwright/test
    call npx playwright install chromium
)
echo ✅ Playwright 已安装
echo.

REM 检查后端服务
echo [检查3] 检查后端服务是否运行...
curl -s http://localhost:8000/api/v1/health >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 后端服务未运行
    echo.
    echo 请先启动后端服务：
    echo   1. 打开新的命令提示符窗口
    echo   2. cd packages\backend
    echo   3. venv\Scripts\activate
    echo   4. python src\main.py
    echo.
    pause
    exit /b 1
)
echo ✅ 后端服务正在运行 (http://localhost:8000)
echo.

REM 检查前端服务
echo [检查4] 检查前端服务是否运行...
curl -s http://localhost:5174 >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 前端服务未运行
    echo.
    echo 请先启动前端服务：
    echo   1. 打开新的命令提示符窗口
    echo   2. cd packages\frontend
    echo   3. npm run dev
    echo.
    pause
    exit /b 1
)
echo ✅ 前端服务正在运行 (http://localhost:5174)
echo.

REM 创建截图目录
echo [准备] 创建截图目录...
if not exist "screenshots" mkdir screenshots
echo ✅ 截图目录已创建
echo.

REM 运行测试
echo ================================================================================
echo 开始运行测试...
echo ================================================================================
echo.

REM 根据参数选择运行模式
if "%1"=="--debug" (
    echo 以调试模式运行...
    npx playwright test tests/e2e/test_task_item_assignment.spec.ts --debug
) else if "%1"=="--ui" (
    echo 以UI模式运行...
    npx playwright test tests/e2e/test_task_item_assignment.spec.ts --ui
) else if "%1"=="--headed" (
    echo 显示浏览器窗口运行...
    npx playwright test tests/e2e/test_task_item_assignment.spec.ts --headed
) else (
    echo 以无头模式运行...
    npx playwright test tests/e2e/test_task_item_assignment.spec.ts
)

REM 检查测试结果
if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo ✅ 测试执行成功！
    echo ================================================================================
    echo.
    echo 查看测试结果：
    echo   - 截图目录: screenshots\
    echo   - HTML报告: npx playwright show-report
    echo.
) else (
    echo.
    echo ================================================================================
    echo ❌ 测试执行失败
    echo ================================================================================
    echo.
    echo 故障排查：
    echo   1. 检查后端和前端服务是否正常运行
    echo   2. 检查数据库是否已迁移（添加 zhixing_ren_id 字段）
    echo   3. 检查是否有工单和用户数据
    echo   4. 查看截图目录了解失败原因
    echo   5. 以调试模式运行: run-task-assignment-test.bat --debug
    echo.
)

pause

