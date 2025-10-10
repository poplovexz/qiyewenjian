<template>
  <div class="contract-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>合同列表</span>
          <div class="header-actions">
            <el-button @click="handlePartyManage">
              <el-icon><User /></el-icon>
              乙方主体管理
            </el-button>
            <el-dropdown @command="handleCreateAction">
              <el-button type="primary">
                <el-icon><Plus /></el-icon>
                新增合同
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="create">创建空白合同</el-dropdown-item>
                  <el-dropdown-item command="from_quote">基于报价创建</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :model="searchForm" inline>
          <el-form-item label="合同编号">
            <el-input
              v-model="searchForm.contractNumber"
              placeholder="请输入合同编号"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="客户名称">
            <el-input
              v-model="searchForm.customerName"
              placeholder="请输入客户名称"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="合同状态">
            <el-select
              v-model="searchForm.status"
              placeholder="请选择状态"
              clearable
              style="width: 150px"
            >
              <el-option label="草稿" value="draft" />
              <el-option label="生效" value="active" />
              <el-option label="完成" value="completed" />
              <el-option label="终止" value="terminated" />
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
      </div>

      <!-- 表格区域 -->
      <el-table
        v-loading="loading"
        :data="contractList"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="contractNumber" label="合同编号" width="150" />
        <el-table-column prop="customerName" label="客户名称" width="200" />
        <el-table-column prop="contractType" label="合同类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getContractTypeTag(row.contractType)">
              {{ getContractTypeText(row.contractType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="合同金额" width="120">
          <template #default="{ row }">
            ¥{{ row.amount?.toLocaleString() || '0' }}
          </template>
        </el-table-column>
        <el-table-column prop="startDate" label="开始日期" width="120" />
        <el-table-column prop="endDate" label="结束日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
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
import { Plus, Search, Refresh, User, ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useContractManagementStore } from '@/stores/modules/contractManagement'

const router = useRouter()
const contractStore = useContractManagementStore()

// 响应式数据
const loading = ref(false)
const contractList = ref([])

// 搜索表单
const searchForm = reactive({
  contractNumber: '',
  customerName: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取合同列表
const getContractList = async () => {
  loading.value = true
  try {
    // 调用真实的API
    const params = {
      page: pagination.page,
      size: pagination.size,
      hetong_bianhao: searchForm.contractNumber || undefined,
      kehu_mingcheng: searchForm.customerName || undefined,
      hetong_zhuangtai: searchForm.status || undefined
    }

    const response = await contractStore.fetchContracts(params)

    // 转换数据格式以适配现有的表格结构
    contractList.value = response.items.map(contract => ({
      id: contract.id,
      contractNumber: contract.hetong_bianhao,
      customerName: contract.kehu?.gongsi_mingcheng || '未知客户',
      contractType: contract.hetong_moban?.hetong_leixing || 'unknown',
      amount: contract.hetong_jine || 0,
      startDate: contract.shengxiao_riqi ? contract.shengxiao_riqi.split('T')[0] : '',
      endDate: contract.daoqi_riqi ? contract.daoqi_riqi.split('T')[0] : '',
      status: contract.hetong_zhuangtai,
      createdAt: contract.created_at ? contract.created_at.replace('T', ' ').split('.')[0] : '',
      // 保留原始数据以便详细查看
      _original: contract
    }))

    pagination.total = response.total
  } catch (error) {
    console.error('获取合同列表失败:', error)
    ElMessage.error('获取合同列表失败')

    // 如果API调用失败，显示空列表
    contractList.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 合同类型标签
const getContractTypeTag = (type: string) => {
  const tags = {
    daili_jizhang: 'primary',
    zengzhi_fuwu: 'success',
    zixun_fuwu: 'warning'
  }
  return tags[type] || 'info'
}

// 合同类型文本
const getContractTypeText = (type: string) => {
  const texts = {
    daili_jizhang: '代理记账',
    zengzhi_fuwu: '增值服务',
    zixun_fuwu: '咨询服务'
  }
  return texts[type] || '未知'
}

// 状态标签
const getStatusTag = (status: string) => {
  const tags = {
    draft: 'info',
    active: 'success',
    completed: 'primary',
    terminated: 'danger'
  }
  return tags[status] || 'info'
}

// 状态文本
const getStatusText = (status: string) => {
  const texts = {
    draft: '草稿',
    active: '生效',
    completed: '完成',
    terminated: '终止'
  }
  return texts[status] || '未知'
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getContractList()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    contractNumber: '',
    customerName: '',
    status: ''
  })
  pagination.page = 1
  getContractList()
}

// 新增合同下拉菜单处理
const handleCreateAction = (command: string) => {
  if (command === 'create') {
    router.push('/contracts/create')
  } else if (command === 'from_quote') {
    ElMessage.info('请先在线索列表中选择已确认的报价，然后点击"生成合同"按钮')
    router.push('/leads')
  }
}

// 新增（保持向后兼容）
const handleCreate = () => {
  router.push('/contracts/create')
}

// 查看
const handleView = (row: any) => {
  ElMessage.info(`查看合同: ${row.contractNumber}`)
}

// 编辑
const handleEdit = (row: any) => {
  ElMessage.info(`编辑合同: ${row.contractNumber}`)
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除合同 "${row.contractNumber}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success('删除成功')
    getContractList()
  } catch {
    // 用户取消删除
  }
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  getContractList()
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  pagination.page = page
  getContractList()
}

// 乙方主体管理
const handlePartyManage = () => {
  router.push('/contract-parties')
}

// 组件挂载
onMounted(() => {
  getContractList()
})
</script>

<style scoped>
.contract-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-area {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>
