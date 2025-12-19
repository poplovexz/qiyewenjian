<template>
  <div class="finance-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>财务概览</h1>
      <p>查看支付订单、流水记录和财务统计信息</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32" color="#409EFF">
                <Money />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatCurrency(statistics.total_amount) }}</div>
              <div class="stat-label">总订单金额</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32" color="#67C23A">
                <SuccessFilled />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatCurrency(statistics.paid_amount) }}</div>
              <div class="stat-label">已支付金额</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32" color="#E6A23C">
                <Clock />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatCurrency(statistics.pending_amount) }}</div>
              <div class="stat-label">待支付金额</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32" color="#F56C6C">
                <Document />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_count }}</div>
              <div class="stat-label">总订单数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card class="quick-actions" header="快速操作">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button
            type="primary"
            size="large"
            @click="$router.push('/finance/payment-orders')"
            block
          >
            <el-icon><Money /></el-icon>
            支付订单管理
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button
            type="success"
            size="large"
            @click="$router.push('/finance/payment-records')"
            block
          >
            <el-icon><Document /></el-icon>
            支付流水管理
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button
            type="info"
            size="large"
            @click="$router.push('/finance/contract-parties')"
            block
          >
            <el-icon><User /></el-icon>
            乙方主体管理
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button
            type="warning"
            size="large"
            @click="$router.push('/finance/payment-methods')"
            block
          >
            <el-icon><CreditCard /></el-icon>
            支付方式管理
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近订单 -->
    <el-card class="recent-orders" header="最近支付订单">
      <el-table :data="recentOrders" v-loading="loading">
        <el-table-column prop="dingdan_bianhao" label="订单编号" width="150" />
        <el-table-column prop="dingdan_mingcheng" label="订单名称" />
        <el-table-column prop="dingdan_jine" label="订单金额" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.dingdan_jine) }}
          </template>
        </el-table-column>
        <el-table-column prop="zhifu_zhuangtai" label="支付状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.zhifu_zhuangtai)">
              {{ getStatusText(row.zhifu_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chuangjian_shijian" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.chuangjian_shijian) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewOrder(row.id)"> 查看 </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
        <el-button type="primary" @click="$router.push('/finance/payment-orders')">
          查看全部订单
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Money, SuccessFilled, Clock, Document, User, CreditCard } from '@element-plus/icons-vue'
import { formatCurrency, formatDateTime } from '@/utils/format'
import request from '@/utils/request'

// 响应式数据
const loading = ref(false)
const statistics = ref({
  total_count: 0,
  pending_count: 0,
  paid_count: 0,
  failed_count: 0,
  total_amount: 0,
  paid_amount: 0,
  pending_amount: 0,
})
const recentOrders = ref([])

// 获取统计信息
const fetchStatistics = async () => {
  try {
    const response = await request.get('/payment-orders/statistics')
    statistics.value = response
  } catch (error) {
    ElMessage.error('获取统计信息失败')
  }
}

// 获取最近订单
const fetchRecentOrders = async () => {
  loading.value = true
  try {
    const response = await request.get('/payment-orders/', {
      params: { page: 1, size: 10 },
    })
    recentOrders.value = response.items || []
  } catch (error) {
    ElMessage.error('获取最近订单失败')
  } finally {
    loading.value = false
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'warning',
    paying: 'info',
    paid: 'success',
    failed: 'danger',
    cancelled: 'info',
    refunded: 'warning',
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
    refunded: '已退款',
  }
  return statusMap[status] || status
}

// 查看订单详情
const viewOrder = (id: string) => {
  // TODO: 跳转到订单详情页面
}

// 页面加载时获取数据
onMounted(() => {
  fetchStatistics()
  fetchRecentOrders()
})
</script>

<style scoped>
.finance-dashboard {
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

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  margin-bottom: 24px;
}

.recent-orders {
  margin-bottom: 24px;
}

.table-footer {
  margin-top: 16px;
  text-align: center;
}
</style>
