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
          v-if="permission.showCreateRoleButton()"
          type="primary" 
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon active">
                <el-icon><User /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ activeRoles }}</div>
                <div class="stats-label">启用角色</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon inactive">
                <el-icon><Close /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ inactiveRoles }}</div>
                <div class="stats-label">禁用角色</div>
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
                <div class="stats-number">{{ total }}</div>
                <div class="stats-label">总角色数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon users">
                <el-icon><User /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ totalUsers }}</div>
                <div class="stats-label">关联用户</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 角色列表 -->
    <el-card class="table-card">
      <el-table 
        :data="roles" 
        :loading="loading"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="jiaose_ming" label="角色名称" min-width="120">
          <template #default="{ row }">
            <div class="role-name">
              <el-tag 
                :type="row.zhuangtai === 'active' ? 'success' : 'danger'"
                size="small"
                style="margin-right: 8px"
              >
                {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
              </el-tag>
              {{ row.jiaose_ming }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="jiaose_bianma" label="角色编码" min-width="120" />
        
        <el-table-column prop="miaoshu" label="角色描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column label="权限数量" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ row.permissions?.length || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="关联用户" width="100">
          <template #default="{ row }">
            <el-tag type="primary" size="small">
              {{ row.users?.length || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="permission.canViewRoles()"
              type="primary" 
              size="small" 
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button 
              v-if="permission.showEditRoleButton()"
              type="success" 
              size="small" 
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-dropdown 
              v-if="permission.showPermissionManageButton() || permission.showDeleteRoleButton()"
              @command="(command) => handleDropdownCommand(command, row)"
            >
              <el-button size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item 
                    v-if="permission.showPermissionManageButton()"
                    command="permissions"
                  >
                    权限管理
                  </el-dropdown-item>
                  <el-dropdown-item 
                    v-if="permission.showStatusManageButton()"
                    command="status"
                  >
                    状态管理
                  </el-dropdown-item>
                  <el-dropdown-item 
                    v-if="permission.showDeleteRoleButton()"
                    command="delete" 
                    divided
                  >
                    删除角色
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
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

    <!-- 角色表单对话框 -->
    <!-- <RoleForm
      v-model:visible="formVisible"
      :mode="formMode"
      :role="currentRole"
      @success="handleFormSuccess"
    /> -->

    <!-- 权限管理对话框 -->
    <!-- <RolePermissionDialog
      v-model:visible="permissionDialogVisible"
      :role="currentRole"
      @success="handlePermissionSuccess"
    /> -->

    <!-- 状态管理对话框 -->
    <!-- <RoleStatusDialog
      v-model:visible="statusDialogVisible"
      :role="currentRole"
      @success="handleStatusSuccess"
    /> -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, 
  Refresh, 
  Plus, 
  User, 
  Close, 
  DataAnalysis,
  ArrowDown
} from '@element-plus/icons-vue'
// import { useRoleStore } from '@/stores/modules/role'
import { usePermission } from '@/utils/permissions'
// import RoleForm from './components/RoleForm.vue'
// import RolePermissionDialog from './components/RolePermissionDialog.vue'
// import RoleStatusDialog from './components/RoleStatusDialog.vue'
// import type { Role } from '@/api/modules/role'

const router = useRouter()
// const roleStore = useRoleStore()
const permission = usePermission()

// 响应式数据
const searchForm = ref({
  search: '',
  zhuangtai: ''
})

const formVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const currentRole = ref<Role | null>(null)
const permissionDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const selectedRoles = ref<Role[]>([])

// 模拟数据
const roles = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const activeRoles = ref(0)
const inactiveRoles = ref(0)
const totalUsers = ref(0)

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 事件处理
const handleSearch = async () => {
  console.log('搜索角色:', searchForm.value)
  // TODO: 实现搜索逻辑
}

const handleReset = () => {
  searchForm.value = {
    search: '',
    zhuangtai: ''
  }
  handleSearch()
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

const handleDropdownCommand = (command: string, role: Role) => {
  currentRole.value = role
  
  switch (command) {
    case 'permissions':
      permissionDialogVisible.value = true
      break
    case 'status':
      statusDialogVisible.value = true
      break
    case 'delete':
      handleDelete(role)
      break
  }
}

const handleDelete = async (role: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色"${role.jiaose_ming}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    console.log('删除角色:', role.id)
    ElMessage.success('角色删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('角色删除失败')
    }
  }
}

const handleSelectionChange = (selection: any[]) => {
  selectedRoles.value = selection
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  handleSearch()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  handleSearch()
}

const handleFormSuccess = () => {
  formVisible.value = false
  handleSearch()
}

const handlePermissionSuccess = () => {
  permissionDialogVisible.value = false
  handleSearch()
}

const handleStatusSuccess = () => {
  statusDialogVisible.value = false
  handleSearch()
}

// 初始化
onMounted(() => {
  handleSearch()
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

.stats-icon.active {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stats-icon.inactive {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.stats-icon.total {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.stats-icon.users {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
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

.role-name {
  display: flex;
  align-items: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
