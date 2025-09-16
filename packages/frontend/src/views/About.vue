<template>
  <div class="about-container">
    <el-card>
      <template #header>
        <h1>关于系统</h1>
      </template>
      
      <div class="about-content">
        <h2>代理记账营运内部系统</h2>
        <p>这是一个专为代理记账公司设计的内部营运管理系统，提供完整的业务流程管理功能。</p>
        
        <h3>主要功能模块</h3>
        <ul>
          <li>用户管理 - 用户账户、角色权限管理</li>
          <li>客户管理 - 客户信息、服务记录管理</li>
          <li>合同管理 - 合同模板、合同签署管理</li>
          <li>订单收费 - 订单处理、发票管理</li>
          <li>任务管理 - 工作任务分配与跟踪</li>
          <li>财务账务 - 凭证录入、账簿管理</li>
        </ul>
        
        <h3>技术架构</h3>
        <div class="tech-stack">
          <div class="tech-section">
            <h4>前端技术</h4>
            <ul>
              <li>Vue 3 + TypeScript</li>
              <li>Element Plus UI 组件库</li>
              <li>Pinia 状态管理</li>
              <li>Vue Router 路由管理</li>
              <li>Vite 构建工具</li>
            </ul>
          </div>
          
          <div class="tech-section">
            <h4>后端技术</h4>
            <ul>
              <li>FastAPI + Python</li>
              <li>SQLAlchemy ORM</li>
              <li>PostgreSQL 数据库</li>
              <li>JWT 认证</li>
              <li>RBAC 权限控制</li>
            </ul>
          </div>
        </div>
        
        <div class="version-info">
          <p><strong>版本:</strong> v1.1.0</p>
          <p><strong>更新时间:</strong> 2024年</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 关于页面组件
</script>

<style scoped>
.about-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.about-content {
  line-height: 1.6;
}

.about-content h2 {
  color: #2c3e50;
  margin-bottom: 16px;
}

.about-content h3 {
  color: #34495e;
  margin: 24px 0 12px 0;
}

.about-content h4 {
  color: #34495e;
  margin: 16px 0 8px 0;
}

.about-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.about-content li {
  margin: 4px 0;
}

.tech-stack {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin: 20px 0;
}

.tech-section {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.version-info {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  color: #666;
}

@media (max-width: 768px) {
  .tech-stack {
    grid-template-columns: 1fr;
  }
}
</style>
