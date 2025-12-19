<template>
  <div class="service-order-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>服务工单管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建工单
      </el-button>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="工单编号">
          <el-input
            v-model="searchForm.gongdan_bianhao"
            placeholder="请输入工单编号"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="工单标题">
          <el-input
            v-model="searchForm.gongdan_biaoti"
            placeholder="请输入工单标题"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="服务类型">
          <el-select
            v-model="searchForm.fuwu_leixing"
            placeholder="请选择服务类型"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="(label, value) in serviceOrderStore.serviceTypeMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="工单状态">
          <el-select
            v-model="searchForm.gongdan_zhuangtai"
            placeholder="请选择工单状态"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="(label, value) in serviceOrderStore.statusMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-select
            v-model="searchForm.youxian_ji"
            placeholder="请选择优先级"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="(label, value) in serviceOrderStore.priorityMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="searchForm.is_overdue">仅显示逾期</el-checkbox>
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

    <!-- 统计卡片 -->
    <div class="statistics-cards" v-if="statistics">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.total_count }}</div>
              <div class="stat-label">总工单数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.in_progress_count }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.overdue_count }}</div>
              <div class="stat-label">逾期工单</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.completion_rate.toFixed(1) }}%</div>
              <div class="stat-label">完成率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 工单列表 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="serviceOrderStore.loading"
        :data="serviceOrderStore.serviceOrders"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="gongdan_bianhao" label="工单编号" width="150" />

        <el-table-column prop="gongdan_biaoti" label="工单标题" min-width="200" />

        <el-table-column prop="fuwu_leixing" label="服务类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ serviceOrderStore.serviceTypeMap[row.fuwu_leixing] }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="gongdan_zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.gongdan_zhuangtai)">
              {{ serviceOrderStore.statusMap[row.gongdan_zhuangtai] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="youxian_ji" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.youxian_ji)" size="small">
              {{ serviceOrderStore.priorityMap[row.youxian_ji] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="progress_percentage" label="进度" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress_percentage"
              :color="getProgressColor(row.progress_percentage)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>

        <el-table-column prop="jihua_jieshu_shijian" label="计划完成时间" width="180">
          <template #default="{ row }">
            <div :class="{ 'overdue-text': row.is_overdue }">
              {{ formatDateTime(row.jihua_jieshu_shijian) }}
              <el-icon v-if="row.is_overdue" color="#f56c6c"><Warning /></el-icon>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row.id)"> 查看 </el-button>

            <el-button
              v-if="row.gongdan_zhuangtai === 'created'"
              type="success"
              size="small"
              @click="showAssignDialog(row)"
            >
              分配
            </el-button>

            <el-button
              v-if="row.gongdan_zhuangtai === 'assigned'"
              type="warning"
              size="small"
              @click="startOrder(row.id)"
            >
              开始
            </el-button>

            <el-dropdown
              v-if="row.gongdan_zhuangtai !== 'completed' && row.gongdan_zhuangtai !== 'cancelled'"
            >
              <el-button size="small">
                更多<el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="editOrder(row)">编辑</el-dropdown-item>
                  <el-dropdown-item @click="showCancelDialog(row)" divided>取消</el-dropdown-item>
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
          :total="serviceOrderStore.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建工单对话框 -->
    <ServiceOrderForm v-model:visible="showCreateDialog" @success="handleCreateSuccess" />

    <!-- 分配工单对话框 -->
    <AssignOrderDialog
      v-model:visible="showAssignOrderDialog"
      :order="selectedOrder"
      @success="handleAssignSuccess"
    />

    <!-- 取消工单对话框 -->
    <CancelOrderDialog
      v-model:visible="showCancelOrderDialog"
      :order="selectedOrder"
      @success="handleCancelSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Warning, ArrowDown } from '@element-plus/icons-vue'
import { useServiceOrderStore, type ServiceOrder } from '@/stores/modules/serviceOrderManagement'
import ServiceOrderForm from './components/ServiceOrderForm.vue'
import AssignOrderDialog from './components/AssignOrderDialog.vue'
import CancelOrderDialog from './components/CancelOrderDialog.vue'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const serviceOrderStore = useServiceOrderStore()

// 响应式数据
const showCreateDialog = ref(false)
const showAssignOrderDialog = ref(false)
const showCancelOrderDialog = ref(false)
const selectedOrder = ref<ServiceOrder | null>(null)
const statistics = ref(null)

const currentPage = ref(1)
const pageSize = ref(20)

const searchForm = reactive({
  gongdan_bianhao: '',
  gongdan_biaoti: '',
  fuwu_leixing: '',
  gongdan_zhuangtai: '',
  youxian_ji: '',
  is_overdue: false,
})

// 计算属性
const searchParams = computed(() => ({
  page: currentPage.value,
  size: pageSize.value,
  ...searchForm,
}))

// 方法
const loadData = async () => {
  try {
    await serviceOrderStore.fetchServiceOrders(searchParams.value)
    statistics.value = await serviceOrderStore.fetchStatistics()
  } catch (error) {}
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    gongdan_bianhao: '',
    gongdan_biaoti: '',
    fuwu_leixing: '',
    gongdan_zhuangtai: '',
    youxian_ji: '',
    is_overdue: false,
  })
  handleSearch()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadData()
}

const viewDetail = (id: string) => {
  router.push(`/service-orders/${id}`)
}

const showAssignDialog = (order: ServiceOrder) => {
  selectedOrder.value = order
  showAssignOrderDialog.value = true
}

const showCancelDialog = (order: ServiceOrder) => {
  selectedOrder.value = order
  showCancelOrderDialog.value = true
}

const startOrder = async (id: string) => {
  try {
    await ElMessageBox.confirm('确认开始执行此工单？', '确认操作', {
      type: 'warning',
    })

    await serviceOrderStore.startServiceOrder(id)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
    }
  }
}

const editOrder = (order: ServiceOrder) => {
  router.push(`/service-orders/${order.id}/edit`)
}

const handleCreateSuccess = () => {
  showCreateDialog.value = false
  loadData()
}

const handleAssignSuccess = () => {
  showAssignOrderDialog.value = false
  loadData()
}

const handleCancelSuccess = () => {
  showCancelOrderDialog.value = false
  loadData()
}

// 辅助方法
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    created: 'info',
    assigned: 'warning',
    in_progress: 'primary',
    pending_review: 'warning',
    completed: 'success',
    cancelled: 'danger',
  }
  return typeMap[status] || 'info'
}

const getPriorityType = (priority: string) => {
  const typeMap: Record<string, string> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    urgent: 'danger',
  }
  return typeMap[priority] || 'info'
}

const getProgressColor = (percentage: number) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.service-order-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.search-card {
  margin-bottom: 20px;
}

.statistics-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.overdue-text {
  color: #f56c6c;
  font-weight: bold;
}
</style>
