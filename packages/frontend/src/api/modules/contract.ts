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

// ==================== 合同管理相关接口 ====================

// 合同相关接口类型定义
export interface Contract {
  id: string
  hetong_bianhao: string
  hetong_mingcheng: string
  hetong_leixing: string
  moban_id?: string
  baojia_id?: string
  yifang_zhuti_id?: string
  hetong_neirong: string
  hetong_zhuangtai: string
  qianding_riqi?: string
  shengxiao_riqi?: string
  jieshu_riqi?: string
  hetong_jine?: number
  dianziqianming_lujing?: string
  qianming_ren_id?: string
  qianming_shijian?: string
  beizhu?: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface ContractCreate {
  hetong_bianhao?: string
  hetong_mingcheng: string
  hetong_leixing: string
  moban_id?: string
  baojia_id?: string
  yifang_zhuti_id?: string
  hetong_neirong: string
  hetong_zhuangtai?: string
  qianding_riqi?: string
  shengxiao_riqi?: string
  jieshu_riqi?: string
  hetong_jine?: number
  beizhu?: string
}

export interface ContractUpdate {
  hetong_mingcheng?: string
  hetong_leixing?: string
  hetong_neirong?: string
  hetong_zhuangtai?: string
  qianding_riqi?: string
  shengxiao_riqi?: string
  jieshu_riqi?: string
  hetong_jine?: number
  beizhu?: string
}

export interface ContractListParams {
  page?: number
  size?: number
  search?: string
  hetong_leixing?: string
  hetong_zhuangtai?: string
  baojia_id?: string
}

export interface ContractListResponse {
  total: number
  items: Contract[]
  page: number
  size: number
}

export interface ContractPreview {
  moban_id: string
  baojia_id?: string
  bianliang_zhis: Record<string, any>
}

export interface ContractSignature {
  qianming_tupian?: string
  qianming_wenben?: string
}

// 乙方主体相关接口类型定义
export interface ContractParty {
  id: string
  zhuti_mingcheng: string
  zhuti_leixing: string
  tongyi_shehui_xinyong_daima?: string
  yingyezhizhao_haoma?: string
  faren_daibiao?: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  zhuce_dizhi?: string
  yinhang_mingcheng?: string
  yinhang_zhanghu?: string
  yinhang_kaihuhang?: string
  beizhu?: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface ContractPartyCreate {
  zhuti_mingcheng: string
  zhuti_leixing: string
  tongyi_shehui_xinyong_daima?: string
  yingyezhizhao_haoma?: string
  faren_daibiao?: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  zhuce_dizhi?: string
  yinhang_mingcheng?: string
  yinhang_zhanghu?: string
  yinhang_kaihuhang?: string
  beizhu?: string
}

export interface ContractPartyUpdate {
  zhuti_mingcheng?: string
  zhuti_leixing?: string
  tongyi_shehui_xinyong_daima?: string
  yingyezhizhao_haoma?: string
  faren_daibiao?: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  zhuce_dizhi?: string
  yinhang_mingcheng?: string
  yinhang_zhanghu?: string
  yinhang_kaihuhang?: string
  beizhu?: string
}

export interface ContractPartyListParams {
  page?: number
  size?: number
  search?: string
  zhuti_leixing?: string
}

export interface ContractPartyListResponse {
  total: number
  items: ContractParty[]
  page: number
  size: number
}

// 支付方式相关接口类型定义
export interface PaymentMethod {
  id: string
  yifang_zhuti_id: string
  zhifu_leixing: string
  zhifu_mingcheng: string
  zhanghu_mingcheng?: string
  zhanghu_haoma?: string
  kaihuhang_mingcheng?: string
  lianhang_hao?: string
  weixin_haoma?: string
  zhifubao_haoma?: string
  erweima_lujing?: string
  zhifu_zhuangtai: string
  shi_moren: boolean
  beizhu?: string
  created_at: string
  updated_at: string
  created_by: string
  yifang_zhuti?: ContractParty
}

export interface PaymentMethodCreate {
  yifang_zhuti_id: string
  zhifu_leixing: string
  zhifu_mingcheng: string
  zhanghu_mingcheng?: string
  zhanghu_haoma?: string
  kaihuhang_mingcheng?: string
  lianhang_hao?: string
  weixin_haoma?: string
  zhifubao_haoma?: string
  erweima_lujing?: string
  zhifu_zhuangtai?: string
  shi_moren?: boolean
  beizhu?: string
}

export interface PaymentMethodUpdate {
  zhifu_leixing?: string
  zhifu_mingcheng?: string
  zhanghu_mingcheng?: string
  zhanghu_haoma?: string
  kaihuhang_mingcheng?: string
  lianhang_hao?: string
  weixin_haoma?: string
  zhifubao_haoma?: string
  erweima_lujing?: string
  zhifu_zhuangtai?: string
  shi_moren?: boolean
  beizhu?: string
}

export interface PaymentMethodListParams {
  page?: number
  size?: number
  search?: string
  yifang_zhuti_id?: string
  zhifu_leixing?: string
  zhifu_zhuangtai?: string
}

export interface PaymentMethodListResponse {
  total: number
  items: PaymentMethod[]
  page: number
  size: number
}

// ==================== 合同管理 API ====================

// 合同管理 API
export const contractApi = {
  // 创建合同
  create: (data: ContractCreate) => {
    return request.post<Contract>('/api/v1/contracts/', data)
  },

  // 获取合同列表
  getList: (params: ContractListParams = {}) => {
    return request.get<ContractListResponse>('/api/v1/contracts/', { params })
  },

  // 获取合同详情
  getDetail: (id: string) => {
    return request.get<Contract>(`/api/v1/contracts/${id}`)
  },

  // 更新合同信息
  update: (id: string, data: ContractUpdate) => {
    return request.put<Contract>(`/api/v1/contracts/${id}`, data)
  },

  // 删除合同
  delete: (id: string) => {
    return request.delete(`/api/v1/contracts/${id}`)
  },

  // 基于报价自动生成合同
  createFromQuote: (baojiaId: string, mobanId?: string) => {
    return request.post<Contract>('/api/v1/contracts/from-quote', {
      baojia_id: baojiaId,
      moban_id: mobanId
    })
  },

  // 预览合同内容
  preview: (data: ContractPreview) => {
    return request.post<{ content: string }>('/api/v1/contracts/preview', data)
  },

  // 签署合同
  sign: (id: string, signature: ContractSignature) => {
    return request.post<Contract>(`/api/v1/contracts/${id}/sign`, signature)
  },

  // 更新合同状态
  updateStatus: (id: string, status: string) => {
    return request.patch<Contract>(`/api/v1/contracts/${id}/status`, null, {
      params: { new_status: status }
    })
  },

  // 批量删除
  batchDelete: (ids: string[]) => {
    return Promise.all(ids.map(id => request.delete(`/api/v1/contracts/${id}`)))
  }
}

// 乙方主体管理 API
export const contractPartyApi = {
  // 创建乙方主体
  create: (data: ContractPartyCreate) => {
    return request.post<ContractParty>('/api/v1/contract-parties/', data)
  },

  // 获取乙方主体列表
  getList: (params: ContractPartyListParams = {}) => {
    return request.get<ContractPartyListResponse>('/api/v1/contract-parties/', { params })
  },

  // 获取乙方主体详情
  getDetail: (id: string) => {
    return request.get<ContractParty>(`/api/v1/contract-parties/${id}`)
  },

  // 更新乙方主体信息
  update: (id: string, data: ContractPartyUpdate) => {
    return request.put<ContractParty>(`/api/v1/contract-parties/${id}`, data)
  },

  // 删除乙方主体
  delete: (id: string) => {
    return request.delete(`/api/v1/contract-parties/${id}`)
  },

  // 批量删除
  batchDelete: (ids: string[]) => {
    return Promise.all(ids.map(id => request.delete(`/api/v1/contract-parties/${id}`)))
  }
}

// 支付方式管理 API
export const paymentMethodApi = {
  // 创建支付方式
  create: (data: PaymentMethodCreate) => {
    return request.post<PaymentMethod>('/api/v1/contract-payment-methods/', data)
  },

  // 获取支付方式列表
  getList: (params: PaymentMethodListParams = {}) => {
    return request.get<PaymentMethodListResponse>('/api/v1/contract-payment-methods/', { params })
  },

  // 获取支付方式详情
  getDetail: (id: string) => {
    return request.get<PaymentMethod>(`/api/v1/contract-payment-methods/${id}`)
  },

  // 更新支付方式信息
  update: (id: string, data: PaymentMethodUpdate) => {
    return request.put<PaymentMethod>(`/api/v1/contract-payment-methods/${id}`, data)
  },

  // 删除支付方式
  delete: (id: string) => {
    return request.delete(`/api/v1/contract-payment-methods/${id}`)
  },

  // 设置默认支付方式
  setDefault: (id: string) => {
    return request.patch<PaymentMethod>(`/api/v1/contract-payment-methods/${id}/set-default`)
  },

  // 批量删除
  batchDelete: (ids: string[]) => {
    return Promise.all(ids.map(id => request.delete(`/api/v1/contract-payment-methods/${id}`)))
  }
}

// ==================== 选项配置 ====================

// 合同状态选项
export const contractStatusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '待签署', value: 'pending_signature' },
  { label: '已签署', value: 'signed' },
  { label: '生效中', value: 'active' },
  { label: '已完成', value: 'completed' },
  { label: '已终止', value: 'terminated' }
]

// 主体类型选项
export const partyTypeOptions = [
  { label: '企业', value: 'enterprise' },
  { label: '个体工商户', value: 'individual_business' },
  { label: '个人', value: 'individual' }
]

// 支付方式选项
export const paymentTypeOptions = [
  { label: '银行转账', value: 'bank_transfer' },
  { label: '微信支付', value: 'wechat_pay' },
  { label: '支付宝', value: 'alipay' },
  { label: '现金', value: 'cash' }
]
