<template>
  <div class="service-record-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>服务记录管理</h2>
      <p>管理所有客户的服务记录和沟通历史</p>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索客户名称、沟通内容..."
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.goutong_fangshi"
          placeholder="沟通方式"
          style="width: 120px"
          clearable
        >
          <el-option label="电话" value="phone" />
          <el-option label="微信" value="wechat" />
          <el-option label="邮件" value="email" />
          <el-option label="面谈" value="meeting" />
          <el-option label="其他" value="other" />
        </el-select>
        
        <el-select
          v-model="searchForm.chuli_zhuangtai"
          placeholder="处理状态"
          style="width: 120px"
          clearable
        >
          <el-option label="待处理" value="pending" />
          <el-option label="处理中" value="processing" />
          <el-option label="已完成" value="completed" />
          <el-option label="已关闭" value="closed" />
        </el-select>
        
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      
      <div class="search-right">
        <el-button
          v-if="selectedRecords.length > 0"
          type="warning"
          @click="handleBatchUpdateStatus"
        >
          <el-icon><Edit /></el-icon>
          批量更新状态
        </el-button>
        <el-button
          v-if="selectedRecords.length > 0"
          type="danger"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ statistics.total_records || 0 }}</div>
          <div class="stat-label">总记录数</div>
        </div>
        <div class="stat-icon total">
          <el-icon><Document /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ statistics.pending_records || 0 }}</div>
          <div class="stat-label">待处理</div>
        </div>
        <div class="stat-icon pending">
          <el-icon><Clock /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ statistics.completed_records || 0 }}</div>
          <div class="stat-label">已完成</div>
        </div>
        <div class="stat-icon completed">
          <el-icon><Check /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ statistics.today_records || 0 }}</div>
          <div class="stat-label">今日新增</div>
        </div>
        <div class="stat-icon today">
          <el-icon><Plus /></el-icon>
        </div>
      </el-card>
    </div>

    <!-- 服务记录表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="serviceRecords"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="kehu_mingcheng" label="客户名称" min-width="150">
          <template #default="{ row }">
            <router-link 
              :to="`/customers/${row.kehu_id}`"
              class="customer-link"
            >
              {{ row.kehu_mingcheng }}
            </router-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="goutong_fangshi" label="沟通方式" width="100">
          <template #default="{ row }">
            <el-tag :type="getCommunicationType(row.goutong_fangshi)" size="small">
              {{ getCommunicationText(row.goutong_fangshi) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="goutong_neirong" label="沟通内容" min-width="200">
          <template #default="{ row }">
            <div class="content-cell">
              {{ row.goutong_neirong }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="wenti_leixing" label="问题类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.wenti_leixing" type="info" size="small">
              {{ getProblemTypeText(row.wenti_leixing) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="chuli_zhuangtai" label="处理状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getProcessStatusType(row.chuli_zhuangtai)" size="small">
              {{ getProcessStatusText(row.chuli_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="goutong_shijian" label="沟通时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.goutong_shijian) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
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

    <!-- 服务记录详情/编辑对话框 -->
    <ServiceRecordDialog
      v-model:visible="dialogVisible"
      :customer-id="currentRecord?.kehu_id || ''"
      :customer-name="currentRecord?.kehu_mingcheng || ''"
      :record="currentRecord"
      :mode="dialogMode"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Edit,
  Delete,
  Document,
  Clock,
  Check,
  Plus
} from '@element-plus/icons-vue'
import { serviceRecordApi, type ServiceRecord } from '@/api/modules/customer'
import ServiceRecordDialog from './components/ServiceRecordDialog.vue'
import { formatDateTime } from '@/utils/date'

// 响应式数据
const loading = ref(false)
const serviceRecords = ref<ServiceRecord[]>([])
const selectedRecords = ref<ServiceRecord[]>([])
const dialogVisible = ref(false)
const currentRecord = ref<ServiceRecord | null>(null)
const dialogMode = ref<'view' | 'edit'>('view')

const searchForm = ref({
  search: '',
  goutong_fangshi: '',
  chuli_zhuangtai: ''
})

const pagination = ref({
  page: 1,
  size: 20,
  total: 0
})

const statistics = ref({
  total_records: 0,
  pending_records: 0,
  completed_records: 0,
  today_records: 0
})

// 计算属性
const hasSelection = computed(() => selectedRecords.value.length > 0)

// 方法
const loadServiceRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size,
      ...searchForm.value
    }

    // 过滤空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const response = await serviceRecordApi.getList(params)
    serviceRecords.value = response.items
    pagination.value.total = response.total
  } catch (error) {
    console.error('加载服务记录失败:', error)
    ElMessage.error('加载服务记录失败')
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const stats = await serviceRecordApi.getStatistics()
    statistics.value = stats
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  loadServiceRecords()
}

const handleReset = () => {
  searchForm.value = {
    search: '',
    goutong_fangshi: '',
    chuli_zhuangtai: ''
  }
  pagination.value.page = 1
  loadServiceRecords()
}

const handleSelectionChange = (selection: ServiceRecord[]) => {
  selectedRecords.value = selection
}

const handleView = (record: ServiceRecord) => {
  currentRecord.value = record
  dialogMode.value = 'view'
  dialogVisible.value = true
}

const handleEdit = (record: ServiceRecord) => {
  currentRecord.value = record
  dialogMode.value = 'edit'
  dialogVisible.value = true
}

const handleDelete = async (record: ServiceRecord) => {
  try {
    await ElMessageBox.confirm('确定要删除这条服务记录吗？', '确认删除', {
      type: 'warning'
    })

    await serviceRecordApi.delete(record.id)
    ElMessage.success('删除成功')
    loadServiceRecords()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除服务记录失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchUpdateStatus = async () => {
  if (selectedRecords.value.length === 0) {
    ElMessage.warning('请选择要更新的服务记录')
    return
  }

  try {
    const { value: status } = await ElMessageBox.prompt('请选择新状态', '批量更新状态', {
      inputType: 'select',
      inputOptions: [
        { label: '待处理', value: 'pending' },
        { label: '处理中', value: 'processing' },
        { label: '已完成', value: 'completed' },
        { label: '已关闭', value: 'closed' }
      ]
    })

    const recordIds = selectedRecords.value.map(record => record.id)
    await serviceRecordApi.batchUpdateStatus(recordIds, status)
    ElMessage.success('批量更新成功')
    selectedRecords.value = []
    loadServiceRecords()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量更新失败:', error)
      ElMessage.error('批量更新失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedRecords.value.length === 0) {
    ElMessage.warning('请选择要删除的服务记录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 条服务记录吗？`,
      '确认批量删除',
      { type: 'warning' }
    )

    const recordIds = selectedRecords.value.map(record => record.id)
    await serviceRecordApi.batchDelete(recordIds)
    ElMessage.success('批量删除成功')
    selectedRecords.value = []
    loadServiceRecords()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  pagination.value.page = 1
  loadServiceRecords()
}

const handleCurrentChange = (page: number) => {
  pagination.value.page = page
  loadServiceRecords()
}

const handleDialogSuccess = () => {
  dialogVisible.value = false
  loadServiceRecords()
  loadStatistics()
}

// 辅助方法
const getCommunicationType = (type: string) => {
  const typeMap = {
    phone: 'success',
    wechat: 'primary',
    email: 'info',
    meeting: 'warning',
    other: ''
  }
  return typeMap[type] || ''
}

const getCommunicationText = (type: string) => {
  const textMap = {
    phone: '电话',
    wechat: '微信',
    email: '邮件',
    meeting: '面谈',
    other: '其他'
  }
  return textMap[type] || type
}

const getProblemTypeText = (type: string) => {
  const textMap = {
    shuiwu: '税务',
    gongshang: '工商',
    caiwu: '财务',
    fawu: '法务',
    zixun: '咨询',
    other: '其他'
  }
  return textMap[type] || type
}

const getProcessStatusType = (status: string) => {
  const statusMap = {
    pending: 'warning',
    processing: 'primary',
    completed: 'success',
    closed: 'info'
  }
  return statusMap[status] || ''
}

const getProcessStatusText = (status: string) => {
  const textMap = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    closed: '已关闭'
  }
  return textMap[status] || status
}

// 生命周期
onMounted(() => {
  loadServiceRecords()
  loadStatistics()
})
</script>

<style scoped>
.service-record-list {
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

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-right {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.pending {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.today {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.table-card {
  border-radius: 8px;
}

.customer-link {
  color: #409eff;
  text-decoration: none;
}

.customer-link:hover {
  text-decoration: underline;
}

.content-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
