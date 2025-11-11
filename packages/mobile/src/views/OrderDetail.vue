<template>
  <div class="order-detail-container">
    <van-nav-bar title="工单详情" left-arrow @click-left="router.back()" fixed placeholder />
    
    <van-empty description="功能开发中" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.order-detail-container {
  min-height: 100vh;
  background-color: #f7f8fa;
}
</style>

