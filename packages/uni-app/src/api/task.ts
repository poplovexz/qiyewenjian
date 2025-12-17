/**
 * 任务相关 API
 */
import { get, post } from '@/utils/request'

// 任务列表参数
export interface TaskListParams {
  status?: string
  page?: number
  pageSize?: number
}

// 获取我的任务列表
export const getMyTasks = (params: TaskListParams = {}) => {
  return get('/task-items/my-tasks', params)
}

// 获取任务详情
export const getTaskDetail = (id: number) => {
  return get(`/task-items/${id}`)
}

// 开始任务
export const startTask = (id: number) => {
  return post(`/task-items/${id}/start`)
}

// 完成任务
export const completeTask = (id: number) => {
  return post(`/task-items/${id}/complete`)
}

// 暂停任务
export const pauseTask = (id: number) => {
  return post(`/task-items/${id}/pause`)
}

// 获取任务统计
export const getTaskStatistics = () => {
  return get('/task-items/statistics')
}

