<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>控制台</h1>
      <div class="user-info">
        <span>欢迎，{{ authStore.user?.name }}</span>
        <button @click="handleLogout" class="btn btn-outline">退出</button>
      </div>
    </header>

    <div class="dashboard-content">
      <div class="stats-grid">
        <div class="stat-card">
          <h3>总客户数</h3>
          <div class="stat-number">{{ stats.totalCustomers }}</div>
        </div>

        <div class="stat-card">
          <h3>活跃客户</h3>
          <div class="stat-number">{{ stats.activeCustomers }}</div>
        </div>

        <div class="stat-card">
          <h3>待处理任务</h3>
          <div class="stat-number">{{ stats.pendingTasks }}</div>
        </div>

        <div class="stat-card">
          <h3>本月收入</h3>
          <div class="stat-number">¥{{ stats.monthlyRevenue.toLocaleString() }}</div>
        </div>
      </div>

      <div class="dashboard-sections">
        <section class="recent-tasks">
          <h2>最近任务</h2>
          <div class="task-list">
            <div v-for="task in recentTasks" :key="task.id" class="task-item">
              <div class="task-info">
                <h4>{{ task.title }}</h4>
                <p>{{ task.description }}</p>
              </div>
              <div class="task-status" :class="task.status">
                {{ getStatusText(task.status) }}
              </div>
            </div>
          </div>
        </section>

        <section class="quick-actions">
          <h2>快速操作</h2>
          <div class="action-buttons">
            <button class="action-btn">新增客户</button>
            <button class="action-btn">创建任务</button>
            <button class="action-btn">生成报表</button>
            <button class="action-btn">系统设置</button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import type { Task } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  totalCustomers: 156,
  activeCustomers: 142,
  pendingTasks: 23,
  monthlyRevenue: 125000,
})

const recentTasks = ref<Task[]>([
  {
    id: '1',
    customerId: '1',
    title: '月度账务处理',
    description: '处理客户A的月度账务',
    type: 'accounting',
    priority: 'high',
    status: 'in_progress',
    dueDate: '2024-03-20',
    createdAt: '2024-03-15',
    updatedAt: '2024-03-15',
  },
  {
    id: '2',
    customerId: '2',
    title: '税务申报',
    description: '完成客户B的税务申报',
    type: 'tax_filing',
    priority: 'medium',
    status: 'pending',
    dueDate: '2024-03-25',
    createdAt: '2024-03-16',
    updatedAt: '2024-03-16',
  },
])

const getStatusText = (status: string) => {
  const statusMap = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // 这里可以加载仪表板数据
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dashboard-header {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h1 {
  margin: 0;
  color: #2c3e50;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.dashboard-content {
  padding: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 1rem 0;
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.dashboard-sections {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.recent-tasks,
.quick-actions {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.recent-tasks h2,
.quick-actions h2 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.task-info h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.task-info p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.task-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.task-status.pending {
  background: #fff3cd;
  color: #856404;
}

.task-status.in_progress {
  background: #d1ecf1;
  color: #0c5460;
}

.task-status.completed {
  background: #d4edda;
  color: #155724;
}

.action-buttons {
  display: grid;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.action-btn:hover {
  background: #0056b3;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline {
  background: transparent;
  border: 1px solid #6c757d;
  color: #6c757d;
}

.btn-outline:hover {
  background: #6c757d;
  color: white;
}
</style>
