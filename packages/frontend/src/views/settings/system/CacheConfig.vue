<template>
  <div class="cache-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>缓存配置</span>
          <el-button type="primary" size="small" @click="loadConfigs" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-form :model="formData" label-width="180px" style="max-width: 600px">
        <el-form-item label="默认缓存时间">
          <el-input-number
            v-model="formData.cache_default_minutes"
            :min="1"
            :max="1440"
            :step="1"
          />
          <span style="margin-left: 10px; color: #909399">分钟</span>
          <div class="form-tip">一般数据的默认缓存时间，建议10-30分钟</div>
        </el-form-item>

        <el-form-item label="长期缓存时间">
          <el-input-number
            v-model="formData.cache_long_hours"
            :min="1"
            :max="168"
            :step="1"
          />
          <span style="margin-left: 10px; color: #909399">小时</span>
          <div class="form-tip">不常变动数据的缓存时间，如配置项、字典数据等，建议12-48小时</div>
        </el-form-item>

        <el-form-item label="短期缓存时间">
          <el-input-number
            v-model="formData.cache_short_seconds"
            :min="10"
            :max="600"
            :step="10"
          />
          <span style="margin-left: 10px; color: #909399">秒</span>
          <div class="form-tip">频繁变动数据的缓存时间，建议30-120秒</div>
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
        <span>缓存说明</span>
      </template>
      
      <el-alert type="info" :closable="false">
        <template #title>
          <div style="line-height: 1.8">
            <p><strong>默认缓存：</strong>用于一般业务数据，如用户列表、客户列表等</p>
            <p><strong>长期缓存：</strong>用于不常变动的数据，如系统配置、产品列表、字典数据等</p>
            <p><strong>短期缓存：</strong>用于频繁变动的数据，如实时统计、在线用户等</p>
            <p style="color: #E6A23C; margin-top: 10px">
              <el-icon><Warning /></el-icon>
              缓存时间设置过长会导致数据不及时，设置过短会增加数据库压力
            </p>
          </div>
        </template>
      </el-alert>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>缓存使用建议</span>
      </template>
      
      <el-table :data="cacheExamples" border>
        <el-table-column prop="type" label="缓存类型" width="120" />
        <el-table-column prop="usage" label="适用场景" />
        <el-table-column prop="time" label="建议时间" width="120" />
      </el-table>
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
  cache_default_minutes: 15,
  cache_long_hours: 24,
  cache_short_seconds: 60
})

// 缓存使用示例
const cacheExamples = [
  { type: '长期缓存', usage: '系统配置、产品列表、字典数据、权限配置', time: '12-48小时' },
  { type: '默认缓存', usage: '用户列表、客户列表、合同列表、订单列表', time: '10-30分钟' },
  { type: '短期缓存', usage: '实时统计、在线用户、待办事项数量', time: '30-120秒' }
]

// 加载配置
const loadConfigs = async () => {
  loading.value = true
  try {
    const configs = await getAllConfigs('cache')
    
    // 解析配置值
    configs.forEach(config => {
      if (config.config_key === 'cache_default_minutes') {
        formData.value.cache_default_minutes = parseInt(config.config_value || '15')
      } else if (config.config_key === 'cache_long_hours') {
        formData.value.cache_long_hours = parseInt(config.config_value || '24')
      } else if (config.config_key === 'cache_short_seconds') {
        formData.value.cache_short_seconds = parseInt(config.config_value || '60')
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
      cache_default_minutes: formData.value.cache_default_minutes.toString(),
      cache_long_hours: formData.value.cache_long_hours.toString(),
      cache_short_seconds: formData.value.cache_short_seconds.toString()
    }

    await batchUpdateConfigs(configs)
    ElMessage.success('缓存配置已保存')
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
.cache-config {
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
