<template>
  <div class="security-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>安全配置</span>
          <el-button type="primary" size="small" @click="loadConfigs" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-form :model="formData" label-width="180px" style="max-width: 600px">
        <el-form-item label="Token过期时间">
          <el-input-number v-model="formData.token_expire_hours" :min="1" :max="168" :step="1" />
          <span style="margin-left: 10px; color: #909399">小时</span>
          <div class="form-tip">用户登录Token的有效期，建议设置为8-24小时</div>
        </el-form-item>

        <el-form-item label="刷新Token过期时间">
          <el-input-number
            v-model="formData.refresh_token_expire_days"
            :min="1"
            :max="90"
            :step="1"
          />
          <span style="margin-left: 10px; color: #909399">天</span>
          <div class="form-tip">刷新Token的有效期，建议设置为7-30天</div>
        </el-form-item>

        <el-form-item label="密码最小长度">
          <el-input-number v-model="formData.password_min_length" :min="6" :max="20" :step="1" />
          <span style="margin-left: 10px; color: #909399">位</span>
          <div class="form-tip">用户密码的最小长度要求，建议不少于6位</div>
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
        <span>安全提示</span>
      </template>

      <el-alert type="info" :closable="false">
        <template #title>
          <div style="line-height: 1.8">
            <p>
              <strong>Token过期时间：</strong>设置过短会导致用户频繁登录，设置过长会增加安全风险
            </p>
            <p><strong>刷新Token：</strong>用于在Token过期后自动续期，避免用户频繁输入密码</p>
            <p><strong>密码长度：</strong>密码越长安全性越高，但也要考虑用户体验</p>
            <p style="color: #e6a23c; margin-top: 10px">
              <el-icon><Warning /></el-icon>
              修改安全配置后，新配置将在下次用户登录时生效
            </p>
          </div>
        </template>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Check, RefreshLeft, Warning } from '@element-plus/icons-vue'
import { getAllConfigs, batchUpdateConfigs } from '@/api/modules/settings'

const loading = ref(false)
const saving = ref(false)

// 表单数据
const formData = ref({
  token_expire_hours: 8,
  refresh_token_expire_days: 30,
  password_min_length: 6,
})

// 加载配置
const loadConfigs = async () => {
  loading.value = true
  try {
    const configs = await getAllConfigs('security')

    // 解析配置值
    configs.forEach((config) => {
      if (config.config_key === 'token_expire_hours') {
        formData.value.token_expire_hours = parseInt(config.config_value || '8')
      } else if (config.config_key === 'refresh_token_expire_days') {
        formData.value.refresh_token_expire_days = parseInt(config.config_value || '30')
      } else if (config.config_key === 'password_min_length') {
        formData.value.password_min_length = parseInt(config.config_value || '6')
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
  saving.value = true
  try {
    const configs = {
      token_expire_hours: formData.value.token_expire_hours.toString(),
      refresh_token_expire_days: formData.value.refresh_token_expire_days.toString(),
      password_min_length: formData.value.password_min_length.toString(),
    }

    await batchUpdateConfigs(configs)
    ElMessage.success('安全配置已保存')
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
.security-config {
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
