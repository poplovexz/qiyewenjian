<template>
  <div class="reimbursement-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报销申请管理</span>
          <el-button type="primary" @click="handleCreate">新建报销申请</el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="审核状态">
          <el-select v-model="searchForm.shenhe_zhuangtai" placeholder="请选择" clearable>
            <el-option label="待审核" value="daishehe" />
            <el-option label="审核中" value="shenhezhong" />
            <el-option label="已通过" value="tongguo" />
            <el-option label="已拒绝" value="jujue" />
          </el-select>
        </el-form-item>
        <el-form-item label="报销类型">
          <el-select
            v-model="searchForm.baoxiao_leixing"
            placeholder="请选择"
            clearable
            :loading="baoxiaoLeibieLoading"
          >
            <el-option
              v-for="item in baoxiaoLeibieOptions"
              :key="item.id"
              :label="item.mingcheng"
              :value="item.mingcheng"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="searchForm.search" placeholder="申请编号/原因" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" border>
        <el-table-column prop="shenqing_bianhao" label="申请编号" width="150" />
        <el-table-column prop="shenqing_ren_xingming" label="申请人" width="100" />
        <el-table-column prop="baoxiao_leixing" label="报销类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getTypeLabel(row.baoxiao_leixing) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="baoxiao_jine" label="报销金额" width="120">
          <template #default="{ row }">
            ¥{{ row.baoxiao_jine }}
          </template>
        </el-table-column>
        <el-table-column prop="baoxiao_yuanyin" label="报销原因" show-overflow-tooltip />
        <el-table-column prop="shenhe_zhuangtai" label="审核状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.shenhe_zhuangtai)">
              {{ getStatusLabel(row.shenhe_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button 
              link 
              type="primary" 
              size="small" 
              @click="handleEdit(row)"
              v-if="row.shenhe_zhuangtai === 'daishehe'"
            >
              编辑
            </el-button>
            <el-button 
              link 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
              v-if="row.shenhe_zhuangtai === 'daishehe'"
            >
              删除
            </el-button>
            <el-button 
              link 
              type="success" 
              size="small" 
              @click="handleSubmit(row)"
              v-if="row.shenhe_zhuangtai === 'daishehe'"
            >
              提交审批
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  getMyReimbursementList,
  deleteReimbursement,
  submitReimbursementForApproval,
  type ReimbursementApplication
} from '@/api/office'
import { getBaoxiaoLeibieList, type BaoxiaoLeibie } from '@/api/modules/finance-settings'

const router = useRouter()
const loading = ref(false)
const tableData = ref<ReimbursementApplication[]>([])

// 报销类别选项
const baoxiaoLeibieOptions = ref<BaoxiaoLeibie[]>([])
const baoxiaoLeibieLoading = ref(false)

const searchForm = reactive({
  shenhe_zhuangtai: '',
  baoxiao_leixing: '',
  search: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 加载报销类别列表
const loadBaoxiaoLeibieOptions = async () => {
  baoxiaoLeibieLoading.value = true
  try {
    const res = await getBaoxiaoLeibieList({ page: 1, size: 100 })
    const allItems = (res as { items?: BaoxiaoLeibie[] }).items || []
    // 只显示启用状态的类别
    baoxiaoLeibieOptions.value = allItems.filter((item: BaoxiaoLeibie) => item.zhuangtai === 'active')
  } catch (error: unknown) {
    // 静默失败，不影响主要功能
    baoxiaoLeibieOptions.value = []
  } finally {
    baoxiaoLeibieLoading.value = false
  }
}

// 获取列表数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMyReimbursementList({
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    })
    tableData.value = res.items
    pagination.total = res.total
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
  searchForm.shenhe_zhuangtai = ''
  searchForm.baoxiao_leixing = ''
  searchForm.search = ''
  handleSearch()
}

// 新建
const handleCreate = () => {
  router.push('/office/reimbursement/create')
}

// 查看
const handleView = (row: ReimbursementApplication) => {
  router.push(`/office/reimbursement/detail/${row.id}`)
}

// 编辑
const handleEdit = (row: ReimbursementApplication) => {
  router.push(`/office/reimbursement/edit/${row.id}`)
}

// 删除
const handleDelete = async (row: ReimbursementApplication) => {
  try {
    await ElMessageBox.confirm('确定要删除这条报销申请吗？', '提示', {
      type: 'warning'
    })
    await deleteReimbursement(row.id!)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    // 用户取消
  }
}

// 提交审批
const handleSubmit = async (row: ReimbursementApplication) => {
  try {
    await ElMessageBox.confirm('确定要提交审批吗？', '提示', {
      type: 'info'
    })
    await submitReimbursementForApproval(row.id!)
    ElMessage.success('提交成功')
    fetchData()
  } catch (error) {
    // 用户取消
  }
}

// 分页
const handleSizeChange = () => {
  fetchData()
}

const handleCurrentChange = () => {
  fetchData()
}

// 辅助函数
const getTypeLabel = (type: string) => {
  // 现在报销类型直接存储类别名称，无需映射
  return type || '-'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    daishehe: '待审核',
    shenhezhong: '审核中',
    tongguo: '已通过',
    jujue: '已拒绝'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daishehe: 'info',
    shenhezhong: 'warning',
    tongguo: 'success',
    jujue: 'danger'
  }
  return map[status] || 'info'
}

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadBaoxiaoLeibieOptions()
  fetchData()
})
</script>

<style scoped lang="scss">
.reimbursement-list {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>

