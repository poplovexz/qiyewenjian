<template>
  <div class="user-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">用户管理</h1>
        <p class="page-description">管理系统用户账户、角色和权限</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="handleCreate"
          v-if="hasPermission('user:create')"
        >
          新增用户
        </el-button>
      </div>
    </div>

    <!-- 搜索筛选区域 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.yonghu_ming"
            placeholder="请输入用户名"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input
            v-model="searchForm.xingming"
            placeholder="请输入姓名"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.zhuangtai"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="yonghu_ming" label="用户名" width="120" />
        <el-table-column prop="xingming" label="姓名" width="100" />
        <el-table-column prop="youxiang" label="邮箱" width="200" />
        <el-table-column prop="shouji" label="手机号" width="130" />
        <el-table-column prop="zhuangtai" label="状态" width="80">
          <template #default="{ row }">
            <el-tag
              :type="row.zhuangtai === 'active' ? 'success' : 'danger'"
              size="small"
            >
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="denglu_cishu" label="登录次数" width="100" />
        <el-table-column prop="zuihou_denglu" label="最后登录" width="160">
          <template #default="{ row }">
            {{ row.zuihou_denglu ? formatDateTime(row.zuihou_denglu) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="handleView(row)"
              v-if="hasPermission('user:read')"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
              v-if="hasPermission('user:update')"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
              v-if="hasPermission('user:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 用户详情对话框 -->
    <UserDetail
      v-model:visible="detailVisible"
      :user-id="selectedUserId"
      @refresh="fetchUserList"
    />

    <!-- 用户编辑对话框 -->
    <UserForm
      v-model:visible="formVisible"
      :user-id="selectedUserId"
      :mode="formMode"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import { userApi } from '@/api/modules/user'
import { useAuthStore } from '@/stores/modules/auth'
import { formatDateTime } from '@/utils/date'
import UserDetail from '@/components/user/UserDetail.vue'
import UserForm from '@/components/user/UserForm.vue'
import type { User, UserListParams } from '@/types/user'

// 权限检查
const authStore = useAuthStore()
const hasPermission = (permission: string) => {
  return authStore.hasPermission(permission)
}

// 响应式数据
const loading = ref(false)
const userList = ref<User[]>([])
const detailVisible = ref(false)
const formVisible = ref(false)
const selectedUserId = ref<string>('')
const formMode = ref<'create' | 'edit'>('create')

// 搜索表单
const searchForm = reactive<UserListParams>({
  page: 1,
  size: 20,
  yonghu_ming: '',
  xingming: '',
  zhuangtai: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取用户列表
const fetchUserList = async () => {
  try {
    loading.value = true
    const params = {
      ...searchForm,
      page: pagination.page,
      size: pagination.size
    }
    
    const response = await userApi.getUserList(params)
    userList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchUserList()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    page: 1,
    size: 20,
    yonghu_ming: '',
    xingming: '',
    zhuangtai: ''
  })
  pagination.page = 1
  fetchUserList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  fetchUserList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchUserList()
}

// 操作处理
const handleCreate = () => {
  selectedUserId.value = ''
  formMode.value = 'create'
  formVisible.value = true
}

const handleView = (row: User) => {
  selectedUserId.value = row.id
  detailVisible.value = true
}

const handleEdit = (row: User) => {
  selectedUserId.value = row.id
  formMode.value = 'edit'
  formVisible.value = true
}

const handleDelete = async (row: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.xingming}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await userApi.deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除用户失败')
    }
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  fetchUserList()
}

// 初始化
onMounted(() => {
  fetchUserList()
})
</script>

<style scoped>
.user-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 4px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
