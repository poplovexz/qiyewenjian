/**
 * 路由拦截和登录检查
 */

// 白名单页面（不需要登录）
const whiteList = ['/pages/login/index']

// 检查是否已登录
export const isLoggedIn = (): boolean => {
  const token = uni.getStorageSync('token')
  return !!token
}

// 路由拦截器
export const setupRouterGuard = () => {
  // 拦截 uni.switchTab
  const originalSwitchTab = uni.switchTab
  uni.switchTab = (options) => {
    if (!isLoggedIn() && !whiteList.includes(options.url)) {
      return uni.reLaunch({ url: '/pages/login/index' })
    }
    return originalSwitchTab(options)
  }

  // 拦截 uni.navigateTo
  const originalNavigateTo = uni.navigateTo
  uni.navigateTo = (options) => {
    const url = options.url.split('?')[0]
    if (!isLoggedIn() && !whiteList.includes(url)) {
      return uni.reLaunch({ url: '/pages/login/index' })
    }
    return originalNavigateTo(options)
  }

  // 拦截 uni.redirectTo
  const originalRedirectTo = uni.redirectTo
  uni.redirectTo = (options) => {
    const url = options.url.split('?')[0]
    if (!isLoggedIn() && !whiteList.includes(url)) {
      return uni.reLaunch({ url: '/pages/login/index' })
    }
    return originalRedirectTo(options)
  }
}

// 检查登录状态并跳转
export const checkLoginAndRedirect = () => {
  if (!isLoggedIn()) {
    uni.reLaunch({ url: '/pages/login/index' })
    return false
  }
  return true
}

