import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright 配置文件
 * 用于端到端测试
 */
export default defineConfig({
  testDir: './tests',
  
  // 测试超时时间
  timeout: 60000,
  
  // 每个测试的重试次数
  retries: 0,
  
  // 并行执行的worker数量
  workers: 1,
  
  // 报告配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  
  // 全局配置
  use: {
    // 基础URL
    baseURL: 'http://localhost:5174',
    
    // 浏览器上下文选项
    viewport: { width: 1920, height: 1080 },
    
    // 截图配置
    screenshot: 'only-on-failure',
    
    // 视频录制
    video: 'retain-on-failure',
    
    // 追踪
    trace: 'retain-on-failure',
    
    // 操作超时
    actionTimeout: 10000,
    
    // 导航超时
    navigationTimeout: 30000,
  },

  // 项目配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Web服务器配置（可选）
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:5174',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },
})

