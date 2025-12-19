<template>
  <div class="deploy-management">
    <!-- 生产环境提示 -->
    <el-alert
      v-if="isProduction"
      title="部署管理功能仅在开发环境可用"
      type="warning"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    >
      <template #default>
        <p>为了安全起见，部署管理功能只能在开发环境使用。</p>
        <p>如需部署到生产环境，请在开发环境（http://localhost:5174/settings/deploy）进行操作。</p>
      </template>
    </el-alert>

    <!-- 开发环境才显示部署功能 -->
    <template v-if="!isProduction">
      <el-card class="header-card">
        <template #header>
          <div class="card-header">
            <span class="title">
              <el-icon><Upload /></el-icon>
              部署管理
            </span>
            <div class="header-actions">
              <el-button @click="showConfigDialog = true"> 配置管理 </el-button>
              <el-button
                type="primary"
                :icon="Upload"
                @click="showDeployDialog = true"
                :loading="deploying"
              >
                一键部署
              </el-button>
            </div>
          </div>
        </template>

        <!-- 当前部署状态 -->
        <div v-if="currentDeploy" class="current-deploy">
          <el-alert
            :title="`正在部署到 ${currentDeploy.environment} 环境...`"
            type="info"
            :closable="false"
          >
            <template #default>
              <div class="deploy-info">
                <p><strong>分支:</strong> {{ currentDeploy.branch }}</p>
                <p><strong>部署人:</strong> {{ currentDeploy.deployed_by }}</p>
                <p><strong>开始时间:</strong> {{ formatDateTime(currentDeploy.started_at) }}</p>
              </div>
              <el-progress
                :percentage="deployProgress"
                :status="deployProgressStatus"
                :indeterminate="currentDeploy.status === 'running'"
              />
              <div class="deploy-actions">
                <el-button size="small" @click="viewLogs(currentDeploy.deploy_id)">
                  查看日志
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="handleCancelDeploy"
                  v-if="currentDeploy.status === 'running'"
                >
                  取消部署
                </el-button>
              </div>
            </template>
          </el-alert>
        </div>
      </el-card>

      <!-- 部署历史 -->
      <el-card class="history-card">
        <template #header>
          <div class="card-header">
            <span class="title">部署历史</span>
            <div class="filters">
              <el-select
                v-model="filters.environment"
                placeholder="环境"
                clearable
                style="width: 150px; margin-right: 10px"
                @change="loadHistory"
              >
                <el-option label="生产环境" value="production" />
                <el-option label="预发布环境" value="staging" />
                <el-option label="开发环境" value="development" />
              </el-select>
              <el-select
                v-model="filters.status"
                placeholder="状态"
                clearable
                style="width: 120px"
                @change="loadHistory"
              >
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
                <el-option label="运行中" value="running" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </div>
          </div>
        </template>

        <el-table :data="historyList" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column label="环境" width="120">
            <template #default="{ row }">
              <el-tag :type="getEnvironmentType(row.environment)">
                {{ getEnvironmentLabel(row.environment) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="branch" label="分支" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deployed_by" label="部署人" width="120" />
          <el-table-column label="开始时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.started_at) }}
            </template>
          </el-table-column>
          <el-table-column label="耗时" width="100">
            <template #default="{ row }">
              {{ formatDuration(row.duration) }}
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewLogs(row.id)">
                查看日志
              </el-button>
              <el-button
                link
                type="warning"
                size="small"
                @click="handleRollback(row)"
                v-if="row.status === 'success'"
              >
                回滚
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadHistory"
            @current-change="loadHistory"
          />
        </div>
      </el-card>

      <!-- 部署对话框 -->
      <el-dialog v-model="showDeployDialog" title="触发部署" width="600px">
        <!-- 部署前检查结果 -->
        <el-alert
          v-if="preCheckResult"
          :title="preCheckResult.message"
          :type="
            preCheckResult.overall_status === 'success'
              ? 'success'
              : preCheckResult.overall_status === 'error'
                ? 'error'
                : 'warning'
          "
          :closable="false"
          style="margin-bottom: 20px"
          show-icon
        >
          <template #default>
            <div class="check-results">
              <div v-for="(check, index) in preCheckResult.checks" :key="index" class="check-item">
                <el-icon v-if="check.status === 'success'" color="#67C23A"><CircleCheck /></el-icon>
                <el-icon v-else-if="check.status === 'error'" color="#F56C6C"
                  ><CircleClose
                /></el-icon>
                <el-icon v-else-if="check.status === 'warning'" color="#E6A23C"
                  ><Warning
                /></el-icon>
                <el-icon v-else color="#909399"><Loading /></el-icon>
                <span class="check-name">{{ check.name }}:</span>
                <span class="check-message">{{ check.message }}</span>
              </div>
            </div>
          </template>
        </el-alert>

        <el-form :model="deployForm" label-width="100px">
          <el-form-item label="部署环境">
            <el-select v-model="deployForm.environment" style="width: 100%">
              <el-option label="生产环境" value="production" />
              <el-option label="预发布环境" value="staging" />
              <el-option label="开发环境" value="development" />
            </el-select>
          </el-form-item>
          <el-form-item label="Git分支">
            <el-select
              v-model="deployForm.branch"
              placeholder="请选择分支"
              style="width: 100%"
              filterable
              :loading="branchesLoading"
            >
              <el-option
                v-for="branch in gitBranches"
                :key="branch"
                :label="branch"
                :value="branch"
              >
                <span>{{ branch }}</span>
                <el-tag
                  v-if="branch === currentBranch"
                  size="small"
                  type="success"
                  style="margin-left: 8px"
                >
                  当前
                </el-tag>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="部署说明">
            <el-input
              v-model="deployForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入部署说明（可选）"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="deployForm.skip_build">跳过构建步骤</el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="deployForm.skip_migration">跳过数据库迁移</el-checkbox>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showDeployDialog = false">取消</el-button>
          <el-button @click="runPreCheck(false)" :loading="preChecking">
            <el-icon><Search /></el-icon>
            快速检查
          </el-button>
          <el-button @click="runPreCheck(true)" :loading="preChecking">
            <el-icon><Search /></el-icon>
            深度检查
          </el-button>
          <el-button
            type="primary"
            @click="handleDeploy"
            :loading="deploying"
            :disabled="preCheckResult && !preCheckResult.can_deploy"
          >
            开始部署
          </el-button>
        </template>
      </el-dialog>

      <!-- 日志对话框 -->
      <el-dialog
        v-model="showLogsDialog"
        title="部署日志"
        width="80%"
        :close-on-click-modal="false"
      >
        <div class="logs-container">
          <div class="logs-content" ref="logsContentRef">
            <pre v-for="(log, index) in logs" :key="index">{{ log }}</pre>
          </div>
        </div>
        <template #footer>
          <el-button @click="showLogsDialog = false">关闭</el-button>
          <el-button type="primary" @click="refreshLogs" :loading="logsLoading"> 刷新 </el-button>
        </template>
      </el-dialog>

      <!-- 配置管理对话框 -->
      <el-dialog
        v-model="showConfigDialog"
        title="部署配置管理"
        width="900px"
        :close-on-click-modal="false"
      >
        <div class="config-management">
          <div class="config-actions">
            <el-button type="primary" @click="showConfigFormDialog = true"> 添加配置 </el-button>
          </div>

          <el-table :data="configList" v-loading="configLoading" stripe style="margin-top: 20px">
            <el-table-column prop="environment" label="环境" width="120" />
            <el-table-column prop="host" label="服务器IP" width="150" />
            <el-table-column prop="port" label="SSH端口" width="100" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="deploy_path" label="部署目录" min-width="200" />
            <el-table-column prop="backend_port" label="后端端口" width="100" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editConfig(row)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="deleteConfig(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-dialog>

      <!-- 配置表单对话框 -->
      <el-dialog
        v-model="showConfigFormDialog"
        :title="configFormMode === 'create' ? '添加配置' : '编辑配置'"
        width="600px"
      >
        <el-form :model="configForm" label-width="120px">
          <el-form-item label="环境名称" required>
            <el-input
              v-model="configForm.environment"
              :disabled="configFormMode === 'edit'"
              placeholder="如: production"
            />
          </el-form-item>
          <el-form-item label="服务器IP" required>
            <el-input v-model="configForm.host" placeholder="如: 172.16.2.221" />
          </el-form-item>
          <el-form-item label="SSH端口">
            <el-input-number v-model="configForm.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="SSH用户名" required>
            <el-input v-model="configForm.username" placeholder="如: saas" />
          </el-form-item>
          <el-form-item label="SSH密码">
            <el-input
              v-model="configForm.password"
              type="password"
              show-password
              placeholder="留空则不修改"
            />
          </el-form-item>
          <el-form-item label="部署目录" required>
            <el-input v-model="configForm.deploy_path" placeholder="如: /home/saas/proxy-system" />
          </el-form-item>
          <el-form-item label="备份目录">
            <el-input v-model="configForm.backup_path" placeholder="可选" />
          </el-form-item>
          <el-form-item label="后端端口">
            <el-input-number v-model="configForm.backend_port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="前端端口">
            <el-input-number v-model="configForm.frontend_port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="说明">
            <el-input v-model="configForm.description" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showConfigFormDialog = false">取消</el-button>
          <el-button type="primary" @click="saveConfig" :loading="configSaving"> 保存 </el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, CircleCheck, CircleClose, Warning, Loading, Search } from '@element-plus/icons-vue'
import {
  triggerDeploy,
  getDeployStatus,
  getDeployLogs,
  getDeployHistory,
  cancelDeploy,
  rollbackDeploy,
  getAllDeployConfigs,
  createDeployConfig,
  updateDeployConfig,
  deleteDeployConfig as deleteDeployConfigApi,
  getGitBranches,
  preDeployCheck,
  type DeployHistoryItem,
  type DeployStatusResponse,
  type DeployTriggerRequest,
  type DeployConfig,
  type DeployConfigCreate,
  type PreDeployCheckResult,
  type DeployConfigUpdate,
} from '@/api/modules/deploy'

// 环境检测：判断是否是生产环境
// 生产环境的API_BASE_URL是相对路径（/api/v1），开发环境是完整URL
const isProduction = computed(() => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''
  // 如果API_BASE_URL是相对路径（以/开头但不是http://），则认为是生产环境
  return apiBaseUrl.startsWith('/') && !apiBaseUrl.startsWith('http')
})

// Git分支相关
const gitBranches = ref<string[]>([])
const currentBranch = ref<string>('main')
const branchesLoading = ref(false)

// 部署表单
const showDeployDialog = ref(false)
const deploying = ref(false)
const deployForm = ref<DeployTriggerRequest>({
  environment: 'production',
  branch: 'main',
  description: '',
  skip_build: false,
  skip_migration: false,
})

// 部署前检查
const preChecking = ref(false)
const preCheckResult = ref<PreDeployCheckResult | null>(null)

// 当前部署
const currentDeploy = ref<DeployStatusResponse | null>(null)
const deployProgress = ref(0)
const deployProgressStatus = ref<'success' | 'exception' | 'warning' | ''>('')

// 部署历史
const loading = ref(false)
const historyList = ref<DeployHistoryItem[]>([])
const filters = ref({
  environment: '',
  status: '',
})
const pagination = ref({
  page: 1,
  size: 20,
  total: 0,
})

// 日志
const showLogsDialog = ref(false)
const logsLoading = ref(false)
const logs = ref<string[]>([])
const currentLogDeployId = ref<number | null>(null)
const logsContentRef = ref<HTMLElement>()

// 配置管理
const showConfigDialog = ref(false)
const showConfigFormDialog = ref(false)
const configLoading = ref(false)
const configSaving = ref(false)
const configList = ref<DeployConfig[]>([])
const configFormMode = ref<'create' | 'edit'>('create')
const configForm = ref<DeployConfigCreate & { id?: number }>({
  environment: '',
  host: '',
  port: 22,
  username: '',
  password: '',
  deploy_path: '',
  backup_path: '',
  backend_port: 8000,
  frontend_port: undefined,
  description: '',
})

// 轮询定时器
let pollingTimer: number | null = null

// 加载Git分支列表
const loadGitBranches = async () => {
  branchesLoading.value = true
  try {
    const res = await getGitBranches()
    gitBranches.value = res.branches
    currentBranch.value = res.current_branch
    // 默认选中当前分支
    if (!deployForm.value.branch || deployForm.value.branch === 'main') {
      deployForm.value.branch = res.current_branch
    }
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载分支列表失败')
    // 失败时使用默认值
    gitBranches.value = ['main']
    currentBranch.value = 'main'
  } finally {
    branchesLoading.value = false
  }
}

// 加载部署历史
const loadHistory = async () => {
  loading.value = true
  try {
    const res = await getDeployHistory({
      page: pagination.value.page,
      size: pagination.value.size,
      environment: filters.value.environment || undefined,
      status: filters.value.status || undefined,
    })
    historyList.value = res.items
    pagination.value.total = res.total
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载部署历史失败')
  } finally {
    loading.value = false
  }
}

// 运行部署前检查
const runPreCheck = async (deepCheck = false) => {
  try {
    preChecking.value = true
    preCheckResult.value = null

    const checkType = deepCheck ? '深度检查' : '快速检查'
    ElMessage.info(`正在执行${checkType}...${deepCheck ? '（可能需要1-2分钟）' : ''}`)

    const result = await preDeployCheck(deepCheck)
    preCheckResult.value = result

    if (result.overall_status === 'success') {
      ElMessage.success(`${checkType}通过，可以部署`)
    } else if (result.overall_status === 'error') {
      ElMessage.error(`${checkType}失败：${result.errors} 个错误`)
    } else {
      ElMessage.warning(`${checkType}完成：${result.warnings} 个警告`)
    }
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '部署前检查失败')
  } finally {
    preChecking.value = false
  }
}

// 触发部署
const handleDeploy = async () => {
  try {
    deploying.value = true
    const res = await triggerDeploy(deployForm.value)
    currentDeploy.value = res
    showDeployDialog.value = false
    preCheckResult.value = null // 清空检查结果
    ElMessage.success('部署已启动')

    // 开始轮询状态
    startPolling()

    // 刷新历史列表
    loadHistory()
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '触发部署失败')
  } finally {
    deploying.value = false
  }
}

// 开始轮询部署状态
const startPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
  }

  pollingTimer = window.setInterval(async () => {
    if (!currentDeploy.value) {
      stopPolling()
      return
    }

    try {
      const status = await getDeployStatus(currentDeploy.value.deploy_id)
      currentDeploy.value = status

      // 更新进度
      if (status.status === 'running') {
        deployProgress.value = 50
        deployProgressStatus.value = ''
      } else if (status.status === 'success') {
        deployProgress.value = 100
        deployProgressStatus.value = 'success'
        stopPolling()
        ElMessage.success('部署成功！')
        loadHistory()
      } else if (status.status === 'failed') {
        deployProgress.value = 100
        deployProgressStatus.value = 'exception'
        stopPolling()
        ElMessage.error('部署失败：' + (status.error_message || '未知错误'))
        loadHistory()
      } else if (status.status === 'cancelled') {
        deployProgress.value = 100
        deployProgressStatus.value = 'warning'
        stopPolling()
        ElMessage.warning('部署已取消')
        loadHistory()
      }
    } catch (error) {
    }
  }, 3000) // 每3秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 取消部署
const handleCancelDeploy = async () => {
  if (!currentDeploy.value) return

  try {
    await ElMessageBox.confirm('确定要取消当前部署吗？', '提示', {
      type: 'warning',
    })

    await cancelDeploy(currentDeploy.value.deploy_id)
    ElMessage.success('部署已取消')
    currentDeploy.value = null
    stopPolling()
    loadHistory()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { message?: string }
      ElMessage.error(err.message || '取消部署失败')
    }
  }
}

// 查看日志
const viewLogs = async (deployId: number) => {
  currentLogDeployId.value = deployId
  showLogsDialog.value = true
  await refreshLogs()
}

// 刷新日志
const refreshLogs = async () => {
  if (!currentLogDeployId.value) return

  logsLoading.value = true
  try {
    const res = await getDeployLogs(currentLogDeployId.value)
    logs.value = res.logs

    // 滚动到底部
    await nextTick()
    if (logsContentRef.value) {
      logsContentRef.value.scrollTop = logsContentRef.value.scrollHeight
    }
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载日志失败')
  } finally {
    logsLoading.value = false
  }
}

// 回滚
const handleRollback = async (deploy: DeployHistoryItem) => {
  try {
    const { value } = await ElMessageBox.prompt(`确定要回滚到部署 #${deploy.id} 吗？`, '回滚确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入回滚说明（可选）',
    })

    const res = await rollbackDeploy({
      deploy_id: deploy.id,
      description: value || undefined,
    })

    currentDeploy.value = res
    ElMessage.success('回滚已启动')
    startPolling()
    loadHistory()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { message?: string }
      ElMessage.error(err.message || '回滚失败')
    }
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string | null) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 格式化耗时
const formatDuration = (seconds: number | null) => {
  if (!seconds) return '-'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return minutes > 0 ? `${minutes}分${secs}秒` : `${secs}秒`
}

// 获取环境标签
const getEnvironmentLabel = (env: string) => {
  const labels: Record<string, string> = {
    production: '生产环境',
    staging: '预发布',
    development: '开发环境',
  }
  return labels[env] || env
}

// 获取环境类型
const getEnvironmentType = (env: string) => {
  const types: Record<string, any> = {
    production: 'danger',
    staging: 'warning',
    development: 'info',
  }
  return types[env] || ''
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消',
  }
  return labels[status] || status
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger',
    cancelled: '',
  }
  return types[status] || ''
}

// 加载配置列表
const loadConfigs = async () => {
  configLoading.value = true
  try {
    configList.value = await getAllDeployConfigs()
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载配置失败')
  } finally {
    configLoading.value = false
  }
}

// 编辑配置
const editConfig = (config: DeployConfig) => {
  configFormMode.value = 'edit'
  configForm.value = {
    id: config.id,
    environment: config.environment,
    host: config.host,
    port: config.port,
    username: config.username,
    password: '',
    deploy_path: config.deploy_path,
    backup_path: config.backup_path,
    backend_port: config.backend_port,
    frontend_port: config.frontend_port,
    description: config.description,
  }
  showConfigFormDialog.value = true
}

// 保存配置
const saveConfig = async () => {
  configSaving.value = true
  try {
    if (configFormMode.value === 'create') {
      await createDeployConfig(configForm.value)
      ElMessage.success('配置创建成功')
    } else {
      const { environment, ...updateData } = configForm.value
      await updateDeployConfig(environment, updateData as DeployConfigUpdate)
      ElMessage.success('配置更新成功')
    }
    showConfigFormDialog.value = false
    await loadConfigs()
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '保存配置失败')
  } finally {
    configSaving.value = false
  }
}

// 删除配置
const deleteConfig = async (config: DeployConfig) => {
  try {
    await ElMessageBox.confirm(`确定要删除环境 "${config.environment}" 的配置吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await deleteDeployConfigApi(config.environment)
    ElMessage.success('配置已删除')
    await loadConfigs()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { message?: string }
      ElMessage.error(err.message || '删除配置失败')
    }
  }
}

// 监听配置对话框打开
watch(showConfigDialog, (newVal) => {
  if (newVal) {
    loadConfigs()
  }
})

// 监听配置表单对话框打开
watch(showConfigFormDialog, (newVal) => {
  if (newVal && configFormMode.value === 'create') {
    // 重置表单
    configForm.value = {
      environment: '',
      host: '',
      port: 22,
      username: '',
      password: '',
      deploy_path: '',
      backup_path: '',
      backend_port: 8000,
      frontend_port: undefined,
      description: '',
    }
  }
})

// 监听部署对话框打开，加载分支列表
watch(showDeployDialog, (newVal) => {
  if (newVal) {
    loadGitBranches()
  }
})

onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.deploy-management {
  .header-card {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 500;
    }

    .header-actions {
      display: flex;
      gap: 10px;
    }

    .filters {
      display: flex;
      align-items: center;
    }
  }

  .current-deploy {
    .deploy-info {
      margin-bottom: 10px;

      p {
        margin: 5px 0;
      }
    }

    .deploy-actions {
      margin-top: 10px;
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }

  .logs-container {
    height: 500px;
    overflow: hidden;

    .logs-content {
      height: 100%;
      overflow-y: auto;
      background-color: #1e1e1e;
      color: #d4d4d4;
      padding: 15px;
      border-radius: 4px;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.5;

      pre {
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
      }
    }
  }

  .config-management {
    .config-actions {
      margin-bottom: 20px;
    }
  }

  .check-results {
    .check-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 8px 0;

      .check-name {
        font-weight: 500;
        min-width: 120px;
      }

      .check-message {
        color: #606266;
      }
    }
  }
}
</style>
