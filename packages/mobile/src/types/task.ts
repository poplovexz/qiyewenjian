/**
 * 任务项类型定义
 */

// 任务项状态
export type TaskItemStatus = 'pending' | 'in_progress' | 'completed' | 'skipped'

// 工单状态
export type OrderStatus = 'draft' | 'pending' | 'in_progress' | 'completed' | 'cancelled'

// 服务类型
export type ServiceType = 'zengzhi_fuwu' | 'daili_jizhang'

// 客户信息
export interface CustomerInfo {
  id: string
  kehu_mingcheng: string
}

// 工单信息
export interface OrderInfo {
  id: string
  gongdan_bianhao: string
  gongdan_biaoti: string
  fuwu_leixing: string
  gongdan_zhuangtai: string
}

// 任务项
export interface TaskItem {
  id: string
  gongdan_id: string
  chanpin_buzou_id: string
  renwu_mingcheng: string
  renwu_miaoshu?: string
  jihua_gongshi: number
  shiji_gongshi?: number
  xiangmu_zhuangtai: TaskItemStatus
  zhixing_ren_id?: string
  kaishi_shijian?: string
  jieshu_shijian?: string
  beizhu?: string
  paixu: number
  gongdan: OrderInfo
  kehu?: CustomerInfo
}

// 任务项列表响应
export interface TaskItemListResponse {
  total: number
  items: TaskItem[]
  page: number
  size: number
  pages: number
}

// 任务项统计
export interface TaskItemStatistics {
  total_count: number
  pending_count: number
  in_progress_count: number
  completed_count: number
  skipped_count: number
  total_jihua_gongshi: number
  total_shiji_gongshi: number
  avg_completion_rate: number
}

// 任务项列表查询参数
export interface TaskItemListParams {
  page?: number
  size?: number
  xiangmu_zhuangtai?: TaskItemStatus
  gongdan_zhuangtai?: OrderStatus
  fuwu_leixing?: ServiceType
}

// 完成任务项请求
export interface CompleteTaskRequest {
  shiji_gongshi: number
  beizhu?: string
}

// 暂停任务项请求
export interface PauseTaskRequest {
  beizhu?: string
}

