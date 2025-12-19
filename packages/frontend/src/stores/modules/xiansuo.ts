/**
 * 线索管理状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  xiansuoApi,
  xiansuoLaiyuanApi,
  xiansuoZhuangtaiApi,
  xiansuoGenjinApi,
  xiansuoBaojiaApi,
} from '@/api/modules/xiansuo'
import type {
  Xiansuo,
  XiansuoCreate,
  XiansuoUpdate,
  XiansuoDetail,
  XiansuoListParams,
  XiansuoStatusUpdate,
  XiansuoAssignUpdate,
  XiansuoStatistics,
  XiansuoLaiyuan,
  XiansuoLaiyuanCreate,
  XiansuoLaiyuanUpdate,
  XiansuoLaiyuanListParams,
  XiansuoZhuangtai,
  XiansuoGenjin,
  XiansuoGenjinCreate,
  XiansuoBaojia,
  XiansuoBaojiaCreate,
  XiansuoBaojiaUpdate,
  XiansuoBaojiaDetail,
  ChanpinDataForBaojia,
} from '@/types/xiansuo'

export const useXiansuoStore = defineStore('xiansuo', () => {
  // 状态
  const loading = ref(false)
  const xiansuo_list = ref<Xiansuo[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 线索来源
  const laiyuan_list = ref<XiansuoLaiyuan[]>([])
  const active_laiyuan_list = ref<XiansuoLaiyuan[]>([])

  // 线索状态
  const zhuangtai_list = ref<XiansuoZhuangtai[]>([])
  const active_zhuangtai_list = ref<XiansuoZhuangtai[]>([])

  // 跟进记录
  const genjin_list = ref<XiansuoGenjin[]>([])

  // 报价相关
  const baojiaMap = ref<Record<string, XiansuoBaojia[]>>({})
  const current_baojia = ref<XiansuoBaojia | null>(null)
  const product_data = ref<ChanpinDataForBaojia | null>(null)

  // 统计数据
  const statistics = ref<XiansuoStatistics | null>(null)

  // 缓存控制
  const cache = ref({
    laiyuan_loaded: false,
    laiyuan_timestamp: 0,
    zhuangtai_loaded: false,
    zhuangtai_timestamp: 0,
    statistics_loaded: false,
    statistics_timestamp: 0,
    xiansuo_cache: new Map<string, { data: Xiansuo[]; total: number; timestamp: number }>(),
  })

  // 缓存过期时间（5分钟）
  const CACHE_EXPIRE_TIME = 5 * 60 * 1000

  // 计算属性
  const newXiansuo = computed(
    () => xiansuo_list.value.filter((x) => x.xiansuo_zhuangtai === 'new').length
  )

  const followingXiansuo = computed(
    () => xiansuo_list.value.filter((x) => x.xiansuo_zhuangtai === 'following').length
  )

  const interestedXiansuo = computed(
    () => xiansuo_list.value.filter((x) => x.xiansuo_zhuangtai === 'interested').length
  )

  const wonXiansuo = computed(
    () => xiansuo_list.value.filter((x) => x.xiansuo_zhuangtai === 'won').length
  )

  // 线索管理方法
  const fetchXiansuoList = async (params: XiansuoListParams = {}, forceRefresh = false) => {
    try {
      loading.value = true

      // 生成缓存键
      const cacheKey = JSON.stringify({
        page: params.page || currentPage.value,
        size: params.size || pageSize.value,
        search: params.search || '',
        xiansuo_zhuangtai: params.xiansuo_zhuangtai || '',
        laiyuan_id: params.laiyuan_id || '',
        zhiliang_pinggu: params.zhiliang_pinggu || '',
      })

      // 检查缓存
      const now = Date.now()
      const cachedData = cache.value.xiansuo_cache.get(cacheKey)
      const isExpired = cachedData ? now - cachedData.timestamp > CACHE_EXPIRE_TIME : true

      if (!forceRefresh && cachedData && !isExpired) {
        xiansuo_list.value = cachedData.data
        total.value = cachedData.total
        currentPage.value = params.page || currentPage.value
        pageSize.value = params.size || pageSize.value

        // 即使使用缓存数据，也要预取报价信息以确保按钮状态正确

        await prefetchBaojiaForLeads(cachedData.data)

        return
      }

      const requestParams = {
        page: params.page || currentPage.value,
        size: params.size || pageSize.value,
        search: params.search || '',
        xiansuo_zhuangtai: params.xiansuo_zhuangtai || '',
        laiyuan_id: params.laiyuan_id || '',
        zhiliang_pinggu: params.zhiliang_pinggu || '',
      }
      const response = await xiansuoApi.getList(requestParams)

      xiansuo_list.value = response.items
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      // 更新缓存
      cache.value.xiansuo_cache.set(cacheKey, {
        data: response.items,
        total: response.total,
        timestamp: now,
      })

      // 预取报价信息，保证按钮状态准确

      await prefetchBaojiaForLeads(response.items)
    } catch (error) {
      ElMessage.error('获取线索列表失败')
    } finally {
      loading.value = false
    }
  }

  const createXiansuo = async (data: XiansuoCreate) => {
    try {
      loading.value = true
      await xiansuoApi.create(data)
      ElMessage.success('线索创建成功')
      // 清除线索列表缓存，强制重新加载
      cache.value.xiansuo_cache.clear()
      return true
    } catch (error) {
      ElMessage.error('创建线索失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const updateXiansuo = async (id: string, data: XiansuoUpdate) => {
    try {
      loading.value = true
      await xiansuoApi.update(id, data)
      ElMessage.success('线索更新成功')
      // 清除线索列表缓存，强制重新加载
      cache.value.xiansuo_cache.clear()
      return true
    } catch (error) {
      ElMessage.error('更新线索失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const deleteXiansuo = async (id: string) => {
    try {
      loading.value = true
      await xiansuoApi.delete(id)
      ElMessage.success('线索删除成功')
      // 清除线索列表缓存，强制重新加载
      cache.value.xiansuo_cache.clear()
      return true
    } catch (error) {
      ElMessage.error('删除线索失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const updateXiansuoStatus = async (id: string, data: XiansuoStatusUpdate) => {
    try {
      loading.value = true
      await xiansuoApi.updateStatus(id, data)
      ElMessage.success('线索状态更新成功')
      return true
    } catch (error) {
      ElMessage.error('更新线索状态失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const assignXiansuo = async (id: string, data: XiansuoAssignUpdate) => {
    try {
      loading.value = true
      await xiansuoApi.assign(id, data)
      ElMessage.success('线索分配成功')
      return true
    } catch (error) {
      ElMessage.error('分配线索失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const getXiansuoDetail = async (id: string): Promise<XiansuoDetail | null> => {
    try {
      loading.value = true
      const response = await xiansuoApi.getDetail(id)
      return response
    } catch (error) {
      ElMessage.error('获取线索详情失败')
      return null
    } finally {
      loading.value = false
    }
  }

  const fetchStatistics = async (
    params: { start_date?: string; end_date?: string; fenpei_ren_id?: string } = {}
  ) => {
    try {
      const response = await xiansuoApi.getStatistics(params)
      statistics.value = response
    } catch (error) {
      ElMessage.error('获取线索统计失败')
    }
  }

  // 线索来源管理方法
  const fetchLaiyuanList = async (params: XiansuoLaiyuanListParams = {}) => {
    try {
      loading.value = true
      const response = await xiansuoLaiyuanApi.getList(params)
      laiyuan_list.value = response.items
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size
    } catch (error) {
      ElMessage.error('获取线索来源列表失败')
    } finally {
      loading.value = false
    }
  }

  const fetchActiveLaiyuanList = async (forceRefresh = false) => {
    // 检查缓存是否有效
    const now = Date.now()
    const isExpired = now - cache.value.laiyuan_timestamp > CACHE_EXPIRE_TIME

    if (
      !forceRefresh &&
      cache.value.laiyuan_loaded &&
      !isExpired &&
      active_laiyuan_list.value.length > 0
    ) {
      return
    }

    try {
      const response = await xiansuoLaiyuanApi.getActiveList()
      active_laiyuan_list.value = response

      // 更新缓存状态
      cache.value.laiyuan_loaded = true
      cache.value.laiyuan_timestamp = now
    } catch (error) {
      ElMessage.error('获取启用线索来源失败')
    }
  }

  const createLaiyuan = async (data: XiansuoLaiyuanCreate) => {
    try {
      loading.value = true
      await xiansuoLaiyuanApi.create(data)
      ElMessage.success('线索来源创建成功')
      // 清除线索来源缓存，强制重新加载
      cache.value.laiyuan_loaded = false
      cache.value.laiyuan_timestamp = 0
      return true
    } catch (error) {
      ElMessage.error('创建线索来源失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 线索状态管理方法
  const fetchActiveZhuangtaiList = async (forceRefresh = false) => {
    // 检查缓存是否有效
    const now = Date.now()
    const isExpired = now - cache.value.zhuangtai_timestamp > CACHE_EXPIRE_TIME

    if (
      !forceRefresh &&
      cache.value.zhuangtai_loaded &&
      !isExpired &&
      active_zhuangtai_list.value.length > 0
    ) {
      return
    }

    try {
      const response = await xiansuoZhuangtaiApi.getActiveList()
      active_zhuangtai_list.value = response

      // 更新缓存状态
      cache.value.zhuangtai_loaded = true
      cache.value.zhuangtai_timestamp = now
    } catch (error) {
      ElMessage.error('获取启用线索状态失败')
    }
  }

  const fetchZhuangtaiList = async (
    params: {
      page?: number
      size?: number
      search?: string
      zhuangtai_leixing?: string
      zhuangtai?: string
    } = {}
  ) => {
    try {
      loading.value = true
      const response = await xiansuoZhuangtaiApi.getList(params)
      zhuangtai_list.value = response.items
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size
    } catch (error) {
      ElMessage.error('获取线索状态列表失败')
    } finally {
      loading.value = false
    }
  }

  const deleteZhuangtai = async (id: string) => {
    try {
      await xiansuoZhuangtaiApi.delete(id)
      // 清除缓存，强制重新获取
      cache.value.zhuangtai_loaded = false
    } catch (error) {
      ElMessage.error('删除线索状态失败')
      throw error
    }
  }

  // 跟进记录管理方法
  const createGenjin = async (data: XiansuoGenjinCreate) => {
    try {
      loading.value = true
      await xiansuoGenjinApi.create(data)
      ElMessage.success('跟进记录创建成功')
      return true
    } catch (error) {
      ElMessage.error('创建跟进记录失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const fetchGenjinByXiansuo = async (xiansuoId: string) => {
    try {
      const response = await xiansuoGenjinApi.getByXiansuo(xiansuoId)
      genjin_list.value = response
    } catch (error) {
      ElMessage.error('获取跟进记录失败')
    }
  }

  // 缓存管理方法
  const clearCache = () => {
    cache.value.laiyuan_loaded = false
    cache.value.laiyuan_timestamp = 0
    cache.value.zhuangtai_loaded = false
    cache.value.zhuangtai_timestamp = 0
    cache.value.statistics_loaded = false
    cache.value.statistics_timestamp = 0
    cache.value.xiansuo_cache.clear()
  }

  const clearXiansuoCache = () => {
    cache.value.xiansuo_cache.clear()
  }

  const refreshAllData = async () => {
    clearCache()
    await Promise.all([
      fetchActiveLaiyuanList(true),
      fetchActiveZhuangtaiList(true),
      fetchXiansuoList({}, true),
    ])
  }

  // 初始化数据（带缓存）
  const initializeData = async () => {
    await Promise.all([fetchActiveLaiyuanList(), fetchActiveZhuangtaiList()])
  }

  // 报价相关方法
  const quoteLoading = ref(false)

  const setBaojiaList = (xiansuoId: string, list: XiansuoBaojia[]) => {
    baojiaMap.value = {
      ...baojiaMap.value,
      [xiansuoId]: list,
    }
  }

  const prefetchBaojiaForLeads = async (leads: Xiansuo[]) => {
    const ids = leads.filter((lead) => !baojiaMap.value[lead.id]).map((lead) => lead.id)

    if (!ids.length) {
      return
    }

    await Promise.all(
      ids.map(async (id) => {
        try {
          const list = await xiansuoBaojiaApi.getByXiansuo(id)

          setBaojiaList(id, list)
        } catch (error) {
        }
      })
    )
  }

  const fetchBaojiaByXiansuo = async (xiansuoId: string, forceRefresh = false) => {
    if (!forceRefresh && baojiaMap.value[xiansuoId]) {
      return baojiaMap.value[xiansuoId]
    }

    try {
      quoteLoading.value = true
      const response = await xiansuoBaojiaApi.getByXiansuo(xiansuoId)
      setBaojiaList(xiansuoId, response)
      return response
    } catch (error) {
      ElMessage.error('获取报价信息失败')
      throw error
    } finally {
      quoteLoading.value = false
    }
  }

  const createBaojia = async (payload: XiansuoBaojiaCreate) => {
    try {
      quoteLoading.value = true
      const response = await xiansuoBaojiaApi.create(payload)
      current_baojia.value = response

      const list = baojiaMap.value[payload.xiansuo_id] || []
      setBaojiaList(payload.xiansuo_id, [response, ...list])

      ElMessage.success('报价创建成功')
      return response
    } catch (error) {
      ElMessage.error('创建报价失败')
      throw error
    } finally {
      quoteLoading.value = false
    }
  }

  const updateBaojia = async (id: string, data: XiansuoBaojiaUpdate) => {
    try {
      quoteLoading.value = true
      const response = await xiansuoBaojiaApi.update(id, data)
      current_baojia.value = response

      const list = baojiaMap.value[response.xiansuo_id] || []
      const updatedList = list.map((item) => (item.id === id ? response : item))
      setBaojiaList(response.xiansuo_id, updatedList)

      ElMessage.success('报价更新成功')
      return response
    } catch (error) {
      ElMessage.error('更新报价失败')
      throw error
    } finally {
      quoteLoading.value = false
    }
  }

  const deleteBaojia = async (xiansuoId: string, baojiaId: string) => {
    try {
      quoteLoading.value = true
      await xiansuoBaojiaApi.delete(baojiaId)

      const list = baojiaMap.value[xiansuoId] || []
      const updatedList = list.filter((item) => item.id !== baojiaId)
      setBaojiaList(xiansuoId, updatedList)
      if (current_baojia.value?.id === baojiaId) {
        current_baojia.value = null
      }

      ElMessage.success('报价删除成功')
    } catch (error) {
      ElMessage.error('删除报价失败')
      throw error
    } finally {
      quoteLoading.value = false
    }
  }

  const confirmBaojia = async (id: string) => {
    try {
      quoteLoading.value = true
      const response = await xiansuoBaojiaApi.confirm(id)
      current_baojia.value = response

      // 更新缓存中的报价状态
      const list = baojiaMap.value[response.xiansuo_id] || []
      const updatedList = list.map((item) => (item.id === id ? response : item))
      setBaojiaList(response.xiansuo_id, updatedList)

      return response
    } catch (error) {
      throw error
    } finally {
      quoteLoading.value = false
    }
  }

  const rejectBaojia = async (id: string) => {
    try {
      quoteLoading.value = true
      const response = await xiansuoBaojiaApi.reject(id)
      current_baojia.value = response

      // 更新缓存中的报价状态
      const list = baojiaMap.value[response.xiansuo_id] || []
      const updatedList = list.map((item) => (item.id === id ? response : item))
      setBaojiaList(response.xiansuo_id, updatedList)

      return response
    } catch (error) {
      throw error
    } finally {
      quoteLoading.value = false
    }
  }

  const fetchProductData = async () => {
    try {
      const response = await xiansuoBaojiaApi.getProductData()

      product_data.value = response

      return response
    } catch (error) {
      ElMessage.error('获取产品数据失败')
      throw error
    }
  }

  // 辅助方法：检查特定线索是否有有效报价
  const hasValidBaojia = (xiansuoId: string): boolean => {
    const baojiaList = baojiaMap.value[xiansuoId] || []

    if (baojiaList.length > 0) {
      baojiaList.forEach((b, index) => {})
    }

    const hasValid = baojiaList.some((b) => !b.is_expired && b.baojia_zhuangtai !== 'rejected')

    return hasValid
  }

  const getBaojiaListByXiansuo = (xiansuoId: string): XiansuoBaojia[] => {
    return baojiaMap.value[xiansuoId] || []
  }

  const getBaojiaDetail = async (id: string) => {
    try {
      const response = await xiansuoBaojiaApi.getDetail(id)
      current_baojia.value = response
      return response
    } catch (error) {
      ElMessage.error('获取报价详情失败')
      throw error
    }
  }

  const getBaojiaDetailWithXiansuo = async (id: string): Promise<XiansuoBaojiaDetail> => {
    try {
      return await xiansuoBaojiaApi.getDetailWithXiansuo(id)
    } catch (error) {
      throw error
    }
  }

  return {
    // 状态
    loading,
    xiansuo_list,
    total,
    currentPage,
    pageSize,
    laiyuan_list,
    active_laiyuan_list,
    zhuangtai_list,
    active_zhuangtai_list,
    genjin_list,
    baojiaMap,
    current_baojia,
    product_data,
    quoteLoading,
    statistics,
    cache,

    // 计算属性
    newXiansuo,
    followingXiansuo,
    interestedXiansuo,
    wonXiansuo,

    // 方法
    fetchXiansuoList,
    createXiansuo,
    updateXiansuo,
    deleteXiansuo,
    updateXiansuoStatus,
    assignXiansuo,
    getXiansuoDetail,
    fetchStatistics,
    fetchLaiyuanList,
    fetchActiveLaiyuanList,
    createLaiyuan,
    fetchActiveZhuangtaiList,
    fetchZhuangtaiList,
    deleteZhuangtai,
    createGenjin,
    fetchGenjinByXiansuo,

    // 报价相关方法
    fetchBaojiaByXiansuo,
    createBaojia,
    updateBaojia,
    deleteBaojia,
    confirmBaojia,
    rejectBaojia,
    fetchProductData,
    getBaojiaDetail,
    getBaojiaDetailWithXiansuo,
    hasValidBaojia,
    getBaojiaListByXiansuo,
    prefetchBaojiaForLeads,

    // 缓存管理方法
    clearCache,
    clearXiansuoCache,
    refreshAllData,
    initializeData,
  }
})
