<template>
  <div class="approval-workflow">
    <div v-if="workflowId && records.length > 0" class="workflow-content">
      <el-timeline>
        <el-timeline-item
          v-for="record in records"
          :key="record.id"
          :timestamp="formatDateTime(record.created_at)"
          :type="getTimelineType(record.jilu_zhuangtai)"
          placement="top"
        >
          <el-card class="step-card">
            <div class="step-header">
              <h4>{{ record.buzhou_mingcheng }}</h4>
              <el-tag :type="getStatusType(record.jilu_zhuangtai)" size="small">
                {{ getStatusLabel(record.jilu_zhuangtai) }}
              </el-tag>
            </div>
            
            <div class="step-content">
              <p class="auditor">
                <span class="label">审核人：</span>
                <span>{{ record.shenhe_ren_xingming || '待处理' }}</span>
              </p>
              
              <p v-if="record.shenhe_yijian" class="opinion">
                <span class="label">审核意见：</span>
                <span>{{ record.shenhe_yijian }}</span>
              </p>
              
              <p v-if="record.shenhe_shijian" class="time">
                <span class="label">处理时间：</span>
                <span>{{ formatDateTime(record.shenhe_shijian) }}</span>
              </p>
              
              <p v-else-if="record.qiwang_shijian" class="time">
                <span class="label">期望处理时间：</span>
                <span>{{ formatDateTime(record.qiwang_shijian) }}</span>
              </p>
              
              <div v-if="record.fujian_lujing" class="attachments">
                <span class="label">附件：</span>
                <el-link :href="record.fujian_lujing" target="_blank" rel="noopener noreferrer" type="primary">
                  <el-icon><Document /></el-icon>
                  {{ record.fujian_miaoshu || '查看附件' }}
                </el-link>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
    
    <el-empty v-else description="暂无审批流程" :image-size="80" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { auditRecordApi } from '@/api/modules/audit'

interface Props {
  workflowId?: string
  records?: any[]
  autoFetch?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  workflowId: '',
  records: () => [],
  autoFetch: true
})

const loading = ref(false)
const records = ref<any[]>([])

// 监听 props.records 变化
watch(() => props.records, (newRecords) => {
  if (newRecords && newRecords.length > 0) {
    records.value = newRecords
  }
}, { immediate: true })

// 监听 workflowId 变化
watch(() => props.workflowId, (newId) => {
  if (newId && props.autoFetch) {
    fetchRecords()
  }
}, { immediate: true })

// 获取审批记录
const fetchRecords = async () => {
  if (!props.workflowId) return
  
  loading.value = true
  try {
    const response = await auditRecordApi.getByWorkflow(props.workflowId)
    records.value = response.data || []
  } catch (error) {
    console.error('获取审批记录失败:', error)
    ElMessage.error('获取审批记录失败')
  } finally {
    loading.value = false
  }
}

// 辅助函数
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    daichuli: '待处理',
    chulizhong: '处理中',
    tongguo: '已通过',
    jujue: '已拒绝',
    zhuanfa: '已转发',
    tiaoguo: '已跳过'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daichuli: 'info',
    chulizhong: 'warning',
    tongguo: 'success',
    jujue: 'danger',
    zhuanfa: 'primary',
    tiaoguo: 'info'
  }
  return map[status] || 'info'
}

const getTimelineType = (status: string) => {
  const map: Record<string, any> = {
    daichuli: 'primary',
    chulizhong: 'warning',
    tongguo: 'success',
    jujue: 'danger',
    zhuanfa: 'primary',
    tiaoguo: 'info'
  }
  return map[status] || 'primary'
}

const formatDateTime = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  if (props.workflowId && props.autoFetch && props.records.length === 0) {
    fetchRecords()
  }
})
</script>

<style scoped lang="scss">
.approval-workflow {
  .workflow-content {
    margin-top: 20px;
  }

  .step-card {
    .step-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      h4 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }

    .step-content {
      p {
        margin: 8px 0;
        line-height: 1.6;
        color: #606266;

        .label {
          font-weight: 500;
          color: #909399;
          margin-right: 8px;
        }
      }

      .auditor {
        font-size: 14px;
      }

      .opinion {
        font-size: 14px;
        white-space: pre-wrap;
      }

      .time {
        font-size: 13px;
        color: #909399;
      }

      .attachments {
        margin-top: 12px;
        display: flex;
        align-items: center;
        gap: 8px;

        .label {
          font-weight: 500;
          color: #909399;
        }
      }
    }
  }
}
</style>

