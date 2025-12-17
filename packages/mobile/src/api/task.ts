import request from '@/utils/request'
import type {
  TaskItemListParams,
  TaskItemListResponse,
  TaskItemStatistics,
  TaskItem,
  CompleteTaskRequest,
  PauseTaskRequest
} from '@/types/task'

/**
 * 获取我的任务项列表
 */
export function getMyTaskItems(params: TaskItemListParams): Promise<TaskItemListResponse> {
  return request({
    url: '/task-items/my-tasks',
    method: 'get',
    params
  })
}

/**
 * 获取任务项统计
 */
export function getTaskItemStatistics(): Promise<TaskItemStatistics> {
  return request({
    url: '/task-items/statistics',
    method: 'get'
  })
}

/**
 * 开始任务项
 */
export function startTaskItem(itemId: string): Promise<TaskItem> {
  return request({
    url: `/task-items/${itemId}/start`,
    method: 'post'
  })
}

/**
 * 完成任务项
 */
export function completeTaskItem(itemId: string, data: CompleteTaskRequest): Promise<TaskItem> {
  return request({
    url: `/task-items/${itemId}/complete`,
    method: 'post',
    params: data
  })
}

/**
 * 暂停任务项
 */
export function pauseTaskItem(itemId: string, data: PauseTaskRequest): Promise<TaskItem> {
  return request({
    url: `/task-items/${itemId}/pause`,
    method: 'post',
    params: data
  })
}

