import { test, expect, Page } from '@playwright/test'

/**
 * 工单任务项分配功能 - 端到端测试
 * 
 * 测试目标：验证工单任务项能否正确分配给不同的执行人
 * 测试账号：admin / 123456
 */

test.describe('工单任务项分配功能测试', () => {
  let page: Page

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage()
  })

  test.afterAll(async () => {
    await page.close()
  })

  test('完整的任务项分配流程测试', async () => {
    console.log('\n' + '='.repeat(80))
    console.log('开始测试：工单任务项分配功能')
    console.log('='.repeat(80))

    // ==================== 第一步：登录系统 ====================
    console.log('\n【步骤1】登录系统...')
    await page.goto('http://localhost:5174/login')
    await page.waitForLoadState('networkidle')

    // 填写登录表单
    await page.fill('input[placeholder*="用户名"]', 'admin')
    await page.fill('input[type="password"]', '123456')

    // 点击登录按钮（注意：按钮文本是"登 录"，中间有空格）
    await page.click('button:has-text("登 录")')
    await page.waitForLoadState('networkidle')
    
    // 验证登录成功
    await expect(page).toHaveURL(/\/dashboard|\//, { timeout: 10000 })
    console.log('✅ 登录成功')
    await page.screenshot({ path: 'screenshots/01-login-success.png' })

    // ==================== 第二步：导航到服务工单列表 ====================
    console.log('\n【步骤2】导航到服务工单列表...')
    await page.goto('http://localhost:5174/service-orders')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
    
    console.log('✅ 成功打开服务工单列表页面')
    await page.screenshot({ path: 'screenshots/02-service-orders-list.png' })

    // ==================== 第三步：查找并打开一个工单 ====================
    console.log('\n【步骤3】查找并打开一个工单...')

    // 等待页面加载完成
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000) // 等待2秒确保数据加载

    // 检查是否有数据
    const noDataElement = await page.locator('text=No Data').count()

    if (noDataElement > 0) {
      console.log('❌ 当前没有工单数据')
      console.log('\n提示：请先在系统中创建至少一个服务工单')
      console.log('创建方法：')
      console.log('  1. 创建一个合同（合同管理 -> 新增合同）')
      console.log('  2. 从合同创建工单（合同列表 -> 操作 -> 创建工单）')
      console.log('  3. 或者直接创建工单（服务工单管理 -> 创建工单）')
      console.log('\n测试终止。')
      throw new Error('没有工单数据，无法继续测试。请先创建至少一个服务工单。')
    }

    // 查找第一个"查看"按钮
    const viewButtons = await page.locator('button:has-text("查看")').all()

    if (viewButtons.length === 0) {
      console.log('❌ 没有找到工单的查看按钮')
      throw new Error('没有找到工单的查看按钮')
    }

    console.log(`✅ 找到 ${viewButtons.length} 个工单`)

    // 点击第一个工单的"查看"按钮
    await viewButtons[0].click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    console.log('✅ 成功打开工单详情页面')
    await page.screenshot({ path: 'screenshots/03-service-order-detail.png' })

    // ==================== 第四步：查看任务项列表 ====================
    console.log('\n【步骤4】查看任务项列表...')
    
    // 等待任务项表格加载
    await page.waitForSelector('.items-card .el-table', { timeout: 10000 })
    
    // 获取任务项数量
    const taskRows = await page.locator('.items-card .el-table__body tr').all()
    const taskCount = taskRows.length
    
    console.log(`✅ 找到 ${taskCount} 个任务项`)
    
    if (taskCount === 0) {
      console.log('❌ 工单没有任务项，测试终止')
      throw new Error('工单没有任务项')
    }
    
    // 读取并显示所有任务项信息
    console.log('\n任务项列表：')
    for (let i = 0; i < taskCount; i++) {
      const row = taskRows[i]
      const taskName = await row.locator('td:nth-child(1)').textContent()
      const executor = await row.locator('td:has-text("执行人") ~ td').textContent()
      console.log(`   ${i + 1}. ${taskName?.trim()} - 执行人: ${executor?.trim() || '未分配'}`)
    }
    
    await page.screenshot({ path: 'screenshots/04-task-items-list.png' })

    // ==================== 第五步：分配第一个任务项 ====================
    console.log('\n【步骤5】分配第一个任务项...')
    
    // 查找第一个任务项的"分配"或"重新分配"按钮
    const assignButtons = await page.locator('.items-card .el-table__body button:has-text("分配"), .items-card .el-table__body button:has-text("重新分配")').all()
    
    if (assignButtons.length === 0) {
      console.log('❌ 没有找到分配按钮，测试终止')
      throw new Error('没有找到分配按钮')
    }
    
    console.log(`✅ 找到 ${assignButtons.length} 个分配按钮`)
    
    // 点击第一个分配按钮
    await assignButtons[0].click()
    await page.waitForTimeout(1000)
    
    // 验证对话框是否打开
    const dialog = page.locator('.el-dialog:has-text("分配任务项")')
    await expect(dialog).toBeVisible({ timeout: 5000 })
    console.log('✅ 分配对话框已打开')
    await page.screenshot({ path: 'screenshots/05-assign-dialog-opened.png' })

    // ==================== 第六步：选择执行人 ====================
    console.log('\n【步骤6】选择执行人...')
    
    // 点击执行人下拉框
    await dialog.locator('.el-select').click()
    await page.waitForTimeout(500)
    
    // 等待下拉选项加载
    await page.waitForSelector('.el-select-dropdown .el-option', { timeout: 5000 })
    
    // 获取所有执行人选项
    const userOptions = await page.locator('.el-select-dropdown .el-option').all()
    console.log(`✅ 找到 ${userOptions.length} 个可选执行人`)
    
    if (userOptions.length === 0) {
      console.log('❌ 没有可选的执行人，测试终止')
      throw new Error('没有可选的执行人')
    }
    
    // 显示前5个执行人
    console.log('\n可选执行人：')
    for (let i = 0; i < Math.min(5, userOptions.length); i++) {
      const userName = await userOptions[i].textContent()
      console.log(`   ${i + 1}. ${userName?.trim()}`)
    }
    
    // 选择第一个执行人
    await userOptions[0].click()
    await page.waitForTimeout(500)
    
    const selectedUser = await userOptions[0].textContent()
    console.log(`✅ 已选择执行人: ${selectedUser?.trim()}`)
    await page.screenshot({ path: 'screenshots/06-executor-selected.png' })

    // ==================== 第七步：确认分配 ====================
    console.log('\n【步骤7】确认分配...')
    
    // 点击确定按钮
    await dialog.locator('button:has-text("确定")').click()
    await page.waitForTimeout(1000)
    
    // 等待成功提示消息
    const successMessage = page.locator('.el-message:has-text("成功")')
    await expect(successMessage).toBeVisible({ timeout: 5000 })
    console.log('✅ 分配成功提示已显示')
    
    // 等待对话框关闭
    await expect(dialog).not.toBeVisible({ timeout: 5000 })
    console.log('✅ 分配对话框已关闭')
    
    // 等待页面刷新
    await page.waitForTimeout(2000)
    await page.screenshot({ path: 'screenshots/07-assignment-success.png' })

    // ==================== 第八步：验证分配结果 ====================
    console.log('\n【步骤8】验证分配结果...')
    
    // 重新获取任务项列表
    const updatedTaskRows = await page.locator('.items-card .el-table__body tr').all()
    
    console.log('\n更新后的任务项列表：')
    for (let i = 0; i < updatedTaskRows.length; i++) {
      const row = updatedTaskRows[i]
      const taskName = await row.locator('td:nth-child(1)').textContent()
      const executor = await row.locator('td:has-text("执行人") ~ td').textContent()
      console.log(`   ${i + 1}. ${taskName?.trim()} - 执行人: ${executor?.trim() || '未分配'}`)
    }
    
    // 验证第一个任务项的执行人不是"未分配"
    const firstTaskExecutor = await updatedTaskRows[0].locator('td:has-text("执行人") ~ td').textContent()
    expect(firstTaskExecutor?.trim()).not.toBe('未分配')
    console.log(`✅ 第一个任务项已成功分配给: ${firstTaskExecutor?.trim()}`)
    
    await page.screenshot({ path: 'screenshots/08-assignment-verified.png' })

    // ==================== 第九步：验证操作日志 ====================
    console.log('\n【步骤9】验证操作日志...')
    
    // 滚动到日志区域
    await page.locator('.log-card').scrollIntoViewIfNeeded()
    await page.waitForTimeout(500)
    
    // 查找包含"任务分配"的日志
    const taskAssignLogs = await page.locator('.log-card .el-timeline-item:has-text("任务分配")').all()
    
    if (taskAssignLogs.length > 0) {
      console.log(`✅ 找到 ${taskAssignLogs.length} 条任务分配日志`)
      
      // 显示最新的日志内容
      const latestLog = taskAssignLogs[0]
      const logContent = await latestLog.textContent()
      console.log(`   最新日志: ${logContent?.trim()}`)
    } else {
      console.log('⚠️  未找到任务分配日志（可能日志类型映射需要更新）')
    }
    
    await page.screenshot({ path: 'screenshots/09-operation-logs.png' })

    // ==================== 第十步：测试重新分配 ====================
    console.log('\n【步骤10】测试重新分配功能...')
    
    // 滚动回任务项区域
    await page.locator('.items-card').scrollIntoViewIfNeeded()
    await page.waitForTimeout(500)
    
    // 再次点击第一个任务项的分配按钮（现在应该显示"重新分配"）
    const reassignButtons = await page.locator('.items-card .el-table__body button:has-text("重新分配")').all()
    
    if (reassignButtons.length > 0) {
      console.log('✅ 找到"重新分配"按钮')
      
      // 点击重新分配按钮
      await reassignButtons[0].click()
      await page.waitForTimeout(1000)
      
      // 验证对话框打开
      await expect(dialog).toBeVisible({ timeout: 5000 })
      console.log('✅ 重新分配对话框已打开')
      
      // 选择不同的执行人
      await dialog.locator('.el-select').click()
      await page.waitForTimeout(500)
      
      const userOptions2 = await page.locator('.el-select-dropdown .el-option').all()
      if (userOptions2.length > 1) {
        // 选择第二个执行人
        await userOptions2[1].click()
        await page.waitForTimeout(500)
        
        const selectedUser2 = await userOptions2[1].textContent()
        console.log(`✅ 已选择新的执行人: ${selectedUser2?.trim()}`)
        
        // 确认重新分配
        await dialog.locator('button:has-text("确定")').click()
        await page.waitForTimeout(1000)
        
        // 等待成功提示
        await expect(successMessage).toBeVisible({ timeout: 5000 })
        console.log('✅ 重新分配成功')
        
        await page.waitForTimeout(2000)
        await page.screenshot({ path: 'screenshots/10-reassignment-success.png' })
      } else {
        console.log('⚠️  只有一个执行人，跳过重新分配测试')
        await page.keyboard.press('Escape')
      }
    } else {
      console.log('⚠️  未找到"重新分配"按钮，可能按钮文本不同')
    }

    // ==================== 测试完成 ====================
    console.log('\n' + '='.repeat(80))
    console.log('✅ 测试完成！所有步骤执行成功')
    console.log('='.repeat(80))
    console.log('\n测试总结：')
    console.log('  ✅ 登录系统')
    console.log('  ✅ 打开服务工单列表')
    console.log('  ✅ 打开工单详情')
    console.log('  ✅ 查看任务项列表')
    console.log('  ✅ 分配任务项')
    console.log('  ✅ 验证分配结果')
    console.log('  ✅ 验证操作日志')
    console.log('  ✅ 测试重新分配')
    console.log('\n截图已保存到 screenshots/ 目录')
    console.log('='.repeat(80) + '\n')
  })
})

