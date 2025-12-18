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
              <el-option label="作废" value="voided" />
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
      <el-table v-loading="loading" :data="contractList" stripe style="width: 100%">
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
          <template #default="{ row }"> ¥{{ row.amount?.toLocaleString() || '0' }} </template>
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
        <el-table-column label="操作" width="520" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button
              v-if="row.status !== 'voided'"
              type="warning"
              size="small"
              @click="handleEdit(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              v-if="row.hetong_zhuangtai === 'signed' && !row.has_service_order"
              type="success"
              size="small"
              @click="handleCreateServiceOrder(row)"
            >
              <el-icon><DocumentAdd /></el-icon>
              创建工单
            </el-button>
            <el-button
              v-if="row.hetong_zhuangtai === 'signed' && row.has_service_order"
              type="info"
              size="small"
              @click="handleViewServiceOrder(row)"
            >
              <el-icon><Document /></el-icon>
              查看工单
            </el-button>
            <el-button
              v-if="row.status !== 'voided'"
              type="success"
              size="small"
              @click="handleGenerateSignLink(row)"
            >
              <el-icon><Link /></el-icon>
              签署链接
            </el-button>
            <el-button
              v-if="row.status !== 'voided'"
              type="info"
              size="small"
              @click="handleVoid(row)"
            >
              <el-icon><CircleClose /></el-icon>
              作废
            </el-button>
            <el-button
              v-if="row.status !== 'voided'"
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon>
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

    <!-- 查看合同对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="查看合同"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentContract" class="contract-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="合同编号">
            {{ currentContract.hetong_bianhao }}
          </el-descriptions-item>
          <el-descriptions-item label="合同名称">
            {{ currentContract.hetong_mingcheng }}
          </el-descriptions-item>
          <el-descriptions-item label="合同状态">
            <el-tag :type="getStatusTag(currentContract.hetong_zhuangtai)">
              {{ getStatusText(currentContract.hetong_zhuangtai) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="签署日期">
            {{ currentContract.qianshu_riqi || '未签署' }}
          </el-descriptions-item>
          <el-descriptions-item label="生效日期">
            {{ currentContract.shengxiao_riqi || '未生效' }}
          </el-descriptions-item>
          <el-descriptions-item label="到期日期">
            {{ currentContract.daoqi_riqi }}
          </el-descriptions-item>
          <el-descriptions-item label="支付状态">
            <el-tag :type="getPaymentStatusTag(currentContract.payment_status)">
              {{ getPaymentStatusText(currentContract.payment_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="支付金额">
            {{ currentContract.payment_amount || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ currentContract.created_at }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">合同内容</el-divider>
        <div
          class="contract-content"
          v-html="sanitizeContractHtml(currentContract.hetong_neirong)"
        ></div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 编辑合同对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑合同"
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form v-if="currentContract" ref="editFormRef" :model="editForm" label-width="120px">
        <el-form-item label="合同名称" prop="hetong_mingcheng">
          <el-input v-model="editForm.hetong_mingcheng" />
        </el-form-item>
        <el-form-item label="合同状态" prop="hetong_zhuangtai">
          <el-select v-model="editForm.hetong_zhuangtai" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending" />
            <el-option label="已审批" value="approved" />
            <el-option label="已签署" value="signed" />
            <el-option label="已过期" value="expired" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="到期日期" prop="daoqi_riqi">
          <el-date-picker
            v-model="editForm.daoqi_riqi"
            type="datetime"
            placeholder="选择日期时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="支付金额" prop="payment_amount">
          <el-input v-model="editForm.payment_amount" placeholder="请输入金额" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit" :loading="saving"> 保存 </el-button>
      </template>
    </el-dialog>

    <!-- 签署链接对话框 -->
    <el-dialog
      v-model="signLinkDialogVisible"
      title="客户签署链接"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="signLinkInfo" class="sign-link-info">
        <el-alert
          title="签署链接已生成"
          type="success"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #default>
            <p>请将以下链接发送给客户进行签署和支付</p>
            <p>链接有效期：{{ formatExpireTime(signLinkInfo.expires_at) }}</p>
          </template>
        </el-alert>

        <el-form label-width="100px">
          <el-form-item label="签署链接">
            <el-input v-model="signLinkInfo.sign_link" readonly>
              <template #append>
                <el-button @click="copySignLink">复制</el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="签署令牌">
            <el-input v-model="signLinkInfo.sign_token" readonly />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="signLinkDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="openSignLink"> 在新窗口打开 </el-button>
      </template>
    </el-dialog>

    <!-- 作废合同对话框 -->
    <el-dialog
      v-model="voidDialogVisible"
      title="作废合同"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-alert title="作废提示" type="warning" :closable="false" style="margin-bottom: 20px">
        <template #default>
          <p>作废后的合同将无法编辑、签署和删除</p>
          <p>但会保留在系统中用于历史记录和审计追溯</p>
          <p style="color: #e6a23c; font-weight: bold">此操作不可撤销，请谨慎操作！</p>
        </template>
      </el-alert>

      <el-form ref="voidFormRef" :model="voidForm" :rules="voidFormRules" label-width="100px">
        <el-form-item label="合同编号">
          <el-input :value="currentContract?.contractNumber" disabled />
        </el-form-item>
        <el-form-item label="客户名称">
          <el-input :value="currentContract?.customerName" disabled />
        </el-form-item>
        <el-form-item label="作废原因" prop="voidReason">
          <el-input
            v-model="voidForm.voidReason"
            type="textarea"
            :rows="4"
            placeholder="请输入作废原因（必填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="voidDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleConfirmVoid" :loading="voiding">
          确认作废
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  User,
  ArrowDown,
  View,
  Edit,
  Delete,
  Link,
  CircleClose,
  Document,
  DocumentAdd,
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { contractApi } from '@/api/modules/contract'
import { serviceOrderApi } from '@/api/modules/serviceOrder'
import { sanitizeContractHtml } from '@/utils/sanitize'

const router = useRouter()
const contractStore = useContractManagementStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const voiding = ref(false)
const contractList = ref([])
const currentContract = ref<any>(null)
const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)
const signLinkDialogVisible = ref(false)
const voidDialogVisible = ref(false)
const signLinkInfo = ref<any>(null)
const editFormRef = ref()
const voidFormRef = ref()
const editForm = reactive({
  hetong_mingcheng: '',
  hetong_zhuangtai: '',
  daoqi_riqi: '',
  payment_amount: '',
})
const voidForm = reactive({
  voidReason: '',
})

// 作废表单验证规则
const voidFormRules = {
  voidReason: [
    { required: true, message: '请输入作废原因', trigger: 'blur' },
    { min: 10, message: '作废原因至少10个字符', trigger: 'blur' },
  ],
}

// 搜索表单
const searchForm = reactive({
  contractNumber: '',
  customerName: '',
  status: '',
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
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
      hetong_zhuangtai: searchForm.status || undefined,
    }

    const response = await contractStore.fetchContracts(params)

    // 转换数据格式以适配现有的表格结构
    contractList.value = response.items.map((contract) => ({
      id: contract.id,
      contractNumber: contract.hetong_bianhao,
      customerName: contract.kehu?.gongsi_mingcheng || '未知客户',
      contractType: contract.hetong_moban?.hetong_leixing || 'unknown',
      amount: contract.hetong_jine || 0,
      startDate: contract.shengxiao_riqi ? contract.shengxiao_riqi.split('T')[0] : '',
      endDate: contract.daoqi_riqi ? contract.daoqi_riqi.split('T')[0] : '',
      status: contract.hetong_zhuangtai,
      hetong_zhuangtai: contract.hetong_zhuangtai,
      has_service_order: contract.has_service_order || false,
      createdAt: contract.created_at ? contract.created_at.replace('T', ' ').split('.')[0] : '',
      // 保留原始数据以便详细查看
      _original: contract,
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
    zixun_fuwu: 'warning',
  }
  return tags[type] || 'info'
}

// 合同类型文本
const getContractTypeText = (type: string) => {
  const texts = {
    daili_jizhang: '代理记账',
    zengzhi_fuwu: '增值服务',
    zixun_fuwu: '咨询服务',
  }
  return texts[type] || '未知'
}

// 状态标签
const getStatusTag = (status: string) => {
  const tags = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    signed: 'success',
    active: 'success',
    completed: 'primary',
    terminated: 'danger',
    voided: 'warning',
  }
  return tags[status] || 'info'
}

// 状态文本
const getStatusText = (status: string) => {
  const texts = {
    draft: '草稿',
    pending: '待审核',
    approved: '已批准',
    rejected: '已拒绝',
    signed: '已签署',
    active: '生效',
    completed: '完成',
    terminated: '终止',
    voided: '作废',
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
    status: '',
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
const handleView = async (row: any) => {
  try {
    loading.value = true
    const response = await contractApi.getDetail(row.id)
    currentContract.value = response.data || response
    viewDialogVisible.value = true
  } catch (error) {
    console.error('获取合同详情失败:', error)
    ElMessage.error('获取合同详情失败')
  } finally {
    loading.value = false
  }
}

// 编辑
const handleEdit = async (row: any) => {
  try {
    loading.value = true
    const response = await contractApi.getDetail(row.id)
    currentContract.value = response.data || response

    // 填充编辑表单
    Object.assign(editForm, {
      hetong_mingcheng: currentContract.value.hetong_mingcheng,
      hetong_zhuangtai: currentContract.value.hetong_zhuangtai,
      daoqi_riqi: currentContract.value.daoqi_riqi,
      payment_amount: currentContract.value.payment_amount || '',
    })

    editDialogVisible.value = true
  } catch (error) {
    console.error('获取合同详情失败:', error)
    ElMessage.error('获取合同详情失败')
  } finally {
    loading.value = false
  }
}

// 保存编辑
const handleSaveEdit = async () => {
  try {
    saving.value = true
    await contractApi.update(currentContract.value.id, editForm)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    getContractList()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 生成签署链接
const handleGenerateSignLink = async (row: any) => {
  try {
    loading.value = true
    const response = await contractApi.generateSignLink(row.id)
    signLinkInfo.value = response.data || response
    signLinkDialogVisible.value = true

    // 根据合同状态显示不同的提示
    if (row.hetong_zhuangtai === 'signed') {
      ElMessage.success('签署链接已生成（合同已签署，客户可查看或补充支付）')
    } else {
      ElMessage.success('签署链接生成成功')
    }
  } catch (error: any) {
    console.error('生成签署链接失败:', error)
    const errorMsg = error.response?.data?.detail || '生成签署链接失败'
    ElMessage.error(errorMsg)

    // 如果是状态问题，给出更详细的提示
    if (errorMsg.includes('状态')) {
      ElMessage.warning('提示：只有草稿、已审批、已生效或已签署状态的合同可以生成签署链接')
    }
  } finally {
    loading.value = false
  }
}

// 复制签署链接
const copySignLink = async () => {
  try {
    await navigator.clipboard.writeText(signLinkInfo.value.sign_link)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

// 在新窗口打开签署链接
const openSignLink = () => {
  window.open(signLinkInfo.value.sign_link, '_blank')
}

// 格式化过期时间
const formatExpireTime = (expireTime: string) => {
  const date = new Date(expireTime)
  return date.toLocaleString('zh-CN')
}

// 作废合同
const handleVoid = async (row: any) => {
  currentContract.value = row
  voidForm.voidReason = ''
  voidDialogVisible.value = true
}

// 确认作废
const handleConfirmVoid = async () => {
  if (!voidFormRef.value) return

  try {
    await voidFormRef.value.validate()
    voiding.value = true

    // 调用作废API
    await contractApi.voidContract(currentContract.value.id, {
      void_reason: voidForm.voidReason,
    })

    ElMessage.success('合同已作废')
    voidDialogVisible.value = false
    getContractList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('作废失败:', error)
      ElMessage.error(error.response?.data?.detail || '作废失败')
    }
  } finally {
    voiding.value = false
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除合同 "${row.hetong_bianhao}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await contractApi.delete(row.id)
    ElMessage.success('删除成功')
    getContractList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 支付状态标签
const getPaymentStatusTag = (status: string) => {
  const tags: Record<string, string> = {
    pending: 'warning',
    paid: 'success',
    failed: 'danger',
    refunded: 'info',
  }
  return tags[status] || 'info'
}

// 支付状态文本
const getPaymentStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待支付',
    paid: '已支付',
    failed: '支付失败',
    refunded: '已退款',
  }
  return texts[status] || '未知'
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

// 创建服务工单
const handleCreateServiceOrder = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要为合同 "${row.contractNumber}" 创建服务工单吗？`,
      '确认创建',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )

    loading.value = true
    const result = await serviceOrderApi.createFromContract(row.id)
    ElMessage.success('服务工单创建成功')

    // 刷新列表以更新按钮状态
    await getContractList()

    // 跳转到工单详情页
    if (result && result.data && result.data.id) {
      router.push(`/service-orders/${result.data.id}`)
    } else if (result && result.id) {
      router.push(`/service-orders/${result.id}`)
    } else {
      console.warn('工单创建成功，但无法获取工单ID，无法跳转')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('创建服务工单失败:', error)
      const errorMsg = error.response?.data?.detail || '创建服务工单失败'
      ElMessage.error(errorMsg)
    }
  } finally {
    loading.value = false
  }
}

// 查看服务工单
const handleViewServiceOrder = async (row: any) => {
  try {
    loading.value = true
    // 获取合同关联的工单
    const result = await serviceOrderApi.getByContract(row.id)

    // 检查返回数据的多种可能结构
    if (result && result.data && result.data.items && result.data.items.length > 0) {
      // 跳转到第一个工单的详情页
      router.push(`/service-orders/${result.data.items[0].id}`)
    } else if (result && result.items && result.items.length > 0) {
      // 备用：直接在result中的items
      router.push(`/service-orders/${result.items[0].id}`)
    } else {
      ElMessage.warning('该合同暂无关联工单')
    }
  } catch (error: any) {
    console.error('获取工单失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '获取工单失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
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

.contract-detail {
  max-height: 600px;
  overflow-y: auto;
}

.contract-content {
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  max-height: 400px;
  overflow-y: auto;
}

.sign-link-info {
  padding: 10px 0;
}
</style>
