<template>
  <div class="audit-workflow-config">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>审核流程配置</h2>
      <p>配置合同和报价的审核工作流程</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建流程
      </el-button>
      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 流程列表 -->
    <el-card class="workflow-list">
      <el-table v-loading="loading" :data="workflowList" stripe style="width: 100%">
        <el-table-column prop="workflow_name" label="流程名称" width="200" />
        <el-table-column prop="audit_type" label="流程类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.audit_type)">
              {{ getTypeLabel(row.audit_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="步骤数量" width="100">
          <template #default="{ row }">
            {{ row.steps?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
              :disabled="row.status === 'active'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 流程配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="流程名称" prop="liucheng_mingcheng">
          <el-input v-model="formData.liucheng_mingcheng" placeholder="请输入流程名称" />
        </el-form-item>

        <el-form-item label="流程类型" prop="shenhe_leixing">
          <el-select v-model="formData.shenhe_leixing" placeholder="请选择流程类型">
            <el-option label="合同审核" value="contract" />
            <el-option label="客户审核" value="customer" />
            <el-option label="财务审核" value="financial" />
            <el-option label="银行汇款审核" value="yinhang_huikuan" />
          </el-select>
        </el-form-item>

        <el-form-item label="流程描述" prop="liucheng_miaoshu">
          <el-input
            v-model="formData.liucheng_miaoshu"
            type="textarea"
            :rows="3"
            placeholder="请输入流程描述"
          />
        </el-form-item>

        <el-form-item label="流程状态" prop="zhuangtai">
          <el-radio-group v-model="formData.zhuangtai">
            <el-radio label="active">启用</el-radio>
            <el-radio label="draft">草稿</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 审核步骤配置 -->
        <el-form-item label="审核步骤">
          <div class="workflow-steps">
            <div v-for="(step, index) in formData.buzhou_peizhi" :key="index" class="step-item">
              <el-card>
                <div class="step-header">
                  <span class="step-number">步骤 {{ index + 1 }}</span>
                  <el-button
                    size="small"
                    type="danger"
                    text
                    @click="removeStep(index)"
                    :disabled="formData.buzhou_peizhi.length <= 1"
                  >
                    删除
                  </el-button>
                </div>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="步骤名称">
                      <el-input v-model="step.buzhou_mingcheng" placeholder="请输入步骤名称" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="审核人角色">
                      <el-select
                        v-model="step.shenhe_ren_jiaose"
                        placeholder="请选择审核人角色"
                        :loading="rolesLoading"
                      >
                        <el-option
                          v-for="role in availableRoles"
                          :key="role.id"
                          :label="role.jiaose_ming"
                          :value="role.jiaose_bianma"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="步骤描述">
                  <el-input v-model="step.buzhou_miaoshu" placeholder="请输入步骤描述" />
                </el-form-item>
              </el-card>
            </div>

            <el-button type="dashed" style="width: 100%; margin-top: 10px" @click="addStep">
              <el-icon><Plus /></el-icon>
              添加步骤
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 流程详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" title="审核流程详情" size="700px" direction="rtl">
      <div v-if="currentWorkflow" class="workflow-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="流程名称">
            {{ currentWorkflow.workflow_name || currentWorkflow.name }}
          </el-descriptions-item>
          <el-descriptions-item label="流程类型">
            <el-tag :type="getTypeTagType(currentWorkflow.audit_type || 'contract')">
              {{ getTypeLabel(currentWorkflow.audit_type || 'contract') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentWorkflow.status)">
              {{ getStatusLabel(currentWorkflow.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="步骤数量">
            {{ currentWorkflow.steps?.length || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="流程描述">
            {{ currentWorkflow.description || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(currentWorkflow.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(currentWorkflow.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>流程步骤预览</el-divider>
        <div class="workflow-steps">
          <el-timeline>
            <el-timeline-item
              v-for="(step, index) in currentWorkflow.steps"
              :key="index"
              :icon="getStepIcon(step)"
              :type="getStepType(step)"
              :timestamp="getStepTimestamp(step)"
            >
              <el-card class="step-card">
                <div class="step-header">
                  <h4>{{ step.name || step.step_name }}</h4>
                  <el-tag size="small" :type="step.is_required ? 'danger' : 'info'">
                    {{ step.is_required ? '必需' : '可选' }}
                  </el-tag>
                </div>
                <div class="step-content">
                  <p><strong>审批角色：</strong>{{ step.approver_role || step.role }}</p>
                  <p><strong>预期时间：</strong>{{ step.expected_time || 24 }}小时</p>
                  <p v-if="step.description"><strong>步骤描述：</strong>{{ step.description }}</p>
                  <p v-if="step.condition"><strong>触发条件：</strong>{{ step.condition }}</p>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>

        <el-divider>SLA设置</el-divider>
        <div class="sla-settings">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总预期时间">
              {{ getTotalExpectedTime(currentWorkflow.steps) }}小时
            </el-descriptions-item>
            <el-descriptions-item label="最大处理时间">
              {{ getMaxProcessingTime(currentWorkflow.steps) }}小时
            </el-descriptions-item>
            <el-descriptions-item label="平均处理时间">
              {{ getAverageProcessingTime(currentWorkflow.steps) }}小时
            </el-descriptions-item>
            <el-descriptions-item label="关键路径">
              {{ getCriticalPath(currentWorkflow.steps) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Clock, Check, Warning } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import type { FormInstance, FormRules } from 'element-plus'
import { roleAPI, type Role } from '@/api/modules/role'
import { auditWorkflowApi } from '@/api/modules/audit'

// 类型定义
interface WorkflowStep {
  step?: number
  step_order?: number
  step_name?: string
  name?: string
  description?: string
  condition?: string
  approver_role?: string
  is_required?: boolean
  expected_time?: number
}

interface Workflow {
  id: string
  workflow_name: string
  audit_type: string
  description?: string
  status: string
  steps?: WorkflowStep[]
  created_at?: string
  updated_at?: string
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const workflowList = ref([])
const formRef = ref<FormInstance>()
const rolesLoading = ref(false)
const availableRoles = ref<Role[]>([])
const detailDrawerVisible = ref(false)
const currentWorkflow = ref(null)

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

// 表单数据
const formData = reactive({
  id: '',
  liucheng_mingcheng: '',
  shenhe_leixing: '',
  liucheng_miaoshu: '',
  zhuangtai: 'active',
  buzhou_peizhi: [
    {
      buzhou_mingcheng: '',
      buzhou_miaoshu: '',
      shenhe_ren_jiaose: '',
    },
  ],
})

// 表单验证规则
const formRules: FormRules = {
  liucheng_mingcheng: [{ required: true, message: '请输入流程名称', trigger: 'blur' }],
  shenhe_leixing: [{ required: true, message: '请选择流程类型', trigger: 'change' }],
}

// 计算属性
const dialogTitle = computed(() => {
  return isEdit.value ? '编辑审核流程' : '新建审核流程'
})

// 获取类型标签样式
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    contract: 'primary',
    quote: 'success',
    amount_change: 'warning',
    customer: 'info',
    financial: 'warning',
    yinhang_huikuan: 'danger',
  }
  return typeMap[type] || 'info'
}

// 获取类型标签文本
const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    contract: '合同审核',
    quote: '报价审核',
    amount_change: '金额变更审核',
    customer: '客户审核',
    financial: '财务审核',
    yinhang_huikuan: '银行汇款审核',
  }
  return typeMap[type] || type
}

// 获取状态标签样式
const getStatusTagType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
  }
  return statusMap[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '启用',
    inactive: '禁用',
  }
  return statusMap[status] || status
}

// 方法
const fetchWorkflowList = async () => {
  loading.value = true
  try {
    // 修复：调用真实API获取审核流程列表
    const response = await auditWorkflowApi.getList({
      page: pagination.page,
      size: pagination.size,
    })
    workflowList.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    ElMessage.error('获取审核流程列表失败')
  } finally {
    loading.value = false
  }
}

const fetchAvailableRoles = async () => {
  rolesLoading.value = true
  try {
    const response = await roleAPI.getRoleList({
      page: 1,
      size: 100,
      zhuangtai: 'active',
    })
    availableRoles.value = response.items
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    rolesLoading.value = false
  }
}

const refreshData = () => {
  fetchWorkflowList()
  fetchAvailableRoles()
}

const handleCreate = async () => {
  isEdit.value = false
  resetForm()
  await fetchAvailableRoles()
  dialogVisible.value = true
}

const handleEdit = async (row: Workflow) => {
  isEdit.value = true
  // 修复：正确映射后端字段到前端表单字段
  Object.assign(formData, {
    id: row.id,
    liucheng_mingcheng: row.workflow_name,
    shenhe_leixing: row.audit_type,
    liucheng_miaoshu: row.description,
    zhuangtai: row.status,
    buzhou_peizhi:
      row.steps?.map((step: WorkflowStep) => ({
        buzhou_mingcheng: step.step_name || step.name, // 兼容两种字段名
        buzhou_miaoshu: step.description,
        shenhe_ren_jiaose: step.approver_role,
      })) || [],
  })
  await fetchAvailableRoles()
  dialogVisible.value = true
}

const handleView = async (row: Workflow) => {
  try {
    // 获取工作流详情
    const response = await auditWorkflowApi.getById(row.id)
    currentWorkflow.value = response.data || response
    detailDrawerVisible.value = true
  } catch (error) {
    ElMessage.error('获取工作流详情失败')
  }
}

const handleDelete = async (row: Workflow) => {
  try {
    await ElMessageBox.confirm(`确定要删除流程"${row.workflow_name}"吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // 修复：调用真实删除API
    await auditWorkflowApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchWorkflowList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    // 修复：调用真实API保存数据，转换字段名
    const submitData = {
      workflow_name: formData.liucheng_mingcheng,
      audit_type: formData.shenhe_leixing,
      description: formData.liucheng_miaoshu,
      status: formData.zhuangtai,
      steps: formData.buzhou_peizhi.map((step, index) => ({
        step_name: step.buzhou_mingcheng,
        step_order: index + 1,
        approver_role: step.shenhe_ren_jiaose,
        description: step.buzhou_miaoshu,
        expected_time: 24, // 默认24小时
        is_required: true,
      })),
    }

    if (isEdit.value) {
      await auditWorkflowApi.update(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await auditWorkflowApi.create(submitData)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchWorkflowList()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const addStep = () => {
  formData.buzhou_peizhi.push({
    buzhou_mingcheng: '',
    buzhou_miaoshu: '',
    shenhe_ren_jiaose: '',
  })
}

const removeStep = (index: number) => {
  formData.buzhou_peizhi.splice(index, 1)
}

const resetForm = () => {
  Object.assign(formData, {
    id: '',
    liucheng_mingcheng: '',
    shenhe_leixing: '',
    liucheng_miaoshu: '',
    zhuangtai: 'active',
    buzhou_peizhi: [
      {
        buzhou_mingcheng: '',
        buzhou_miaoshu: '',
        shenhe_ren_jiaose: '',
      },
    ],
  })
  formRef.value?.clearValidate()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  fetchWorkflowList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchWorkflowList()
}

// 步骤预览相关函数
const getStepIcon = (step: WorkflowStep) => {
  const icons: Record<number | string, string> = {
    1: 'User',
    2: 'Document',
    3: 'Check',
    default: 'Operation',
  }
  const stepNum = step.step || step.step_order || 'default'
  return icons[stepNum] || icons.default
}

const getStepType = (step: WorkflowStep) => {
  if (step.is_required === false) return 'info'
  return (step.step || 0) <= 2 ? 'primary' : 'success'
}

const getStepTimestamp = (step: WorkflowStep) => {
  return `步骤 ${step.step || step.step_order}`
}

// SLA相关函数
const getTotalExpectedTime = (steps: WorkflowStep[]) => {
  if (!steps || steps.length === 0) return 0
  return steps.reduce((total, step) => total + (step.expected_time || 24), 0)
}

const getMaxProcessingTime = (steps: WorkflowStep[]) => {
  if (!steps || steps.length === 0) return 0
  return Math.max(...steps.map((step) => step.expected_time || 24))
}

const getAverageProcessingTime = (steps: WorkflowStep[]) => {
  if (!steps || steps.length === 0) return 0
  const total = getTotalExpectedTime(steps)
  return Math.round(total / steps.length)
}

const getCriticalPath = (steps: WorkflowStep[]) => {
  if (!steps || steps.length === 0) return '-'
  const requiredSteps = steps.filter((step) => step.is_required !== false)
  return requiredSteps.map((step) => step.name || step.step_name).join(' → ')
}

// 生命周期
onMounted(() => {
  fetchWorkflowList()
  fetchAvailableRoles()
})
</script>

<style scoped>
.audit-workflow-config {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.action-bar {
  margin-bottom: 20px;
}

.workflow-list {
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.workflow-steps {
  width: 100%;
}

.step-item {
  margin-bottom: 15px;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.step-number {
  font-weight: bold;
  color: #409eff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 工作流详情样式 */
.workflow-detail {
  padding: 20px;
}

.workflow-steps {
  margin-top: 20px;
}

.step-card {
  margin-bottom: 10px;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.step-header h4 {
  margin: 0;
  color: #2c3e50;
}

.step-content p {
  margin: 5px 0;
  color: #606266;
  font-size: 14px;
}

.sla-settings {
  margin-top: 20px;
}

.el-timeline-item__timestamp {
  font-weight: bold;
  color: #409eff;
}
</style>
