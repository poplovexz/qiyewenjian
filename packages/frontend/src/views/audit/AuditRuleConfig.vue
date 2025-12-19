<template>
  <div class="audit-rule-config">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>审核规则配置</h2>
      <p>配置触发审核的条件和规则</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建规则
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <div class="right-filters">
        <el-select
          v-model="filterType"
          placeholder="筛选类型"
          clearable
          style="width: 200px; margin-right: 10px"
          @change="fetchRuleList"
        >
          <el-option label="全部" value="" />
          <el-option label="工作流模板" value="workflow_template" />
          <el-option label="合同金额修正" value="hetong_jine_xiuzheng" />
          <el-option label="报价审核" value="baojia_shenhe" />
          <el-option label="金额变更" value="amount_change" />
          <el-option label="折扣率" value="discount_rate" />
          <el-option label="合同金额" value="contract_amount" />
          <el-option label="报价金额" value="quote_amount" />
        </el-select>
        <el-select
          v-model="filterStatus"
          placeholder="筛选状态"
          clearable
          style="width: 150px"
          @change="fetchRuleList"
        >
          <el-option label="全部" value="" />
          <el-option label="启用" value="Y" />
          <el-option label="禁用" value="N" />
        </el-select>
      </div>
    </div>

    <!-- 规则列表 -->
    <el-card class="rule-list">
      <el-table
        v-loading="loading"
        :data="ruleList"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="guize_mingcheng" label="规则名称" width="200" />
        <el-table-column prop="guize_leixing" label="规则类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.guize_leixing)">
              {{ getTypeLabel(row.guize_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chufa_tiaojian" label="触发条件" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatTriggerCondition(row.chufa_tiaojian) }}
          </template>
        </el-table-column>
        <el-table-column prop="shi_qiyong" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.shi_qiyong)">
              {{ getStatusLabel(row.shi_qiyong) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="liucheng_mingcheng" label="关联流程" width="150">
          <template #default="{ row }">
            {{ row.liucheng_mingcheng || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="handleTest(row)">测试</el-button>
            <el-tooltip
              :content="row.shi_qiyong === 'Y' ? '启用中的规则无法删除，请先禁用' : '删除规则'"
              placement="top"
            >
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(row)"
                :disabled="row.shi_qiyong === 'Y'"
              >
                删除
              </el-button>
            </el-tooltip>
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

    <!-- 规则配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="规则名称" prop="guize_mingcheng">
          <el-input v-model="formData.guize_mingcheng" placeholder="请输入规则名称" />
        </el-form-item>
        
        <el-form-item label="规则类型" prop="guize_leixing">
          <el-select v-model="formData.guize_leixing" placeholder="请选择规则类型">
            <!-- 🔧 修复：移除"工作流模板"选项，工作流模板应该在"审核流程配置"页面管理 -->
            <el-option label="合同金额修正" value="hetong_jine_xiuzheng" />
            <el-option label="报价审核" value="baojia_shenhe" />
            <el-option label="金额变更" value="amount_change" />
            <el-option label="折扣率" value="discount_rate" />
            <el-option label="合同金额" value="contract_amount" />
            <el-option label="报价金额" value="quote_amount" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="规则描述" prop="guize_miaoshu">
          <el-input
            v-model="formData.guize_miaoshu"
            type="textarea"
            :rows="3"
            placeholder="请输入规则描述"
          />
        </el-form-item>
        
        <el-form-item label="优先级" prop="youxian_ji">
          <el-select v-model="formData.youxian_ji" placeholder="请选择优先级">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="规则状态" prop="guize_zhuangtai">
          <el-radio-group v-model="formData.guize_zhuangtai">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 🔧 修复：触发条件配置 - 所有审核规则都需要配置触发条件 -->
        <el-form-item label="触发条件">
          <el-card class="condition-config">
            <div class="condition-item">
              <el-row :gutter="30">
                <el-col :span="7">
                  <el-form-item label="条件类型">
                    <el-select
                      v-model="conditionData.condition_type"
                      placeholder="请选择条件类型"
                      style="width: 100%"
                    >
                      <el-option label="金额减少百分比" value="amount_decrease_percent" />
                      <el-option label="金额减少数值" value="amount_decrease_value" />
                      <el-option label="折扣率超过" value="discount_exceed" />
                      <el-option label="金额超过" value="amount_exceed" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="比较操作">
                    <el-select
                      v-model="conditionData.operator"
                      placeholder="请选择操作"
                      style="width: 100%"
                    >
                      <el-option label="大于" value="gt" />
                      <el-option label="大于等于" value="gte" />
                      <el-option label="小于" value="lt" />
                      <el-option label="小于等于" value="lte" />
                      <el-option label="等于" value="eq" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="9">
                  <el-form-item label="阈值">
                    <el-input-number
                      v-model="conditionData.threshold_value"
                      :min="0"
                      :precision="2"
                      placeholder="请输入阈值"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </el-form-item>

        <!-- 🔧 修复：审核动作配置 - 所有审核规则都需要选择审核流程模板 -->
        <el-form-item label="审核流程">
          <el-card class="action-config">
            <el-row :gutter="30">
              <el-col :span="12">
                <el-form-item label="指定审核流程">
                  <el-select
                    v-model="actionData.workflow_id"
                    placeholder="请选择审核流程"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="workflow in workflowOptions"
                      :key="workflow.value"
                      :label="workflow.label"
                      :value="workflow.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="自动分配审核人">
                  <el-switch v-model="actionData.auto_assign" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="通知方式">
              <el-checkbox-group v-model="actionData.notification_methods">
                <el-checkbox label="email">邮件通知</el-checkbox>
                <el-checkbox label="sms">短信通知</el-checkbox>
                <el-checkbox label="system">系统通知</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-card>
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

    <!-- 规则详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="审核规则详情"
      size="600px"
      direction="rtl"
    >
      <div v-if="currentRule" class="rule-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="规则名称">
            {{ currentRule.guize_mingcheng }}
          </el-descriptions-item>
          <el-descriptions-item label="规则类型">
            <el-tag :type="getTypeTagType(currentRule.guize_leixing)">
              {{ getTypeLabel(currentRule.guize_leixing) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentRule.shi_qiyong)">
              {{ getStatusLabel(currentRule.shi_qiyong) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="排序">
            {{ currentRule.paixu }}
          </el-descriptions-item>
          <el-descriptions-item label="规则描述">
            {{ currentRule.guize_miaoshu || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(currentRule.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(currentRule.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>触发条件配置</el-divider>
        <div class="condition-config">
          <pre>{{ formatJSON(currentRule.chufa_tiaojian) }}</pre>
        </div>

        <el-divider>审核流程配置</el-divider>
        <div class="workflow-config">
          <pre>{{ formatJSON(currentRule.shenhe_liucheng_peizhi) }}</pre>
        </div>
      </div>
    </el-drawer>

    <!-- 规则测试对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="规则测试"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="testRule" class="rule-test">
        <el-alert
          title="规则测试说明"
          description="输入测试数据来验证规则的触发条件和工作流程"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="规则名称">{{ testRule.guize_mingcheng }}</el-descriptions-item>
          <el-descriptions-item label="规则类型">{{ getTypeLabel(testRule.guize_leixing) }}</el-descriptions-item>
        </el-descriptions>

        <el-form ref="testFormRef" :model="testData" label-width="120px">
          <el-card header="测试数据" style="margin-bottom: 20px">
            <div v-if="testRule.guize_leixing === 'hetong_jine_xiuzheng'">
              <el-form-item label="原始金额">
                <el-input-number v-model="testData.original_amount" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="新金额">
                <el-input-number v-model="testData.new_amount" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="变更原因">
                <el-input v-model="testData.change_reason" placeholder="请输入变更原因" />
              </el-form-item>
            </div>

            <div v-else-if="testRule.guize_leixing === 'baojia_shenhe'">
              <el-form-item label="报价金额">
                <el-input-number v-model="testData.amount" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="客户名称">
                <el-input v-model="testData.customer" placeholder="请输入客户名称" />
              </el-form-item>
              <el-form-item label="折扣率">
                <el-input-number v-model="testData.discount_rate" :min="0" :max="1" :precision="2" />
              </el-form-item>
            </div>

            <div v-else>
              <el-form-item label="金额">
                <el-input-number v-model="testData.amount" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item label="备注">
                <el-input v-model="testData.remark" placeholder="请输入备注" />
              </el-form-item>
            </div>
          </el-card>

          <el-card header="测试结果" v-if="testResult">
            <div class="test-result">
              <el-result
                :icon="testResult.triggered ? 'success' : 'info'"
                :title="testResult.triggered ? '规则已触发' : '规则未触发'"
                :sub-title="testResult.trigger_reason"
              >
                <template #extra>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="规则名称">{{ testResult.rule_name }}</el-descriptions-item>
                    <el-descriptions-item label="触发状态">
                      <el-tag :type="testResult.triggered ? 'success' : 'info'">
                        {{ testResult.triggered ? '已触发' : '未触发' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="触发原因">{{ testResult.trigger_reason }}</el-descriptions-item>
                  </el-descriptions>

                  <div v-if="testResult.workflow_preview" style="margin-top: 20px">
                    <h4>工作流预览</h4>
                    <el-timeline>
                      <el-timeline-item
                        v-for="step in testResult.workflow_preview.steps"
                        :key="step.step"
                        :type="step.applicable ? 'primary' : 'info'"
                      >
                        <div class="timeline-step">
                          <h5>{{ step.name }}</h5>
                          <p>审批角色: {{ step.role }}</p>
                          <p v-if="step.applicable">预计时间: {{ step.estimated_time }}</p>
                          <p v-else>跳过原因: {{ step.skip_reason }}</p>
                        </div>
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </template>
              </el-result>
            </div>
          </el-card>
        </el-form>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="testDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="runTest" :loading="testing">
            {{ testing ? '测试中...' : '运行测试' }}
          </el-button>
          <el-button type="success" @click="loadTestTemplate">加载模板</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import type { FormInstance, FormRules } from 'element-plus'
import { auditRuleApi, auditWorkflowApi } from '@/api/modules/audit'
import request from '@/utils/request'

// 类型定义
interface TriggerCondition {
  condition_type?: string
  operator?: string
  threshold_value?: string | number
  [key: string]: unknown
}

interface WorkflowConfig {
  workflow_id?: string
  auto_assign?: boolean
  notification_methods?: string[]
  [key: string]: unknown
}

interface AuditRule {
  id: string
  guize_mingcheng: string
  guize_leixing: string
  guize_miaoshu?: string
  chufa_tiaojian: TriggerCondition | string
  shenhe_liucheng_peizhi: WorkflowConfig | string
  shi_qiyong: string
  paixu: number
  liucheng_mingcheng?: string
  created_at?: string
  updated_at?: string
}

interface WorkflowOption {
  value: string
  label: string
}

interface TestResult {
  triggered: boolean
  trigger_reason: string
  rule_name: string
  workflow_preview?: {
    steps: Array<{
      step: number
      name: string
      role: string
      applicable: boolean
      estimated_time?: string
      skip_reason?: string
    }>
  }
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const ruleList = ref<AuditRule[]>([])
const workflowOptions = ref<WorkflowOption[]>([])
const formRef = ref<FormInstance>()
const detailDrawerVisible = ref(false)
const currentRule = ref<AuditRule | null>(null)
const testDialogVisible = ref(false)
const testRule = ref<AuditRule | null>(null)
const testing = ref(false)
const testResult = ref<TestResult | null>(null)
const testFormRef = ref<FormInstance>()
const filterType = ref('')
const filterStatus = ref('')

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const formData = reactive({
  id: '',
  guize_mingcheng: '',
  guize_leixing: '',
  guize_miaoshu: '',
  youxian_ji: 'medium',
  guize_zhuangtai: 'active'
})

// 条件数据
const conditionData = reactive({
  condition_type: '',
  operator: '',
  threshold_value: 0
})

// 动作数据
const actionData = reactive({
  workflow_id: '',
  auto_assign: true,
  notification_methods: ['system']
})

// 测试数据
const testData = reactive({
  amount: 0,
  original_amount: 0,
  new_amount: 0,
  change_reason: '',
  customer: '',
  discount_rate: 0,
  remark: ''
})

// 表单验证规则
const formRules: FormRules = {
  guize_mingcheng: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  guize_leixing: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  return isEdit.value ? '编辑审核规则' : '新建审核规则'
})

// 获取类型标签样式
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    workflow_template: 'primary',
    hetong_jine_xiuzheng: 'danger',
    baojia_shenhe: 'warning',
    amount_change: 'warning',
    discount_rate: 'success',
    contract_amount: 'primary',
    quote_amount: 'info'
  }
  return typeMap[type] || 'info'
}

// 获取类型标签文本
const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    workflow_template: '工作流模板',
    hetong_jine_xiuzheng: '合同金额修正',
    baojia_shenhe: '报价审核',
    amount_change: '金额变更',
    discount_rate: '折扣率',
    contract_amount: '合同金额',
    quote_amount: '报价金额'
  }
  return typeMap[type] || type
}

// 获取状态标签样式
const getStatusTagType = (status: string) => {
  const statusMap: Record<string, string> = {
    'Y': 'success',  // 启用
    'N': 'info',     // 禁用
    active: 'success',
    inactive: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    'Y': '启用',     // 后端返回Y表示启用
    'N': '禁用',     // 后端返回N表示禁用
    active: '启用',
    inactive: '禁用'
  }
  return statusMap[status] || status
}

// 格式化JSON显示
const formatJSON = (data: unknown) => {
  if (!data) return '-'
  try {
    if (typeof data === 'string') {
      return JSON.stringify(JSON.parse(data), null, 2)
    }
    return JSON.stringify(data, null, 2)
  } catch (error) {
    return String(data)
  }
}

// 测试相关方法
const resetTestData = () => {
  Object.assign(testData, {
    amount: 0,
    original_amount: 0,
    new_amount: 0,
    change_reason: '',
    customer: '',
    discount_rate: 0,
    remark: ''
  })
}

const runTest = async () => {
  if (!testRule.value) return

  try {
    testing.value = true

    // 构建测试数据
    const requestData = {
      rule_id: testRule.value.id,
      test_data: { ...testData }
    }

    // 调用测试API - 使用 request 工具自动处理认证
    const result = await request.post('/audit-rules/test/single', requestData) as TestResult
    testResult.value = result

    ElMessage.success('测试完成')
  } catch (error: unknown) {
    console.error('规则测试失败:', error)
    const axiosError = error as { response?: { data?: { detail?: string } }; message?: string }
    const errorMsg = axiosError.response?.data?.detail || axiosError.message || '规则测试失败'
    ElMessage.error(errorMsg)
  } finally {
    testing.value = false
  }
}

// 测试模板类型
interface TestTemplate {
  type: string
  template: Record<string, unknown>
}

const loadTestTemplate = async () => {
  if (!testRule.value) return

  try {
    // 获取测试模板 - 使用 request 工具自动处理认证
    const data = await request.get('/audit-rules/test/templates') as { templates?: TestTemplate[] }
    const templates = data.templates || []

    // 查找匹配的模板
    const template = templates.find((t: TestTemplate) => t.type === testRule.value?.guize_leixing)

    if (template) {
      Object.assign(testData, template.template)
      ElMessage.success('模板加载成功')
    } else {
      ElMessage.warning('未找到匹配的测试模板')
    }
  } catch (error: unknown) {
    console.error('加载测试模板失败:', error)
    const axiosError = error as { response?: { data?: { detail?: string } }; message?: string }
    const errorMsg = axiosError.response?.data?.detail || axiosError.message || '加载测试模板失败'
    ElMessage.error(errorMsg)
  }
}



// 格式化触发条件
const formatTriggerCondition = (condition: TriggerCondition | string | null) => {
  if (!condition) return '-'
  try {
    const parsed = typeof condition === 'string' ? JSON.parse(condition) : condition
    return `${parsed.condition_type} ${parsed.operator} ${parsed.threshold_value}`
  } catch {
    return '-'
  }
}

// 方法
const fetchRuleList = async () => {
  loading.value = true
  try {
    // 修复：调用真实API获取审核规则列表，支持筛选
    const params: Record<string, string | number> = {
      page: pagination.page,
      size: pagination.size
    }

    // 添加筛选条件
    if (filterType.value) {
      params.guize_leixing = filterType.value
    }
    if (filterStatus.value) {
      params.shi_qiyong = filterStatus.value
    }

    const response = await auditRuleApi.getList(params)

    // 🔧 修复：过滤掉工作流模板类型的规则（这些应该只在工作流配置页面显示）
    const filteredItems = (response.items || []).filter(
      (item: AuditRule) => item.guize_leixing !== 'workflow_template'
    )

    ruleList.value = filteredItems
    // 注意：total也需要相应调整，但由于后端返回的total包含了workflow_template，
    // 这里我们使用过滤后的数量。如果需要精确分页，应该在后端过滤
    pagination.total = filteredItems.length
  } catch (error) {
    console.error('获取审核规则列表失败:', error)
    ElMessage.error('获取审核规则列表失败')
  } finally {
    loading.value = false
  }
}

// 工作流响应类型
interface WorkflowItem {
  id: string
  workflow_name: string
}

const fetchWorkflowOptions = async () => {
  try {
    // 修复：调用真实API获取审核流程列表
    const { auditWorkflowApi } = await import('@/api/modules/audit')
    const response = await auditWorkflowApi.getList({
      page: 1,
      size: 100,
      status: 'active'
    })

    // 转换为下拉框选项格式
    workflowOptions.value = (response.items || []).map((workflow: WorkflowItem) => ({
      label: workflow.workflow_name,
      value: workflow.id
    }))
  } catch (error) {
    console.error('获取审核流程选项失败:', error)
    workflowOptions.value = []
  }
}

const refreshData = () => {
  fetchRuleList()
}

const handleCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: AuditRule) => {
  isEdit.value = true

  // 修复：正确映射后端字段到前端表单
  formData.id = row.id
  formData.guize_mingcheng = row.guize_mingcheng
  formData.guize_leixing = row.guize_leixing
  formData.guize_miaoshu = row.guize_miaoshu || ''
  formData.guize_zhuangtai = row.shi_qiyong === 'Y' ? 'active' : 'inactive'  // 状态字段映射

  // 解析触发条件
  if (row.chufa_tiaojian) {
    try {
      const condition = typeof row.chufa_tiaojian === 'string'
        ? JSON.parse(row.chufa_tiaojian)
        : row.chufa_tiaojian
      Object.assign(conditionData, condition)
    } catch (error) {
      console.error('解析触发条件失败:', error)
    }
  }

  // 🔧 修复：解析审核流程配置
  if (row.shenhe_liucheng_peizhi) {
    try {
      const workflow = typeof row.shenhe_liucheng_peizhi === 'string'
        ? JSON.parse(row.shenhe_liucheng_peizhi)
        : row.shenhe_liucheng_peizhi
      actionData.workflow_id = workflow.workflow_id || ''
      actionData.auto_assign = workflow.auto_assign !== undefined ? workflow.auto_assign : true
      actionData.notification_methods = workflow.notification_methods || ['system']
    } catch (error) {
      console.error('解析审核流程配置失败:', error)
    }
  }

  dialogVisible.value = true
}

const handleView = async (row: AuditRule) => {
  try {
    // 获取规则详情
    const response = await auditRuleApi.getById(row.id)
    currentRule.value = response.data || response
    detailDrawerVisible.value = true
  } catch (error) {
    console.error('获取规则详情失败:', error)
    ElMessage.error('获取规则详情失败')
  }
}

const handleTest = (row: AuditRule) => {
  testRule.value = row
  testResult.value = null
  resetTestData()
  testDialogVisible.value = true
}

const handleDelete = async (row: AuditRule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则"${row.guize_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 修复：调用真实删除API
    await auditRuleApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchRuleList()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 提取详细错误信息
      let errorMsg = '删除失败'
      const axiosError = error as { response?: { data?: { detail?: string } } }
      if (axiosError?.response?.data?.detail) {
        errorMsg = axiosError.response.data.detail
      }
      ElMessage.error(errorMsg)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 🔧 修复：验证必须选择审核流程模板
    if (!actionData.workflow_id) {
      ElMessage.warning('请选择审核流程模板')
      return
    }

    submitting.value = true

    // 🔧 修复：构建触发条件配置
    const chufaTiaojian = conditionData

    // 🔧 修复：构建工作流配置，引用选择的工作流模板
    const workflowConfig: WorkflowConfig = {
      workflow_id: actionData.workflow_id,
      auto_assign: actionData.auto_assign,
      notification_methods: actionData.notification_methods
    }

    // 🔧 修复：获取工作流模板的步骤配置
    if (actionData.workflow_id) {
      try {
        // 🔧 修复：使用工作流API获取工作流模板详情，而不是审核规则API
        const workflowDetail = await auditWorkflowApi.getById(actionData.workflow_id)
        const workflow = workflowDetail.data || workflowDetail

        // 从工作流模板中提取步骤配置
        if (workflow.shenhe_liucheng_peizhi) {
          const templateConfig = typeof workflow.shenhe_liucheng_peizhi === 'string'
            ? JSON.parse(workflow.shenhe_liucheng_peizhi)
            : workflow.shenhe_liucheng_peizhi

          // 同步步骤配置到当前规则
          if (templateConfig.steps) {
            workflowConfig.steps = templateConfig.steps
          }
        }
      } catch (error) {
        console.error('获取工作流模板步骤失败:', error)
        ElMessage.warning('无法获取工作流模板步骤配置，请检查模板是否存在')
      }
    }

    const submitData = {
      guize_mingcheng: formData.guize_mingcheng,
      guize_leixing: formData.guize_leixing,
      guize_miaoshu: formData.guize_miaoshu,
      chufa_tiaojian: chufaTiaojian,  // 触发条件配置对象
      shenhe_liucheng_peizhi: workflowConfig,  // 包含步骤配置的完整工作流配置
      shi_qiyong: formData.guize_zhuangtai === 'active' ? 'Y' : 'N',  // 修复：状态字段映射
      paixu: 0  // 默认排序
    }

    // 修复：调用真实API保存数据
    if (isEdit.value) {
      await auditRuleApi.update(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await auditRuleApi.create(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchRuleList()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// 🔧 修复：移除步骤管理方法，这些应该在工作流模板管理页面使用

const resetForm = () => {
  Object.assign(formData, {
    id: '',
    guize_mingcheng: '',
    guize_leixing: '',
    guize_miaoshu: '',
    youxian_ji: 'medium',
    guize_zhuangtai: 'active'
  })
  
  Object.assign(conditionData, {
    condition_type: '',
    operator: '',
    threshold_value: 0
  })

  Object.assign(actionData, {
    workflow_id: '',
    auto_assign: true,
    notification_methods: ['system']
  })

  formRef.value?.clearValidate()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  fetchRuleList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchRuleList()
}

// 生命周期
onMounted(() => {
  fetchRuleList()
  fetchWorkflowOptions()
})
</script>

<style scoped>
.audit-rule-config {
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

.rule-list {
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.condition-config,
.action-config {
  margin-bottom: 15px;
}

.condition-item {
  margin-bottom: 15px;
}

/* 改善表单布局 */
.condition-config .el-form-item {
  margin-bottom: 18px;
}

.condition-config .el-form-item__label {
  font-weight: 500;
  color: #606266;
  width: 80px !important;
  text-align: right;
}

.action-config .el-form-item {
  margin-bottom: 18px;
}

.action-config .el-form-item__label {
  font-weight: 500;
  color: #606266;
  width: 120px !important;
  text-align: right;
}

/* 统一标签宽度实现对齐 */
.condition-config .el-form-item__content,
.action-config .el-form-item__content {
  margin-left: 0 !important;
}

/* 确保选择框和输入框有足够的最小宽度 */
.condition-config .el-select,
.condition-config .el-input-number,
.action-config .el-select {
  min-width: 120px;
}

/* 改善卡片内边距 */
.condition-config .el-card__body,
.action-config .el-card__body {
  padding: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 规则详情样式 */
.rule-detail {
  padding: 20px;
}

.rule-detail .condition-config,
.rule-detail .workflow-config {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.rule-detail .condition-config pre,
.rule-detail .workflow-config pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #2c3e50;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 规则测试样式 */
.rule-test {
  padding: 20px;
}

.test-result {
  margin-top: 20px;
}

.timeline-step h5 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.timeline-step p {
  margin: 2px 0;
  color: #606266;
  font-size: 14px;
}

/* 操作栏样式 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-bar .left-actions {
  display: flex;
  gap: 10px;
}

.action-bar .right-filters {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 步骤配置样式 */
.steps-config {
  background: #f5f7fa;
}

.step-item {
  margin-bottom: 15px;
}

.step-item:last-child {
  margin-bottom: 0;
}
</style>
