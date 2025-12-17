<template>
  <div class="order-list-container">
    <van-nav-bar title="工单列表" fixed placeholder />
    
    <van-empty description="功能开发中" />

    <van-tabbar v-model="active" fixed placeholder>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="todo-list-o" to="/tasks">任务</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/orders">工单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref(2)
</script>

<style scoped>
.order-list-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 60px;
}
</style>

