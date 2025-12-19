<template>
  <div class="payment-method-list">
    <div class="page-header">
      <h1>支付管理</h1>
    </div>

    <!-- 标签页切换 -->
    <el-tabs v-model="activeTab" class="payment-tabs">
      <!-- 支付方式管理 -->
      <el-tab-pane label="支付方式" name="methods">
        <div class="tab-header">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建支付方式
          </el-button>
        </div>

        <!-- 搜索筛选 -->
        <div class="search-bar">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="支付方式名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.zhifu_zhuangtai"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
      stripe
      style="width: 100%"
    >
      <el-table-column label="乙方主体" width="200">
        <template #default="{ row }">
          {{ row.yifang_zhuti?.zhuti_mingcheng || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="zhifu_mingcheng" label="支付方式" width="200" />
      <el-table-column label="支付配置" width="200">
        <template #default="{ row }">
          {{ row.zhifu_peizhi?.peizhi_mingcheng || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="配置类型" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.zhifu_peizhi" :type="getPaymentTypeTagType(row.zhifu_peizhi.peizhi_leixing)">
            {{ getPaymentTypeLabel(row.zhifu_peizhi.peizhi_leixing) }}
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="shi_moren" label="默认支付" width="100">
        <template #default="{ row }">
          <el-tag :type="row.shi_moren === 'Y' ? 'success' : 'info'">
            {{ row.shi_moren === 'Y' ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="zhifu_zhuangtai" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.zhifu_zhuangtai === 'active' ? 'success' : 'danger'">
            {{ row.zhifu_zhuangtai === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="paixu" label="排序" width="80" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button
            v-if="row.shi_moren !== 'Y'"
            type="success"
            size="small"
            @click="handleSetDefault(row)"
          >
            设为默认
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

        <!-- 分页 -->
        <div class="pagination">
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
      </el-tab-pane>

      <!-- 支付配置管理 -->
      <el-tab-pane label="支付配置" name="configs">
        <PaymentConfigManage />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import type { PaymentMethod } from '@/api/modules/contract'
import PaymentConfigManage from '@/views/payment/PaymentConfigManage.vue'

const router = useRouter()
const contractStore = useContractManagementStore()

// 标签页
const activeTab = ref('methods')

// 响应式数据
const loading = ref(false)
const tableData = ref<PaymentMethod[]>([])

// 搜索表单
const searchForm = reactive({
  search: '',
  zhifu_zhuangtai: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: searchForm.search || undefined,
      zhifu_zhuangtai: searchForm.zhifu_zhuangtai || undefined
    }
    const response = await contractStore.fetchPaymentMethods(params)
    tableData.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    search: '',
    zhifu_zhuangtai: ''
  })
  pagination.page = 1
  loadData()
}

// 新建
const handleCreate = () => {
  router.push('/payment-methods/create')
}

// 编辑
const handleEdit = (row: PaymentMethod) => {
  router.push(`/payment-methods/${row.id}/edit`)
}

// 设为默认
const handleSetDefault = async (row: PaymentMethod) => {
  try {
    await contractStore.setDefaultPaymentMethod(row.id)
    ElMessage.success('设置成功')
    loadData()
  } catch (error) {
    ElMessage.error('设置失败')
  }
}

// 删除
const handleDelete = async (row: PaymentMethod) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除支付方式"${row.zhifu_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await contractStore.deletePaymentMethod(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 分页事件
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadData()
}

// 辅助函数：获取支付类型标签
const getPaymentTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    weixin: '微信支付',
    zhifubao: '支付宝',
    yinhang: '银行汇款',
    xianjin: '现金支付'
  }
  return map[type] || type
}

// 辅助函数：获取支付类型标签颜色
const getPaymentTypeTagType = (type: string) => {
  const map: Record<string, string> = {
    weixin: 'success',
    zhifubao: 'primary',
    yinhang: 'warning',
    xianjin: 'info'
  }
  return map[type] || ''
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.payment-method-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.payment-tabs {
  margin-top: 20px;
}

.tab-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.search-bar {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>
