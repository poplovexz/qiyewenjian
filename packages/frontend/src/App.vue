<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/modules/auth'

onMounted(() => {
  // 应用启动时恢复认证状态
  const authStore = useAuthStore()
  authStore.restoreFromStorage()
})
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
