import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { request } from '@/utils/request'

// 合规事项模板类型定义
export interface ComplianceTemplate {
  id: string
  shixiang_mingcheng: string
  shixiang_bianma: string
  shixiang_leixing: string
  shenbao_zhouqi: string
  jiezhi_shijian_guize: string
  tiqian_tixing_tianshu: string
  shiyong_qiye_leixing?: string
  shiyong_hangye?: string
  shixiang_miaoshu?: string
  banli_liucheng?: string
  suoxu_cailiao?: string
  fagui_yiju?: string
  fengxian_dengji: string
  moban_zhuangtai: string
  paixu: number
  fenlei_biaoqian?: string
  kuozhan_shuju?: string
  created_at: string
  updated_at: string
  created_by: string
  updated_by?: string
}

export interface ComplianceTemplateCreateData {
  shixiang_mingcheng: string
  shixiang_bianma: string
  shixiang_leixing: string
  shenbao_zhouqi: string
  jiezhi_shijian_guize: string
  tiqian_tixing_tianshu?: string
  shiyong_qiye_leixing?: string
  shiyong_hangye?: string
  shixiang_miaoshu?: string
  banli_liucheng?: string
  suoxu_cailiao?: string
  fagui_yiju?: string
  fengxian_dengji?: string
  moban_zhuangtai?: string
  paixu?: number
  fenlei_biaoqian?: string
  kuozhan_shuju?: string
}

export interface ComplianceTemplateListParams {
  page: number
  size: number
  search?: string
  shixiang_leixing?: string
  shenbao_zhouqi?: string
  moban_zhuangtai?: string
  fengxian_dengji?: string
}

export interface ComplianceTemplateListResponse {
  items: ComplianceTemplate[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ComplianceOptions {
  shixiang_leixing_options: Array<{ value: string; label: string }>
  shenbao_zhouqi_options: Array<{ value: string; label: string }>
  fengxian_dengji_options: Array<{ value: string; label: string }>
  moban_zhuangtai_options: Array<{ value: string; label: string }>
}

export interface ComplianceCalendarData {
  year: number
  month?: number
  calendar_data: Record<string, any[]>
  summary: {
    period: string
    total_count: number
    completed_count: number
    overdue_count: number
    completion_rate: number
  }
}

export interface ComplianceStatistics {
  total_count: number
  completed_count: number
  pending_count: number
  in_progress_count: number
  overdue_count: number
  completion_rate: number
  overdue_rate: number
  type_statistics: Array<{
    shixiang_leixing: string
    count: number
  }>
}

export const useComplianceStore = defineStore('compliance', () => {
  // 状态
  const templates = ref<ComplianceTemplate[]>([])
  const currentTemplate = ref<ComplianceTemplate | null>(null)
  const options = ref<ComplianceOptions | null>(null)
  const calendarData = ref<ComplianceCalendarData | null>(null)
  const statistics = ref<ComplianceStatistics | null>(null)
  const loading = ref(false)

  // 计算属性
  const templateTypeMap = computed(() => ({
    shuiwu_shenbao: '税务申报',
    nianbao_shenbao: '年报申报',
    zhizhao_nianjian: '执照年检',
    qita_heguishixiang: '其他合规事项'
  }))

  const reportCycleMap = computed(() => ({
    monthly: '月度',
    quarterly: '季度',
    annually: '年度',
    custom: '自定义'
  }))

  const riskLevelMap = computed(() => ({
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重'
  }))

  const templateStatusMap = computed(() => ({
    active: '启用',
    inactive: '停用',
    draft: '草稿'
  }))

  // 方法
  const fetchTemplates = async (params: ComplianceTemplateListParams): Promise<ComplianceTemplateListResponse> => {
    try {
      loading.value = true
      const response = await request.get('/api/v1/compliance/templates', { params })
      templates.value = response.data.items
      return response.data
    } catch (error) {
      ElMessage.error('获取合规事项模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchTemplateDetail = async (templateId: string): Promise<ComplianceTemplate> => {
    try {
      loading.value = true
      const response = await request.get(`/api/v1/compliance/templates/${templateId}`)
      currentTemplate.value = response.data
      return response.data
    } catch (error) {
      ElMessage.error('获取模板详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const createTemplate = async (data: ComplianceTemplateCreateData): Promise<ComplianceTemplate> => {
    try {
      loading.value = true
      const response = await request.post('/api/v1/compliance/templates', data)
      ElMessage.success('创建合规事项模板成功')
      return response.data
    } catch (error) {
      ElMessage.error('创建合规事项模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateTemplate = async (templateId: string, data: Partial<ComplianceTemplateCreateData>): Promise<ComplianceTemplate> => {
    try {
      loading.value = true
      const response = await request.put(`/api/v1/compliance/templates/${templateId}`, data)
      ElMessage.success('更新合规事项模板成功')
      return response.data
    } catch (error) {
      ElMessage.error('更新合规事项模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteTemplate = async (templateId: string): Promise<void> => {
    try {
      loading.value = true
      await request.delete(`/api/v1/compliance/templates/${templateId}`)
      ElMessage.success('删除合规事项模板成功')
    } catch (error) {
      ElMessage.error('删除合规事项模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchTemplateOptions = async (): Promise<ComplianceOptions> => {
    try {
      const response = await request.get('/api/v1/compliance/templates/options')
      options.value = response.data
      return response.data
    } catch (error) {
      ElMessage.error('获取模板选项失败')
      throw error
    }
  }

  const fetchActiveTemplates = async (): Promise<ComplianceTemplate[]> => {
    try {
      const response = await request.get('/api/v1/compliance/templates/active')
      return response.data
    } catch (error) {
      ElMessage.error('获取启用模板失败')
      throw error
    }
  }

  const fetchCalendarData = async (year: number, month?: number, kehu_id?: string, shixiang_leixing?: string): Promise<ComplianceCalendarData> => {
    try {
      loading.value = true
      const params: any = { year }
      if (month) params.month = month
      if (kehu_id) params.kehu_id = kehu_id
      if (shixiang_leixing) params.shixiang_leixing = shixiang_leixing

      const response = await request.get('/api/v1/compliance/calendar', { params })
      calendarData.value = response.data
      return response.data
    } catch (error) {
      ElMessage.error('获取合规日历数据失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchUpcomingItems = async (days: number = 7, kehu_id?: string): Promise<any[]> => {
    try {
      const params: any = { days }
      if (kehu_id) params.kehu_id = kehu_id

      const response = await request.get('/api/v1/compliance/upcoming', { params })
      return response.data
    } catch (error) {
      ElMessage.error('获取即将到期事项失败')
      throw error
    }
  }

  const fetchOverdueItems = async (kehu_id?: string): Promise<any[]> => {
    try {
      const params: any = {}
      if (kehu_id) params.kehu_id = kehu_id

      const response = await request.get('/api/v1/compliance/overdue', { params })
      return response.data
    } catch (error) {
      ElMessage.error('获取逾期事项失败')
      throw error
    }
  }

  const fetchStatistics = async (year: number, month?: number, kehu_id?: string): Promise<ComplianceStatistics> => {
    try {
      const params: any = { year }
      if (month) params.month = month
      if (kehu_id) params.kehu_id = kehu_id

      const response = await request.get('/api/v1/compliance/statistics', { params })
      statistics.value = response.data
      return response.data
    } catch (error) {
      ElMessage.error('获取合规统计数据失败')
      throw error
    }
  }

  return {
    // 状态
    templates,
    currentTemplate,
    options,
    calendarData,
    statistics,
    loading,

    // 计算属性
    templateTypeMap,
    reportCycleMap,
    riskLevelMap,
    templateStatusMap,

    // 方法
    fetchTemplates,
    fetchTemplateDetail,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    fetchTemplateOptions,
    fetchActiveTemplates,
    fetchCalendarData,
    fetchUpcomingItems,
    fetchOverdueItems,
    fetchStatistics
  }
})
