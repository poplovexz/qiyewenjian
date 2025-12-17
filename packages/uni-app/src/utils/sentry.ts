/**
 * Sentry 错误监控 - uni-app 适配版本
 * 由于 uni-app 环境特殊，使用轻量级实现
 */
import { appConfig } from './config'

// Sentry 配置
interface SentryConfig {
  dsn: string
  environment: string
  release: string
  enabled: boolean
}

// 错误上报数据结构
interface ErrorReport {
  message: string
  stack?: string
  level: 'error' | 'warning' | 'info'
  tags: Record<string, string>
  extra: Record<string, unknown>
  user?: { id: string; username?: string }
  timestamp: string
  platform: string
  release: string
  environment: string
}

// 配置
const config: SentryConfig = {
  dsn: '', // 从环境变量或配置获取
  environment: appConfig.env,
  release: `qiyewenjian-uniapp@${appConfig.version}`,
  enabled: !appConfig.isDev // 开发环境默认不上报
}

// 用户信息
let currentUser: { id: string; username?: string } | null = null

// 面包屑队列
const breadcrumbs: Array<{ message: string; category: string; timestamp: string; data?: Record<string, unknown> }> = []
const MAX_BREADCRUMBS = 50

/**
 * 初始化 Sentry
 */
export function initSentry(dsn?: string): void {
  if (dsn) {
    config.dsn = dsn
    config.enabled = true
  }
  
  if (!config.dsn) {
    console.log('[Sentry] DSN not configured, error reporting disabled')
    return
  }

  // 监听全局错误
  uni.onError((error: string) => {
    captureException(new Error(error))
  })

  // 监听未处理的 Promise 拒绝
  uni.onUnhandledRejection?.((res: { reason: unknown }) => {
    const error = res.reason instanceof Error ? res.reason : new Error(String(res.reason))
    captureException(error)
  })

  console.log(`[Sentry] Initialized for ${config.environment} environment`)
}

/**
 * 设置用户
 */
export function setUser(user: { id: string | number; username?: string }): void {
  currentUser = { id: String(user.id), username: user.username }
}

/**
 * 清除用户
 */
export function clearUser(): void {
  currentUser = null
}

/**
 * 添加面包屑
 */
export function addBreadcrumb(message: string, category = 'custom', data?: Record<string, unknown>): void {
  breadcrumbs.push({
    message,
    category,
    timestamp: new Date().toISOString(),
    data
  })
  
  // 保持队列长度
  if (breadcrumbs.length > MAX_BREADCRUMBS) {
    breadcrumbs.shift()
  }
}

/**
 * 捕获异常
 */
export function captureException(error: Error, context?: Record<string, unknown>): void {
  if (!config.enabled || !config.dsn) {
    console.error('[Sentry] Error (not reported):', error)
    return
  }

  const report: ErrorReport = {
    message: error.message,
    stack: error.stack,
    level: 'error',
    tags: { source: 'uni-app' },
    extra: { ...context, breadcrumbs: [...breadcrumbs] },
    user: currentUser || undefined,
    timestamp: new Date().toISOString(),
    platform: getPlatform(),
    release: config.release,
    environment: config.environment
  }

  sendToSentry(report)
}

/**
 * 捕获消息
 */
export function captureMessage(message: string, level: 'info' | 'warning' | 'error' = 'info'): void {
  if (!config.enabled || !config.dsn) return

  const report: ErrorReport = {
    message,
    level,
    tags: { source: 'uni-app' },
    extra: { breadcrumbs: [...breadcrumbs] },
    user: currentUser || undefined,
    timestamp: new Date().toISOString(),
    platform: getPlatform(),
    release: config.release,
    environment: config.environment
  }

  sendToSentry(report)
}

/**
 * 获取平台信息
 */
function getPlatform(): string {
  const systemInfo = uni.getSystemInfoSync()
  return `${systemInfo.platform || 'unknown'}/${systemInfo.system || 'unknown'}`
}

/**
 * 发送到 Sentry
 */
function sendToSentry(report: ErrorReport): void {
  // 使用 Sentry Store API 上报
  // 实际项目中应该使用 Sentry 的官方 API
  uni.request({
    url: config.dsn.replace('https://', 'https://sentry.io/api/').replace('@', '/store/?sentry_key='),
    method: 'POST',
    header: { 'Content-Type': 'application/json' },
    data: report,
    fail: (err) => {
      console.error('[Sentry] Failed to send error report:', err)
    }
  })
}

