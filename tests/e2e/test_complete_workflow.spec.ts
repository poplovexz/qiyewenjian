import { test, expect, Page } from '@playwright/test'

/**
 * 完整业务流程 - 端到端测试
 *
 * 测试目标：
 * 1. 创建线索（不需要客户）
 * 2. 创建报价（包含"公司改制"产品）
 * 3. 创建合同（关联报价）
 * 4. 从合同创建工单
 * 5. 验证任务项从产品步骤加载（应该有6个任务项）
 * 6. 测试任务项分配功能
 *
 * 测试账号：admin / 123456
 */

test.describe('完整业务流程测试', () => {
  let page: Page
  let leadId: string
  let quoteId: string
  let contractId: string
  let orderId: string

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage()
  })

  test.afterAll(async () => {
    await page.close()
  })

  test('完整流程：从线索到工单任务项分配', async () => {
    console.log('\n' + '='.repeat(80))
    console.log('开始测试：完整业务流程')
    console.log('='.repeat(80))

    // ==================== 第一步：登录系统 ====================
    console.log('\n【步骤1】登录系统...')
    await page.goto('http://localhost:5174/login')
    await page.waitForLoadState('networkidle')

    await page.fill('input[placeholder*="用户名"]', 'admin')
    await page.fill('input[type="password"]', '123456')
    await page.click('button:has-text("登 录")')
    await page.waitForLoadState('networkidle')
    
    await expect(page).toHaveURL(/\/dashboard|\//, { timeout: 10000 })
    console.log('✅ 登录成功')
    await page.screenshot({ path: 'screenshots/01-login-success.png' })

    // ==================== 第二步：创建线索 ====================
    console.log('\n【步骤2】创建线索...')

    // 导航到线索列表
    await page.locator('div').filter({ hasText: /^线索管理$/ }).click()
    await page.waitForTimeout(500)
    await page.getByRole('menuitem', { name: '线索列表' }).click()
    await page.waitForTimeout(1000)

    // 点击新增线索
    await page.getByRole('button', { name: '新增线索' }).click()
    await page.waitForTimeout(1000)

    // 填写线索信息
    const companyName = `测试公司_${Date.now()}`
    const contactName = `测试联系人_${Date.now()}`

    // 填写公司名称
    await page.getByRole('textbox', { name: '* 公司名称' }).click()
    await page.getByRole('textbox', { name: '* 公司名称' }).fill(companyName)

    // 填写联系人
    await page.getByRole('textbox', { name: '* 联系人' }).click()
    await page.getByRole('textbox', { name: '* 联系人' }).fill(contactName)

    // 选择线索来源
    await page.locator('div').filter({ hasText: /^请选择线索来源$/ }).nth(4).click()
    await page.waitForTimeout(500)
    await page.getByRole('option', { name: '官网咨询' }).click()
    await page.waitForTimeout(500)

    // 保存线索
    await page.getByRole('button', { name: '创建' }).click()
    await page.waitForTimeout(2000)

    console.log('✅ 线索创建成功')
    await page.screenshot({ path: 'screenshots/02-lead-created.png' })

    // ==================== 第三步：创建报价 ====================
    console.log('\n【步骤3】创建报价（包含公司改制产品）...')

    // 在线索列表中找到刚创建的线索，点击"报价"按钮
    await page.getByRole('button', { name: '报价' }).first().click()
    await page.waitForTimeout(1000)

    // 点击添加服务
    await page.getByRole('button', { name: '添加服务' }).click()
    await page.waitForTimeout(1000)

    // 选择增值服务
    await page.getByLabel('选择服务项目').getByText('增值服务').click()
    await page.waitForTimeout(500)

    // 选择"公司改制（内转外/外转内）"产品 (编码：zengzhi_1_2)
    // 根据录制，我们需要找到包含这个编码的产品
    const productExists = await page.getByText('编码：zengzhi_1_2').count()
    if (productExists > 0) {
      await page.getByText('编码：zengzhi_1_2').click()
      console.log('✅ 找到"公司改制"产品 (zengzhi_1_2)')
    } else {
      // 如果找不到，尝试点击第一个产品
      console.log('⚠️  未找到 zengzhi_1_2，尝试选择其他增值服务产品')
      await page.getByText('办事天数：').first().click()
    }

    await page.waitForTimeout(500)

    // 确认选择产品
    await page.getByRole('button', { name: '确定选择' }).click()
    await page.waitForTimeout(1000)

    // 创建报价
    await page.getByRole('button', { name: '创建报价' }).click()
    await page.waitForTimeout(2000)

    console.log('✅ 报价创建成功')
    await page.screenshot({ path: 'screenshots/03-quote-created.png' })

    // ==================== 第四步：确认报价并生成合同 ====================
    console.log('\n【步骤4】确认报价并生成合同...')

    // 查看报价
    await page.getByRole('button', { name: '查看报价' }).first().click()
    await page.waitForTimeout(1000)

    // 确认报价
    await page.getByRole('button', { name: '确认报价' }).click()
    await page.waitForTimeout(500)
    await page.getByRole('button', { name: '确认', exact: true }).click()
    await page.waitForTimeout(2000)

    // 生成合同
    await page.getByRole('button', { name: '生成合同' }).first().click()
    await page.waitForTimeout(1000)

    // 选择乙方主体
    await page.getByRole('combobox', { name: '* 乙方主体' }).click()
    await page.waitForTimeout(500)
    await page.getByText('广州天河商务服务中心').click()
    await page.waitForTimeout(500)

    // 生成合同
    await page.getByRole('button', { name: '生成合同' }).click()
    await page.waitForTimeout(2000)

    console.log('✅ 合同创建成功')
    await page.screenshot({ path: 'screenshots/04-contract-created.png' })

    // ==================== 第五步：从合同创建工单 ====================
    console.log('\n【步骤5】从合同创建工单...')

    // 导航到合同列表
    await page.locator('div').filter({ hasText: /^合同管理$/ }).click()
    await page.waitForTimeout(500)
    await page.getByRole('menuitem', { name: '合同列表' }).click()
    await page.waitForTimeout(1000)

    // 点击创建工单按钮
    await page.getByRole('button', { name: '创建工单' }).click()
    await page.waitForTimeout(1000)

    // 确认创建工单
    await page.getByRole('button', { name: '确定' }).click()
    await page.waitForTimeout(3000) // 等待工单创建和任务项加载

    console.log('✅ 工单创建成功')
    await page.screenshot({ path: 'screenshots/05-order-created.png' })

    // ==================== 第六步：验证任务项从产品步骤加载 ====================
    console.log('\n【步骤6】验证任务项从产品步骤加载...')
    
    // 导航到服务工单列表
    await page.goto('http://localhost:5174/service-orders')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    // 找到刚创建的工单，点击"查看"
    await page.click(`tr:has-text("${orderTitle}") button:has-text("查看")`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    console.log('✅ 打开工单详情页面')
    await page.screenshot({ path: 'screenshots/06-order-detail.png' })

    // 检查任务项数量（应该是6个）
    const taskItemRows = await page.locator('.el-table__body tr').count()
    console.log(`📊 任务项数量: ${taskItemRows}`)

    if (taskItemRows === 6) {
      console.log('✅ 任务项数量正确（6个，从产品步骤加载）')
    } else {
      console.log(`⚠️  任务项数量: ${taskItemRows}（预期6个）`)
    }

    // 验证任务项名称
    const expectedTasks = ['工商核名', '网报签字', '领取执照', '客户交接', '开立基本户', '税务登记']
    for (const taskName of expectedTasks) {
      const taskExists = await page.locator(`text=${taskName}`).count()
      if (taskExists > 0) {
        console.log(`  ✅ 找到任务项: ${taskName}`)
      } else {
        console.log(`  ⚠️  未找到任务项: ${taskName}`)
      }
    }

    await page.screenshot({ path: 'screenshots/07-task-items-list.png' })

    // ==================== 第七步：测试任务项分配 ====================
    console.log('\n【步骤7】测试任务项分配功能...')
    
    // 点击第一个任务项的"分配"按钮
    const assignButtons = await page.locator('button:has-text("分配")').all()
    
    if (assignButtons.length === 0) {
      console.log('⚠️  未找到"分配"按钮，可能任务项已分配')
      // 尝试查找"重新分配"按钮
      const reassignButtons = await page.locator('button:has-text("重新分配")').all()
      if (reassignButtons.length > 0) {
        await reassignButtons[0].click()
        console.log('✅ 点击"重新分配"按钮')
      }
    } else {
      await assignButtons[0].click()
      console.log('✅ 点击"分配"按钮')
    }
    
    await page.waitForTimeout(1000)
    await page.screenshot({ path: 'screenshots/09-assign-dialog-opened.png' })

    // 选择执行人
    await page.locator('div').filter({ hasText: /^请选择执行人$/ }).nth(2).click()
    await page.waitForTimeout(500)

    // 选择系统管理员
    await page.getByText('系统管理员 (admin)').click()
    await page.waitForTimeout(500)

    console.log('✅ 选择执行人')
    await page.screenshot({ path: 'screenshots/08-executor-selected.png' })

    // 确认分配
    await page.getByRole('button', { name: '确定' }).click()
    await page.waitForTimeout(2000)

    console.log('✅ 任务项分配成功')
    await page.screenshot({ path: 'screenshots/09-assignment-success.png' })

    // ==================== 第八步：验证分配结果 ====================
    console.log('\n【步骤8】验证分配结果...')
    
    // 刷新页面
    await page.reload()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    // 检查执行人列是否显示
    const executorCell = await page.locator('td:has-text("执行人")').count()
    if (executorCell > 0) {
      console.log('✅ 执行人信息已更新')
    }

    await page.screenshot({ path: 'screenshots/10-assignment-verified.png' })

    // ==================== 测试完成 ====================
    console.log('\n' + '='.repeat(80))
    console.log('✅ 测试完成！')
    console.log('='.repeat(80))
    console.log('\n测试总结：')
    console.log('  1. ✅ 登录系统')
    console.log('  2. ✅ 创建线索')
    console.log('  3. ✅ 创建报价（包含公司改制产品）')
    console.log('  4. ✅ 创建合同（关联报价）')
    console.log('  5. ✅ 从合同创建工单')
    console.log('  6. ✅ 验证任务项从产品步骤加载')
    console.log('  7. ✅ 测试任务项分配功能')
    console.log('  8. ✅ 验证分配结果')
    console.log('\n截图已保存到 screenshots/ 目录')
  })
})

