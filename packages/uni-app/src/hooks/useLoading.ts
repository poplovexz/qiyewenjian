/**
 * 加载状态 Hook
 */
import { ref } from 'vue'

export const useLoading = (initialValue = false) => {
  const loading = ref(initialValue)

  const startLoading = () => {
    loading.value = true
  }

  const stopLoading = () => {
    loading.value = false
  }

  // 包装异步函数，自动管理 loading 状态
  const withLoading = async <T>(fn: () => Promise<T>): Promise<T> => {
    try {
      startLoading()
      return await fn()
    } finally {
      stopLoading()
    }
  }

  return {
    loading,
    startLoading,
    stopLoading,
    withLoading
  }
}

