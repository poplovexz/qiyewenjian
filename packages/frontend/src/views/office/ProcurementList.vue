<template>
  <div class="procurement-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购申请管理</span>
          <el-button type="primary" @click="handleCreate">新建采购申请</el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="申请编号">
          <el-input v-model="searchForm.shenqing_bianhao" placeholder="请输入申请编号" clearable />
        </el-form-item>
        <el-form-item label="物品名称">
          <el-input v-model="searchForm.caigou_mingcheng" placeholder="请输入物品名称" clearable />
        </el-form-item>
        <el-form-item label="采购类型">
          <el-select
            v-model="searchForm.caigou_leixing"
            placeholder="请选择"
            clearable
            :loading="zhichuLeibieLoading"
          >
            <el-option
              v-for="item in zhichuLeibieOptions"
              :key="item.id"
              :label="item.mingcheng"
              :value="item.mingcheng"
            />
          </el-select>
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
        <el-table-column prop="caigou_leixing" label="采购类型" width="120">
          <template #default="{ row }">
            {{ getTypeLabel(row.caigou_leixing) }}
          </template>
        </el-table-column>
        <el-table-column prop="caigou_mingcheng" label="物品名称" width="150" />
        <el-table-column prop="caigou_shuliang" label="数量" width="100">
          <template #default="{ row }">
            {{ row.caigou_shuliang }} {{ row.danwei }}
          </template>
        </el-table-column>
        <el-table-column prop="yugu_jine" label="预估金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.yugu_jine }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="yaoqiu_shijian" label="要求到货时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.yaoqiu_shijian) }}
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
            <el-button link type="primary" @click="handleEdit(row)" v-if="row.shenhe_zhuangtai === 'daishehe'">
              编辑
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)" v-if="row.shenhe_zhuangtai === 'daishehe'">
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
import { getProcurementList, deleteProcurement, type ProcurementApplication } from '@/api/office'
import { getZhichuLeibieList, type ZhichuLeibie } from '@/api/modules/finance-settings'

const router = useRouter()
const loading = ref(false)
const tableData = ref<ProcurementApplication[]>([])

// 支出类别选项
const zhichuLeibieOptions = ref<ZhichuLeibie[]>([])
const zhichuLeibieLoading = ref(false)

const searchForm = reactive({
  shenqing_bianhao: '',
  caigou_mingcheng: '',
  caigou_leixing: '',
  shenhe_zhuangtai: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 加载支出类别列表
const loadZhichuLeibieOptions = async () => {
  zhichuLeibieLoading.value = true
  try {
    const res = await getZhichuLeibieList({ page: 1, size: 200 })
    const allItems = (res as { items?: ZhichuLeibie[] }).items || []
    // 只显示启用状态的类别
    zhichuLeibieOptions.value = allItems.filter((item: ZhichuLeibie) => item.zhuangtai === 'active')
  } catch (error: unknown) {
    // 静默失败，不影响主要功能
    zhichuLeibieOptions.value = []
  } finally {
    zhichuLeibieLoading.value = false
  }
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.page_size
    }
    const response = await getProcurementList(params)
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
  searchForm.caigou_mingcheng = ''
  searchForm.caigou_leixing = ''
  searchForm.shenhe_zhuangtai = ''
  handleSearch()
}

// 新建
const handleCreate = () => {
  router.push('/office/procurement/create')
}

// 查看
const handleView = (row: ProcurementApplication) => {
  router.push(`/office/procurement/detail/${row.id}`)
}

// 编辑
const handleEdit = (row: ProcurementApplication) => {
  router.push(`/office/procurement/edit/${row.id}`)
}

// 删除
const handleDelete = async (row: ProcurementApplication) => {
  try {
    await ElMessageBox.confirm('确定要删除这条采购申请吗？', '确认删除', {
      type: 'warning'
    })

    await deleteProcurement(row.id!)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 辅助函数
const getTypeLabel = (type: string) => {
  // 现在采购类型直接存储类别名称，无需映射
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
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadZhichuLeibieOptions()
  fetchData()
})
</script>

<style scoped lang="scss">
.procurement-list {
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

