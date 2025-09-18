<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>工作台</h1>
      <div class="welcome-info">
        <span>欢迎回来，{{ userInfo?.xingming || userInfo?.yonghu_ming }}！</span>
      </div>
    </div>

    <div class="dashboard-content">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-value">{{ userInfo?.denglu_cishu || 0 }}</div>
              <div class="stat-label">登录次数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-value">{{ userRoles.length }}</div>
              <div class="stat-label">拥有角色</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-value">{{ userPermissions.length }}</div>
              <div class="stat-label">拥有权限</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-value">{{ userInfo?.zhuangtai || '未知' }}</div>
              <div class="stat-label">账户状态</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 快捷导航 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>快捷导航</span>
            </template>
            <div class="quick-nav">
              <el-button
                v-if="hasPermission('user:read')"
                type="primary"
                :icon="User"
                @click="$router.push('/users')"
              >
                用户管理
              </el-button>
              <el-button
                type="success"
                :icon="UserFilled"
                @click="$router.push('/customers')"
              >
                客户管理
              </el-button>
              <el-button
                type="warning"
                :icon="Document"
                @click="$router.push('/contracts')"
              >
                合同管理
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>用户信息</span>
            </template>
            <div class="user-details">
              <p><strong>用户名:</strong> {{ userInfo?.yonghu_ming }}</p>
              <p><strong>姓名:</strong> {{ userInfo?.xingming }}</p>
              <p><strong>邮箱:</strong> {{ userInfo?.youxiang }}</p>
              <p><strong>手机:</strong> {{ userInfo?.shouji }}</p>
              <p><strong>最后登录:</strong> {{ formatDate(userInfo?.zuihou_denglu) }}</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>权限信息</span>
            </template>
            <div class="permissions-info">
              <div class="roles-section">
                <h4>角色列表:</h4>
                <el-tag v-for="role in userRoles" :key="role" type="success" style="margin-right: 8px;">
                  {{ role }}
                </el-tag>
                <span v-if="userRoles.length === 0" class="no-data">暂无角色</span>
              </div>
              <div class="permissions-section" style="margin-top: 16px;">
                <h4>权限列表:</h4>
                <el-tag v-for="permission in userPermissions" :key="permission" type="info" style="margin-right: 8px; margin-bottom: 4px;">
                  {{ permission }}
                </el-tag>
                <span v-if="userPermissions.length === 0" class="no-data">暂无权限</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import { User, UserFilled, Document } from '@element-plus/icons-vue'

// 组合式函数
const { userInfo, userRoles, userPermissions, hasPermission } = useAuth()

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.dashboard-header h1 {
  margin: 0;
  color: #2c3e50;
}

.welcome-info {
  color: #666;
  font-size: 14px;
}

.stat-card {
  text-align: center;
}

.stat-item {
  padding: 16px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.user-details p {
  margin: 8px 0;
  line-height: 1.6;
}

.permissions-info h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.no-data {
  color: #999;
  font-style: italic;
}

.roles-section,
.permissions-section {
  line-height: 1.8;
}

.quick-nav {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
</style>
