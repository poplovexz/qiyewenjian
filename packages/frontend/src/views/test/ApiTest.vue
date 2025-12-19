<template>
  <div class="api-test">
    <h1>API测试页面</h1>

    <el-card>
      <h3>认证状态</h3>
      <p>是否已登录: {{ isAuthenticated }}</p>
      <p>用户名: {{ userInfo?.yonghu_ming }}</p>
      <p>权限: {{ userPermissions.join(', ') }}</p>
    </el-card>

    <el-card style="margin-top: 20px">
      <h3>支付方式API测试</h3>
      <el-button @click="testPaymentMethodsApi" :loading="loading">测试支付方式API</el-button>
      <div v-if="apiResult" style="margin-top: 10px">
        <h4>API响应:</h4>
        <pre>{{ JSON.stringify(apiResult, null, 2) }}</pre>
      </div>
      <div v-if="apiError" style="margin-top: 10px; color: red">
        <h4>API错误:</h4>
        <pre>{{ JSON.stringify(apiError, null, 2) }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/modules/auth'
import { paymentMethodApi } from '@/api/modules/contract'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const loading = ref(false)
const apiResult = ref(null)
const apiError = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userInfo = computed(() => authStore.userInfo)
const userPermissions = computed(() => authStore.userPermissions)

const testPaymentMethodsApi = async () => {
  loading.value = true
  apiResult.value = null
  apiError.value = null

  try {
    const response = await paymentMethodApi.getList({ page: 1, size: 10 })

    apiResult.value = response
    ElMessage.success('API调用成功')
  } catch (error) {
    apiError.value = error
    ElMessage.error('API调用失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.api-test {
  padding: 20px;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
