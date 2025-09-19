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
      <el-table
        v-loading="loading"
        :data="workflowList"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="liucheng_mingcheng" label="流程名称" width="200" />
        <el-table-column prop="liucheng_leixing" label="流程类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.liucheng_leixing)">
              {{ getTypeLabel(row.liucheng_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="liucheng_zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.liucheng_zhuangtai)">
              {{ getStatusLabel(row.liucheng_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="buzhou_shuliang" label="步骤数量" width="100" />
        <el-table-column prop="liucheng_miaoshu" label="描述" show-overflow-tooltip />
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
              :disabled="row.liucheng_zhuangtai === 'active'"
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
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="流程名称" prop="liucheng_mingcheng">
          <el-input v-model="formData.liucheng_mingcheng" placeholder="请输入流程名称" />
        </el-form-item>
        
        <el-form-item label="流程类型" prop="liucheng_leixing">
          <el-select v-model="formData.liucheng_leixing" placeholder="请选择流程类型">
            <el-option label="合同审核" value="contract" />
            <el-option label="报价审核" value="quote" />
            <el-option label="金额变更审核" value="amount_change" />
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
        
        <el-form-item label="流程状态" prop="liucheng_zhuangtai">
          <el-radio-group v-model="formData.liucheng_zhuangtai">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 审核步骤配置 -->
        <el-form-item label="审核步骤">
          <div class="workflow-steps">
            <div
              v-for="(step, index) in formData.buzhou_peizhi"
              :key="index"
              class="step-item"
            >
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
                          :value="role.id"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="步骤描述">
                  <el-input
                    v-model="step.buzhou_miaoshu"
                    placeholder="请输入步骤描述"
                  />
                </el-form-item>
              </el-card>
            </div>
            
            <el-button
              type="dashed"
              style="width: 100%; margin-top: 10px;"
              @click="addStep"
            >
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Clock, Check, Warning } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import type { FormInstance, FormRules } from 'element-plus'
import { roleAPI, type Role } from '@/api/modules/role'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const workflowList = ref([])
const formRef = ref<FormInstance>()
const rolesLoading = ref(false)
const availableRoles = ref<Role[]>([])

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const formData = reactive({
  id: '',
  liucheng_mingcheng: '',
  liucheng_leixing: '',
  liucheng_miaoshu: '',
  liucheng_zhuangtai: 'active',
  buzhou_peizhi: [
    {
      buzhou_mingcheng: '',
      buzhou_miaoshu: '',
      shenhe_ren_jiaose: ''
    }
  ]
})

// 表单验证规则
const formRules: FormRules = {
  liucheng_mingcheng: [
    { required: true, message: '请输入流程名称', trigger: 'blur' }
  ],
  liucheng_leixing: [
    { required: true, message: '请选择流程类型', trigger: 'change' }
  ]
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
    amount_change: 'warning'
  }
  return typeMap[type] || 'info'
}

// 获取类型标签文本
const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    contract: '合同审核',
    quote: '报价审核',
    amount_change: '金额变更审核'
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

// 方法
const fetchWorkflowList = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取审核流程列表
    // const response = await auditWorkflowApi.getList(pagination)
    // workflowList.value = response.data.items
    // pagination.total = response.data.total
    
    // 模拟数据
    workflowList.value = []
    pagination.total = 0
  } catch (error) {
    console.error('获取审核流程列表失败:', error)
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
      zhuangtai: 'active'
    })
    availableRoles.value = response.items
  } catch (error) {
    console.error('获取角色列表失败:', error)
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

const handleEdit = async (row: any) => {
  isEdit.value = true
  Object.assign(formData, row)
  await fetchAvailableRoles()
  dialogVisible.value = true
}

const handleView = (row: any) => {
  // TODO: 实现查看详情
  ElMessage.info('查看功能开发中')
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除流程"${row.liucheng_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用删除API
    // await auditWorkflowApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchWorkflowList()
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
    
    // TODO: 调用API保存数据
    if (isEdit.value) {
      // await auditWorkflowApi.update(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      // await auditWorkflowApi.create(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchWorkflowList()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const addStep = () => {
  formData.buzhou_peizhi.push({
    buzhou_mingcheng: '',
    buzhou_miaoshu: '',
    shenhe_ren_jiaose: ''
  })
}

const removeStep = (index: number) => {
  formData.buzhou_peizhi.splice(index, 1)
}

const resetForm = () => {
  Object.assign(formData, {
    id: '',
    liucheng_mingcheng: '',
    liucheng_leixing: '',
    liucheng_miaoshu: '',
    liucheng_zhuangtai: 'active',
    buzhou_peizhi: [
      {
        buzhou_mingcheng: '',
        buzhou_miaoshu: '',
        shenhe_ren_jiaose: ''
      }
    ]
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
</style>
