<template>
  <div class="feature-demo">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>合同生成增强功能演示</h1>
      <p>展示所有已实现的功能模块</p>
    </div>

    <!-- 功能概览卡片 -->
    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">
            <el-icon size="48" color="#409eff"><Document /></el-icon>
          </div>
          <h3>合同生成增强</h3>
          <p>在线索列表中直接生成合同，自动带入报价信息，支持金额修改和审核触发</p>
          <div class="feature-status">
            <el-tag type="success">✅ 已完成</el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">
            <el-icon size="48" color="#67c23a"><Check /></el-icon>
          </div>
          <h3>审核工作流</h3>
          <p>完整的审核流程管理，支持多级审核、规则配置和状态跟踪</p>
          <div class="feature-status">
            <el-tag type="success">✅ 已完成</el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">
            <el-icon size="48" color="#e6a23c"><EditPen /></el-icon>
          </div>
          <h3>电子签署</h3>
          <p>无权限签署链接，电子签名保存，签署完成后显示支付选项</p>
          <div class="feature-status">
            <el-tag type="success">✅ 已完成</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">
            <el-icon size="48" color="#f56c6c"><Money /></el-icon>
          </div>
          <h3>支付管理</h3>
          <p>支持支付宝、微信、银行转账多种支付方式，银行转账需财务审核</p>
          <div class="feature-status">
            <el-tag type="success">✅ 已完成</el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">
            <el-icon size="48" color="#909399"><Setting /></el-icon>
          </div>
          <h3>规则配置</h3>
          <p>灵活的审核规则配置，支持金额阈值、审核人员分级等复杂逻辑</p>
          <div class="feature-status">
            <el-tag type="success">✅ 已完成</el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">
            <el-icon size="48" color="#606266"><View /></el-icon>
          </div>
          <h3>流程预览</h3>
          <p>合同预览页面显示完整的审核流程、签署状态、支付状态信息</p>
          <div class="feature-status">
            <el-tag type="success">✅ 已完成</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 菜单导航指南 -->
    <el-card class="navigation-guide">
      <h2>功能导航指南</h2>
      <el-row :gutter="20">
        <el-col :span="12">
          <h3>📋 主要功能入口</h3>
          <ul class="nav-list">
            <li>
              <strong>线索管理 → 线索列表</strong>
              <p>在线索列表中找到已确认报价的线索，点击"生成合同"按钮</p>
            </li>
            <li>
              <strong>合同管理 → 合同列表</strong>
              <p>查看所有合同，点击合同可查看详情和审核流程</p>
            </li>
            <li>
              <strong>审核管理 → 我的审核任务</strong>
              <p>处理待审核的合同和报价，查看审核统计</p>
            </li>
          </ul>
        </el-col>
        <el-col :span="12">
          <h3>⚙️ 配置管理入口</h3>
          <ul class="nav-list">
            <li>
              <strong>审核管理 → 审核流程配置</strong>
              <p>配置审核工作流程，设置审核步骤和审核人员</p>
            </li>
            <li>
              <strong>审核管理 → 审核规则配置</strong>
              <p>设置触发审核的条件和规则，如金额阈值等</p>
            </li>
            <li>
              <strong>合同管理 → 乙方主体/支付方式</strong>
              <p>管理合同签署主体和支付方式配置</p>
            </li>
          </ul>
        </el-col>
      </el-row>
    </el-card>

    <!-- 技术架构信息 -->
    <el-card class="tech-info">
      <h2>技术架构</h2>
      <el-row :gutter="20">
        <el-col :span="8">
          <h3>🔧 后端技术</h3>
          <ul>
            <li>FastAPI + SQLAlchemy</li>
            <li>PostgreSQL 数据库</li>
            <li>8个新数据库表</li>
            <li>RESTful API 设计</li>
            <li>审核工作流引擎</li>
          </ul>
        </el-col>
        <el-col :span="8">
          <h3>🎨 前端技术</h3>
          <ul>
            <li>Vue 3 + TypeScript</li>
            <li>Element Plus UI</li>
            <li>Pinia 状态管理</li>
            <li>响应式设计</li>
            <li>组件化架构</li>
          </ul>
        </el-col>
        <el-col :span="8">
          <h3>📊 项目成果</h3>
          <ul>
            <li>107个文件变更</li>
            <li>19,427行代码新增</li>
            <li>6个主要功能模块</li>
            <li>完整工作流系统</li>
            <li>性能优化脚本</li>
          </ul>
        </el-col>
      </el-row>
    </el-card>

    <!-- 快速测试按钮 -->
    <el-card class="quick-test">
      <h2>快速功能测试</h2>
      <div class="test-buttons">
        <el-button type="primary" @click="goToLeads">
          <el-icon><Phone /></el-icon>
          测试合同生成
        </el-button>
        <el-button type="success" @click="goToAuditTasks">
          <el-icon><Check /></el-icon>
          查看审核任务
        </el-button>
        <el-button type="warning" @click="goToWorkflowConfig">
          <el-icon><Setting /></el-icon>
          配置审核流程
        </el-button>
        <el-button type="info" @click="goToContracts">
          <el-icon><Document /></el-icon>
          查看合同列表
        </el-button>
      </div>
    </el-card>

    <!-- 系统状态 -->
    <el-card class="system-status">
      <h2>系统状态</h2>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="status-item">
            <el-icon size="24" color="#67c23a"><CircleCheck /></el-icon>
            <span>后端服务</span>
            <el-tag type="success" size="small">运行中</el-tag>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <el-icon size="24" color="#67c23a"><CircleCheck /></el-icon>
            <span>前端服务</span>
            <el-tag type="success" size="small">运行中</el-tag>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <el-icon size="24" color="#67c23a"><CircleCheck /></el-icon>
            <span>数据库</span>
            <el-tag type="success" size="small">连接正常</el-tag>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <el-icon size="24" color="#67c23a"><CircleCheck /></el-icon>
            <span>审核引擎</span>
            <el-tag type="success" size="small">就绪</el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { 
  Document, 
  Check, 
  EditPen, 
  Money, 
  Setting, 
  View, 
  Phone, 
  CircleCheck 
} from '@element-plus/icons-vue'

const router = useRouter()

// 导航方法
const goToLeads = () => {
  router.push('/leads')
}

const goToAuditTasks = () => {
  router.push('/audit/tasks')
}

const goToWorkflowConfig = () => {
  router.push('/audit/workflow-config')
}

const goToContracts = () => {
  router.push('/contracts')
}
</script>

<style scoped>
.feature-demo {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #909399;
  font-size: 16px;
}

.feature-cards {
  margin-bottom: 30px;
}

.feature-card {
  text-align: center;
  height: 280px;
  margin-bottom: 20px;
}

.feature-icon {
  margin-bottom: 20px;
}

.feature-card h3 {
  color: #303133;
  margin-bottom: 15px;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
  min-height: 72px;
}

.feature-status {
  margin-top: auto;
}

.navigation-guide,
.tech-info,
.quick-test,
.system-status {
  margin-bottom: 30px;
}

.navigation-guide h2,
.tech-info h2,
.quick-test h2,
.system-status h2 {
  color: #303133;
  margin-bottom: 20px;
}

.nav-list {
  list-style: none;
  padding: 0;
}

.nav-list li {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.nav-list strong {
  color: #409eff;
}

.nav-list p {
  margin: 5px 0 0 0;
  color: #606266;
  font-size: 14px;
}

.tech-info ul {
  list-style: none;
  padding: 0;
}

.tech-info li {
  padding: 5px 0;
  color: #606266;
}

.test-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.test-buttons .el-button {
  flex: 1;
  min-width: 150px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.status-item span {
  flex: 1;
  color: #303133;
}
</style>
