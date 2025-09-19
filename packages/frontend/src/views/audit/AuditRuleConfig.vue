<template>
  <div class="audit-rule-config">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>审核规则配置</h2>
      <p>配置触发审核的条件和规则</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建规则
      </el-button>
      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
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
        <el-table-column prop="guize_zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.guize_zhuangtai)">
              {{ getStatusLabel(row.guize_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="youxian_ji" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.youxian_ji)">
              {{ getPriorityLabel(row.youxian_ji) }}
            </el-tag>
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
            <el-button 
              size="small" 
              type="danger" 
              @click="handleDelete(row)"
              :disabled="row.guize_zhuangtai === 'active'"
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

        <!-- 触发条件配置 -->
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

        <!-- 审核动作配置 -->
        <el-form-item label="审核动作">
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
                      :key="workflow.id"
                      :label="workflow.liucheng_mingcheng"
                      :value="workflow.id"
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import type { FormInstance, FormRules } from 'element-plus'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const ruleList = ref([])
const workflowOptions = ref([])
const formRef = ref<FormInstance>()

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
    active: 'success',
    inactive: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '启用',
    inactive: '禁用'
  }
  return statusMap[status] || status
}

// 获取优先级标签样式
const getPriorityTagType = (priority: string) => {
  const priorityMap: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return priorityMap[priority] || 'info'
}

// 获取优先级标签文本
const getPriorityLabel = (priority: string) => {
  const priorityMap: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return priorityMap[priority] || priority
}

// 格式化触发条件
const formatTriggerCondition = (condition: any) => {
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
    // TODO: 调用API获取审核规则列表
    // const response = await auditRuleApi.getList(pagination)
    // ruleList.value = response.data.items
    // pagination.total = response.data.total
    
    // 模拟数据
    ruleList.value = []
    pagination.total = 0
  } catch (error) {
    console.error('获取审核规则列表失败:', error)
    ElMessage.error('获取审核规则列表失败')
  } finally {
    loading.value = false
  }
}

const fetchWorkflowOptions = async () => {
  try {
    // TODO: 调用API获取审核流程选项
    // const response = await auditWorkflowApi.getOptions()
    // workflowOptions.value = response.data
    
    // 模拟数据
    workflowOptions.value = []
  } catch (error) {
    console.error('获取审核流程选项失败:', error)
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

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(formData, row)
  
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
  
  // 解析审核动作
  if (row.shenhe_dongzuo) {
    try {
      const action = typeof row.shenhe_dongzuo === 'string' 
        ? JSON.parse(row.shenhe_dongzuo) 
        : row.shenhe_dongzuo
      Object.assign(actionData, action)
    } catch (error) {
      console.error('解析审核动作失败:', error)
    }
  }
  
  dialogVisible.value = true
}

const handleView = (row: any) => {
  // TODO: 实现查看详情
  ElMessage.info('查看功能开发中')
}

const handleDelete = async (row: any) => {
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
    
    // TODO: 调用删除API
    // await auditRuleApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchRuleList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 构建提交数据
    const submitData = {
      ...formData,
      chufa_tiaojian: JSON.stringify(conditionData),
      shenhe_dongzuo: JSON.stringify(actionData)
    }
    
    // TODO: 调用API保存数据
    if (isEdit.value) {
      // await auditRuleApi.update(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      // await auditRuleApi.create(submitData)
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
</style>
