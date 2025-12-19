<template>
  <div class="business-params">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>业务参数配置</span>
          <el-button type="primary" size="small" @click="loadConfigs" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-form :model="formData" label-width="220px" style="max-width: 700px">
        <el-divider content-position="left">合同审核参数</el-divider>

        <el-form-item label="价格差异审核阈值">
          <el-input-number
            v-model="formData.contract_price_diff_threshold"
            :min="0"
            :max="1"
            :step="0.01"
            :precision="2"
          />
          <span style="margin-left: 10px; color: #909399">（0-1之间，如0.05表示5%）</span>
          <div class="form-tip">当合同金额与报价金额差异超过此阈值时，需要审核</div>
        </el-form-item>

        <el-form-item label="审核超时提醒时间">
          <el-input-number v-model="formData.audit_timeout_hours" :min="1" :max="168" :step="1" />
          <span style="margin-left: 10px; color: #909399">小时</span>
          <div class="form-tip">审核任务超过此时间未处理时，系统将发送提醒</div>
        </el-form-item>

        <el-divider content-position="left">合规提醒参数</el-divider>

        <el-form-item label="合规事项提醒天数">
          <el-input
            v-model="formData.compliance_remind_days"
            placeholder="如：15,7,3,1"
            style="width: 300px"
          />
          <div class="form-tip">在合规事项到期前的这些天数发送提醒，多个天数用逗号分隔</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
          <el-button @click="loadConfigs">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>参数说明</span>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="价格差异审核阈值">
          <div style="line-height: 1.8">
            <p>用于控制合同金额与报价金额的差异容忍度</p>
            <p>例如：设置为0.05（5%），报价10000元，合同金额在9500-10500元之间无需审核</p>
            <p style="color: #e6a23c">建议值：0.05（5%）</p>
          </div>
        </el-descriptions-item>

        <el-descriptions-item label="审核超时提醒">
          <div style="line-height: 1.8">
            <p>当审核任务超过设定时间未处理时，系统会发送提醒通知</p>
            <p>帮助管理者及时发现和处理积压的审核任务</p>
            <p style="color: #e6a23c">建议值：24小时</p>
          </div>
        </el-descriptions-item>

        <el-descriptions-item label="合规提醒天数">
          <div style="line-height: 1.8">
            <p>在合规事项到期前的指定天数发送提醒</p>
            <p>例如：设置为"15,7,3,1"，将在到期前15天、7天、3天、1天各发送一次提醒</p>
            <p style="color: #e6a23c">建议值：15,7,3,1</p>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Check, RefreshLeft } from '@element-plus/icons-vue'
import { getAllConfigs, batchUpdateConfigs } from '@/api/modules/settings'

const loading = ref(false)
const saving = ref(false)

// 表单数据
const formData = ref({
  contract_price_diff_threshold: 0.05,
  audit_timeout_hours: 24,
  compliance_remind_days: '15,7,3,1',
})

// 加载配置
const loadConfigs = async () => {
  loading.value = true
  try {
    const configs = await getAllConfigs('business')

    // 解析配置值
    configs.forEach((config) => {
      if (config.config_key === 'contract_price_diff_threshold') {
        formData.value.contract_price_diff_threshold = parseFloat(config.config_value || '0.05')
      } else if (config.config_key === 'audit_timeout_hours') {
        formData.value.audit_timeout_hours = parseInt(config.config_value || '24')
      } else if (config.config_key === 'compliance_remind_days') {
        formData.value.compliance_remind_days = config.config_value || '15,7,3,1'
      }
    })
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载配置失败')
  } finally {
    loading.value = false
  }
}

// 保存配置
const handleSave = async () => {
  // 验证合规提醒天数格式
  const remindDays = formData.value.compliance_remind_days.trim()
  if (!/^\d+(,\d+)*$/.test(remindDays)) {
    ElMessage.error('合规提醒天数格式不正确，应为数字，多个用逗号分隔，如：15,7,3,1')
    return
  }

  saving.value = true
  try {
    const configs = {
      contract_price_diff_threshold: formData.value.contract_price_diff_threshold.toString(),
      audit_timeout_hours: formData.value.audit_timeout_hours.toString(),
      compliance_remind_days: formData.value.compliance_remind_days,
    }

    await batchUpdateConfigs(configs)
    ElMessage.success('业务参数配置已保存')
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '保存配置失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped lang="scss">
.business-params {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
}
</style>
