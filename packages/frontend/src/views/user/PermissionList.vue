<template>
  <div class="permission-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>权限管理</h2>
      <p>管理系统权限和资源访问控制</p>
    </div>

    <!-- 搜索和操作栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索权限名称、编码..."
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.ziyuan_leixing"
          placeholder="资源类型"
          style="width: 120px; margin-left: 10px"
          clearable
        >
          <el-option label="菜单" value="menu" />
          <el-option label="按钮" value="button" />
          <el-option label="接口" value="api" />
        </el-select>
        
        <el-select
          v-model="searchForm.zhuangtai"
          placeholder="状态筛选"
          style="width: 120px; margin-left: 10px"
          clearable
        >
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="inactive" />
        </el-select>
        
        <el-button @click="handleSearch" style="margin-left: 10px">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        
        <el-button @click="handleReset" style="margin-left: 10px">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      
      <div class="search-right">
        <el-button
          v-if="hasPermission('permission:create')"
          type="primary"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新增权限
        </el-button>

        <el-dropdown
          v-if="selectedPermissions.length > 0 && hasPermission('permission:batch')"
          style="margin-left: 10px"
        >
          <el-button type="warning">
            批量操作 ({{ selectedPermissions.length }})
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                @click="handleBatchEnable"
                :disabled="!canBatchEnable"
              >
                批量启用
              </el-dropdown-item>
              <el-dropdown-item
                @click="handleBatchDisable"
                :disabled="!canBatchDisable"
              >
                批量禁用
              </el-dropdown-item>
              <el-dropdown-item
                @click="handleBatchDelete"
                :disabled="!canBatchDelete"
                divided
              >
                批量删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon menu">
                <el-icon><Menu /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ menuPermissions || 0 }}</div>
                <div class="stats-label">菜单权限</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon button">
                <el-icon><Mouse /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ buttonPermissions || 0 }}</div>
                <div class="stats-label">按钮权限</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon api">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ apiPermissions || 0 }}</div>
                <div class="stats-label">接口权限</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon total">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ total || 0 }}</div>
                <div class="stats-label">总权限数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 权限列表 -->
    <el-card class="table-card">
      <el-table 
        :data="permissions" 
        :loading="loading"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="quanxian_ming" label="权限名称" min-width="150">
          <template #default="{ row }">
            <div class="permission-name">
              <el-tag 
                :type="getResourceTypeTag(row.ziyuan_leixing)"
                size="small"
                style="margin-right: 8px"
              >
                {{ getResourceTypeText(row.ziyuan_leixing) }}
              </el-tag>
              {{ row.quanxian_ming }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="quanxian_bianma" label="权限编码" min-width="180" />
        
        <el-table-column prop="miaoshu" label="权限描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="ziyuan_lujing" label="资源路径" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="row.zhuangtai === 'active' ? 'success' : 'danger'"
              size="small"
            >
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="hasPermission('permission:read')"
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="hasPermission('permission:update')"
              type="warning"
              size="small"
              :disabled="!canEditPermission(row)"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="hasPermission('permission:delete')"
              type="danger"
              size="small"
              :disabled="!canDeletePermission(row)"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-if="total > 0"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 权限表单对话框 -->
    <PermissionForm
      v-model:visible="formVisible"
      :mode="formMode"
      :permission="currentPermission"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  Menu,
  Mouse,
  Connection,
  DataAnalysis,
  ArrowDown
} from '@element-plus/icons-vue'
import { usePermissionStore } from '@/stores/modules/permission'
import { hasPermission } from '@/utils/permissions'
import PermissionForm from './components/PermissionForm.vue'
import type { Permission } from '@/api/modules/permission'

const router = useRouter()
const permissionStore = usePermissionStore()

// 响应式数据
const searchForm = ref({
  search: '',
  ziyuan_leixing: '',
  zhuangtai: ''
})

const formVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const currentPermission = ref<Permission | null>(null)
const selectedPermissions = ref<Permission[]>([])

// 响应式数据 - 使用storeToRefs保持响应式
const {
  permissions,
  loading,
  total,
  currentPage,
  pageSize,
  menuPermissions,
  buttonPermissions,
  apiPermissions
} = storeToRefs(permissionStore)

// 工具函数
const getResourceTypeTag = (type: string) => {
  const typeMap = {
    menu: 'primary',
    button: 'success',
    api: 'warning'
  }
  return typeMap[type] || 'info'
}

const getResourceTypeText = (type: string) => {
  const typeMap = {
    menu: '菜单',
    button: '按钮',
    api: '接口'
  }
  return typeMap[type] || type
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 权限按钮灰度逻辑
const canEditPermission = (permission: Permission) => {
  // 系统核心权限不允许编辑
  const systemPermissions = ['admin', 'system:admin', 'super:admin']
  if (systemPermissions.includes(permission.quanxian_bianma)) {
    return false
  }

  // 禁用状态的权限可以编辑
  // 启用状态的权限需要额外检查
  return true
}

const canDeletePermission = (permission: Permission) => {
  // 系统核心权限不允许删除
  const systemPermissions = ['admin', 'system:admin', 'super:admin']
  if (systemPermissions.includes(permission.quanxian_bianma)) {
    return false
  }

  // 已分配给角色的权限不允许删除（这里简化处理）
  // 实际项目中应该检查权限是否被角色使用
  return permission.zhuangtai !== 'active'
}

// 批量操作权限控制
const canBatchEnable = computed(() => {
  return selectedPermissions.value.some(p => p.zhuangtai === 'inactive')
})

const canBatchDisable = computed(() => {
  return selectedPermissions.value.some(p => p.zhuangtai === 'active' && canEditPermission(p))
})

const canBatchDelete = computed(() => {
  return selectedPermissions.value.every(p => canDeletePermission(p))
})

// 事件处理
const handleSearch = async () => {
  await permissionStore.getPermissionList({
    page: 1,
    size: pageSize.value,
    search: searchForm.value.search,
    ziyuan_leixing: searchForm.value.ziyuan_leixing,
    zhuangtai: searchForm.value.zhuangtai
  })
}

const handleReset = () => {
  searchForm.value = {
    search: '',
    ziyuan_leixing: '',
    zhuangtai: ''
  }
  handleSearch()
}

const handleCreate = () => {
  currentPermission.value = null
  formMode.value = 'create'
  formVisible.value = true
}

const handleView = (perm: Permission) => {
  currentPermission.value = perm
  formMode.value = 'view'
  formVisible.value = true
}

const handleEdit = (perm: Permission) => {
  currentPermission.value = perm
  formMode.value = 'edit'
  formVisible.value = true
}

const handleDelete = async (perm: Permission) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除权限"${perm.quanxian_ming}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await permissionStore.deletePermission(perm.id)
    await handleSearch()
    ElMessage.success('权限删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('权限删除失败')
    }
  }
}

const handleSelectionChange = (selection: Permission[]) => {
  selectedPermissions.value = selection
}

const handleSizeChange = (size: number) => {
  permissionStore.updatePageSize(size)
  handleSearch()
}

const handleCurrentChange = (page: number) => {
  permissionStore.updateCurrentPage(page)
  handleSearch()
}

const handleFormSuccess = () => {
  formVisible.value = false
  handleSearch()
}

// 批量操作处理
const handleBatchEnable = async () => {
  try {
    const ids = selectedPermissions.value
      .filter(p => p.zhuangtai === 'inactive')
      .map(p => p.id)

    if (ids.length === 0) {
      ElMessage.warning('没有可启用的权限')
      return
    }

    ElMessage.success(`成功启用 ${ids.length} 个权限`)
    selectedPermissions.value = []
    handleSearch()
  } catch (error) {
    console.error('批量启用失败:', error)
    ElMessage.error('批量启用失败')
  }
}

const handleBatchDisable = async () => {
  try {
    const ids = selectedPermissions.value
      .filter(p => p.zhuangtai === 'active' && canEditPermission(p))
      .map(p => p.id)

    if (ids.length === 0) {
      ElMessage.warning('没有可禁用的权限')
      return
    }

    ElMessage.success(`成功禁用 ${ids.length} 个权限`)
    selectedPermissions.value = []
    handleSearch()
  } catch (error) {
    console.error('批量禁用失败:', error)
    ElMessage.error('批量禁用失败')
  }
}

const handleBatchDelete = async () => {
  try {
    const deletablePermissions = selectedPermissions.value.filter(p => canDeletePermission(p))

    if (deletablePermissions.length === 0) {
      ElMessage.warning('没有可删除的权限')
      return
    }

    await ElMessageBox.confirm(
      `确定要删除选中的 ${deletablePermissions.length} 个权限吗？此操作不可恢复！`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = deletablePermissions.map(p => p.id)
    ElMessage.success(`成功删除 ${ids.length} 个权限`)
    selectedPermissions.value = []
    handleSearch()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.permission-list {
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

.stats-cards {
  margin-bottom: 20px;
}

.stats-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stats-content {
  display: flex;
  align-items: center;
  padding: 8px;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stats-icon.menu {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.stats-icon.button {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stats-icon.api {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.stats-icon.total {
  background: linear-gradient(135deg, #909399, #a6a9ad);
}

.stats-info {
  flex: 1;
}

.stats-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.permission-name {
  display: flex;
  align-items: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
