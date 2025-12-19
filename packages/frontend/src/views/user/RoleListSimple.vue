<template>
  <div class="role-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>角色管理</h2>
      <p>管理系统角色和权限分配</p>
    </div>

    <!-- 搜索和操作栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索角色名称、编码..."
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-button @click="handleSearch" style="margin-left: 10px">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <div class="search-right">
        <el-button type="primary" @click="handleCreate" v-if="hasPermission('role:create')">
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
        <el-button @click="handleRefresh"> 刷新 </el-button>
      </div>
    </div>

    <!-- 角色列表 -->
    <el-card class="table-card">
      <el-table :data="roleStore.roles" :loading="roleStore.loading" stripe style="width: 100%">
        <el-table-column prop="jiaose_ming" label="角色名称" min-width="120" />
        <el-table-column prop="jiaose_bianma" label="角色编码" min-width="120" />
        <el-table-column prop="miaoshu" label="角色描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.zhuangtai === 'active' ? 'success' : 'danger'" size="small">
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
              v-if="hasPermission('role:read')"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEdit(row)"
              v-if="hasPermission('role:update')"
            >
              编辑
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="handlePermissions(row)"
              v-if="hasPermission('role:permission_manage')"
            >
              权限
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              v-if="hasPermission('role:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 角色表单对话框 -->
    <RoleForm
      v-model:visible="formVisible"
      :role="currentRole"
      :mode="formMode"
      @success="handleFormSuccess"
    />

    <!-- 权限管理对话框 -->
    <RolePermissionDialog
      v-model:visible="permissionVisible"
      :role="currentRole"
      @success="handlePermissionSuccess"
    />

    <!-- 状态管理对话框 -->
    <RoleStatusDialog
      v-model:visible="statusVisible"
      :role="currentRole"
      @success="handleStatusSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { useRoleStore } from '@/stores/modules/role'
import { hasPermission } from '@/utils/permissions'
import type { Role } from '@/api/modules/role'
import RoleForm from './components/RoleForm.vue'
import RolePermissionDialog from './components/RolePermissionDialog.vue'
import RoleStatusDialog from './components/RoleStatusDialog.vue'

// Store
const roleStore = useRoleStore()

// 响应式数据
const searchForm = ref({
  search: '',
  zhuangtai: '',
})

const formVisible = ref(false)
const permissionVisible = ref(false)
const statusVisible = ref(false)
const currentRole = ref<Role | null>(null)
const formMode = ref<'create' | 'edit' | 'view'>('create')

// 方法
const handleSearch = async () => {
  await roleStore.getRoleList(searchForm.value)
}

const handleRefresh = async () => {
  searchForm.value = { search: '', zhuangtai: '' }
  await roleStore.getRoleList()
}

const handleCreate = () => {
  currentRole.value = null
  formMode.value = 'create'
  formVisible.value = true
}

const handleView = (role: Role) => {
  currentRole.value = role
  formMode.value = 'view'
  formVisible.value = true
}

const handleEdit = (role: Role) => {
  currentRole.value = role
  formMode.value = 'edit'
  formVisible.value = true
}

const handlePermissions = (role: Role) => {
  currentRole.value = role
  permissionVisible.value = true
}

const handleStatusChange = (role: Role) => {
  currentRole.value = role
  statusVisible.value = true
}

const handleDelete = async (role: Role) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.jiaose_ming}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await roleStore.deleteRole(role.id)
  } catch (error) {
    if (error !== 'cancel') {
    }
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  handleRefresh()
}

const handlePermissionSuccess = () => {
  permissionVisible.value = false
  handleRefresh()
}

const handleStatusSuccess = () => {
  statusVisible.value = false
  handleRefresh()
}

// 生命周期
onMounted(() => {
  handleRefresh()
})
</script>

<style scoped>
.role-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-left {
  display: flex;
  align-items: center;
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
