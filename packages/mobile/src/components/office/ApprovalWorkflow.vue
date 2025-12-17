<template>
  <div class="approval-workflow">
    <van-cell-group v-if="records.length > 0" inset title="审批流程">
      <van-steps direction="vertical" :active="activeStep">
        <van-step v-for="(record, index) in records" :key="record.id">
          <template #inactive-icon>
            <van-icon
              :name="getStepIcon(record.jilu_zhuangtai)"
              :color="getStepColor(record.jilu_zhuangtai)"
            />
          </template>
          <template #active-icon>
            <van-icon
              :name="getStepIcon(record.jilu_zhuangtai)"
              :color="getStepColor(record.jilu_zhuangtai)"
            />
          </template>
          <template #finish-icon>
            <van-icon
              :name="getStepIcon(record.jilu_zhuangtai)"
              :color="getStepColor(record.jilu_zhuangtai)"
            />
          </template>
          <div class="step-content">
            <div class="step-title">{{ record.buzhou_mingcheng }}</div>
            <div class="step-info">
              <div class="info-item">
                <span class="label">审核人：</span>
                <span>{{ record.shenhe_ren_xingming }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态：</span>
                <van-tag :type="getStatusType(record.jilu_zhuangtai)">
                  {{ getStatusText(record.jilu_zhuangtai) }}
                </van-tag>
              </div>
              <div v-if="record.shenhe_yijian" class="info-item">
                <span class="label">审核意见：</span>
                <span>{{ record.shenhe_yijian }}</span>
              </div>
              <div class="info-item">
                <span class="label">处理时间：</span>
                <span>{{ formatDateTime(record.created_at) }}</span>
              </div>
            </div>
          </div>
        </van-step>
      </van-steps>
    </van-cell-group>
    <van-empty v-else description="暂无审批流程" :image-size="60" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { getAuditRecords, type AuditRecord } from '@/api/office'
import dayjs from 'dayjs'

interface Props {
  workflowId?: string
  records?: AuditRecord[]
  autoFetch?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  workflowId: '',
  records: () => [],
  autoFetch: true
})

const localRecords = ref<AuditRecord[]>([])

// 使用传入的records或本地加载的records
const records = computed(() => {
  return props.records.length > 0 ? props.records : localRecords.value
})

// 当前激活的步骤
const activeStep = computed(() => {
  const index = records.value.findIndex(r => r.jilu_zhuangtai === 'daichuli')
  return index >= 0 ? index : records.value.length - 1
})

// 加载审批记录
const loadRecords = async () => {
  if (!props.workflowId || !props.autoFetch) return
  
  try {
    localRecords.value = await getAuditRecords(props.workflowId)
  } catch (error) {
    console.error('Load audit records error:', error)
  }
}

// 获取步骤图标
const getStepIcon = (status: string) => {
  const map: Record<string, string> = {
    daichuli: 'clock-o',
    tongguo: 'success',
    jujue: 'cross',
    yichexiao: 'revoke'
  }
  return map[status] || 'clock-o'
}

// 获取步骤颜色
const getStepColor = (status: string) => {
  const map: Record<string, string> = {
    daichuli: '#969799',
    tongguo: '#07c160',
    jujue: '#ee0a24',
    yichexiao: '#ff976a'
  }
  return map[status] || '#969799'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daichuli: 'default',
    tongguo: 'success',
    jujue: 'danger',
    yichexiao: 'warning'
  }
  return map[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    daichuli: '待处理',
    tongguo: '已通过',
    jujue: '已拒绝',
    yichexiao: '已撤销'
  }
  return map[status] || status
}

// 格式化日期时间
const formatDateTime = (datetime: string) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

watch(() => props.workflowId, () => {
  loadRecords()
})

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.approval-workflow {
  margin-top: 12px;
}

.step-content {
  padding: 8px 0;
}

.step-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
  margin-bottom: 8px;
}

.step-info {
  font-size: 13px;
  color: #646566;
}

.info-item {
  margin-bottom: 4px;
  display: flex;
  align-items: flex-start;
}

.info-item .label {
  color: #969799;
  margin-right: 4px;
  flex-shrink: 0;
}
</style>

