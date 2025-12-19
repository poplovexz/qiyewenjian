<template>
  <div class="compliance-templates">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>合规事项模板</h2>
        <p class="subtitle">管理税务申报、年报等合规事项模板</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建模板
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="搜索模板名称、编码"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="事项类型">
          <el-select
            v-model="searchForm.shixiang_leixing"
            placeholder="选择事项类型"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="(label, value) in complianceStore.templateTypeMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="申报周期">
          <el-select
            v-model="searchForm.shenbao_zhouqi"
            placeholder="选择申报周期"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="(label, value) in complianceStore.reportCycleMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="searchForm.moban_zhuangtai"
            placeholder="选择状态"
            clearable
            style="width: 100px"
          >
            <el-option
              v-for="(label, value) in complianceStore.templateStatusMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 模板列表 -->
    <el-card shadow="never">
      <el-table
        :data="tableData"
        v-loading="complianceStore.loading"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="shixiang_mingcheng" label="事项名称" min-width="200">
          <template #default="{ row }">
            <div class="template-name">
              <div class="name">{{ row.shixiang_mingcheng }}</div>
              <div class="code">{{ row.shixiang_bianma }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="shixiang_leixing" label="事项类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.shixiang_leixing)">
              {{ complianceStore.templateTypeMap[row.shixiang_leixing] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="shenbao_zhouqi" label="申报周期" width="100">
          <template #default="{ row }">
            {{ complianceStore.reportCycleMap[row.shenbao_zhouqi] }}
          </template>
        </el-table-column>

        <el-table-column prop="fengxian_dengji" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.fengxian_dengji)" size="small">
              {{ complianceStore.riskLevelMap[row.fengxian_dengji] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="tiqian_tixing_tianshu" label="提醒天数" width="120">
          <template #default="{ row }">
            <el-tag v-for="day in row.tiqian_tixing_tianshu.split(',')" :key="day" size="small" class="reminder-tag">
              {{ day }}天
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="moban_zhuangtai" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.moban_zhuangtai)" size="small">
              {{ complianceStore.templateStatusMap[row.moban_zhuangtai] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="160">
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
            <el-button type="primary" link @click="handleCopy(row)">
              复制
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
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑模板对话框 -->
    <TemplateFormDialog
      v-model:visible="showCreateDialog"
      :template-id="editingTemplateId"
      @success="handleFormSuccess"
    />

    <!-- 模板详情对话框 -->
    <TemplateDetailDialog
      v-model:visible="showDetailDialog"
      :template-id="viewingTemplateId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useComplianceStore } from '@/stores/modules/complianceManagement'
import { format } from 'date-fns'
import TemplateFormDialog from './components/TemplateFormDialog.vue'
import TemplateDetailDialog from './components/TemplateDetailDialog.vue'

// 模板类型
interface ComplianceTemplate {
  id: string
  shixiang_mingcheng: string
  shixiang_bianma: string
  shixiang_leixing?: string
  shenbao_zhouqi?: string
  moban_zhuangtai?: string
  fengxian_dengji?: string
  [key: string]: unknown
}

// Store
const complianceStore = useComplianceStore()

// 响应式数据
const searchForm = reactive({
  search: '',
  shixiang_leixing: '',
  shenbao_zhouqi: '',
  moban_zhuangtai: '',
  fengxian_dengji: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const tableData = ref([])
const selectedRows = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingTemplateId = ref('')
const viewingTemplateId = ref('')

// 计算属性
const hasSelection = computed(() => selectedRows.value.length > 0)

// 方法
const loadTemplates = async () => {
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    const response = await complianceStore.fetchTemplates(params)
    tableData.value = response.items
    pagination.total = response.total
  } catch (error) {
    console.error('加载模板列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadTemplates()
}

const handleReset = () => {
  Object.assign(searchForm, {
    search: '',
    shixiang_leixing: '',
    shenbao_zhouqi: '',
    moban_zhuangtai: '',
    fengxian_dengji: ''
  })
  pagination.page = 1
  loadTemplates()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadTemplates()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadTemplates()
}

const handleSelectionChange = (selection: ComplianceTemplate[]) => {
  selectedRows.value = selection
}

const handleView = (row: ComplianceTemplate) => {
  viewingTemplateId.value = row.id
  showDetailDialog.value = true
}

const handleEdit = (row: ComplianceTemplate) => {
  editingTemplateId.value = row.id
  showCreateDialog.value = true
}

const handleCopy = async (row: ComplianceTemplate) => {
  try {
    const templateData: Record<string, unknown> = {
      ...row,
      shixiang_mingcheng: `${row.shixiang_mingcheng}（副本）`,
      shixiang_bianma: `${row.shixiang_bianma}_COPY_${Date.now()}`,
      moban_zhuangtai: 'draft'
    }

    delete templateData.id
    delete templateData.created_at
    delete templateData.updated_at
    delete templateData.created_by
    delete templateData.updated_by

    await complianceStore.createTemplate(templateData)
    loadTemplates()
  } catch (error) {
    console.error('复制模板失败:', error)
  }
}

const handleDelete = async (row: ComplianceTemplate) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${row.shixiang_mingcheng}"吗？`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    await complianceStore.deleteTemplate(row.id)
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
    }
  }
}

const handleFormSuccess = () => {
  showCreateDialog.value = false
  editingTemplateId.value = ''
  loadTemplates()
}

const getTypeTagType = (type: string) => {
  const typeMap = {
    shuiwu_shenbao: 'danger',
    nianbao_shenbao: 'warning',
    zhizhao_nianjian: 'primary',
    qita_heguishixiang: 'info'
  }
  return typeMap[type] || 'info'
}

const getRiskTagType = (risk: string) => {
  const riskMap = {
    low: 'success',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return riskMap[risk] || 'info'
}

const getStatusTagType = (status: string) => {
  const statusMap = {
    active: 'success',
    inactive: 'info',
    draft: 'warning'
  }
  return statusMap[status] || 'info'
}

const formatDateTime = (dateString: string) => {
  return format(new Date(dateString), 'yyyy-MM-dd HH:mm')
}

// 生命周期
onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.compliance-templates {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.template-name .name {
  font-weight: 500;
  color: #303133;
}

.template-name .code {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.reminder-tag {
  margin-right: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
