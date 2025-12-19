<template>
  <div class="payment-application-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>对外付款申请管理</span>
          <el-button type="primary" @click="handleCreate">新建付款申请</el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="申请编号">
          <el-input v-model="searchForm.shenqing_bianhao" placeholder="请输入申请编号" clearable />
        </el-form-item>
        <el-form-item label="付款对象">
          <el-input v-model="searchForm.fukuan_duixiang" placeholder="请输入付款对象" clearable />
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="searchForm.shenhe_zhuangtai" placeholder="请选择" clearable>
            <el-option label="待审核" value="daishehe" />
            <el-option label="审核中" value="shenhezhong" />
            <el-option label="已通过" value="tongguo" />
            <el-option label="已拒绝" value="jujue" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="shenqing_bianhao" label="申请编号" width="150" />
        <el-table-column prop="shenqing_ren_xingming" label="申请人" width="100" />
        <el-table-column prop="fukuan_duixiang" label="付款对象" width="150" />
        <el-table-column prop="fukuan_jine" label="付款金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.fukuan_jine }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fukuan_fangshi" label="付款方式" width="120">
          <template #default="{ row }">
            {{ getPaymentMethodLabel(row.fukuan_fangshi) }}
          </template>
        </el-table-column>
        <el-table-column prop="yaoqiu_fukuan_shijian" label="要求付款时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.yaoqiu_fukuan_shijian) }}
          </template>
        </el-table-column>
        <el-table-column prop="shenhe_zhuangtai" label="审核状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.shenhe_zhuangtai)">
              {{ getStatusLabel(row.shenhe_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button
              link
              type="primary"
              @click="handleEdit(row)"
              v-if="row.shenhe_zhuangtai === 'daishehe'"
            >
              编辑
            </el-button>
            <el-button
              link
              type="danger"
              @click="handleDelete(row)"
              v-if="row.shenhe_zhuangtai === 'daishehe'"
            >
              删除
            </el-button>
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
        @size-change="fetchData"
        @current-change="fetchData"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPaymentList, deletePayment, type PaymentApplication } from '@/api/office'

const router = useRouter()
const loading = ref(false)
const tableData = ref<PaymentApplication[]>([])

const searchForm = reactive({
  shenqing_bianhao: '',
  fukuan_duixiang: '',
  shenhe_zhuangtai: '',
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.page_size,
    }
    const response = await getPaymentList(params)
    tableData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.shenqing_bianhao = ''
  searchForm.fukuan_duixiang = ''
  searchForm.shenhe_zhuangtai = ''
  handleSearch()
}

// 新建
const handleCreate = () => {
  router.push('/office/payment/create')
}

// 查看
const handleView = (row: PaymentApplication) => {
  router.push(`/office/payment/detail/${row.id}`)
}

// 编辑
const handleEdit = (row: PaymentApplication) => {
  router.push(`/office/payment/edit/${row.id}`)
}

// 删除
const handleDelete = async (row: PaymentApplication) => {
  try {
    await ElMessageBox.confirm('确定要删除这条付款申请吗？', '确认删除', {
      type: 'warning',
    })

    await deletePayment(row.id!)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 辅助函数
const getPaymentMethodLabel = (method: string) => {
  const map: Record<string, string> = {
    yinhang_zhuanzhang: '银行转账',
    zhipiao: '支票',
    xianjin: '现金',
    zhifubao: '支付宝',
    weixin: '微信',
    qita: '其他',
  }
  return map[method] || method
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    daishehe: '待审核',
    shenhezhong: '审核中',
    tongguo: '已通过',
    jujue: '已拒绝',
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daishehe: 'info',
    shenhezhong: 'warning',
    tongguo: 'success',
    jujue: 'danger',
  }
  return map[status] || 'info'
}

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.payment-application-list {
  padding: 20px;

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
