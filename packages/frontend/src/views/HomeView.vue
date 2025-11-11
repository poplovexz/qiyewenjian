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

    <div class="bookkeeping-intro">
      <h2>代理记账服务</h2>
      <p>提供基础记账、税务申报、财务报表编制等核心服务，支持小微企业与一般纳税人。内置套餐管理与增值服务组合，与合同、订单、任务、审核流程深度打通。</p>
      <div class="intro-list">
        <div class="intro-item">
          <h4>基础记账</h4>
          <p>凭证管理、账簿生成、月度结账</p>
        </div>
        <div class="intro-item">
          <h4>税务申报</h4>
          <p>增值税、所得税等周期性申报与合规管理</p>
        </div>
        <div class="intro-item">
          <h4>财务报表</h4>
          <p>月度/季度报表与经营分析</p>
        </div>
      </div>
    </div>
    
    <div class="actions">
      <router-link to="/bookkeeping-packages" class="btn btn-primary">查看代理记账套餐</router-link>
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

.bookkeeping-intro {
  margin: 3rem 0;
  text-align: left;
}
.bookkeeping-intro h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
}
.intro-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}
.intro-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.intro-item h4 {
  margin-bottom: 0.5rem;
  color: #495057;
}
</style>
