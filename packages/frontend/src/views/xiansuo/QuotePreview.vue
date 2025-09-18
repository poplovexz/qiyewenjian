<template>
  <div class="quote-preview" v-loading="loading">
    <div v-if="error" class="error">
      <p>{{ error }}</p>
      <el-button type="primary" @click="reload">重新加载</el-button>
    </div>
    <div v-else-if="baojia" class="quote-container">
      <header class="quote-header">
        <div>
          <h1>{{ baojia.baojia_mingcheng }}</h1>
          <p class="quote-code">报价编号：{{ baojia.baojia_bianma }}</p>
        </div>
        <div class="quote-actions">
          <!-- 报价确认操作按钮 -->
          <div v-if="showConfirmActions" class="confirm-actions">
            <el-button
              type="success"
              @click="confirmQuote"
              :loading="confirmLoading"
              :disabled="!canConfirm"
            >
              确认报价
            </el-button>
            <el-button
              type="danger"
              @click="rejectQuote"
              :loading="rejectLoading"
              :disabled="!canReject"
            >
              拒绝报价
            </el-button>
          </div>
          <el-button type="primary" @click="printQuote" :icon="Printer">打印/导出PDF</el-button>
        </div>
      </header>

      <section class="quote-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户公司" :span="2">
            <div class="customer-info">
              <div class="company">{{ baojia.xiansuo_info.gongsi_mingcheng }}</div>
              <div class="contact">
                <span>{{ baojia.xiansuo_info.lianxi_ren }}</span>
                <span v-if="baojia.xiansuo_info.lianxi_dianhua"> · {{ baojia.xiansuo_info.lianxi_dianhua }}</span>
                <span v-if="baojia.xiansuo_info.lianxi_youxiang"> · {{ baojia.xiansuo_info.lianxi_youxiang }}</span>
              </div>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="报价总额">
            <span class="highlight">¥{{ formatAmount(baojia.zongji_jine) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="有效期至">
            {{ formatDate(baojia.youxiao_qi) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(baojia.baojia_zhuangtai)">
              {{ getStatusText(baojia.baojia_zhuangtai) }}
            </el-tag>
            <el-tag v-if="baojia.is_expired" type="danger" class="ml-8">已过期</el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="baojia.beizhu" label="备注" :span="2">
            {{ baojia.beizhu }}
          </el-descriptions-item>
        </el-descriptions>
      </section>

      <section class="quote-items">
        <h2>服务项目明细</h2>
        <el-table :data="baojia.xiangmu_list" border>
          <el-table-column label="服务名称" min-width="200">
            <template #default="{ row }">
              <div class="service-name">
                <div class="name">{{ row.xiangmu_mingcheng }}</div>
                <div v-if="row.danwei" class="unit">单位：{{ row.danwei }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="shuliang" label="数量" width="100" align="center" />
          <el-table-column label="单价" width="120" align="right">
            <template #default="{ row }">
              ¥{{ formatAmount(row.danjia) }}
            </template>
          </el-table-column>
          <el-table-column label="小计" width="140" align="right">
            <template #default="{ row }">
              <span class="highlight">¥{{ formatAmount(row.xiaoji) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="beizhu" label="备注" min-width="160">
            <template #default="{ row }">
              <span>{{ row.beizhu || '-' }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div class="total-row">
          <span>合计：</span>
          <span class="highlight">¥{{ formatAmount(baojia.zongji_jine) }}</span>
        </div>
      </section>

      <footer class="quote-footer">
        <p>如需确认此报价，请联系您的专属顾问或回复此邮件。</p>
        <p>生成时间：{{ formatDateTime(baojia.created_at) }}</p>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Printer } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import { useAuthStore } from '@/stores/modules/auth'
import type { XiansuoBaojiaDetail } from '@/types/xiansuo'

const route = useRoute()
const router = useRouter()
const xiansuoStore = useXiansuoStore()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref<string | null>(null)
const baojia = ref<XiansuoBaojiaDetail | null>(null)

// 确认/拒绝操作状态
const confirmLoading = ref(false)
const rejectLoading = ref(false)

const normalizeBaojia = (detail: XiansuoBaojiaDetail): XiansuoBaojiaDetail => {
  return {
    ...detail,
    zongji_jine: Number(detail.zongji_jine),
    xiangmu_list: detail.xiangmu_list.map(item => ({
      ...item,
      shuliang: Number(item.shuliang),
      danjia: Number(item.danjia),
      xiaoji: Number(item.xiaoji)
    }))
  }
}

const formatAmount = (value?: number | string) => {
  const num = Number(value ?? 0)
  return Number.isFinite(num) ? num.toFixed(2) : '0.00'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    draft: 'info',
    sent: 'warning',
    accepted: 'success',
    rejected: 'danger',
    expired: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    sent: '已发送',
    accepted: '已接受',
    rejected: '已拒绝',
    expired: '已过期'
  }
  return map[status] || status
}

// 计算属性：是否显示确认操作按钮
const showConfirmActions = computed(() => {
  // 只有已登录用户才能看到确认操作按钮
  return authStore.isAuthenticated && baojia.value && !route.query.payload
})

// 计算属性：是否可以确认
const canConfirm = computed(() => {
  if (!baojia.value) return false
  // 只有草稿或已发送状态的未过期报价可以确认
  return ['draft', 'sent'].includes(baojia.value.baojia_zhuangtai) && !baojia.value.is_expired
})

// 计算属性：是否可以拒绝
const canReject = computed(() => {
  if (!baojia.value) return false
  // 只有草稿或已发送状态的报价可以拒绝（即使过期也可以拒绝）
  return ['draft', 'sent'].includes(baojia.value.baojia_zhuangtai)
})

const fetchDetail = async () => {
  const id = route.params.id as string
  if (!id) {
    error.value = '缺少报价ID'
    return
  }
  loading.value = true
  error.value = null
  const payload = route.query.payload as string | undefined
  if (payload) {
    try {
    const decoded = JSON.parse(decodeURIComponent(escape(atob(payload)))) as XiansuoBaojiaDetail
    baojia.value = normalizeBaojia(decoded)
  } catch (errorDecode) {
    console.error('解析分享数据失败:', errorDecode)
    error.value = '分享链接无效或已过期。'
    } finally {
      loading.value = false
    }
    return
  }

  try {
    const detail = await xiansuoStore.getBaojiaDetailWithXiansuo(id)
    baojia.value = normalizeBaojia(detail)
  } catch (err: any) {
    if (err?.response?.status === 401) {
      error.value = '需要登录后才能查看此报价。'
    } else if (err?.response?.status === 404) {
      error.value = '未找到该报价。'
    } else {
      error.value = '加载报价详情失败，请稍后重试。'
    }
    console.error('加载报价详情失败:', err)
  } finally {
    loading.value = false
  }
}

const reload = () => {
  void fetchDetail()
}

const printQuote = () => {
  window.print()
  ElMessage.success('正在调用浏览器打印功能，可选择保存为PDF。')
}

// 确认报价
const confirmQuote = async () => {
  if (!baojia.value) return

  try {
    await ElMessageBox.confirm(
      '确认此报价后，将自动触发合同生成流程。确定要确认这个报价吗？',
      '确认报价',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    confirmLoading.value = true
    await xiansuoStore.confirmBaojia(baojia.value.id)

    // 重新获取报价详情以更新状态
    await fetchDetail()

    ElMessage.success('报价确认成功！')

    // 询问是否生成合同
    try {
      await ElMessageBox.confirm(
        '报价已确认成功！是否立即基于此报价生成合同？',
        '生成合同',
        {
          confirmButtonText: '生成合同',
          cancelButtonText: '稍后处理',
          type: 'info'
        }
      )

      // 跳转到合同创建页面，并预填报价信息
      router.push({
        path: '/contracts/create',
        query: { baojia_id: baojia.value.id }
      })
    } catch (error) {
      // 用户选择稍后处理，不做任何操作
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('确认报价失败:', error)
      ElMessage.error(error.message || '确认报价失败')
    }
  } finally {
    confirmLoading.value = false
  }
}

// 拒绝报价
const rejectQuote = async () => {
  if (!baojia.value) return

  try {
    await ElMessageBox.confirm(
      '确定要拒绝这个报价吗？拒绝后可以重新创建新的报价。',
      '拒绝报价',
      {
        confirmButtonText: '拒绝',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    rejectLoading.value = true
    await xiansuoStore.rejectBaojia(baojia.value.id)

    // 重新获取报价详情以更新状态
    await fetchDetail()

    ElMessage.success('报价已拒绝')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('拒绝报价失败:', error)
      ElMessage.error(error.message || '拒绝报价失败')
    }
  } finally {
    rejectLoading.value = false
  }
}

onMounted(() => {
  void fetchDetail()
})
</script>

<style scoped>
.quote-preview {
  min-height: 100vh;
  padding: 40px;
  background: #f5f7fa;
}

.quote-container {
  max-width: 960px;
  margin: 0 auto;
  background: #fff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
}

.quote-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.quote-header h1 {
  margin: 0;
  font-size: 28px;
  color: #303133;
}

.quote-code {
  color: #909399;
  margin-top: 8px;
}

.quote-info {
  margin-bottom: 24px;
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

.quote-items {
  margin-top: 24px;
}

.quote-items h2 {
  font-size: 20px;
  margin-bottom: 16px;
}

.service-name .name {
  font-weight: 600;
  color: #303133;
}

.service-name .unit {
  color: #909399;
  font-size: 12px;
}

.highlight {
  color: #E6A23C;
  font-weight: 700;
}

.total-row {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  font-size: 18px;
}

.quote-footer {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  color: #606266;
  font-size: 14px;
}

.error {
  max-width: 480px;
  margin: 120px auto;
  background: #fff;
  padding: 32px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.error p {
  margin-bottom: 16px;
  color: #f56c6c;
}

.ml-8 {
  margin-left: 8px;
}

@media print {
  .quote-preview {
    background: #fff;
    padding: 0;
  }
  .quote-container {
    box-shadow: none;
    margin: 0;
    border: none;
  }
  .quote-actions {
    display: none;
  }
}
</style>
