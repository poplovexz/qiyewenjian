/**
 * 任务相关 API
 * 对接后端 /api/v1/task-items 路由
 */
import { get, post } from '@/utils/request'

// 任务列表参数
export interface TaskListParams {
  page?: number
  pageSize?: number
  xiangmu_zhuangtai?: string  // pending | in_progress | completed | skipped
  gongdan_zhuangtai?: string  // 工单状态筛选
  fuwu_leixing?: string       // 服务类型筛选
}

// 任务列表响应
export interface TaskListResponse {
  items: TaskItemData[]
  total: number
  page: number
  size: number
}

// 任务项数据
export interface TaskItemData {
  id: string
  gongdan_id: string
  gongdan_bianhao?: string
  chanpin_id?: string
  chanpin_mingcheng?: string
  buzou_id?: string
  buzou_mingcheng?: string
  kehu_id?: string
  kehu_mingcheng?: string
  zhixing_ren_id: number
  zhixing_ren_mingcheng?: string
  xiangmu_zhuangtai: 'pending' | 'in_progress' | 'completed' | 'skipped'
  jihua_gongshi?: number
  shiji_gongshi?: number
  kaishi_shijian?: string
  jieshu_shijian?: string
  beizhu?: string
  chuangjian_shijian: string
  gengxin_shijian: string
}

// 任务统计
export interface TaskStatisticsData {
  total: number
  pending: number
  in_progress: number
  completed: number
  skipped: number
  total_jihua_gongshi?: number
  total_shiji_gongshi?: number
  avg_completion_rate?: number
}

// 完成任务参数
export interface CompleteTaskParams {
  shiji_gongshi: number
  beizhu?: string
}

// 获取我的任务列表
export const getMyTasks = (params: TaskListParams = {}): Promise<TaskListResponse> => {
  // 转换参数名
  const apiParams: Record<string, any> = {
    page: params.page || 1,
    size: params.pageSize || 20
  }
  if (params.xiangmu_zhuangtai) {
    apiParams.xiangmu_zhuangtai = params.xiangmu_zhuangtai
  }
  if (params.gongdan_zhuangtai) {
    apiParams.gongdan_zhuangtai = params.gongdan_zhuangtai
  }
  if (params.fuwu_leixing) {
    apiParams.fuwu_leixing = params.fuwu_leixing
  }
  return get('/task-items/my-tasks', apiParams, { showLoading: false })
}

// 获取任务详情
export const getTaskDetail = (id: string): Promise<TaskItemData> => {
  return get(`/task-items/${id}`, {}, { showLoading: true })
}

// 开始任务
export const startTask = (id: string): Promise<TaskItemData> => {
  return post(`/task-items/${id}/start`, {}, { showLoading: true, loadingText: '处理中...' })
}

// 完成任务
export const completeTask = (id: string, params: CompleteTaskParams): Promise<TaskItemData> => {
  // 后端使用 Query 参数
  const queryParams = new URLSearchParams({
    shiji_gongshi: String(params.shiji_gongshi)
  })
  if (params.beizhu) {
    queryParams.append('beizhu', params.beizhu)
  }
  return post(`/task-items/${id}/complete?${queryParams.toString()}`, {}, {
    showLoading: true,
    loadingText: '处理中...'
  })
}

// 暂停任务
export const pauseTask = (id: string): Promise<TaskItemData> => {
  return post(`/task-items/${id}/pause`, {}, { showLoading: true, loadingText: '处理中...' })
}

// 跳过任务
export const skipTask = (id: string, reason?: string): Promise<TaskItemData> => {
  const queryParams = reason ? `?tiaoguo_yuanyin=${encodeURIComponent(reason)}` : ''
  return post(`/task-items/${id}/skip${queryParams}`, {}, { showLoading: true, loadingText: '处理中...' })
}

// 获取任务统计
export const getTaskStatistics = (): Promise<TaskStatisticsData> => {
  return get('/task-items/statistics', {}, { showLoading: false })
}

