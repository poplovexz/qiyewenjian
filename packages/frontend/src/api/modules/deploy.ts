/**
 * 部署管理API
 */
import request from '@/utils/request'

/**
 * 部署状态
 */
export type DeployStatus = 'pending' | 'running' | 'success' | 'failed' | 'cancelled'

/**
 * 部署环境
 */
export type DeployEnvironment = 'production' | 'staging' | 'development'

/**
 * 触发部署请求
 */
export interface DeployTriggerRequest {
  environment?: DeployEnvironment
  branch?: string
  description?: string
  skip_build?: boolean
  skip_migration?: boolean
}

/**
 * 部署状态响应
 */
export interface DeployStatusResponse {
  deploy_id: number
  status: DeployStatus
  environment: string
  branch: string
  started_at: string | null
  completed_at: string | null
  duration: number | null
  deployed_by: string
  commit_hash: string | null
  error_message: string | null
}

/**
 * 部署日志响应
 */
export interface DeployLogResponse {
  deploy_id: number
  logs: string[]
  is_complete: boolean
}

/**
 * 部署历史项
 */
export interface DeployHistoryItem {
  id: number
  environment: string
  branch: string
  status: DeployStatus
  started_at: string
  completed_at: string | null
  duration: number | null
  deployed_by: string
  commit_hash: string | null
  description: string | null
}

/**
 * 部署历史列表响应
 */
export interface DeployHistoryListResponse {
  items: DeployHistoryItem[]
  total: number
  page: number
  size: number
}

/**
 * 部署详情响应
 */
export interface DeployHistoryResponse {
  id: number
  environment: string
  branch: string
  status: DeployStatus
  started_at: string
  completed_at: string | null
  duration: number | null
  deployed_by: string
  commit_hash: string | null
  description: string | null
  logs: string | null
  error_message: string | null
  created_at: string
  updated_at: string
}

/**
 * 回滚请求
 */
export interface RollbackRequest {
  deploy_id: number
  description?: string
}

export interface DeployConfig {
  id: number
  environment: string
  host: string
  port: number
  username: string
  deploy_path: string
  backup_path?: string
  backend_port: number
  frontend_port?: number
  description?: string
  created_at: string
  updated_at: string
}

export interface DeployConfigCreate {
  environment: string
  host: string
  port?: number
  username: string
  password?: string
  deploy_path: string
  backup_path?: string
  backend_port?: number
  frontend_port?: number
  description?: string
}

export interface DeployConfigUpdate {
  host?: string
  port?: number
  username?: string
  password?: string
  deploy_path?: string
  backup_path?: string
  backend_port?: number
  frontend_port?: number
  description?: string
}

/**
 * 触发部署
 */
export function triggerDeploy(data: DeployTriggerRequest) {
  return request<DeployStatusResponse>({
    url: '/deploy/trigger',
    method: 'post',
    data
  })
}

/**
 * 获取部署状态
 */
export function getDeployStatus(deployId: number) {
  return request<DeployStatusResponse>({
    url: `/deploy/status/${deployId}`,
    method: 'get'
  })
}

/**
 * 获取部署日志
 */
export function getDeployLogs(deployId: number) {
  return request<DeployLogResponse>({
    url: `/deploy/logs/${deployId}`,
    method: 'get'
  })
}

/**
 * 获取部署历史列表
 */
export function getDeployHistory(params: {
  page?: number
  size?: number
  environment?: string
  status?: string
}) {
  return request<DeployHistoryListResponse>({
    url: '/deploy/history',
    method: 'get',
    params
  })
}

/**
 * 获取部署详情
 */
export function getDeployDetail(deployId: number) {
  return request<DeployHistoryResponse>({
    url: `/deploy/history/${deployId}`,
    method: 'get'
  })
}

/**
 * 取消部署
 */
export function cancelDeploy(deployId: number) {
  return request({
    url: `/deploy/cancel/${deployId}`,
    method: 'post'
  })
}

/**
 * 回滚部署
 */
export function rollbackDeploy(data: RollbackRequest) {
  return request<DeployStatusResponse>({
    url: '/deploy/rollback',
    method: 'post',
    data
  })
}

/**
 * 获取所有部署配置
 */
export function getAllDeployConfigs() {
  return request<DeployConfig[]>({
    url: '/deploy/configs',
    method: 'get'
  })
}

/**
 * 获取指定环境的配置
 */
export function getDeployConfig(environment: string) {
  return request<DeployConfig>({
    url: `/deploy/configs/${environment}`,
    method: 'get'
  })
}

/**
 * 创建部署配置
 */
export function createDeployConfig(data: DeployConfigCreate) {
  return request<DeployConfig>({
    url: '/deploy/configs',
    method: 'post',
    data
  })
}

/**
 * 更新部署配置
 */
export function updateDeployConfig(environment: string, data: DeployConfigUpdate) {
  return request<DeployConfig>({
    url: `/deploy/configs/${environment}`,
    method: 'put',
    data
  })
}

/**
 * 删除部署配置
 */
export function deleteDeployConfig(environment: string) {
  return request({
    url: `/deploy/configs/${environment}`,
    method: 'delete'
  })
}

/**
 * Git分支信息
 */
export interface GitBranchesResponse {
  current_branch: string
  branches: string[]
}

/**
 * 获取Git分支列表
 */
export function getGitBranches() {
  return request<GitBranchesResponse>({
    url: '/deploy/branches',
    method: 'get'
  })
}

/**
 * 部署前检查结果
 */
export interface PreDeployCheckResult {
  overall_status: 'success' | 'warning' | 'error'
  errors: number
  warnings: number
  checks: Array<{
    name: string
    status: 'success' | 'warning' | 'error' | 'checking'
    message: string
  }>
  can_deploy: boolean
  message: string
  deep_check: boolean
}

/**
 * 部署前检查
 * @param deepCheck 是否执行深度检查（包括实际构建和依赖安装测试）
 */
export function preDeployCheck(deepCheck = false) {
  return request<PreDeployCheckResult>({
    url: '/deploy/pre-check',
    method: 'get',
    params: { deep_check: deepCheck }
  })
}

