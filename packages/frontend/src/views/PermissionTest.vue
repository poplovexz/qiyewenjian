<template>
  <div class="permission-test">
    <el-card class="test-card">
      <h2>权限测试页面</h2>
      <p>测试admin用户是否可以访问审核管理功能</p>
      
      <!-- 用户信息 -->
      <el-divider content-position="left">用户信息</el-divider>
      <div class="user-info">
        <p><strong>用户名:</strong> {{ userInfo?.yonghu_ming || '未登录' }}</p>
        <p><strong>用户ID:</strong> {{ userInfo?.id || '无' }}</p>
        <p><strong>角色:</strong> {{ userRoles.join(', ') || '无角色' }}</p>
        <p><strong>权限数量:</strong> {{ userPermissions.length }}</p>
      </div>

      <!-- 权限测试 -->
      <el-divider content-position="left">权限测试</el-divider>
      <div class="permission-tests">
        <div class="test-item" v-for="permission in testPermissions" :key="permission.code">
          <el-tag 
            :type="hasPermission(permission.code) ? 'success' : 'danger'"
            size="large"
          >
            {{ permission.name }}: {{ hasPermission(permission.code) ? '✅ 有权限' : '❌ 无权限' }}
          </el-tag>
          <span class="permission-code">{{ permission.code }}</span>
        </div>
      </div>

      <!-- 导航测试 -->
      <el-divider content-position="left">导航测试</el-divider>
      <div class="navigation-tests">
        <el-button 
          type="primary" 
          @click="navigateToAuditTasks"
          :disabled="!hasPermission('audit_manage')"
        >
          访问审核任务页面
        </el-button>
        
        <el-button 
          type="primary" 
          @click="navigateToAuditConfig"
          :disabled="!hasPermission('audit_config')"
        >
          访问审核配置页面
        </el-button>
        
        <el-button 
          type="success" 
          @click="navigateToPermissionManager"
        >
          访问权限管理工具
        </el-button>
      </div>

      <!-- 权限列表 -->
      <el-divider content-position="left">用户权限列表</el-divider>
      <div class="permissions-list">
        <el-tag 
          v-for="permission in userPermissions" 
          :key="permission"
          type="info"
          size="small"
          style="margin: 2px;"
        >
          {{ permission }}
        </el-tag>
        <p v-if="userPermissions.length === 0" class="no-permissions">
          当前用户没有明确的权限列表（admin用户拥有所有权限）
        </p>
      </div>

      <!-- 刷新按钮 -->
      <el-divider></el-divider>
      <div class="actions">
        <el-button @click="refreshUserInfo" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新用户信息
        </el-button>
        
        <el-button type="warning" @click="logout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/modules/auth'
import { ElMessage } from 'element-plus'
import { Refresh, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

// 计算属性
const userInfo = computed(() => authStore.userInfo)
const userRoles = computed(() => authStore.userRoles)
const userPermissions = computed(() => authStore.userPermissions)
const hasPermission = computed(() => authStore.hasPermission)

// 测试权限列表
const testPermissions = [
  { name: '审核管理菜单', code: 'audit_menu' },
  { name: '审核任务管理', code: 'audit_manage' },
  { name: '审核流程配置', code: 'audit_config' },
  { name: '审核规则配置', code: 'audit_rule_config' },
  { name: '查看审核任务', code: 'audit:read' },
  { name: '处理审核任务', code: 'audit:process' },
  { name: '合同审核', code: 'contract_audit' },
  { name: '报价审核', code: 'quote_audit' },
  { name: '用户管理', code: 'user:read' },
  { name: '客户管理', code: 'customer:read' },
  { name: '合同管理', code: 'contract_manage' },
  { name: '财务管理', code: 'finance_manage' }
]

// 方法
const refreshUserInfo = async () => {
  loading.value = true
  try {
    await authStore.getCurrentUser()
    ElMessage.success('用户信息刷新成功')
  } catch (error) {
    console.error('刷新用户信息失败:', error)
    ElMessage.error('刷新用户信息失败')
  } finally {
    loading.value = false
  }
}

const logout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
    ElMessage.error('退出登录失败')
  }
}

const navigateToAuditTasks = () => {
  router.push('/audit/tasks')
}

const navigateToAuditConfig = () => {
  router.push('/audit/workflow-config')
}

const navigateToPermissionManager = () => {
  router.push('/permission-manager')
}

// 生命周期
onMounted(() => {
  if (!userInfo.value) {
    refreshUserInfo()
  }
})
</script>

<style scoped>
.permission-test {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.test-card {
  padding: 20px;
}

.user-info {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin: 10px 0;
}

.user-info p {
  margin: 8px 0;
  font-size: 14px;
}

.permission-tests {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 15px 0;
}

.test-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.permission-code {
  font-family: monospace;
  font-size: 12px;
  color: #666;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

.navigation-tests {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 15px 0;
}

.permissions-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  margin: 10px 0;
}

.no-permissions {
  color: #909399;
  font-style: italic;
  text-align: center;
  margin: 20px 0;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

h2 {
  color: #303133;
  margin-bottom: 10px;
}

p {
  color: #606266;
  margin-bottom: 20px;
}
</style>
