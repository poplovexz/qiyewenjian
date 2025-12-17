/**
 * 分页 Hook
 */
import { ref, computed } from 'vue'
import { PAGINATION } from '@/constants'

interface PaginationOptions {
  page?: number
  pageSize?: number
}

export const usePagination = <T>(
  fetchFn: (params: { page: number; pageSize: number }) => Promise<{ items: T[]; total: number }>,
  options: PaginationOptions = {}
) => {
  const list = ref<T[]>([]) as { value: T[] }
  const loading = ref(false)
  const refreshing = ref(false)
  const finished = ref(false)
  const page = ref(options.page || PAGINATION.PAGE)
  const pageSize = ref(options.pageSize || PAGINATION.PAGE_SIZE)
  const total = ref(0)

  // 是否有更多数据
  const hasMore = computed(() => list.value.length < total.value)

  // 加载数据
  const loadData = async (isRefresh = false) => {
    if (loading.value) return
    
    if (isRefresh) {
      refreshing.value = true
      page.value = 1
      finished.value = false
    }
    
    loading.value = true
    
    try {
      const res = await fetchFn({ page: page.value, pageSize: pageSize.value })
      
      if (isRefresh) {
        list.value = res.items
      } else {
        list.value = [...list.value, ...res.items]
      }
      
      total.value = res.total
      
      if (list.value.length >= res.total) {
        finished.value = true
      } else {
        page.value++
      }
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      loading.value = false
      refreshing.value = false
    }
  }

  // 刷新
  const refresh = () => loadData(true)

  // 加载更多
  const loadMore = () => {
    if (!finished.value && !loading.value) {
      loadData(false)
    }
  }

  // 重置
  const reset = () => {
    list.value = []
    page.value = 1
    total.value = 0
    finished.value = false
  }

  return {
    list,
    loading,
    refreshing,
    finished,
    page,
    pageSize,
    total,
    hasMore,
    loadData,
    refresh,
    loadMore,
    reset
  }
}

