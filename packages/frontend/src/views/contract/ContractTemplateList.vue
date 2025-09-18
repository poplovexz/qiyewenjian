<template>
  <div class="contract-template-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>合同模板管理</h2>
      <p>管理系统中的合同模板，支持创建、编辑、预览和版本控制</p>
    </div>

    <!-- 搜索和筛选区域 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="请输入模板名称或编码"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="合同类型">
          <el-select
            v-model="searchForm.hetong_leixing"
            placeholder="请选择合同类型"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="option in contractTypeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模板状态">
          <el-select
            v-model="searchForm.moban_zhuangtai"
            placeholder="请选择模板状态"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="option in templateStatusOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="当前版本">
          <el-select
            v-model="searchForm.shi_dangqian_banben"
            placeholder="请选择"
            clearable
            style="width: 100px"
          >
            <el-option label="是" value="Y" />
            <el-option label="否" value="N" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="action-card" shadow="never">
      <div class="action-bar">
        <div class="action-left">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建模板
          </el-button>
          
          <el-button 
            type="danger" 
            :disabled="!hasSelection"
            @click="handleBatchDelete"
          >
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
          
          <el-dropdown @command="handleBatchAction">
            <el-button :disabled="!hasSelection">
              批量操作
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="active">批量启用</el-dropdown-item>
                <el-dropdown-item command="draft">批量设为草稿</el-dropdown-item>
                <el-dropdown-item command="archived">批量归档</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <div class="action-right">
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="contractStore.loading"
        :data="contractStore.templates"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="moban_mingcheng" label="模板名称" min-width="200">
          <template #default="{ row }">
            <div class="template-name">
              <span class="name">{{ row.moban_mingcheng }}</span>
              <el-tag 
                v-if="row.shi_dangqian_banben === 'Y'" 
                type="success" 
                size="small"
                style="margin-left: 8px"
              >
                当前版本
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="moban_bianma" label="模板编码" width="150" />
        
        <el-table-column prop="hetong_leixing" label="合同类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getContractTypeTagType(row.hetong_leixing)">
              {{ getContractTypeLabel(row.hetong_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="banben_hao" label="版本号" width="100" />
        
        <el-table-column prop="moban_zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.moban_zhuangtai)">
              {{ getStatusLabel(row.moban_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="shiyong_cishu" label="使用次数" width="100" />
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">
              查看
            </el-button>
            <el-button type="primary" link @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="primary" link @click="handlePreview(row)">
              预览
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="contractStore.templatePage"
          v-model:page-size="contractStore.templateSize"
          :total="contractStore.templateTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 合同模板表单对话框 -->
    <ContractTemplateForm
      v-model:visible="formVisible"
      :mode="formMode"
      :template="currentTemplate"
      @success="handleFormSuccess"
    />

    <!-- 预览对话框 -->
    <ContractTemplatePreview
      v-model:visible="previewVisible"
      :template="previewTemplate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete, ArrowDown } from '@element-plus/icons-vue'
import { useContractStore } from '@/stores/modules/contract'
import { contractTypeOptions, templateStatusOptions } from '@/api/modules/contract'
import type { ContractTemplate } from '@/api/modules/contract'
import ContractTemplateForm from './components/ContractTemplateForm.vue'
import ContractTemplatePreview from './components/ContractTemplatePreview.vue'
import { formatDateTime } from '@/utils/date'

// Store
const contractStore = useContractStore()

// 响应式数据
const searchForm = reactive({
  search: '',
  hetong_leixing: '',
  moban_zhuangtai: '',
  shi_dangqian_banben: ''
})

const selectedTemplates = ref<ContractTemplate[]>([])
const formVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const currentTemplate = ref<ContractTemplate | null>(null)
const previewVisible = ref(false)
const previewTemplate = ref<ContractTemplate | null>(null)

// 计算属性
const hasSelection = computed(() => selectedTemplates.value.length > 0)

// 方法
const handleSearch = async () => {
  contractStore.setPage(1)
  await contractStore.fetchTemplates(searchForm)
}

const handleReset = async () => {
  Object.assign(searchForm, {
    search: '',
    hetong_leixing: '',
    moban_zhuangtai: '',
    shi_dangqian_banben: ''
  })
  await handleSearch()
}

const handleRefresh = async () => {
  await contractStore.fetchTemplates(searchForm)
}

const handleCreate = () => {
  formMode.value = 'create'
  currentTemplate.value = null
  formVisible.value = true
}

const handleView = (template: ContractTemplate) => {
  formMode.value = 'view'
  currentTemplate.value = template
  formVisible.value = true
}

const handleEdit = (template: ContractTemplate) => {
  formMode.value = 'edit'
  currentTemplate.value = template
  formVisible.value = true
}

const handlePreview = (template: ContractTemplate) => {
  previewTemplate.value = template
  previewVisible.value = true
}

const handleDelete = async (template: ContractTemplate) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除合同模板"${template.moban_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await contractStore.deleteTemplate(template.id)
    await handleRefresh()
  } catch (error) {
    // 用户取消删除
  }
}

const handleSelectionChange = (selection: ContractTemplate[]) => {
  selectedTemplates.value = selection
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTemplates.value.length} 个合同模板吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const ids = selectedTemplates.value.map(item => item.id)
    await contractStore.batchDeleteTemplates(ids)
    await handleRefresh()
  } catch (error) {
    // 用户取消删除
  }
}

const handleBatchAction = async (command: string) => {
  const ids = selectedTemplates.value.map(item => item.id)
  await contractStore.batchUpdateStatus(ids, command)
  await handleRefresh()
}

const handlePageChange = async (page: number) => {
  contractStore.setPage(page)
  await contractStore.fetchTemplates(searchForm)
}

const handleSizeChange = async (size: number) => {
  contractStore.setSize(size)
  await contractStore.fetchTemplates(searchForm)
}

const handleFormSuccess = async () => {
  formVisible.value = false
  await handleRefresh()
}

// 辅助方法
const getContractTypeLabel = (type: string) => {
  const option = contractTypeOptions.find(item => item.value === type)
  return option?.label || type
}

const getContractTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    'daili_jizhang': 'primary',
    'zengzhi_fuwu': 'success',
    'zixun_fuwu': 'warning'
  }
  return typeMap[type] || 'info'
}

const getStatusLabel = (status: string) => {
  const option = templateStatusOptions.find(item => item.value === status)
  return option?.label || status
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, string> = {
    'draft': 'info',
    'active': 'success',
    'archived': 'warning'
  }
  return statusMap[status] || 'info'
}

// 生命周期
onMounted(async () => {
  await contractStore.fetchTemplates()
})
</script>

<style scoped>
.contract-template-list {
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
  color: #606266;
  font-size: 14px;
}

.search-card,
.action-card,
.table-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left {
  display: flex;
  gap: 12px;
}

.template-name {
  display: flex;
  align-items: center;
}

.template-name .name {
  font-weight: 500;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
