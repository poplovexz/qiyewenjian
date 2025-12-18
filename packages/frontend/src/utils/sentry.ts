/**
 * Sentry 错误监控配置
 * 用于捕获和上报前端错误、性能数据
 */
import * as Sentry from '@sentry/vue'
import type { App } from 'vue'
import type { Router } from 'vue-router'

// Sentry 配置选项
interface SentryConfig {
  dsn: string
  environment: string
  release?: string
  tracesSampleRate?: number
  replaysSessionSampleRate?: number
  replaysOnErrorSampleRate?: number
}

// 默认配置
const defaultConfig: Partial<SentryConfig> = {
  tracesSampleRate: 0.1, // 采样 10% 的请求进行性能追踪
  replaysSessionSampleRate: 0.1, // 采样 10% 的会话进行回放
  replaysOnErrorSampleRate: 1.0, // 100% 错误会话进行回放
}

/**
 * 初始化 Sentry
 */
export function initSentry(app: App, router: Router): void {
  const dsn = import.meta.env.VITE_SENTRY_DSN
  const environment = import.meta.env.MODE || 'development'
  const release = import.meta.env.VITE_APP_VERSION || '1.0.0'

  // 如果没有配置 DSN，跳过初始化
  if (!dsn) {
    
    return
  }

  try {
    Sentry.init({
      app,
      dsn,
      environment,
      release: `qiyewenjian-frontend@${release}`,
      
      // 性能监控
      tracesSampleRate: defaultConfig.tracesSampleRate,
      
      // 路由追踪
      integrations: [
        Sentry.browserTracingIntegration({ router }),
        Sentry.replayIntegration({
          maskAllText: false,
          blockAllMedia: false,
        }),
      ],
      
      // 会话回放
      replaysSessionSampleRate: defaultConfig.replaysSessionSampleRate,
      replaysOnErrorSampleRate: defaultConfig.replaysOnErrorSampleRate,

      // 错误过滤
      beforeSend(event, hint) {
        const error = hint.originalException

        // 过滤掉网络错误（通常是用户网络问题）
        if (error instanceof Error) {
          if (error.message.includes('Network Error') ||
              error.message.includes('Failed to fetch') ||
              error.message.includes('Load failed')) {
            return null
          }
        }

        // 过滤掉取消的请求
        if (error && typeof error === 'object' && 'code' in error) {
          if ((error as { code: string }).code === 'ERR_CANCELED') {
            return null
          }
        }

        return event
      },

      // 忽略的错误
      ignoreErrors: [
        'ResizeObserver loop limit exceeded',
        'ResizeObserver loop completed with undelivered notifications',
        'Non-Error promise rejection captured',
        /^Loading chunk .* failed/,
        /^ChunkLoadError/,
      ],

      // 允许的 URL
      allowUrls: [
        /https?:\/\/(www\.)?qiyewenjian\.com/,
        /https?:\/\/localhost/,
        /https?:\/\/127\.0\.0\.1/,
      ],
    })

    
  } catch (error) {
    console.error('[Sentry] Failed to initialize:', error)
  }
}

/**
 * 设置用户上下文
 */
export function setUser(user: { id: string | number; username?: string; email?: string; role?: string }): void {
  Sentry.setUser({
    id: String(user.id),
    username: user.username,
    email: user.email,
    role: user.role,
  })
}

/**
 * 清除用户上下文（退出登录时调用）
 */
export function clearUser(): void {
  Sentry.setUser(null)
}

/**
 * 添加面包屑
 */
export function addBreadcrumb(message: string, category?: string, data?: Record<string, unknown>): void {
  Sentry.addBreadcrumb({
    message,
    category: category || 'custom',
    level: 'info',
    data,
  })
}

/**
 * 手动捕获异常
 */
export function captureException(error: Error, context?: Record<string, unknown>): void {
  Sentry.captureException(error, {
    extra: context,
  })
}

/**
 * 手动捕获消息
 */
export function captureMessage(message: string, level: 'info' | 'warning' | 'error' = 'info'): void {
  Sentry.captureMessage(message, level)
}

/**
 * 设置标签
 */
export function setTag(key: string, value: string): void {
  Sentry.setTag(key, value)
}

/**
 * 设置额外上下文
 */
export function setExtra(key: string, value: unknown): void {
  Sentry.setExtra(key, value)
}

// 导出 Sentry 实例供高级用法
export { Sentry }

