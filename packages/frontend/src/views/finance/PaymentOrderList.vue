<template>
  <div class="payment-order-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>支付订单管理</h1>
      <p>管理所有支付订单，查看支付状态和订单详情</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="订单编号、订单名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="支付状态">
          <el-select v-model="searchForm.zhifu_zhuangtai" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待支付" value="pending" />
            <el-option label="支付中" value="paying" />
            <el-option label="已支付" value="paid" />
            <el-option label="支付失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已退款" value="refunded" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="searchForm.zhifu_leixing" placeholder="全部方式" clearable style="width: 120px">
            <el-option label="微信支付" value="weixin" />
            <el-option label="支付宝" value="zhifubao" />
            <el-option label="银行转账" value="yinhangzhuanzhang" />
            <el-option label="现金" value="xianjin" />
            <el-option label="其他" value="qita" />
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

    <!-- 订单列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>支付订单列表</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建订单
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="dingdan_bianhao" label="订单编号" width="180" />
        <el-table-column prop="hetong_bianhao" label="合同编号" width="150">
          <template #default="{ row }">
            {{ row.hetong_bianhao || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="hetong_mingcheng" label="合同名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.hetong_mingcheng || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="dingdan_jine" label="订单金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.dingdan_jine) }}
          </template>
        </el-table-column>
        <el-table-column prop="shifu_jine" label="实付金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.shifu_jine) }}
          </template>
        </el-table-column>
        <el-table-column prop="zhifu_leixing" label="支付方式" width="100">
          <template #default="{ row }">
            {{ getPaymentTypeText(row.zhifu_leixing) }}
          </template>
        </el-table-column>
        <el-table-column prop="zhifu_zhuangtai" label="支付状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.zhifu_zhuangtai)">
              {{ getStatusText(row.zhifu_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="zhifu_shijian" label="支付时间" width="180">
          <template #default="{ row }">
            {{ row.zhifu_shijian ? formatDateTime(row.zhifu_shijian) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleEdit(row)"
              v-if="row.zhifu_zhuangtai === 'pending'"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleCancel(row)"
              v-if="row.zhifu_zhuangtai === 'pending'"
            >
              取消
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

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="支付订单详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单编号">
          {{ currentOrder.dingdan_bianhao }}
        </el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(currentOrder.zhifu_zhuangtai)">
            {{ getStatusText(currentOrder.zhifu_zhuangtai) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="合同编号">
          {{ currentOrder.hetong_bianhao || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="合同名称">
          {{ currentOrder.hetong_mingcheng || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="订单名称" :span="2">
          {{ currentOrder.dingdan_mingcheng }}
        </el-descriptions-item>
        <el-descriptions-item label="订单描述" :span="2">
          {{ currentOrder.dingdan_miaoshu || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="订单金额">
          {{ formatCurrency(currentOrder.dingdan_jine) }}
        </el-descriptions-item>
        <el-descriptions-item label="应付金额">
          {{ formatCurrency(currentOrder.yingfu_jine) }}
        </el-descriptions-item>
        <el-descriptions-item label="实付金额">
          {{ formatCurrency(currentOrder.shifu_jine) }}
        </el-descriptions-item>
        <el-descriptions-item label="退款金额">
          {{ formatCurrency(currentOrder.tuikuan_jine || 0) }}
        </el-descriptions-item>
        <el-descriptions-item label="支付方式">
          {{ getPaymentTypeText(currentOrder.zhifu_leixing) }}
        </el-descriptions-item>
        <el-descriptions-item label="支付平台">
          {{ currentOrder.zhifu_pingtai || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="第三方订单号" :span="2">
          {{ currentOrder.disanfang_dingdan_hao || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="第三方流水号" :span="2">
          {{ currentOrder.disanfang_liushui_hao || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(currentOrder.chuangjian_shijian) }}
        </el-descriptions-item>
        <el-descriptions-item label="支付时间">
          {{ currentOrder.zhifu_shijian ? formatDateTime(currentOrder.zhifu_shijian) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="过期时间" :span="2">
          {{ currentOrder.guoqi_shijian ? formatDateTime(currentOrder.guoqi_shijian) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentOrder.beizhu || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
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
const detailDialogVisible = ref(false)
const currentOrder = ref(null)

// 搜索表单
const searchForm = reactive({
  search: '',
  zhifu_zhuangtai: '',
  zhifu_leixing: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取订单列表
const fetchOrderList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: searchForm.search || undefined,
      zhifu_zhuangtai: searchForm.zhifu_zhuangtai || undefined,
      zhifu_leixing: searchForm.zhifu_leixing || undefined
    }

    const response = await request.get('/payment-orders/', { params })
    tableData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchOrderList()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    search: '',
    zhifu_zhuangtai: '',
    zhifu_leixing: ''
  })
  pagination.page = 1
  fetchOrderList()
}

// 新建订单
const handleCreate = () => {
  // TODO: 跳转到新建订单页面
  ElMessage.info('新建订单功能开发中')
}

// 查看订单
const handleView = (row: any) => {
  currentOrder.value = row
  detailDialogVisible.value = true
}

// 编辑订单
const handleEdit = (row: any) => {
  // TODO: 跳转到编辑订单页面
  ElMessage.info(`编辑订单: ${row.dingdan_bianhao}`)
}

// 取消订单
const handleCancel = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消订单 ${row.dingdan_bianhao} 吗？`,
      '取消订单',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用取消订单API
    ElMessage.success('订单已取消')
    fetchOrderList()
  } catch (error) {
    // 用户取消操作
  }
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  fetchOrderList()
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchOrderList()
}

// 获取支付方式文本
const getPaymentTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    weixin: '微信支付',
    zhifubao: '支付宝',
    yinhangzhuanzhang: '银行转账',
    xianjin: '现金',
    qita: '其他'
  }
  return typeMap[type] || type
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'warning',
    paying: 'info',
    paid: 'success',
    failed: 'danger',
    cancelled: 'info',
    refunded: 'warning'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待支付',
    paying: '支付中',
    paid: '已支付',
    failed: '支付失败',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return statusMap[status] || status
}

// 页面加载时获取数据
onMounted(() => {
  fetchOrderList()
})
</script>

<style scoped>
.payment-order-list {
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
