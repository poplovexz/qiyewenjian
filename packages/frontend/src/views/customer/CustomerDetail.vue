<template>
  <div class="customer-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="title-section">
          <h2>{{ customer?.gongsi_mingcheng || '客户详情' }}</h2>
          <div class="subtitle">
            <el-tag :type="getStatusType(customer?.kehu_zhuangtai)">
              {{ getStatusText(customer?.kehu_zhuangtai) }}
            </el-tag>
            <span class="credit-code">{{ customer?.tongyi_shehui_xinyong_daima }}</span>
          </div>
        </div>
      </div>
      
      <div class="header-actions">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑客户
        </el-button>
        <el-button @click="handleStatusChange">
          <el-icon><Switch /></el-icon>
          状态管理
        </el-button>
        <el-dropdown @command="handleDropdownCommand">
          <el-button>
            更多操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="records">服务记录</el-dropdown-item>
              <el-dropdown-item command="contracts">合同管理</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除客户</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 客户信息卡片 -->
    <div class="content-grid">
      <!-- 基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-icon><OfficeBuilding /></el-icon>
          </div>
        </template>
        
        <div class="info-grid">
          <div class="info-item">
            <label>公司名称</label>
            <span>{{ customer?.gongsi_mingcheng || '-' }}</span>
          </div>
          <div class="info-item">
            <label>统一社会信用代码</label>
            <span>{{ customer?.tongyi_shehui_xinyong_daima || '-' }}</span>
          </div>
          <div class="info-item">
            <label>成立日期</label>
            <span>{{ customer?.chengli_riqi ? formatDate(customer.chengli_riqi) : '-' }}</span>
          </div>
          <div class="info-item">
            <label>客户状态</label>
            <el-tag :type="getStatusType(customer?.kehu_zhuangtai)">
              {{ getStatusText(customer?.kehu_zhuangtai) }}
            </el-tag>
          </div>
          <div class="info-item full-width">
            <label>注册地址</label>
            <span>{{ customer?.zhuce_dizhi || '-' }}</span>
          </div>
        </div>
      </el-card>

      <!-- 法人信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>法人信息</span>
            <el-icon><User /></el-icon>
          </div>
        </template>
        
        <div class="info-grid">
          <div class="info-item">
            <label>法人姓名</label>
            <span>{{ customer?.faren_xingming || '-' }}</span>
          </div>
          <div class="info-item">
            <label>身份证号码</label>
            <span>{{ customer?.faren_shenfenzheng || '-' }}</span>
          </div>
          <div class="info-item full-width">
            <label>联系方式</label>
            <span>{{ customer?.faren_lianxi || '-' }}</span>
          </div>
        </div>
      </el-card>

      <!-- 联系信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>联系信息</span>
            <el-icon><Phone /></el-icon>
          </div>
        </template>
        
        <div class="info-grid">
          <div class="info-item">
            <label>联系电话</label>
            <span>{{ customer?.lianxi_dianhua || '-' }}</span>
          </div>
          <div class="info-item">
            <label>联系邮箱</label>
            <span>{{ customer?.lianxi_youxiang || '-' }}</span>
          </div>
          <div class="info-item full-width">
            <label>联系地址</label>
            <span>{{ customer?.lianxi_dizhi || '-' }}</span>
          </div>
        </div>
      </el-card>

      <!-- 服务信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>服务信息</span>
            <el-icon><Calendar /></el-icon>
          </div>
        </template>
        
        <div class="info-grid">
          <div class="info-item">
            <label>服务开始日期</label>
            <span>{{ customer?.fuwu_kaishi_riqi ? formatDate(customer.fuwu_kaishi_riqi) : '-' }}</span>
          </div>
          <div class="info-item">
            <label>服务结束日期</label>
            <span>{{ customer?.fuwu_jieshu_riqi ? formatDate(customer.fuwu_jieshu_riqi) : '-' }}</span>
          </div>
          <div class="info-item">
            <label>营业执照有效期</label>
            <span>{{ customer?.yingye_zhizhao_youxiao_qi ? formatDate(customer.yingye_zhizhao_youxiao_qi) : '-' }}</span>
          </div>
          <div class="info-item">
            <label>创建时间</label>
            <span>{{ customer?.created_at ? formatDateTime(customer.created_at) : '-' }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 最近服务记录 -->
    <el-card class="records-card">
      <template #header>
        <div class="card-header">
          <span>最近服务记录</span>
          <el-button type="primary" size="small" @click="viewAllRecords">
            查看全部
          </el-button>
        </div>
      </template>
      
      <div v-if="serviceRecords.length === 0" class="empty-records">
        <el-empty description="暂无服务记录" />
      </div>
      
      <div v-else class="records-list">
        <div
          v-for="record in serviceRecords.slice(0, 5)"
          :key="record.id"
          class="record-item"
        >
          <div class="record-header">
            <el-tag :type="getCommunicationType(record.goutong_fangshi)" size="small">
              {{ getCommunicationText(record.goutong_fangshi) }}
            </el-tag>
            <span class="record-time">{{ formatDateTime(record.created_at) }}</span>
          </div>
          <div class="record-content">{{ record.goutong_neirong }}</div>
          <div v-if="record.wenti_leixing" class="record-problem">
            <el-tag type="info" size="small">{{ getProblemTypeText(record.wenti_leixing) }}</el-tag>
            <el-tag :type="getProcessStatusType(record.chuli_zhuangtai)" size="small">
              {{ getProcessStatusText(record.chuli_zhuangtai) }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 客户表单对话框 -->
    <CustomerForm
      v-model:visible="formVisible"
      :customer="customer"
      mode="edit"
      @success="handleFormSuccess"
    />

    <!-- 状态管理对话框 -->
    <CustomerStatusDialog
      v-model:visible="statusDialogVisible"
      :customer="customer"
      @success="handleStatusSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Edit,
  Switch,
  ArrowDown,
  OfficeBuilding,
  User,
  Phone,
  Calendar
} from '@element-plus/icons-vue'
import { useCustomerStore } from '@/stores/modules/customer'
import CustomerForm from './components/CustomerForm.vue'
import CustomerStatusDialog from './components/CustomerStatusDialog.vue'
import type { Customer, ServiceRecord } from '@/api/modules/customer'

const route = useRoute()
const router = useRouter()
const customerStore = useCustomerStore()

// 响应式数据
const customer = ref<Customer | null>(null)
const serviceRecords = ref<ServiceRecord[]>([])
const formVisible = ref(false)
const statusDialogVisible = ref(false)
const loading = ref(false)

// 方法
const fetchCustomerDetail = async () => {
  const customerId = route.params.id as string
  if (!customerId) return
  
  try {
    loading.value = true
    customer.value = await customerStore.fetchCustomerDetail(customerId)
    
    // 获取最近的服务记录
    const recordsResponse = await customerStore.fetchCustomerServiceRecords(customerId, { page: 1, size: 10 })
    serviceRecords.value = recordsResponse.items
  } catch (error) {
    console.error('获取客户详情失败:', error)
    ElMessage.error('获取客户详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const handleEdit = () => {
  formVisible.value = true
}

const handleStatusChange = () => {
  statusDialogVisible.value = true
}

const handleDropdownCommand = (command: string) => {
  switch (command) {
    case 'records':
      viewAllRecords()
      break
    case 'contracts':
      // TODO: 跳转到合同管理
      ElMessage.info('合同管理功能开发中')
      break
    case 'delete':
      handleDelete()
      break
  }
}

const handleDelete = async () => {
  if (!customer.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除客户"${customer.value.gongsi_mingcheng}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await customerStore.deleteCustomer(customer.value.id)
    ElMessage.success('客户删除成功')
    router.push('/customers')
  } catch (error) {
    // 用户取消删除
  }
}

const viewAllRecords = () => {
  if (customer.value) {
    router.push(`/customers/${customer.value.id}/records`)
  }
}

const handleFormSuccess = async () => {
  formVisible.value = false
  await fetchCustomerDetail()
}

const handleStatusSuccess = async () => {
  statusDialogVisible.value = false
  await fetchCustomerDetail()
}

// 工具方法
const getStatusType = (status?: string) => {
  const statusMap = {
    active: 'success',
    renewing: 'warning',
    terminated: 'danger'
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

const getStatusText = (status?: string) => {
  const statusMap = {
    active: '活跃',
    renewing: '续约中',
    terminated: '已终止'
  }
  return statusMap[status as keyof typeof statusMap] || status || '-'
}

const getCommunicationType = (type: string) => {
  const typeMap = {
    phone: 'warning',
    email: 'success',
    online: 'primary',
    meeting: 'info'
  }
  return typeMap[type as keyof typeof typeMap] || 'info'
}

const getCommunicationText = (type: string) => {
  const typeMap = {
    phone: '电话',
    email: '邮件',
    online: '在线',
    meeting: '会议'
  }
  return typeMap[type as keyof typeof typeMap] || type
}

const getProblemTypeText = (type: string) => {
  const typeMap = {
    zhangwu: '账务类',
    shuiwu: '税务类',
    zixun: '咨询类',
    other: '其他'
  }
  return typeMap[type as keyof typeof typeMap] || type
}

const getProcessStatusType = (status: string) => {
  const statusMap = {
    pending: 'warning',
    processing: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

const getProcessStatusText = (status: string) => {
  const statusMap = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchCustomerDetail()
})
</script>

<style scoped>
.customer-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.title-section h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  display: flex;
  align-items: center;
  gap: 12px;
}

.credit-code {
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.info-card {
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.info-item span {
  color: #303133;
  font-size: 14px;
}

.records-card {
  border-radius: 8px;
  overflow: hidden;
}

.empty-records {
  padding: 40px 0;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.record-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-time {
  font-size: 12px;
  color: #909399;
}

.record-content {
  color: #303133;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.record-problem {
  display: flex;
  gap: 8px;
}

:deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
