/**
 * 合同模板管理 API
 */
import { request } from '@/utils/request'

// 合同模板相关接口类型定义
export interface ContractTemplate {
  id: string
  moban_mingcheng: string
  moban_bianma: string
  hetong_leixing: string
  moban_neirong: string
  bianliang_peizhi?: string
  banben_hao: string
  shi_dangqian_banben: string
  moban_fenlei?: string
  moban_zhuangtai: string
  shiyong_cishu: number
  shenpi_zhuangtai: string
  shenpi_ren?: string
  shenpi_shijian?: string
  shenpi_yijian?: string
  beizhu?: string
  paixu: number
  created_at: string
  updated_at: string
  created_by: string
}

export interface ContractTemplateCreate {
  moban_mingcheng: string
  moban_bianma: string
  hetong_leixing: string
  moban_neirong: string
  bianliang_peizhi?: string
  banben_hao?: string
  shi_dangqian_banben?: string
  moban_fenlei?: string
  moban_zhuangtai?: string
  beizhu?: string
  paixu?: number
}

export interface ContractTemplateUpdate {
  moban_mingcheng?: string
  moban_bianma?: string
  hetong_leixing?: string
  moban_neirong?: string
  bianliang_peizhi?: string
  banben_hao?: string
  shi_dangqian_banben?: string
  moban_fenlei?: string
  moban_zhuangtai?: string
  beizhu?: string
  paixu?: number
}

export interface ContractTemplateListParams {
  page?: number
  size?: number
  search?: string
  hetong_leixing?: string
  moban_zhuangtai?: string
  moban_fenlei?: string
  shi_dangqian_banben?: string
}

export interface ContractTemplateListResponse {
  total: number
  items: ContractTemplate[]
  page: number
  size: number
}

export interface ContractTemplatePreview {
  moban_id: string
  bianliang_zhis: Record<string, any>
}

export interface ContractTemplateStatistics {
  total_count: number
  active_count: number
  draft_count: number
  archived_count: number
  type_statistics: Record<string, number>
}

// 合同模板管理 API
export const contractTemplateApi = {
  // 创建合同模板
  create: (data: ContractTemplateCreate) => {
    return request.post<ContractTemplate>('/api/v1/contract-templates/', data)
  },

  // 获取合同模板列表
  getList: (params: ContractTemplateListParams = {}) => {
    return request.get<ContractTemplateListResponse>('/api/v1/contract-templates/', { params })
  },

  // 获取合同模板详情
  getDetail: (id: string) => {
    return request.get<ContractTemplate>(`/api/v1/contract-templates/${id}`)
  },

  // 更新合同模板信息
  update: (id: string, data: ContractTemplateUpdate) => {
    return request.put<ContractTemplate>(`/api/v1/contract-templates/${id}`, data)
  },

  // 删除合同模板
  delete: (id: string) => {
    return request.delete(`/api/v1/contract-templates/${id}`)
  },

  // 更新模板状态
  updateStatus: (id: string, status: string) => {
    return request.patch<ContractTemplate>(`/api/v1/contract-templates/${id}/status`, null, {
      params: { new_status: status }
    })
  },

  // 预览合同模板
  preview: (id: string, variables: Record<string, any>) => {
    return request.post<{ content: string }>(`/api/v1/contract-templates/${id}/preview`, {
      moban_id: id,
      bianliang_zhis: variables
    })
  },

  // 获取模板变量配置
  getVariables: (id: string) => {
    return request.get<{ variables: Record<string, any> }>(`/api/v1/contract-templates/${id}/variables`)
  },

  // 获取统计信息
  getStatistics: () => {
    return request.get<ContractTemplateStatistics>('/api/v1/contract-templates/statistics/overview')
  },

  // 批量删除
  batchDelete: (ids: string[]) => {
    return Promise.all(ids.map(id => request.delete(`/api/v1/contract-templates/${id}`)))
  },

  // 批量更新状态
  batchUpdateStatus: (ids: string[], status: string) => {
    return Promise.all(ids.map(id => 
      request.patch(`/api/v1/contract-templates/${id}/status`, null, {
        params: { new_status: status }
      })
    ))
  }
}

// 合同类型选项
export const contractTypeOptions = [
  { label: '代理记账合同', value: 'daili_jizhang' },
  { label: '增值服务合同', value: 'zengzhi_fuwu' },
  { label: '咨询服务合同', value: 'zixun_fuwu' }
]

// 模板状态选项
export const templateStatusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '启用', value: 'active' },
  { label: '归档', value: 'archived' }
]

// 模板分类选项
export const templateCategoryOptions = [
  { label: '标准模板', value: 'biaozhun' },
  { label: '定制模板', value: 'dingzhi' }
]

// 审批状态选项
export const approvalStatusOptions = [
  { label: '待审批', value: 'pending' },
  { label: '已审批', value: 'approved' },
  { label: '已拒绝', value: 'rejected' }
]
