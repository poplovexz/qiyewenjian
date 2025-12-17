<template>
  <div class="invoice-list-container">
    <el-card class="page-header">
      <div class="header-content">
        <h2>开票申请管理</h2>
        <p>管理开票申请的创建、审核和处理流程</p>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>开票申请列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建申请
            </el-button>
            <el-button @click="refreshList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="搜索">
          <el-input 
            v-model="searchForm.search" 
            placeholder="申请编号、开票名称、购物方名称"
            style="width: 250px"
            clearable
          />
        </el-form-item>
        <el-form-item label="开票类型">
          <el-select v-model="searchForm.kaipiao_leixing" placeholder="请选择" clearable>
            <el-option label="增值税专用发票" value="zengzhishui" />
            <el-option label="普通发票" value="putong" />
            <el-option label="电子发票" value="dianzifapiao" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请状态">
          <el-select v-model="searchForm.shenqing_zhuangtai" placeholder="请选择" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已审批" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已开票" value="invoiced" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="开票状态">
          <el-select v-model="searchForm.kaipiao_zhuangtai" placeholder="请选择" clearable>
            <el-option label="待开票" value="pending" />
            <el-option label="开票中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="开票失败" value="failed" />
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
        <el-table-column prop="shenqing_bianhao" label="申请编号" width="150" />
        <el-table-column prop="kaipiao_mingcheng" label="开票名称" min-width="200" />
        <el-table-column prop="kaipiao_leixing" label="开票类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getInvoiceTypeTag(row.kaipiao_leixing)">
              {{ getInvoiceTypeName(row.kaipiao_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="jia_shui_jine" label="价税合计" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.jia_shui_jine?.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="gouwu_fang_mingcheng" label="购物方" min-width="150" />
        <el-table-column prop="shenqing_zhuangtai" label="申请状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getApplicationStatusTag(row.shenqing_zhuangtai)">
              {{ getApplicationStatusName(row.shenqing_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="kaipiao_zhuangtai" label="开票状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getInvoiceStatusTag(row.kaipiao_zhuangtai)">
              {{ getInvoiceStatusName(row.kaipiao_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shenqing_shijian" label="申请时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.shenqing_shijian) }}
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
                  <el-dropdown-item v-if="canProcess(row)" @click="handleProcess(row)">
                    开票处理
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
    <el-dialog v-model="auditDialogVisible" title="开票申请审核" width="600px">
      <el-form :model="auditForm" label-width="100px">
        <el-form-item label="申请编号">
          <span>{{ currentRecord?.shenqing_bianhao }}</span>
        </el-form-item>
        <el-form-item label="开票名称">
          <span>{{ currentRecord?.kaipiao_mingcheng }}</span>
        </el-form-item>
        <el-form-item label="价税合计">
          <span class="amount">¥{{ currentRecord?.jia_shui_jine?.toLocaleString() }}</span>
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

    <!-- 开票处理对话框 -->
    <el-dialog v-model="processDialogVisible" title="开票处理" width="600px">
      <el-form :model="processForm" label-width="100px">
        <el-form-item label="申请编号">
          <span>{{ currentRecord?.shenqing_bianhao }}</span>
        </el-form-item>
        <el-form-item label="发票号码" required>
          <el-input v-model="processForm.fapiao_hao" placeholder="请输入发票号码" />
        </el-form-item>
        <el-form-item label="发票代码" required>
          <el-input v-model="processForm.fapiao_daima" placeholder="请输入发票代码" />
        </el-form-item>
        <el-form-item label="发票文件">
          <el-input v-model="processForm.fapiao_wenjian_lujing" placeholder="发票文件路径（可选）" />
        </el-form-item>
        <el-form-item label="开票时间">
          <el-date-picker
            v-model="processForm.kaipiao_shijian"
            type="datetime"
            placeholder="选择开票时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="processDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmProcess" :loading="processLoading">
          确认开票
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, ArrowDown } from '@element-plus/icons-vue'

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
  kaipiao_leixing: '',
  shenqing_zhuangtai: '',
  kaipiao_zhuangtai: ''
})

const auditDialogVisible = ref(false)
const processDialogVisible = ref(false)
const currentRecord = ref(null)
const auditLoading = ref(false)
const processLoading = ref(false)

const auditForm = reactive({
  shenhe_jieguo: '',
  shenhe_yijian: ''
})

const processForm = reactive({
  fapiao_hao: '',
  fapiao_daima: '',
  fapiao_wenjian_lujing: '',
  kaipiao_shijian: null
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

    const response = await fetch(`/invoices?${params}`)
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
  router.push('/finance/invoices/create')
}

const handleView = (row: any) => {
  router.push(`/finance/invoices/${row.id}`)
}

const handleEdit = (row: any) => {
  router.push(`/finance/invoices/${row.id}/edit`)
}

const handleSubmit = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认要提交该开票申请吗？', '确认操作', {
      type: 'warning'
    })

    const response = await fetch(`/invoices/${row.id}/submit`, {
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
    const response = await fetch('/invoices/audit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        shenqing_id: currentRecord.value.id,
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

const handleProcess = (row: any) => {
  currentRecord.value = row
  processForm.fapiao_hao = ''
  processForm.fapiao_daima = ''
  processForm.fapiao_wenjian_lujing = ''
  processForm.kaipiao_shijian = null
  processDialogVisible.value = true
}

const confirmProcess = async () => {
  if (!processForm.fapiao_hao || !processForm.fapiao_daima) {
    ElMessage.warning('请填写发票号码和发票代码')
    return
  }

  processLoading.value = true
  try {
    const response = await fetch('/invoices/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        shenqing_id: currentRecord.value.id,
        ...processForm
      })
    })
    
    if (response.ok) {
      ElMessage.success('开票处理成功')
      processDialogVisible.value = false
      fetchData()
    } else {
      const data = await response.json()
      ElMessage.error(data.detail || '开票处理失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    processLoading.value = false
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认要删除该开票申请吗？', '确认删除', {
      type: 'warning'
    })

    const response = await fetch(`/invoices/${row.id}`, {
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

// 权限判断方法
const canEdit = (row: any) => {
  return row.shenqing_zhuangtai === 'draft'
}

const canSubmit = (row: any) => {
  return row.shenqing_zhuangtai === 'draft'
}

const canAudit = (row: any) => {
  return row.shenqing_zhuangtai === 'submitted'
}

const canProcess = (row: any) => {
  return row.shenqing_zhuangtai === 'approved'
}

const canDelete = (row: any) => {
  return row.shenqing_zhuangtai === 'draft'
}

const hasMoreActions = (row: any) => {
  return canSubmit(row) || canAudit(row) || canProcess(row) || canDelete(row)
}

// 辅助方法
const getInvoiceTypeTag = (type: string) => {
  const typeMap = {
    'zengzhishui': 'danger',
    'putong': 'primary',
    'dianzifapiao': 'success'
  }
  return typeMap[type] || 'info'
}

const getInvoiceTypeName = (type: string) => {
  const nameMap = {
    'zengzhishui': '增值税专用发票',
    'putong': '普通发票',
    'dianzifapiao': '电子发票'
  }
  return nameMap[type] || type
}

const getApplicationStatusTag = (status: string) => {
  const statusMap = {
    'draft': 'info',
    'submitted': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'invoiced': 'success',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}

const getApplicationStatusName = (status: string) => {
  const nameMap = {
    'draft': '草稿',
    'submitted': '已提交',
    'approved': '已审批',
    'rejected': '已拒绝',
    'invoiced': '已开票',
    'cancelled': '已取消'
  }
  return nameMap[status] || status
}

const getInvoiceStatusTag = (status: string) => {
  const statusMap = {
    'pending': 'warning',
    'processing': 'primary',
    'completed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getInvoiceStatusName = (status: string) => {
  const nameMap = {
    'pending': '待开票',
    'processing': '开票中',
    'completed': '已完成',
    'failed': '开票失败'
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
.invoice-list-container {
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
