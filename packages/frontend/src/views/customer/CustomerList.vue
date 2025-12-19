<template>
  <div class="customer-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>客户管理</h2>
      <p>管理客户信息、服务状态和客户关系</p>
    </div>

    <!-- 搜索和操作栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索公司名称、信用代码、法人姓名..."
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.kehu_zhuangtai"
          placeholder="客户状态"
          style="width: 150px"
          clearable
          @change="handleSearch"
        >
          <el-option label="活跃" value="active" />
          <el-option label="续约中" value="renewing" />
          <el-option label="已终止" value="terminated" />
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
          v-if="selectedCustomers.length > 0"
          type="warning"
          @click="handleBatchUpdateStatus"
        >
          <el-icon><Edit /></el-icon>
          批量更新状态
        </el-button>
        <el-button
          v-if="selectedCustomers.length > 0"
          type="danger"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button
          v-if="permission.showCreateCustomerButton()"
          type="primary"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新增客户
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ activeCustomers.length }}</div>
          <div class="stat-label">活跃客户</div>
        </div>
        <div class="stat-icon active">
          <el-icon><User /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ renewingCustomers.length }}</div>
          <div class="stat-label">续约中</div>
        </div>
        <div class="stat-icon renewing">
          <el-icon><Clock /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ terminatedCustomers.length }}</div>
          <div class="stat-label">已终止</div>
        </div>
        <div class="stat-icon terminated">
          <el-icon><Close /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ total }}</div>
          <div class="stat-label">总客户数</div>
        </div>
        <div class="stat-icon total">
          <el-icon><DataAnalysis /></el-icon>
        </div>
      </el-card>
    </div>

    <!-- 客户表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="customers"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="gongsi_mingcheng" label="公司名称" min-width="200">
          <template #default="{ row }">
            <div class="company-info">
              <div class="company-name">{{ row.gongsi_mingcheng }}</div>
              <div class="company-code">{{ row.tongyi_shehui_xinyong_daima }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="faren_xingming" label="法人代表" width="120" />
        
        <el-table-column prop="lianxi_dianhua" label="联系电话" width="130" />
        
        <el-table-column prop="kehu_zhuangtai" label="客户状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.kehu_zhuangtai)">
              {{ getStatusText(row.kehu_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="fuwu_kaishi_riqi" label="服务开始" width="120">
          <template #default="{ row }">
            {{ row.fuwu_kaishi_riqi ? formatDate(row.fuwu_kaishi_riqi) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="permission.canViewCustomers()"
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="permission.showEditCustomerButton()"
              type="success"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-dropdown
              v-if="permission.showStatusManageButton() || permission.showServiceRecordButton() || permission.showDeleteCustomerButton()"
              @command="(command) => handleDropdownCommand(command, row)"
            >
              <el-button size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-if="permission.showStatusManageButton()"
                    command="status"
                  >
                    状态管理
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="permission.showServiceRecordButton()"
                    command="records"
                  >
                    服务记录
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="permission.showDeleteCustomerButton()"
                    command="delete"
                    divided
                  >
                    删除客户
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 客户表单对话框 -->
    <CustomerForm
      v-model:visible="formVisible"
      :customer="currentCustomer"
      :mode="formMode"
      @success="handleFormSuccess"
    />

    <!-- 状态管理对话框 -->
    <CustomerStatusDialog
      v-model:visible="statusDialogVisible"
      :customer="currentCustomer"
      @success="handleStatusSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  User,
  Clock,
  Close,
  DataAnalysis,
  ArrowDown,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import { useCustomerStore } from '@/stores/modules/customer'
import { usePermission } from '@/utils/permissions'
import CustomerForm from './components/CustomerForm.vue'
import CustomerStatusDialog from './components/CustomerStatusDialog.vue'
import { customerApi, type Customer } from '@/api/modules/customer'

const router = useRouter()
const customerStore = useCustomerStore()
const permission = usePermission()

// 响应式数据
const searchForm = ref({
  search: '',
  kehu_zhuangtai: ''
})

const formVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const currentCustomer = ref<Customer | null>(null)
const statusDialogVisible = ref(false)
const selectedCustomers = ref<Customer[]>([])

// 计算属性
const { 
  customers, 
  loading, 
  total, 
  currentPage, 
  pageSize,
  activeCustomers,
  renewingCustomers,
  terminatedCustomers
} = customerStore

// 方法
const handleSearch = async () => {
  await customerStore.fetchCustomers(searchForm.value)
}

const handleReset = async () => {
  searchForm.value = {
    search: '',
    kehu_zhuangtai: ''
  }
  await customerStore.fetchCustomers()
}

const handleCreate = () => {
  currentCustomer.value = null
  formMode.value = 'create'
  formVisible.value = true
}

const handleView = (customer: Customer) => {
  router.push(`/customers/${customer.id}`)
}

const handleEdit = (customer: Customer) => {
  currentCustomer.value = customer
  formMode.value = 'edit'
  formVisible.value = true
}

const handleDropdownCommand = (command: string, customer: Customer) => {
  currentCustomer.value = customer
  
  switch (command) {
    case 'status':
      statusDialogVisible.value = true
      break
    case 'records':
      router.push(`/customers/${customer.id}/records`)
      break
    case 'delete':
      handleDelete(customer)
      break
  }
}

const handleDelete = async (customer: Customer) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除客户"${customer.gongsi_mingcheng}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await customerStore.deleteCustomer(customer.id)
    await handleSearch()
  } catch (error) {
    // 用户取消删除
  }
}

const handleSelectionChange = (selection: Customer[]) => {
  selectedCustomers.value = selection
}

const handleSizeChange = async (size: number) => {
  customerStore.pageSize = size
  await handleSearch()
}

const handleCurrentChange = async (page: number) => {
  customerStore.currentPage = page
  await handleSearch()
}

const handleFormSuccess = async () => {
  formVisible.value = false
  await handleSearch()
}

const handleStatusSuccess = async () => {
  statusDialogVisible.value = false
  await handleSearch()
}

const handleBatchUpdateStatus = async () => {
  if (selectedCustomers.value.length === 0) {
    ElMessage.warning('请选择要更新的客户')
    return
  }

  try {
    const { value: status } = await ElMessageBox.prompt('请选择新状态', '批量更新客户状态', {
      inputType: 'select',
      inputOptions: [
        { label: '活跃', value: 'active' },
        { label: '续约中', value: 'renewing' },
        { label: '已终止', value: 'terminated' }
      ]
    })

    const customerIds = selectedCustomers.value.map(customer => customer.id)
    await customerApi.batchUpdateStatus(customerIds, status)
    ElMessage.success('批量更新成功')
    selectedCustomers.value = []
    await handleSearch()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量更新失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedCustomers.value.length === 0) {
    ElMessage.warning('请选择要删除的客户')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedCustomers.value.length} 个客户吗？`,
      '确认批量删除',
      { type: 'warning' }
    )

    const customerIds = selectedCustomers.value.map(customer => customer.id)
    await customerApi.batchDelete(customerIds)
    ElMessage.success('批量删除成功')
    selectedCustomers.value = []
    await handleSearch()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 工具方法
const getStatusType = (status: string) => {
  const statusMap = {
    active: 'success',
    renewing: 'warning',
    terminated: 'danger'
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '活跃',
    renewing: '续约中',
    terminated: '已终止'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(async () => {
  await customerStore.fetchCustomers()
})
</script>

<style scoped>
.customer-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
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
  font-weight: 600;
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
  font-size: 24px;
  color: #fff;
}

.stat-icon.active {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stat-icon.renewing {
  background: linear-gradient(135deg, #e6a23c, #f0a020);
}

.stat-icon.terminated {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.stat-icon.total {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.table-card {
  border-radius: 8px;
  overflow: hidden;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.company-info {
  line-height: 1.4;
}

.company-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.company-code {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  padding: 16px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #ebeef5;
}

:deep(.el-table) {
  border-radius: 0;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 500;
}

:deep(.el-table td) {
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-table tr:hover > td) {
  background-color: #f5f7fa;
}
</style>
