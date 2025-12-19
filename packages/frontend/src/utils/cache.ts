/**
 * 前端缓存工具类
 * 提供内存缓存和本地存储缓存功能
 */

export interface CacheItem<T = any> {
  data: T
  timestamp: number
  expireTime?: number
}

export interface CacheOptions {
  /** 缓存过期时间（毫秒），默认5分钟 */
  expireTime?: number
  /** 是否使用本地存储，默认false（使用内存缓存） */
  useLocalStorage?: boolean
  /** 本地存储的key前缀 */
  storagePrefix?: string
}

/**
 * 内存缓存管理器
 */
export class MemoryCache {
  private cache = new Map<string, CacheItem>()
  private defaultExpireTime: number

  constructor(defaultExpireTime = 5 * 60 * 1000) {
    this.defaultExpireTime = defaultExpireTime
  }

  /**
   * 设置缓存
   */
  set<T>(key: string, data: T, expireTime?: number): void {
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      expireTime: expireTime || this.defaultExpireTime,
    }
    this.cache.set(key, item)
  }

  /**
   * 获取缓存
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key)
    if (!item) {
      return null
    }

    const now = Date.now()
    const isExpired = item.expireTime && now - item.timestamp > item.expireTime

    if (isExpired) {
      this.cache.delete(key)
      return null
    }

    return item.data as T
  }

  /**
   * 检查缓存是否存在且有效
   */
  has(key: string): boolean {
    return this.get(key) !== null
  }

  /**
   * 删除缓存
   */
  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
  }

  /**
   * 获取缓存大小
   */
  size(): number {
    return this.cache.size
  }

  /**
   * 清理过期缓存
   */
  cleanup(): void {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (item.expireTime && now - item.timestamp > item.expireTime) {
        this.cache.delete(key)
      }
    }
  }
}

/**
 * 本地存储缓存管理器
 */
export class LocalStorageCache {
  private prefix: string
  private defaultExpireTime: number

  constructor(prefix = 'cache_', defaultExpireTime = 5 * 60 * 1000) {
    this.prefix = prefix
    this.defaultExpireTime = defaultExpireTime
  }

  private getKey(key: string): string {
    return `${this.prefix}${key}`
  }

  /**
   * 设置缓存
   */
  set<T>(key: string, data: T, expireTime?: number): void {
    try {
      const item: CacheItem<T> = {
        data,
        timestamp: Date.now(),
        expireTime: expireTime || this.defaultExpireTime,
      }
      localStorage.setItem(this.getKey(key), JSON.stringify(item))
    } catch (error) {}
  }

  /**
   * 获取缓存
   */
  get<T>(key: string): T | null {
    try {
      const itemStr = localStorage.getItem(this.getKey(key))
      if (!itemStr) {
        return null
      }

      const item: CacheItem<T> = JSON.parse(itemStr)
      const now = Date.now()
      const isExpired = item.expireTime && now - item.timestamp > item.expireTime

      if (isExpired) {
        localStorage.removeItem(this.getKey(key))
        return null
      }

      return item.data
    } catch (error) {
      return null
    }
  }

  /**
   * 检查缓存是否存在且有效
   */
  has(key: string): boolean {
    return this.get(key) !== null
  }

  /**
   * 删除缓存
   */
  delete(key: string): boolean {
    try {
      localStorage.removeItem(this.getKey(key))
      return true
    } catch (error) {
      return false
    }
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    try {
      const keys = Object.keys(localStorage)
      keys.forEach((key) => {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key)
        }
      })
    } catch (error) {}
  }

  /**
   * 清理过期缓存
   */
  cleanup(): void {
    try {
      const keys = Object.keys(localStorage)
      const now = Date.now()

      keys.forEach((key) => {
        if (key.startsWith(this.prefix)) {
          try {
            const itemStr = localStorage.getItem(key)
            if (itemStr) {
              const item: CacheItem = JSON.parse(itemStr)
              if (item.expireTime && now - item.timestamp > item.expireTime) {
                localStorage.removeItem(key)
              }
            }
          } catch (error) {
            // 解析失败的项目直接删除
            localStorage.removeItem(key)
          }
        }
      })
    } catch (error) {}
  }
}

/**
 * 统一缓存管理器
 */
export class CacheManager {
  private memoryCache: MemoryCache
  private localStorageCache: LocalStorageCache

  constructor(options: CacheOptions = {}) {
    this.memoryCache = new MemoryCache(options.expireTime)
    this.localStorageCache = new LocalStorageCache(options.storagePrefix, options.expireTime)
  }

  /**
   * 设置缓存
   */
  set<T>(key: string, data: T, options: CacheOptions = {}): void {
    if (options.useLocalStorage) {
      this.localStorageCache.set(key, data, options.expireTime)
    } else {
      this.memoryCache.set(key, data, options.expireTime)
    }
  }

  /**
   * 获取缓存
   */
  get<T>(key: string, useLocalStorage = false): T | null {
    if (useLocalStorage) {
      return this.localStorageCache.get<T>(key)
    } else {
      return this.memoryCache.get<T>(key)
    }
  }

  /**
   * 检查缓存是否存在且有效
   */
  has(key: string, useLocalStorage = false): boolean {
    if (useLocalStorage) {
      return this.localStorageCache.has(key)
    } else {
      return this.memoryCache.has(key)
    }
  }

  /**
   * 删除缓存
   */
  delete(key: string, useLocalStorage = false): boolean {
    if (useLocalStorage) {
      return this.localStorageCache.delete(key)
    } else {
      return this.memoryCache.delete(key)
    }
  }

  /**
   * 清空所有缓存
   */
  clear(useLocalStorage = false): void {
    if (useLocalStorage) {
      this.localStorageCache.clear()
    } else {
      this.memoryCache.clear()
    }
  }

  /**
   * 清空所有缓存（内存和本地存储）
   */
  clearAll(): void {
    this.memoryCache.clear()
    this.localStorageCache.clear()
  }

  /**
   * 清理过期缓存
   */
  cleanup(): void {
    this.memoryCache.cleanup()
    this.localStorageCache.cleanup()
  }
}

// 创建默认的缓存管理器实例
export const defaultCache = new CacheManager({
  expireTime: 5 * 60 * 1000, // 5分钟
  storagePrefix: 'app_cache_',
})

// 导出常用的缓存时间常量
export const CACHE_TIME = {
  MINUTE_1: 1 * 60 * 1000,
  MINUTE_5: 5 * 60 * 1000,
  MINUTE_15: 15 * 60 * 1000,
  MINUTE_30: 30 * 60 * 1000,
  HOUR_1: 60 * 60 * 1000,
  HOUR_24: 24 * 60 * 60 * 1000,
} as const
