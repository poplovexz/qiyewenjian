<template>
  <div class="baojia-list">
    <!-- 头部操作栏 -->
    <div class="list-header">
      <div class="header-title">
        <h3>报价记录</h3>
        <span class="count">共 {{ baojiaList.length }} 条</span>
      </div>
      <el-button type="primary" @click="handleCreate" :disabled="!canCreateBaojia">
        <el-icon><Plus /></el-icon>
        创建报价
      </el-button>
    </div>

    <!-- 报价列表 -->
    <div v-loading="loading" class="baojia-content">
      <div v-if="baojiaList.length === 0" class="empty-state">
        <el-empty description="暂无报价记录">
          <el-button type="primary" @click="handleCreate">创建第一个报价</el-button>
        </el-empty>
      </div>

      <div v-else class="baojia-cards">
        <div
          v-for="baojia in baojiaList"
          :key="baojia.id"
          class="baojia-card"
          :class="{ expired: baojia.is_expired }"
        >
          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="baojia-info">
              <div class="baojia-code">{{ baojia.baojia_bianma }}</div>
              <div class="baojia-status">
                <el-tag :type="getStatusTagType(baojia.baojia_zhuangtai)" size="small">
                  {{ getStatusText(baojia.baojia_zhuangtai) }}
                </el-tag>
                <el-tag v-if="baojia.is_expired" type="danger" size="small"> 已过期 </el-tag>
              </div>
            </div>
            <div class="card-actions">
              <el-dropdown @command="(command) => handleAction(command, baojia)">
                <el-button type="text" size="small">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="view">查看详情</el-dropdown-item>
                    <el-dropdown-item command="edit" :disabled="baojia.is_expired">
                      编辑报价
                    </el-dropdown-item>
                    <el-dropdown-item command="copy"> 复制报价 </el-dropdown-item>
                    <el-dropdown-item command="delete" divided> 删除报价 </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <!-- 卡片内容 -->
          <div class="card-content">
            <!-- 金额信息 -->
            <div class="amount-section">
              <div class="total-amount">
                <span class="amount-label">报价总额</span>
                <span class="amount-value">¥{{ baojia.zongji_jine.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 服务项目 -->
            <div class="xiangmu-section">
              <div class="section-title">服务项目 ({{ baojia.xiangmu_list.length }}项)</div>
              <div class="xiangmu-list">
                <div
                  v-for="xiangmu in baojia.xiangmu_list.slice(0, 3)"
                  :key="xiangmu.id"
                  class="xiangmu-item"
                >
                  <span class="xiangmu-name">{{ xiangmu.xiangmu_mingcheng }}</span>
                  <span class="xiangmu-price">¥{{ xiangmu.xiaoji.toFixed(2) }}</span>
                </div>
                <div v-if="baojia.xiangmu_list.length > 3" class="xiangmu-more">
                  还有 {{ baojia.xiangmu_list.length - 3 }} 项...
                </div>
              </div>
            </div>

            <!-- 时间信息 -->
            <div class="time-section">
              <div class="time-item">
                <el-icon><Calendar /></el-icon>
                <span>创建时间：{{ formatDate(baojia.created_at) }}</span>
              </div>
              <div class="time-item">
                <el-icon><Clock /></el-icon>
                <span>有效期至：{{ formatDate(baojia.youxiao_qi) }}</span>
              </div>
            </div>

            <!-- 备注 -->
            <div v-if="baojia.beizhu" class="beizhu-section">
              <div class="section-title">备注</div>
              <div class="beizhu-content">{{ baojia.beizhu }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 报价表单弹窗 -->
    <XiansuoBaojiaForm
      v-model:visible="formVisible"
      :mode="formMode"
      :xiansuo="xiansuo"
      :baojia="currentBaojia"
      @success="handleFormSuccess"
    />

    <!-- 报价详情弹窗 -->
    <XiansuoBaojiaDetail v-model:visible="detailVisible" :baojia-id="currentBaojiaId" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled, Calendar, Clock } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import XiansuoBaojiaForm from './XiansuoBaojiaForm.vue'
import XiansuoBaojiaDetail from './XiansuoBaojiaDetail.vue'
import type { XiansuoBaojia, Xiansuo } from '@/types/xiansuo'

// Props
interface Props {
  xiansuo: Xiansuo
}

const props = defineProps<Props>()

// Store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const loading = ref(false)
const formVisible = ref(false)
const detailVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const currentBaojia = ref<XiansuoBaojia | null>(null)
const currentBaojiaId = ref('')
const baojiaList = ref<XiansuoBaojia[]>([])

const canCreateBaojia = computed(() => {
  return !baojiaList.value.some((b) => !b.is_expired && b.baojia_zhuangtai !== 'rejected')
})

// 方法
const loadBaojiaList = async () => {
  try {
    loading.value = true
    const list = await xiansuoStore.fetchBaojiaByXiansuo(props.xiansuo.id)
    baojiaList.value = list
  } catch (error) {
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  formMode.value = 'create'
  currentBaojia.value = null
  formVisible.value = true
}

const handleAction = async (command: string, baojia: XiansuoBaojia) => {
  switch (command) {
    case 'view':
      currentBaojiaId.value = baojia.id
      detailVisible.value = true
      break
    case 'edit':
      formMode.value = 'edit'
      currentBaojia.value = baojia
      formVisible.value = true
      break
    case 'copy':
      await handleCopy(baojia)
      break
    case 'delete':
      await handleDelete(baojia)
      break
  }
}

const handleCopy = async (baojia: XiansuoBaojia) => {
  try {
    await ElMessageBox.confirm('确定要复制这个报价吗？将创建一个新的报价。', '确认复制', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info',
    })

    const copyData = {
      xiansuo_id: baojia.xiansuo_id,
      baojia_mingcheng: `${baojia.baojia_mingcheng} - 副本`,
      youxiao_qi: baojia.youxiao_qi,
      beizhu: baojia.beizhu,
      xiangmu_list: baojia.xiangmu_list.map((item, index) => ({
        chanpin_xiangmu_id: item.chanpin_xiangmu_id,
        xiangmu_mingcheng: item.xiangmu_mingcheng,
        shuliang: item.shuliang,
        danjia: item.danjia,
        danwei: item.danwei,
        paixu: index,
        beizhu: item.beizhu,
      })),
    }

    await xiansuoStore.createBaojia(copyData)
    await loadBaojiaList()
    ElMessage.success('报价复制成功')
  } catch (error) {
    if (error !== 'cancel') {
    }
  }
}

const handleDelete = async (baojia: XiansuoBaojia) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报价"${baojia.baojia_bianma}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await xiansuoStore.deleteBaojia(baojia.xiansuo_id, baojia.id)
    await loadBaojiaList()
  } catch (error) {
    if (error !== 'cancel') {
    }
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  void loadBaojiaList()
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    sent: 'warning',
    accepted: 'success',
    rejected: 'danger',
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    sent: '已发送',
    accepted: '已接受',
    rejected: '已拒绝',
  }
  return texts[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 监听器
watch(
  () => props.xiansuo.id,
  (id) => {
    if (id) {
      void loadBaojiaList()
    }
  },
  { immediate: true }
)

// 生命周期
onMounted(() => {
  if (props.xiansuo.id) {
    void loadBaojiaList()
  }
})
</script>

<style scoped>
.baojia-list {
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-title h3 {
  margin: 0;
  color: #303133;
}

.count {
  color: #909399;
  font-size: 14px;
  margin-left: 8px;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.baojia-cards {
  display: grid;
  gap: 20px;
}

.baojia-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
}

.baojia-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.baojia-card.expired {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.baojia-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.baojia-code {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.baojia-status {
  display: flex;
  gap: 8px;
}

.amount-section {
  margin-bottom: 16px;
}

.total-amount {
  display: flex;
  align-items: center;
  gap: 12px;
}

.amount-label {
  color: #606266;
  font-size: 14px;
}

.amount-value {
  color: #e6a23c;
  font-weight: 700;
  font-size: 20px;
}

.xiangmu-section {
  margin-bottom: 16px;
}

.section-title {
  color: #303133;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
}

.xiangmu-list {
  space-y: 4px;
}

.xiangmu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 14px;
}

.xiangmu-name {
  color: #606266;
}

.xiangmu-price {
  color: #303133;
  font-weight: 600;
}

.xiangmu-more {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

.time-section {
  margin-bottom: 16px;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 4px;
}

.beizhu-section {
  margin-bottom: 16px;
}

.beizhu-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}
</style>
