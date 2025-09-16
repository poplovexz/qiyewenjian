<template>
  <div class="home">
    <h1>代理记账营运内部系统</h1>
    <p>欢迎使用代理记账营运内部系统</p>
    
    <div class="features">
      <div class="feature-card">
        <h3>用户管理</h3>
        <p>管理系统用户和权限</p>
      </div>
      
      <div class="feature-card">
        <h3>客户管理</h3>
        <p>管理客户信息和状态</p>
      </div>
      
      <div class="feature-card">
        <h3>合同管理</h3>
        <p>管理合同模板和签署</p>
      </div>
      
      <div class="feature-card">
        <h3>任务管理</h3>
        <p>分配和跟踪工作任务</p>
      </div>
    </div>
    
    <div class="actions">
      <router-link to="/login" class="btn btn-primary">登录系统</router-link>
      <router-link to="/dashboard" class="btn btn-secondary">进入控制台</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
}

.feature-card {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  color: #495057;
  margin-bottom: 1rem;
}

.actions {
  margin-top: 3rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  margin: 0 0.5rem;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}
</style>
