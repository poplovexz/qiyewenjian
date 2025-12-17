<template>
  <div class="refund-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>退款管理</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="退款状态">
          <el-select v-model="searchForm.tuikuan_zhuangtai" placeholder="请选择" clearable>
            <el-option label="处理中" value="chuli_zhong" />
            <el-option label="成功" value="chenggong" />
            <el-option label="失败" value="shibai" />
            <el-option label="已关闭" value="yiguanbi" />
          </el-select>
        </el-form-item>

        <el-form-item label="退款平台">
          <el-select v-model="searchForm.tuikuan_pingtai" placeholder="请选择" clearable>
            <el-option label="微信支付" value="weixin" />
            <el-option label="支付宝" value="zhifubao" />
          </el-select>
        </el-form-item>

        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="退款单号/原始订单号"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 退款列表 -->
      <el-table :data="refundList" border stripe v-loading="loading">
        <el-table-column prop="tuikuan_danhao" label="退款单号" width="180" />
        <el-table-column prop="yuanshi_dingdan_hao" label="原始订单号" width="180" />
        <el-table-column prop="tuikuan_jine" label="退款金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.tuikuan_jine }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="tuikuan_pingtai" label="退款平台" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.tuikuan_pingtai === 'weixin'" type="success">微信</el-tag>
            <el-tag v-else-if="row.tuikuan_pingtai === 'zhifubao'" type="primary">支付宝</el-tag>
            <el-tag v-else type="info">{{ row.tuikuan_pingtai }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tuikuan_zhuangtai" label="退款状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.tuikuan_zhuangtai === 'chenggong'" type="success">成功</el-tag>
            <el-tag v-else-if="row.tuikuan_zhuangtai === 'shibai'" type="danger">失败</el-tag>
            <el-tag v-else-if="row.tuikuan_zhuangtai === 'chuli_zhong'" type="warning">处理中</el-tag>
            <el-tag v-else type="info">{{ row.tuikuan_zhuangtai }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tuikuan_yuanyin" label="退款原因" show-overflow-tooltip />
        <el-table-column prop="shenqing_shijian" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.shenqing_shijian) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="pagination"
      />
    </el-card>

    <!-- 退款详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="退款详情"
      width="600px"
    >
      <el-descriptions :column="1" border v-if="currentRefund">
        <el-descriptions-item label="退款单号">{{ currentRefund.tuikuan_danhao }}</el-descriptions-item>
        <el-descriptions-item label="原始订单号">{{ currentRefund.yuanshi_dingdan_hao }}</el-descriptions-item>
        <el-descriptions-item label="第三方退款号">{{ currentRefund.disanfang_tuikuan_hao || '-' }}</el-descriptions-item>
        <el-descriptions-item label="原始金额">¥{{ currentRefund.yuanshi_jine }}</el-descriptions-item>
        <el-descriptions-item label="退款金额">¥{{ currentRefund.tuikuan_jine }}</el-descriptions-item>
        <el-descriptions-item label="退款平台">
          <el-tag v-if="currentRefund.tuikuan_pingtai === 'weixin'" type="success">微信</el-tag>
          <el-tag v-else-if="currentRefund.tuikuan_pingtai === 'zhifubao'" type="primary">支付宝</el-tag>
          <el-tag v-else type="info">{{ currentRefund.tuikuan_pingtai }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="退款状态">
          <el-tag v-if="currentRefund.tuikuan_zhuangtai === 'chenggong'" type="success">成功</el-tag>
          <el-tag v-else-if="currentRefund.tuikuan_zhuangtai === 'shibai'" type="danger">失败</el-tag>
          <el-tag v-else-if="currentRefund.tuikuan_zhuangtai === 'chuli_zhong'" type="warning">处理中</el-tag>
          <el-tag v-else type="info">{{ currentRefund.tuikuan_zhuangtai }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="退款原因">{{ currentRefund.tuikuan_yuanyin || '-' }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ formatDateTime(currentRefund.shenqing_shijian) }}</el-descriptions-item>
        <el-descriptions-item label="成功时间">{{ formatDateTime(currentRefund.chenggong_shijian) }}</el-descriptions-item>
        <el-descriptions-item label="处理结果">{{ currentRefund.chuli_jieguo || '-' }}</el-descriptions-item>
        <el-descriptions-item label="错误信息" v-if="currentRefund.cuowu_xinxi">
          <el-text type="danger">{{ currentRefund.cuowu_xinxi }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="错误代码" v-if="currentRefund.cuowu_daima">
          <el-text type="danger">{{ currentRefund.cuowu_daima }}</el-text>
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
import { ElMessage } from 'element-plus'
import { refundApi, type Refund, type RefundListParams } from '@/api/modules/refund'
import { formatDateTime } from '@/utils/format'

// 搜索表单
const searchForm = reactive<RefundListParams>({
  tuikuan_zhuangtai: '',
  tuikuan_pingtai: '',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 退款列表
const refundList = ref<Refund[]>([])
const loading = ref(false)

// 详情对话框
const detailDialogVisible = ref(false)
const currentRefund = ref<Refund | null>(null)

/**
 * 获取退款列表
 */
const fetchRefundList = async () => {
  loading.value = true
  try {
    const params: RefundListParams = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    const response = await refundApi.getList(params)
    refundList.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    console.error('获取退款列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取退款列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 搜索
 */
const handleSearch = () => {
  pagination.page = 1
  fetchRefundList()
}

/**
 * 重置
 */
const handleReset = () => {
  searchForm.tuikuan_zhuangtai = ''
  searchForm.tuikuan_pingtai = ''
  searchForm.search = ''
  pagination.page = 1
  fetchRefundList()
}

/**
 * 分页大小改变
 */
const handleSizeChange = (size: number) => {
  pagination.page_size = size
  pagination.page = 1
  fetchRefundList()
}

/**
 * 当前页改变
 */
const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchRefundList()
}

/**
 * 查看详情
 */
const handleViewDetail = async (row: Refund) => {
  try {
    const refund = await refundApi.getDetail(row.id)
    currentRefund.value = refund
    detailDialogVisible.value = true
  } catch (error: any) {
    console.error('获取退款详情失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取退款详情失败')
  }
}

// 初始化
onMounted(() => {
  fetchRefundList()
})
</script>

<style scoped lang="scss">
.refund-manage {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 20px;
  }

  .amount {
    color: #f56c6c;
    font-weight: bold;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>

