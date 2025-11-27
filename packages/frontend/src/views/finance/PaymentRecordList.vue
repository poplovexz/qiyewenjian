<template>
  <div class="payment-record-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>支付流水管理</h1>
      <p>管理所有支付流水记录，进行财务确认和对账</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="流水编号、第三方流水号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="流水类型">
          <el-select v-model="searchForm.liushui_leixing" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="收入" value="income" />
            <el-option label="支出" value="expense" />
            <el-option label="退款" value="refund" />
            <el-option label="手续费" value="fee" />
          </el-select>
        </el-form-item>
        <el-form-item label="流水状态">
          <el-select v-model="searchForm.liushui_zhuangtai" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="处理中" value="processing" />
          </el-select>
        </el-form-item>
        <el-form-item label="对账状态">
          <el-select v-model="searchForm.duizhang_zhuangtai" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待对账" value="pending" />
            <el-option label="已对账" value="matched" />
            <el-option label="未对账" value="unmatched" />
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

    <!-- 流水列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>支付流水列表</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            登记流水
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="liushui_bianhao" label="流水编号" width="150" />
        <el-table-column prop="liushui_leixing" label="流水类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.liushui_leixing)">
              {{ getTypeText(row.liushui_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="jiaoyijine" label="交易金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.jiaoyijine) }}
          </template>
        </el-table-column>
        <el-table-column prop="shouxufei" label="手续费" width="100" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.shouxufei) }}
          </template>
        </el-table-column>
        <el-table-column prop="shiji_shouru" label="实际收入" width="120" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.shiji_shouru) }}
          </template>
        </el-table-column>
        <el-table-column prop="zhifu_fangshi" label="支付方式" width="100">
          <template #default="{ row }">
            {{ getPaymentTypeText(row.zhifu_fangshi) }}
          </template>
        </el-table-column>
        <el-table-column prop="liushui_zhuangtai" label="流水状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.liushui_zhuangtai)">
              {{ getStatusText(row.liushui_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duizhang_zhuangtai" label="对账状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getReconcileType(row.duizhang_zhuangtai)">
              {{ getReconcileText(row.duizhang_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="jiaoyishijian" label="交易时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.jiaoyishijian) }}
          </template>
        </el-table-column>
        <el-table-column prop="caiwu_queren_shijian" label="财务确认时间" width="180">
          <template #default="{ row }">
            {{ row.caiwu_queren_shijian ? formatDateTime(row.caiwu_queren_shijian) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleConfirm(row)"
              v-if="row.duizhang_zhuangtai === 'pending'"
            >
              财务确认
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleEdit(row)"
              v-if="row.duizhang_zhuangtai === 'pending'"
            >
              编辑
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { formatCurrency, formatDateTime } from '@/utils/format'
import request from '@/utils/request'

// 响应式数据
const loading = ref(false)
const tableData = ref([])

// 搜索表单
const searchForm = reactive({
  search: '',
  liushui_leixing: '',
  liushui_zhuangtai: '',
  duizhang_zhuangtai: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取流水列表
const fetchRecordList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: searchForm.search || undefined,
      liushui_leixing: searchForm.liushui_leixing || undefined,
      liushui_zhuangtai: searchForm.liushui_zhuangtai || undefined,
      duizhang_zhuangtai: searchForm.duizhang_zhuangtai || undefined
    }

    const response = await request.get('/payment-records/', { params })
    tableData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取流水列表失败:', error)
    ElMessage.error('获取流水列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchRecordList()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    search: '',
    liushui_leixing: '',
    liushui_zhuangtai: '',
    duizhang_zhuangtai: ''
  })
  pagination.page = 1
  fetchRecordList()
}

// 登记流水
const handleCreate = () => {
  // TODO: 跳转到登记流水页面
  ElMessage.info('登记流水功能开发中')
}

// 查看流水
const handleView = (row: any) => {
  // TODO: 跳转到流水详情页面
  ElMessage.info(`查看流水: ${row.liushui_bianhao}`)
}

// 财务确认
const handleConfirm = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要财务确认流水 ${row.liushui_bianhao} 吗？`,
      '财务确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await request.post(`/payment-records/${row.id}/confirm`)
    ElMessage.success('财务确认成功')
    fetchRecordList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('财务确认失败:', error)
      ElMessage.error(error.message || '财务确认失败')
    }
  }
}

// 编辑流水
const handleEdit = (row: any) => {
  // TODO: 跳转到编辑流水页面
  ElMessage.info(`编辑流水: ${row.liushui_bianhao}`)
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  fetchRecordList()
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchRecordList()
}

// 获取流水类型标签类型
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    income: 'success',
    expense: 'danger',
    refund: 'warning',
    fee: 'info'
  }
  return typeMap[type] || 'info'
}

// 获取流水类型文本
const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    income: '收入',
    expense: '支出',
    refund: '退款',
    fee: '手续费'
  }
  return typeMap[type] || type
}

// 获取支付方式文本
const getPaymentTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    weixin: '微信支付',
    zhifubao: '支付宝',
    yinhangzhuanzhang: '银行转账',
    baoxiao: '报销',
    offline: '线下支付',
    xianjin: '现金',
    qita: '其他'
  }
  return typeMap[type] || type
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    processing: 'warning'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    success: '成功',
    failed: '失败',
    processing: '处理中'
  }
  return statusMap[status] || status
}

// 获取对账状态类型
const getReconcileType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'warning',
    matched: 'success',
    unmatched: 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取对账状态文本
const getReconcileText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待对账',
    matched: '已对账',
    unmatched: '未对账'
  }
  return statusMap[status] || status
}

// 页面加载时获取数据
onMounted(() => {
  fetchRecordList()
})
</script>

<style scoped>
.payment-record-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}
</style>
