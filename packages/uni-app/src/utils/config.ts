/**
 * 环境配置 - 企业级多环境
 */

// 环境类型
type EnvType = 'development' | 'test' | 'production'

// 当前环境
const ENV: EnvType = (import.meta.env.MODE as EnvType) || 'development'

// 环境配置
interface EnvConfig {
  apiBaseUrl: string
  uploadUrl: string
  wsUrl: string
  debug: boolean
}

const ENV_CONFIG: Record<EnvType, EnvConfig> = {
  development: {
    apiBaseUrl: 'http://localhost:8000/api/v1',
    uploadUrl: 'http://localhost:8000/api/v1/upload',
    wsUrl: 'ws://localhost:8000/ws',
    debug: true
  },
  test: {
    apiBaseUrl: 'https://test-api.example.com/api/v1',
    uploadUrl: 'https://test-api.example.com/api/v1/upload',
    wsUrl: 'wss://test-api.example.com/ws',
    debug: true
  },
  production: {
    apiBaseUrl: 'https://api.example.com/api/v1',
    uploadUrl: 'https://api.example.com/api/v1/upload',
    wsUrl: 'wss://api.example.com/ws',
    debug: false
  }
}

// 当前环境配置
const currentConfig = ENV_CONFIG[ENV]

// 应用配置
export const appConfig = {
  // 环境
  env: ENV,
  isDev: ENV === 'development',
  isProd: ENV === 'production',

  // 应用信息
  appName: '服务人员任务管理',
  version: '1.0.0',

  // API 配置
  apiBaseUrl: currentConfig.apiBaseUrl,
  uploadUrl: currentConfig.uploadUrl,
  wsUrl: currentConfig.wsUrl,

  // 请求配置
  requestTimeout: 30000,
  retryCount: 3,

  // 调试模式
  debug: currentConfig.debug,

  // 存储 Key 前缀
  storagePrefix: 'task_app_'
}

export default appConfig

