<template>
  <div class="handover-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>工作交接单管理</span>
          <el-button type="primary" @click="handleCreate">新建交接单</el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="交接编号">
          <el-input v-model="searchForm.jiaojie_bianhao" placeholder="请输入交接编号" clearable />
        </el-form-item>
        <el-form-item label="交接原因">
          <el-select v-model="searchForm.jiaojie_yuanyin" placeholder="请选择" clearable>
            <el-option label="离职" value="lizhi" />
            <el-option label="调岗" value="diaogang" />
            <el-option label="休假" value="xiujia" />
            <el-option label="其他" value="qita" />
          </el-select>
        </el-form-item>
        <el-form-item label="交接状态">
          <el-select v-model="searchForm.jiaojie_zhuangtai" placeholder="请选择" clearable>
            <el-option label="待确认" value="daiqueren" />
            <el-option label="已确认" value="yiqueren" />
            <el-option label="已拒绝" value="yijujue" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="jiaojie_bianhao" label="交接编号" width="150" />
        <el-table-column prop="jiaojie_ren_xingming" label="交接人" width="100" />
        <el-table-column prop="jieshou_ren_xingming" label="接收人" width="100" />
        <el-table-column prop="jiaojie_yuanyin" label="交接原因" width="100">
          <template #default="{ row }">
            {{ getReasonLabel(row.jiaojie_yuanyin) }}
          </template>
        </el-table-column>
        <el-table-column prop="jiaojie_shijian" label="交接时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.jiaojie_shijian) }}
          </template>
        </el-table-column>
        <el-table-column prop="jiaojie_zhuangtai" label="交接状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.jiaojie_zhuangtai)">
              {{ getStatusLabel(row.jiaojie_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="queren_shijian" label="确认时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.queren_shijian) }}
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
            <el-button link type="primary" @click="handleEdit(row)" v-if="row.jiaojie_zhuangtai === 'daiqueren'">
              编辑
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)" v-if="row.jiaojie_zhuangtai === 'daiqueren'">
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
import { getHandoverList, deleteHandover, type HandoverApplication } from '@/api/office'

const router = useRouter()
const loading = ref(false)
const tableData = ref<HandoverApplication[]>([])

const searchForm = reactive({
  jiaojie_bianhao: '',
  jiaojie_yuanyin: '',
  jiaojie_zhuangtai: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.page_size
    }
    const response = await getHandoverList(params)
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
  searchForm.jiaojie_bianhao = ''
  searchForm.jiaojie_yuanyin = ''
  searchForm.jiaojie_zhuangtai = ''
  handleSearch()
}

// 新建
const handleCreate = () => {
  router.push('/office/handover/create')
}

// 查看
const handleView = (row: HandoverApplication) => {
  router.push(`/office/handover/detail/${row.id}`)
}

// 编辑
const handleEdit = (row: HandoverApplication) => {
  router.push(`/office/handover/edit/${row.id}`)
}

// 删除
const handleDelete = async (row: HandoverApplication) => {
  try {
    await ElMessageBox.confirm('确定要删除这条工作交接单吗？', '确认删除', {
      type: 'warning'
    })

    await deleteHandover(row.id!)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 辅助函数
const getReasonLabel = (reason: string) => {
  const map: Record<string, string> = {
    lizhi: '离职',
    diaogang: '调岗',
    xiujia: '休假',
    qita: '其他'
  }
  return map[reason] || reason
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    daiqueren: '待确认',
    yiqueren: '已确认',
    yijujue: '已拒绝'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daiqueren: 'warning',
    yiqueren: 'success',
    yijujue: 'danger'
  }
  return map[status] || 'info'
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
.handover-list {
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
