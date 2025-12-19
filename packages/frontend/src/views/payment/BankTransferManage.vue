<template>
  <div class="bank-transfer-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span>银行汇款管理</span>
            <el-tag v-if="pendingCount > 0" type="warning" effect="dark" class="pending-badge">
              待上传凭证：{{ pendingCount }} 个
            </el-tag>
          </div>
          <el-button type="primary" @click="loadData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="queryParams" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="全部状态" clearable>
            <el-option label="待上传凭证" value="waiting_voucher" />
            <el-option label="待审核" value="pending_audit" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="danju_bianhao" label="单据编号" width="180" />
        <el-table-column prop="huikuan_jine" label="汇款金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.huikuan_jine }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="huikuan_ren" label="汇款人" width="120" />
        <el-table-column prop="huikuan_yinhang" label="汇款银行" width="150" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="shenhe_zhuangtai" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.shenhe_zhuangtai)">
              {{ getStatusText(row.shenhe_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="beizhu" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.shenhe_zhuangtai === 'waiting_voucher'"
              type="primary"
              size="small"
              @click="handleUploadVoucher(row)"
            >
              上传凭证
            </el-button>
            <el-button v-else type="info" size="small" @click="handleViewDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        class="pagination"
      />
    </el-card>

    <!-- 上传凭证对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传汇款凭证"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="120px">
        <el-form-item label="单据编号">
          <el-input v-model="currentDanju.danju_bianhao" disabled />
        </el-form-item>
        <el-form-item label="汇款金额">
          <el-input v-model="currentDanju.huikuan_jine" disabled>
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>

        <el-divider content-position="left">汇款信息</el-divider>

        <el-form-item label="汇款人姓名" prop="huikuan_ren">
          <el-input v-model="uploadForm.huikuan_ren" placeholder="请填写汇款人姓名" clearable />
        </el-form-item>

        <el-form-item label="汇款银行" prop="huikuan_yinhang">
          <el-input v-model="uploadForm.huikuan_yinhang" placeholder="请填写汇款银行" clearable />
        </el-form-item>

        <el-form-item label="汇款账户">
          <el-input
            v-model="uploadForm.huikuan_zhanghu"
            placeholder="请填写汇款账户（选填）"
            clearable
          />
        </el-form-item>

        <el-form-item label="汇款日期" prop="huikuan_riqi">
          <el-date-picker
            v-model="uploadForm.huikuan_riqi"
            type="datetime"
            placeholder="请选择汇款日期"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="(time) => time.getTime() > Date.now()"
          />
        </el-form-item>

        <el-divider content-position="left">汇款凭证</el-divider>

        <el-form-item label="凭证图片" prop="voucher_url" required>
          <el-upload
            class="voucher-uploader"
            :action="uploadAction"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept="image/*"
          >
            <img
              v-if="uploadForm.voucher_url"
              :src="uploadForm.voucher_url"
              class="voucher-image"
            />
            <el-icon v-else class="voucher-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持 JPG、PNG 格式，大小不超过 5MB</div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="uploadForm.beizhu"
            type="textarea"
            :rows="3"
            placeholder="请填写备注信息（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitVoucher" :loading="submitting">
          提交
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="汇款单据详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单据编号">{{
          currentDanju.danju_bianhao
        }}</el-descriptions-item>
        <el-descriptions-item label="汇款金额">
          <span class="amount">¥{{ currentDanju.huikuan_jine }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="汇款人">{{ currentDanju.huikuan_ren }}</el-descriptions-item>
        <el-descriptions-item label="汇款银行">{{
          currentDanju.huikuan_yinhang
        }}</el-descriptions-item>
        <el-descriptions-item label="汇款账号">{{
          currentDanju.huikuan_zhanghu
        }}</el-descriptions-item>
        <el-descriptions-item label="汇款日期">
          {{ formatDateTime(currentDanju.huikuan_riqi) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentDanju.shenhe_zhuangtai)">
            {{ getStatusText(currentDanju.shenhe_zhuangtai) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(currentDanju.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="凭证图片" :span="2" v-if="currentDanju.danju_lujing">
          <el-image
            :src="getImageUrl(currentDanju.danju_lujing)"
            :preview-src-list="[getImageUrl(currentDanju.danju_lujing)]"
            fit="contain"
            style="width: 200px; height: 200px"
          />
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentDanju.beizhu || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="审核意见" :span="2" v-if="currentDanju.shenhe_yijian">
          {{ currentDanju.shenhe_yijian }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'
import { request } from '@/utils/request'
import { useAuthStore } from '@/stores/modules/auth'

// 银行汇款单据类型
interface BankTransferDanju {
  id: string
  danju_bianhao: string
  jine: number
  shenhe_zhuangtai: string
  voucher_url?: string
  huikuan_ren?: string
  huikuan_yinhang?: string
  huikuan_zhanghu?: string
  huikuan_riqi?: string
  beizhu?: string
}

// 上传响应类型
interface UploadResponse {
  data?: { url: string }
  url?: string
}

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const tableData = ref<BankTransferDanju[]>([])
const total = ref(0)
const uploadDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const uploadFormRef = ref()

const queryParams = reactive({
  page: 1,
  size: 20,
  status: 'waiting_voucher', // 默认筛选"待上传凭证"状态
})

// 待处理数量
const pendingCount = ref(0)

const currentDanju = ref<BankTransferDanju | Record<string, unknown>>({})

const uploadForm = reactive({
  voucher_url: '',
  beizhu: '',
  // 汇款信息字段
  huikuan_ren: '',
  huikuan_yinhang: '',
  huikuan_zhanghu: '',
  huikuan_riqi: '',
})

const uploadRules = {
  voucher_url: [{ required: true, message: '请上传凭证图片', trigger: 'change' }],
  huikuan_ren: [{ required: true, message: '请填写汇款人姓名', trigger: 'blur' }],
  huikuan_yinhang: [{ required: true, message: '请填写汇款银行', trigger: 'blur' }],
  huikuan_riqi: [{ required: true, message: '请选择汇款日期', trigger: 'change' }],
}

// 上传配置
const uploadAction = `${import.meta.env.VITE_API_BASE_URL}/upload/image`
const uploadHeaders = {
  Authorization: `Bearer ${authStore.accessToken}`,
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const params: Record<string, string | number> = {
      page: queryParams.page,
      size: queryParams.size,
    }
    if (queryParams.status) {
      params.shenhe_zhuangtai = queryParams.status
    }

    const response = await request.get('/bank-transfers/', { params })
    tableData.value = response.data?.items || response.items || []
    total.value = response.data?.total || response.total || 0

    // 加载待处理数量
    await loadPendingCount()
  } catch (error: unknown) {
    const axiosError = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(axiosError.response?.data?.detail || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载待处理数量
const loadPendingCount = async () => {
  try {
    const response = await request.get('/bank-transfers/', {
      params: {
        page: 1,
        size: 1,
        shenhe_zhuangtai: 'waiting_voucher',
      },
    })
    pendingCount.value = response.data?.total || response.total || 0
  } catch (error) {}
}

// 查询
const handleSearch = () => {
  queryParams.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  queryParams.status = 'waiting_voucher' // 重置为默认筛选"待上传凭证"
  queryParams.page = 1
  loadData()
}

// 上传凭证
const handleUploadVoucher = (row: BankTransferDanju) => {
  currentDanju.value = { ...row }
  uploadForm.voucher_url = ''
  uploadForm.beizhu = ''
  uploadForm.huikuan_ren = ''
  uploadForm.huikuan_yinhang = ''
  uploadForm.huikuan_zhanghu = ''
  uploadForm.huikuan_riqi = ''
  uploadDialogVisible.value = true
}

// 查看详情
const handleViewDetail = (row: BankTransferDanju) => {
  currentDanju.value = { ...row }
  detailDialogVisible.value = true
}

// 上传前检查
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 上传成功
const handleUploadSuccess = (response: UploadResponse) => {
  uploadForm.voucher_url = response.data?.url || response.url || ''
  ElMessage.success('图片上传成功')
}

// 上传失败
const handleUploadError = () => {
  ElMessage.error('图片上传失败')
}

// 提交凭证
const handleSubmitVoucher = async () => {
  try {
    await uploadFormRef.value.validate()

    submitting.value = true
    await request.post(`/bank-transfers/${currentDanju.value.id}/upload-voucher`, {
      voucher_url: uploadForm.voucher_url,
      beizhu: uploadForm.beizhu,
      huikuan_ren: uploadForm.huikuan_ren,
      huikuan_yinhang: uploadForm.huikuan_yinhang,
      huikuan_zhanghu: uploadForm.huikuan_zhanghu,
      huikuan_riqi: uploadForm.huikuan_riqi,
    })

    ElMessage.success('凭证上传成功，汇款信息已更新，已提交财务审核')
    uploadDialogVisible.value = false
    loadData()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const axiosError = error as { response?: { data?: { detail?: string } } }
      ElMessage.error(axiosError.response?.data?.detail || '提交失败')
    }
  } finally {
    submitting.value = false
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    waiting_voucher: 'warning',
    pending_audit: 'info',
    approved: 'success',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    waiting_voucher: '待上传凭证',
    pending_audit: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return textMap[status] || status
}

// 获取完整图片URL
const getImageUrl = (url: string) => {
  if (!url) return ''
  // 如果已经是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  // 否则加上后端服务器地址
  return `http://localhost:8000${url}`
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.bank-transfer-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .pending-badge {
    font-size: 13px;
    padding: 6px 12px;
    animation: pulse 2s ease-in-out infinite;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.filter-form {
  margin-bottom: 20px;
}

.amount {
  color: #f56c6c;
  font-weight: bold;
  font-size: 14px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.voucher-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
    }
  }
}

.voucher-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.voucher-image {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: contain;
}

.upload-tip {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}
</style>
