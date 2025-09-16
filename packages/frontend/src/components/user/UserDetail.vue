<template>
  <el-dialog
    v-model="visible"
    title="用户详情"
    width="800px"
    :before-close="handleClose"
  >
    <div v-loading="loading" class="user-detail">
      <template v-if="userInfo">
        <!-- 基本信息 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">基本信息</span>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户名">
              {{ userInfo.yonghu_ming }}
            </el-descriptions-item>
            <el-descriptions-item label="姓名">
              {{ userInfo.xingming }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userInfo.youxiang }}
            </el-descriptions-item>
            <el-descriptions-item label="手机号">
              {{ userInfo.shouji }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag
                :type="userInfo.zhuangtai === 'active' ? 'success' : 'danger'"
                size="small"
              >
                {{ userInfo.zhuangtai === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="登录次数">
              {{ userInfo.denglu_cishu }}
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ userInfo.zuihou_denglu ? formatDateTime(userInfo.zuihou_denglu) : '从未登录' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(userInfo.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 角色信息 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">角色信息</span>
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEditRoles"
                v-if="hasPermission('user:assign_roles')"
              >
                分配角色
              </el-button>
            </div>
          </template>
          
          <div class="roles-container">
            <template v-if="userInfo.roles && userInfo.roles.length > 0">
              <el-tag
                v-for="role in userInfo.roles"
                :key="role.id"
                class="role-tag"
                type="primary"
              >
                {{ role.jiaose_mingcheng }}
              </el-tag>
            </template>
            <el-empty v-else description="暂无角色" :image-size="60" />
          </div>
        </el-card>

        <!-- 权限信息 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">权限信息</span>
            </div>
          </template>
          
          <div class="permissions-container">
            <template v-if="userInfo.permissions && userInfo.permissions.length > 0">
              <el-tag
                v-for="permission in userInfo.permissions"
                :key="permission.id"
                class="permission-tag"
                type="info"
              >
                {{ permission.quanxian_mingcheng }}
              </el-tag>
            </template>
            <el-empty v-else description="暂无权限" :image-size="60" />
          </div>
        </el-card>
      </template>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          type="primary"
          :icon="Edit"
          @click="handleEdit"
          v-if="hasPermission('user:update')"
        >
          编辑用户
        </el-button>
      </div>
    </template>

    <!-- 角色分配对话框 -->
    <UserRoleAssign
      v-model:visible="roleAssignVisible"
      :user-id="userId"
      @success="handleRoleAssignSuccess"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { userApi } from '@/api/modules/user'
import { useAuthStore } from '@/stores/modules/auth'
import { formatDateTime } from '@/utils/date'
import UserRoleAssign from './UserRoleAssign.vue'
import type { User } from '@/types/user'

interface Props {
  visible: boolean
  userId: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'refresh'): void
  (e: 'edit', userId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 权限检查
const authStore = useAuthStore()
const hasPermission = (permission: string) => {
  return authStore.hasPermission(permission)
}

// 响应式数据
const loading = ref(false)
const userInfo = ref<User | null>(null)
const roleAssignVisible = ref(false)

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 获取用户详情
const fetchUserDetail = async () => {
  if (!props.userId) return
  
  try {
    loading.value = true
    userInfo.value = await userApi.getUserById(props.userId)
  } catch (error) {
    console.error('获取用户详情失败:', error)
    ElMessage.error('获取用户详情失败')
  } finally {
    loading.value = false
  }
}

// 事件处理
const handleClose = () => {
  visible.value = false
  userInfo.value = null
}

const handleEdit = () => {
  emit('edit', props.userId)
  handleClose()
}

const handleEditRoles = () => {
  roleAssignVisible.value = true
}

const handleRoleAssignSuccess = () => {
  roleAssignVisible.value = false
  fetchUserDetail()
  emit('refresh')
}

// 监听用户ID变化
watch(
  () => props.userId,
  (newUserId) => {
    if (newUserId && props.visible) {
      fetchUserDetail()
    }
  },
  { immediate: true }
)

// 监听对话框显示状态
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible && props.userId) {
      fetchUserDetail()
    }
  }
)
</script>

<style scoped>
.user-detail {
  min-height: 400px;
}

.info-card {
  margin-bottom: 20px;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
}

.roles-container,
.permissions-container {
  min-height: 60px;
}

.role-tag,
.permission-tag {
  margin: 4px 8px 4px 0;
}

.dialog-footer {
  text-align: right;
}
</style>
