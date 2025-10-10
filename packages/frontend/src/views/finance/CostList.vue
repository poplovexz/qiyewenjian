<template>
  <div class="cost-list-container">
    <el-card class="page-header">
      <div class="header-content">
        <h2>成本记录管理</h2>
        <p>管理成本记录的创建、审核和入账流程</p>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>成本记录列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建记录
            </el-button>
            <el-button @click="refreshList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="showStatistics">
              <el-icon><DataAnalysis /></el-icon>
              统计分析
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="搜索">
          <el-input 
            v-model="searchForm.search" 
            placeholder="成本编号、成本名称、供应商名称"
            style="width: 250px"
            clearable
          />
        </el-form-item>
        <el-form-item label="成本类型">
          <el-select v-model="searchForm.chengben_leixing" placeholder="请选择" clearable>
            <el-option label="人工成本" value="rengong" />
            <el-option label="材料成本" value="cailiao" />
            <el-option label="设备成本" value="shebei" />
            <el-option label="外包成本" value="waibao" />
            <el-option label="其他成本" value="qita" />
          </el-select>
        </el-form-item>
        <el-form-item label="成本分类">
          <el-select v-model="searchForm.chengben_fenlei" placeholder="请选择" clearable>
            <el-option label="直接成本" value="zhijie" />
            <el-option label="间接成本" value="jianjie" />
            <el-option label="固定成本" value="guding" />
            <el-option label="变动成本" value="biandong" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="searchForm.shenhe_zhuangtai" placeholder="请选择" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已审批" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已入账" value="recorded" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table 
        :data="tableData" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="chengben_bianhao" label="成本编号" width="150" />
        <el-table-column prop="chengben_mingcheng" label="成本名称" min-width="200" />
        <el-table-column prop="chengben_leixing" label="成本类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getCostTypeTag(row.chengben_leixing)">
              {{ getCostTypeName(row.chengben_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chengben_fenlei" label="成本分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCostCategoryTag(row.chengben_fenlei)">
              {{ getCostCategoryName(row.chengben_fenlei) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chengben_jine" label="成本金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.chengben_jine?.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="yusuan_jine" label="预算金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.yusuan_jine?.toLocaleString() || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="gongyingshang_mingcheng" label="供应商" min-width="150" />
        <el-table-column prop="shenhe_zhuangtai" label="审核状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getAuditStatusTag(row.shenhe_zhuangtai)">
              {{ getAuditStatusName(row.shenhe_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fasheng_shijian" label="发生时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.fasheng_shijian) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button 
              v-if="canEdit(row)"
              type="warning" 
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-dropdown v-if="hasMoreActions(row)" style="margin-left: 8px">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="canSubmit(row)" @click="handleSubmit(row)">
                    提交审核
                  </el-dropdown-item>
                  <el-dropdown-item v-if="canAudit(row)" @click="handleAudit(row)">
                    审核
                  </el-dropdown-item>
                  <el-dropdown-item v-if="canRecord(row)" @click="handleRecord(row)">
                    入账
                  </el-dropdown-item>
                  <el-dropdown-item v-if="canDelete(row)" @click="handleDelete(row)" divided>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; text-align: right"
      />
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog v-model="auditDialogVisible" title="成本记录审核" width="600px">
      <el-form :model="auditForm" label-width="100px">
        <el-form-item label="成本编号">
          <span>{{ currentRecord?.chengben_bianhao }}</span>
        </el-form-item>
        <el-form-item label="成本名称">
          <span>{{ currentRecord?.chengben_mingcheng }}</span>
        </el-form-item>
        <el-form-item label="成本金额">
          <span class="amount">¥{{ currentRecord?.chengben_jine?.toLocaleString() }}</span>
        </el-form-item>
        <el-form-item label="审核结果" required>
          <el-radio-group v-model="auditForm.shenhe_jieguo">
            <el-radio value="approved">通过</el-radio>
            <el-radio value="rejected">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input 
            v-model="auditForm.shenhe_yijian"
            type="textarea"
            :rows="4"
            placeholder="请输入审核意见"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="auditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAudit" :loading="auditLoading">
          确认审核
        </el-button>
      </template>
    </el-dialog>

    <!-- 入账对话框 -->
    <el-dialog v-model="recordDialogVisible" title="成本入账" width="600px">
      <el-form :model="recordForm" label-width="100px">
        <el-form-item label="成本编号">
          <span>{{ currentRecord?.chengben_bianhao }}</span>
        </el-form-item>
        <el-form-item label="预算金额">
          <span class="amount">¥{{ currentRecord?.chengben_jine?.toLocaleString() }}</span>
        </el-form-item>
        <el-form-item label="实际金额" required>
          <el-input-number 
            v-model="recordForm.shiji_jine" 
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="请输入实际金额"
          />
        </el-form-item>
        <el-form-item label="记账时间">
          <el-date-picker
            v-model="recordForm.jizhangjian"
            type="datetime"
            placeholder="选择记账时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="会计科目">
          <el-input v-model="recordForm.kuaiji_kemu" placeholder="请输入会计科目" />
        </el-form-item>
        <el-form-item label="成本中心">
          <el-input v-model="recordForm.chengben_zhongxin" placeholder="请输入成本中心" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="recordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRecord" :loading="recordLoading">
          确认入账
        </el-button>
      </template>
    </el-dialog>

    <!-- 统计分析对话框 -->
    <el-dialog v-model="statisticsDialogVisible" title="成本统计分析" width="800px">
      <div v-loading="statisticsLoading">
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="6">
            <el-statistic title="总记录数" :value="statistics.total_count" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="总成本金额" :value="statistics.total_amount" prefix="¥" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="预算金额" :value="statistics.budget_amount" prefix="¥" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="实际金额" :value="statistics.actual_amount" prefix="¥" />
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="草稿" :value="statistics.draft_count" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="已提交" :value="statistics.submitted_count" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="已审批" :value="statistics.approved_count" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="已入账" :value="statistics.recorded_count" />
          </el-col>
        </el-row>

        <el-divider />
        
        <div style="text-align: center">
          <h4>预算差异分析</h4>
          <el-statistic 
            title="差异金额" 
            :value="statistics.variance_amount" 
            prefix="¥"
            :value-style="{ color: statistics.variance_amount >= 0 ? '#cf1322' : '#3f8600' }"
          />
          <el-statistic 
            title="差异率" 
            :value="statistics.variance_rate" 
            suffix="%"
            :precision="2"
            :value-style="{ color: statistics.variance_rate >= 0 ? '#cf1322' : '#3f8600' }"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, ArrowDown, DataAnalysis } from '@element-plus/icons-vue'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchForm = reactive({
  search: '',
  chengben_leixing: '',
  chengben_fenlei: '',
  shenhe_zhuangtai: ''
})

const auditDialogVisible = ref(false)
const recordDialogVisible = ref(false)
const statisticsDialogVisible = ref(false)
const currentRecord = ref(null)
const auditLoading = ref(false)
const recordLoading = ref(false)
const statisticsLoading = ref(false)

const auditForm = reactive({
  shenhe_jieguo: '',
  shenhe_yijian: ''
})

const recordForm = reactive({
  shiji_jine: 0,
  jizhangjian: null,
  kuaiji_kemu: '',
  chengben_zhongxin: ''
})

const statistics = reactive({
  total_count: 0,
  draft_count: 0,
  submitted_count: 0,
  approved_count: 0,
  recorded_count: 0,
  rejected_count: 0,
  total_amount: 0,
  budget_amount: 0,
  actual_amount: 0,
  variance_amount: 0,
  variance_rate: 0
})

// 方法
const fetchData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString(),
      ...Object.fromEntries(Object.entries(searchForm).filter(([_, v]) => v))
    })

    const response = await fetch(`/api/v1/costs?${params}`)
    const data = await response.json()
    
    if (response.ok) {
      tableData.value = data.items
      total.value = data.total
    } else {
      ElMessage.error(data.detail || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  statisticsLoading.value = true
  try {
    const response = await fetch('/api/v1/costs/statistics/overview')
    const data = await response.json()
    
    if (response.ok) {
      Object.assign(statistics, data)
    } else {
      ElMessage.error(data.detail || '获取统计数据失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    statisticsLoading.value = false
  }
}

const refreshList = () => {
  fetchData()
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  currentPage.value = 1
  fetchData()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchData()
}

const handleCreate = () => {
  router.push('/finance/costs/create')
}

const handleView = (row: any) => {
  router.push(`/finance/costs/${row.id}`)
}

const handleEdit = (row: any) => {
  router.push(`/finance/costs/${row.id}/edit`)
}

const handleSubmit = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认要提交该成本记录吗？', '确认操作', {
      type: 'warning'
    })

    const response = await fetch(`/api/v1/costs/${row.id}/submit`, {
      method: 'POST'
    })
    
    if (response.ok) {
      ElMessage.success('提交成功')
      fetchData()
    } else {
      const data = await response.json()
      ElMessage.error(data.detail || '提交失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('网络错误')
    }
  }
}

const handleAudit = (row: any) => {
  currentRecord.value = row
  auditForm.shenhe_jieguo = ''
  auditForm.shenhe_yijian = ''
  auditDialogVisible.value = true
}

const confirmAudit = async () => {
  if (!auditForm.shenhe_jieguo) {
    ElMessage.warning('请选择审核结果')
    return
  }

  auditLoading.value = true
  try {
    const response = await fetch('/api/v1/costs/audit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        jilu_id: currentRecord.value.id,
        ...auditForm
      })
    })
    
    if (response.ok) {
      ElMessage.success('审核成功')
      auditDialogVisible.value = false
      fetchData()
    } else {
      const data = await response.json()
      ElMessage.error(data.detail || '审核失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    auditLoading.value = false
  }
}

const handleRecord = (row: any) => {
  currentRecord.value = row
  recordForm.shiji_jine = row.chengben_jine
  recordForm.jizhangjian = null
  recordForm.kuaiji_kemu = ''
  recordForm.chengben_zhongxin = ''
  recordDialogVisible.value = true
}

const confirmRecord = async () => {
  if (!recordForm.shiji_jine || recordForm.shiji_jine <= 0) {
    ElMessage.warning('请输入有效的实际金额')
    return
  }

  recordLoading.value = true
  try {
    const response = await fetch('/api/v1/costs/record', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        jilu_id: currentRecord.value.id,
        ...recordForm
      })
    })
    
    if (response.ok) {
      ElMessage.success('入账成功')
      recordDialogVisible.value = false
      fetchData()
    } else {
      const data = await response.json()
      ElMessage.error(data.detail || '入账失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    recordLoading.value = false
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认要删除该成本记录吗？', '确认删除', {
      type: 'warning'
    })

    const response = await fetch(`/api/v1/costs/${row.id}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('删除成功')
      fetchData()
    } else {
      const data = await response.json()
      ElMessage.error(data.detail || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('网络错误')
    }
  }
}

const showStatistics = () => {
  statisticsDialogVisible.value = true
  fetchStatistics()
}

// 权限判断方法
const canEdit = (row: any) => {
  return row.shenhe_zhuangtai === 'draft'
}

const canSubmit = (row: any) => {
  return row.shenhe_zhuangtai === 'draft'
}

const canAudit = (row: any) => {
  return row.shenhe_zhuangtai === 'submitted'
}

const canRecord = (row: any) => {
  return row.shenhe_zhuangtai === 'approved'
}

const canDelete = (row: any) => {
  return row.shenhe_zhuangtai === 'draft'
}

const hasMoreActions = (row: any) => {
  return canSubmit(row) || canAudit(row) || canRecord(row) || canDelete(row)
}

// 辅助方法
const getCostTypeTag = (type: string) => {
  const typeMap = {
    'rengong': 'primary',
    'cailiao': 'success',
    'shebei': 'warning',
    'waibao': 'danger',
    'qita': 'info'
  }
  return typeMap[type] || 'info'
}

const getCostTypeName = (type: string) => {
  const nameMap = {
    'rengong': '人工成本',
    'cailiao': '材料成本',
    'shebei': '设备成本',
    'waibao': '外包成本',
    'qita': '其他成本'
  }
  return nameMap[type] || type
}

const getCostCategoryTag = (category: string) => {
  const categoryMap = {
    'zhijie': 'success',
    'jianjie': 'warning',
    'guding': 'primary',
    'biandong': 'danger'
  }
  return categoryMap[category] || 'info'
}

const getCostCategoryName = (category: string) => {
  const nameMap = {
    'zhijie': '直接成本',
    'jianjie': '间接成本',
    'guding': '固定成本',
    'biandong': '变动成本'
  }
  return nameMap[category] || category
}

const getAuditStatusTag = (status: string) => {
  const statusMap = {
    'draft': 'info',
    'submitted': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'recorded': 'success'
  }
  return statusMap[status] || 'info'
}

const getAuditStatusName = (status: string) => {
  const nameMap = {
    'draft': '草稿',
    'submitted': '已提交',
    'approved': '已审批',
    'rejected': '已拒绝',
    'recorded': '已入账'
  }
  return nameMap[status] || status
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.cost-list-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.header-content p {
  margin: 0;
  color: #606266;
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

.search-form {
  margin-bottom: 20px;
}

.amount {
  font-weight: bold;
  color: #E6A23C;
}
</style>
