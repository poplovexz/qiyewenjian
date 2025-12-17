<template>
  <div class="basic-info">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统基础信息</span>
          <el-button type="primary" size="small" @click="loadSystemInfo" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统名称">
          {{ systemInfo.system_name }}
        </el-descriptions-item>
        
        <el-descriptions-item label="系统版本">
          <el-tag type="success">{{ systemInfo.version }}</el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="运行环境">
          <el-tag :type="systemInfo.environment === 'production' ? 'danger' : 'warning'">
            {{ systemInfo.environment === 'production' ? '生产环境' : '开发环境' }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="运行时间">
          {{ systemInfo.uptime }}
        </el-descriptions-item>
        
        <el-descriptions-item label="数据库状态">
          <el-tag :type="systemInfo.database_status === '正常' ? 'success' : 'danger'">
            <el-icon><CircleCheck v-if="systemInfo.database_status === '正常'" /><CircleClose v-else /></el-icon>
            {{ systemInfo.database_status }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="Redis状态">
          <el-tag :type="systemInfo.redis_status === '正常' ? 'success' : 'danger'">
            <el-icon><CircleCheck v-if="systemInfo.redis_status === '正常'" /><CircleClose v-else /></el-icon>
            {{ systemInfo.redis_status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>缓存管理</span>
        </div>
      </template>

      <el-alert
        title="缓存清除说明"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      >
        清除缓存会影响系统性能，请谨慎操作。清除后系统会自动重新构建缓存。
      </el-alert>

      <el-form :inline="true">
        <el-form-item label="缓存键模式">
          <el-input
            v-model="cachePattern"
            placeholder="如：user:* 或留空清除所有"
            style="width: 300px"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="danger" @click="handleClearCache" :loading="clearingCache">
            <el-icon><Delete /></el-icon>
            清除缓存
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, CircleCheck, CircleClose, Delete } from '@element-plus/icons-vue'
import { getSystemInfo, clearCache, type SystemInfo } from '@/api/modules/settings'

const loading = ref(false)
const clearingCache = ref(false)
const cachePattern = ref('')

// 系统信息
const systemInfo = ref<SystemInfo>({
  system_name: '',
  version: '',
  environment: '',
  database_status: '',
  redis_status: '',
  uptime: ''
})

// 加载系统信息
const loadSystemInfo = async () => {
  loading.value = true
  try {
    const data = await getSystemInfo()
    systemInfo.value = data
  } catch (error: any) {
    ElMessage.error(error.message || '加载系统信息失败')
  } finally {
    loading.value = false
  }
}

// 清除缓存
const handleClearCache = async () => {
  try {
    await ElMessageBox.confirm(
      cachePattern.value 
        ? `确定要清除匹配 "${cachePattern.value}" 的缓存吗？`
        : '确定要清除所有缓存吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    clearingCache.value = true
    const result = await clearCache(cachePattern.value || undefined)
    ElMessage.success(result.message)
    cachePattern.value = ''
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '清除缓存失败')
    }
  } finally {
    clearingCache.value = false
  }
}

onMounted(() => {
  loadSystemInfo()
})
</script>

<style scoped lang="scss">
.basic-info {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}
</style>

