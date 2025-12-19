<template>
  <el-dialog
    v-model="visible"
    title="分配角色"
    width="500px"
    :before-close="handleClose"
  >
    <div v-loading="loading" class="role-assign-container">
      <div class="user-info">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="用户名">
            {{ userInfo?.yonghu_ming }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ userInfo?.xingming }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="role-selection">
        <h4>选择角色</h4>
        <el-checkbox-group v-model="selectedRoles">
          <el-checkbox
            v-for="role in availableRoles"
            :key="role.id"
            :value="role.id"
            :label="role.id"
          >
            <div class="role-item">
              <div class="role-name">{{ role.jiaose_ming }}</div>
              <div class="role-desc">{{ role.miaoshu || '暂无描述' }}</div>
            </div>
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <div v-if="selectedRoles.length > 0" class="selected-roles">
        <h4>已选择的角色</h4>
        <el-tag
          v-for="roleId in selectedRoles"
          :key="roleId"
          class="role-tag"
          type="primary"
          closable
          @close="handleRemoveRole(roleId)"
        >
          {{ getRoleName(roleId) }}
        </el-tag>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi, roleApi } from '@/api/modules/user'
import type { User, Role } from '@/types/user'

interface Props {
  visible: boolean
  userId: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const userInfo = ref<User | null>(null)
const availableRoles = ref<Role[]>([])
const selectedRoles = ref<string[]>([])

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 获取角色名称
const getRoleName = (roleId: string) => {
  const role = availableRoles.value.find(r => r.id === roleId)
  return role?.jiaose_ming || ''
}

// 获取用户信息
const fetchUserInfo = async () => {
  if (!props.userId) return
  
  try {
    userInfo.value = await userApi.getUserById(props.userId)
    // 设置当前用户的角色
    selectedRoles.value = userInfo.value.roles?.map(role => role.id) || []
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

// 获取可用角色列表
const fetchAvailableRoles = async () => {
  try {
    const response = await roleApi.getRoleList({ page: 1, size: 100 })
    availableRoles.value = response.items
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  }
}

// 初始化数据
const initData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchUserInfo(),
      fetchAvailableRoles()
    ])
  } finally {
    loading.value = false
  }
}

// 移除角色
const handleRemoveRole = (roleId: string) => {
  const index = selectedRoles.value.indexOf(roleId)
  if (index > -1) {
    selectedRoles.value.splice(index, 1)
  }
}

// 提交角色分配
const handleSubmit = async () => {
  try {
    submitting.value = true
    await userApi.assignRoles(props.userId, selectedRoles.value)
    ElMessage.success('角色分配成功')
    emit('success')
  } catch (error) {
    ElMessage.error('角色分配失败')
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  selectedRoles.value = []
  userInfo.value = null
}

// 监听对话框显示状态
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible && props.userId) {
      initData()
    }
  }
)
</script>

<style scoped>
.role-assign-container {
  min-height: 300px;
}

.user-info {
  margin-bottom: 20px;
}

.role-selection {
  margin-bottom: 20px;
}

.role-selection h4,
.selected-roles h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.role-item {
  margin-left: 8px;
}

.role-name {
  font-weight: 500;
  color: #303133;
}

.role-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.selected-roles {
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.role-tag {
  margin: 4px 8px 4px 0;
}

.dialog-footer {
  text-align: right;
}
</style>
