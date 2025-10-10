/**
 * 服务工单管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { request } from '@/utils/request'

// 服务工单接口定义
export interface ServiceOrder {
  id: string
  gongdan_bianhao: string
  hetong_id: string
  kehu_id: string
  zhixing_ren_id?: string
  gongdan_biaoti: string
  gongdan_miaoshu?: string
  fuwu_leixing: string
  youxian_ji: string
  gongdan_zhuangtai: string
  jihua_kaishi_shijian?: string
  jihua_jieshu_shijian: string
  shiji_kaishi_shijian?: string
  shiji_jieshu_shijian?: string
  fenpei_shijian?: string
  fenpei_ren_id?: string
  fenpei_beizhu?: string
  wancheng_qingkuang?: string
  jiaofei_wenjian?: string
  kehu_queren_shijian?: string
  kehu_pingjia?: string
  kehu_pingjia_neirong?: string
  created_at: string
  updated_at: string
  created_by: string
  is_overdue: boolean
  progress_percentage: number
  xiangmu_list?: ServiceOrderItem[]
  rizhi_list?: ServiceOrderLog[]
}

export interface ServiceOrderItem {
  id: string
  gongdan_id: string
  xiangmu_mingcheng: string
  xiangmu_miaoshu?: string
  xiangmu_zhuangtai: string
  paixu: number
  jihua_gongshi?: number
  shiji_gongshi?: number
  kaishi_shijian?: string
  jieshu_shijian?: string
  beizhu?: string
  created_at: string
  updated_at: string
}

export interface ServiceOrderLog {
  id: string
  gongdan_id: string
  caozuo_leixing: string
  caozuo_neirong: string
  caozuo_ren_id: string
  fujian_lujing?: string
  created_at: string
}

export interface ServiceOrderStatistics {
  total_count: number
  created_count: number
  assigned_count: number
  in_progress_count: number
  pending_review_count: number
  completed_count: number
  cancelled_count: number
  overdue_count: number
  avg_completion_days: number
  completion_rate: number
}

export interface ServiceOrderListParams {
  page: number
  size: number
  gongdan_bianhao?: string
  gongdan_biaoti?: string
  fuwu_leixing?: string
  gongdan_zhuangtai?: string
  youxian_ji?: string
  zhixing_ren_id?: string
  kehu_id?: string
  hetong_id?: string
  is_overdue?: boolean
}

export interface ServiceOrderCreateData {
  hetong_id: string
  kehu_id: string
  zhixing_ren_id?: string
  gongdan_biaoti: string
  gongdan_miaoshu?: string
  fuwu_leixing: string
  youxian_ji: string
  jihua_kaishi_shijian?: string
  jihua_jieshu_shijian: string
  fenpei_beizhu?: string
  xiangmu_list?: ServiceOrderItemCreate[]
}

export interface ServiceOrderItemCreate {
  xiangmu_mingcheng: string
  xiangmu_miaoshu?: string
  paixu: number
  jihua_gongshi?: number
  beizhu?: string
}

export const useServiceOrderStore = defineStore('serviceOrder', () => {
  // 状态
  const serviceOrders = ref<ServiceOrder[]>([])
  const currentServiceOrder = ref<ServiceOrder | null>(null)
  const statistics = ref<ServiceOrderStatistics | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 计算属性
  const hasServiceOrders = computed(() => serviceOrders.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 状态映射
  const statusMap = {
    created: '已创建',
    assigned: '已分配',
    in_progress: '进行中',
    pending_review: '待审核',
    completed: '已完成',
    cancelled: '已取消'
  }

  const priorityMap = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }

  const serviceTypeMap = {
    daili_jizhang: '代理记账',
    shuiwu_shenbao: '税务申报',
    caiwu_zixun: '财务咨询',
    qita_fuwu: '其他服务'
  }

  // 获取服务工单列表
  const fetchServiceOrders = async (params: ServiceOrderListParams) => {
    loading.value = true
    try {
      const response = await request.get('/api/v1/service-orders/', { params })
      serviceOrders.value = response.data.items
      total.value = response.data.total
      currentPage.value = response.data.page
      return response.data
    } catch (error) {
      console.error('获取服务工单列表失败:', error)
      ElMessage.error('获取服务工单列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取服务工单详情
  const fetchServiceOrderDetail = async (id: string) => {
    loading.value = true
    try {
      const response = await request.get(`/api/v1/service-orders/${id}`)
      currentServiceOrder.value = response.data
      return response.data
    } catch (error) {
      console.error('获取服务工单详情失败:', error)
      ElMessage.error('获取服务工单详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建服务工单
  const createServiceOrder = async (data: ServiceOrderCreateData) => {
    loading.value = true
    try {
      const response = await request.post('/api/v1/service-orders/', data)
      ElMessage.success('创建服务工单成功')
      return response.data
    } catch (error) {
      console.error('创建服务工单失败:', error)
      ElMessage.error('创建服务工单失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 基于合同创建服务工单
  const createServiceOrderFromContract = async (hetongId: string) => {
    loading.value = true
    try {
      const response = await request.post(`/api/v1/service-orders/from-contract/${hetongId}`)
      ElMessage.success('基于合同创建服务工单成功')
      return response.data
    } catch (error) {
      console.error('基于合同创建服务工单失败:', error)
      ElMessage.error('基于合同创建服务工单失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新服务工单
  const updateServiceOrder = async (id: string, data: Partial<ServiceOrderCreateData>) => {
    loading.value = true
    try {
      const response = await request.put(`/api/v1/service-orders/${id}`, data)
      ElMessage.success('更新服务工单成功')
      return response.data
    } catch (error) {
      console.error('更新服务工单失败:', error)
      ElMessage.error('更新服务工单失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 分配工单
  const assignServiceOrder = async (id: string, zhixingRenId: string, fenpeiBeizhu?: string) => {
    loading.value = true
    try {
      const response = await request.post(`/api/v1/service-orders/${id}/assign`, {
        zhixing_ren_id: zhixingRenId,
        fenpei_beizhu: fenpeiBeizhu
      })
      ElMessage.success('分配工单成功')
      return response.data
    } catch (error) {
      console.error('分配工单失败:', error)
      ElMessage.error('分配工单失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 开始工单
  const startServiceOrder = async (id: string) => {
    loading.value = true
    try {
      const response = await request.post(`/api/v1/service-orders/${id}/start`)
      ElMessage.success('开始工单成功')
      return response.data
    } catch (error) {
      console.error('开始工单失败:', error)
      ElMessage.error('开始工单失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 完成工单
  const completeServiceOrder = async (id: string, wanchengQingkuang: string, jiaofeiWenjian?: string) => {
    loading.value = true
    try {
      const response = await request.post(`/api/v1/service-orders/${id}/complete`, {
        wancheng_qingkuang: wanchengQingkuang,
        jiaofei_wenjian: jiaofeiWenjian
      })
      ElMessage.success('完成工单成功')
      return response.data
    } catch (error) {
      console.error('完成工单失败:', error)
      ElMessage.error('完成工单失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 取消工单
  const cancelServiceOrder = async (id: string, cancelReason: string) => {
    loading.value = true
    try {
      const response = await request.post(`/api/v1/service-orders/${id}/cancel`, {
        cancel_reason: cancelReason
      })
      ElMessage.success('取消工单成功')
      return response.data
    } catch (error) {
      console.error('取消工单失败:', error)
      ElMessage.error('取消工单失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 添加工单评论
  const addServiceOrderComment = async (id: string, comment: string, fujianLujing?: string) => {
    loading.value = true
    try {
      const response = await request.post(`/api/v1/service-orders/${id}/comments`, {
        caozuo_neirong: comment,
        fujian_lujing: fujianLujing
      })
      ElMessage.success('添加评论成功')
      return response.data
    } catch (error) {
      console.error('添加评论失败:', error)
      ElMessage.error('添加评论失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取统计信息
  const fetchStatistics = async (kehuId?: string, zhixingRenId?: string) => {
    loading.value = true
    try {
      const params: any = {}
      if (kehuId) params.kehu_id = kehuId
      if (zhixingRenId) params.zhixing_ren_id = zhixingRenId
      
      const response = await request.get('/api/v1/service-orders/statistics/overview', { params })
      statistics.value = response.data
      return response.data
    } catch (error) {
      console.error('获取统计信息失败:', error)
      ElMessage.error('获取统计信息失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  const resetState = () => {
    serviceOrders.value = []
    currentServiceOrder.value = null
    statistics.value = null
    total.value = 0
    currentPage.value = 1
  }

  return {
    // 状态
    serviceOrders,
    currentServiceOrder,
    statistics,
    loading,
    total,
    currentPage,
    pageSize,
    
    // 计算属性
    hasServiceOrders,
    totalPages,
    statusMap,
    priorityMap,
    serviceTypeMap,
    
    // 方法
    fetchServiceOrders,
    fetchServiceOrderDetail,
    createServiceOrder,
    createServiceOrderFromContract,
    updateServiceOrder,
    assignServiceOrder,
    startServiceOrder,
    completeServiceOrder,
    cancelServiceOrder,
    addServiceOrderComment,
    fetchStatistics,
    resetState
  }
})
