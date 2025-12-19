<template>
  <el-dialog
    v-model="dialogVisible"
    title="报价详情"
    width="800px"
    :before-close="handleClose"
  >
    <div v-loading="loading" class="baojia-detail">
      <div v-if="baojia" class="detail-content">
        <!-- 基本信息 -->
        <el-card class="info-section" shadow="never">
          <template #header>
            <span class="section-title">基本信息</span>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="报价编码">
              {{ baojia.baojia_bianma }}
            </el-descriptions-item>
            <el-descriptions-item label="报价状态">
              <el-tag :type="getStatusTagType(baojia.baojia_zhuangtai)">
                {{ getStatusText(baojia.baojia_zhuangtai) }}
              </el-tag>
              <el-tag v-if="baojia.is_expired" type="danger" style="margin-left: 8px;">
                已过期
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="报价总额">
              <span class="total-amount">¥{{ baojia.zongji_jine.toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="有效期">
              {{ formatDate(baojia.youxiao_qi) }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(baojia.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDateTime(baojia.updated_at) }}
            </el-descriptions-item>
            <el-descriptions-item v-if="baojia.beizhu" label="备注" :span="2">
              {{ baojia.beizhu }}
            </el-descriptions-item>
            <el-descriptions-item v-if="baojia.xiansuo_info" label="客户信息" :span="2">
              <div class="customer-info">
                <div class="company">{{ baojia.xiansuo_info.gongsi_mingcheng }}</div>
                <div class="contact">
                  <span>{{ baojia.xiansuo_info.lianxi_ren }}</span>
                  <span v-if="baojia.xiansuo_info.lianxi_dianhua"> · {{ baojia.xiansuo_info.lianxi_dianhua }}</span>
                  <span v-if="baojia.xiansuo_info.lianxi_youxiang"> · {{ baojia.xiansuo_info.lianxi_youxiang }}</span>
                </div>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 服务项目明细 -->
        <el-card class="xiangmu-section" shadow="never">
          <template #header>
            <span class="section-title">服务项目明细</span>
          </template>
          
          <el-table :data="baojia.xiangmu_list" border>
            <el-table-column prop="xiangmu_mingcheng" label="服务名称" min-width="200">
              <template #default="{ row }">
                <div class="service-name">
                  <div class="name">{{ row.xiangmu_mingcheng }}</div>
                  <div v-if="row.danwei" class="desc">单位：{{ row.danwei }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="shuliang" label="数量" width="100" align="center" />
            <el-table-column prop="danjia" label="单价" width="120" align="right">
              <template #default="{ row }">
                ¥{{ row.danjia.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="xiaoji" label="小计" width="120" align="right">
              <template #default="{ row }">
                <span class="xiaoji-amount">¥{{ row.xiaoji.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="beizhu" label="备注" min-width="150">
              <template #default="{ row }">
                <span v-if="row.beizhu">{{ row.beizhu }}</span>
                <span v-else class="no-remark">-</span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 合计行 -->
          <div class="total-row">
            <div class="total-label">合计金额：</div>
            <div class="total-value">¥{{ baojia.zongji_jine.toFixed(2) }}</div>
          </div>
        </el-card>

        <!-- 操作记录 -->
        <el-card v-if="showOperationLog" class="operation-section" shadow="never">
          <template #header>
            <span class="section-title">操作记录</span>
          </template>
          
          <el-timeline>
            <el-timeline-item
              v-for="(log, index) in operationLogs"
              :key="index"
              :timestamp="formatDateTime(log.created_at)"
              placement="top"
            >
              <div class="log-content">
                <div class="log-action">{{ log.action }}</div>
                <div class="log-operator">操作人：{{ log.operator }}</div>
                <div v-if="log.remark" class="log-remark">{{ log.remark }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button 
          v-if="baojia && !baojia.is_expired" 
          type="primary" 
          @click="handleEdit"
        >
          编辑报价
        </el-button>
        <el-button type="success" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出/打印
        </el-button>
        <el-button type="info" @click="handleCopyLink">
          复制分享链接
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import type { XiansuoBaojiaDetail } from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  baojiaId: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  edit: [baojia: XiansuoBaojia]
}>()

// Store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const loading = ref(false)
const baojia = ref<XiansuoBaojiaDetail | null>(null)
const showOperationLog = ref(false)
const operationLogs = ref<any[]>([])

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 方法
const loadBaojiaDetail = async () => {
  if (!props.baojiaId) return

  try {
    loading.value = true
    baojia.value = await xiansuoStore.getBaojiaDetailWithXiansuo(props.baojiaId)
  } catch (error) {
    ElMessage.error('加载报价详情失败')
  } finally {
    loading.value = false
  }
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    sent: 'warning',
    accepted: 'success',
    rejected: 'danger',
    expired: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    sent: '已发送',
    accepted: '已接受',
    rejected: '已拒绝',
    expired: '已过期'
  }
  return texts[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const handleEdit = () => {
  if (baojia.value) {
    emit('edit', baojia.value)
  }
}

const handleExport = async () => {
  if (!baojia.value) return
  window.open(`/quote-preview/${baojia.value.id}`, '_blank')
}

const handleCopyLink = async () => {
  if (!baojia.value) return
  try {
    const payload = encodeURIComponent(btoa(unescape(encodeURIComponent(JSON.stringify(baojia.value)))))
    const link = `${window.location.origin}/quote-preview/${baojia.value.id}?payload=${payload}`
    await navigator.clipboard.writeText(link)
    ElMessage.success('分享链接已复制，可发送给客户查看报价')
  } catch (error) {
    ElMessage.error('复制分享链接失败')
  }
}

const handleClose = () => {
  emit('update:visible', false)
  baojia.value = null
}

// 监听器
watch(() => props.visible, (visible) => {
  if (visible && props.baojiaId) {
    loadBaojiaDetail()
  }
})

watch(() => props.baojiaId, (baojiaId) => {
  if (props.visible && baojiaId) {
    loadBaojiaDetail()
  }
})
</script>

<style scoped>
.baojia-detail {
  min-height: 400px;
}

.info-section,
.xiangmu-section,
.operation-section {
  margin-bottom: 20px;
}

.info-section :deep(.el-card__body),
.xiangmu-section :deep(.el-card__body),
.operation-section :deep(.el-card__body) {
  padding: 20px;
}

.section-title {
  font-weight: 600;
  color: #303133;
}

.total-amount {
  color: #E6A23C;
  font-weight: 700;
  font-size: 18px;
}

.service-name .name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.service-name .unit {
  color: #909399;
  font-size: 12px;
}

.xiaoji-amount {
  color: #E6A23C;
  font-weight: 600;
}

.no-remark {
  color: #C0C4CC;
}

.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
  gap: 16px;
}

.total-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.total-value {
  font-size: 20px;
  font-weight: 700;
  color: #E6A23C;
}

.customer-info .company {
  font-weight: 600;
  color: #303133;
}

.customer-info .contact {
  margin-top: 4px;
  color: #606266;
  font-size: 14px;
}

.log-content {
  padding: 8px 0;
}

.log-action {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.log-operator {
  color: #606266;
  font-size: 14px;
  margin-bottom: 4px;
}

.log-remark {
  color: #909399;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
