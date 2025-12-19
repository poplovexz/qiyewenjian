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

        <el-button @click="handleSearch" style="margin-left: 10px">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <div class="search-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增权限
        </el-button>
      </div>
    </div>

    <!-- 权限列表 -->
    <el-card class="table-card">
      <el-table :data="permissions" :loading="loading" stripe style="width: 100%">
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
        <el-table-column
          prop="ziyuan_lujing"
          label="资源路径"
          min-width="200"
          show-overflow-tooltip
        />

        <el-table-column prop="zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.zhuangtai === 'active' ? 'success' : 'danger'" size="small">
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)"> 查看 </el-button>
            <el-button type="success" size="small" @click="handleEdit(row)"> 编辑 </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)"> 删除 </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'

// 权限类型
interface Permission {
  id: string
  quanxian_ming: string
  quanxian_bianma: string
  miaoshu?: string
  ziyuan_leixing: string
  ziyuan_lujing?: string
  zhuangtai: string
}

// 响应式数据
const searchForm = ref({
  search: '',
  ziyuan_leixing: '',
})

const loading = ref(false)

// 模拟权限数据
const permissions = ref([
  {
    id: '1',
    quanxian_ming: '用户管理菜单',
    quanxian_bianma: 'user:menu',
    miaoshu: '访问用户管理菜单的权限',
    ziyuan_leixing: 'menu',
    ziyuan_lujing: '/users',
    zhuangtai: 'active',
  },
  {
    id: '2',
    quanxian_ming: '查看用户',
    quanxian_bianma: 'user:read',
    miaoshu: '查看用户信息的权限',
    ziyuan_leixing: 'api',
    ziyuan_lujing: '/users/*',
    zhuangtai: 'active',
  },
  {
    id: '3',
    quanxian_ming: '新增用户按钮',
    quanxian_bianma: 'user:create_button',
    miaoshu: '显示新增用户按钮的权限',
    ziyuan_leixing: 'button',
    ziyuan_lujing: 'user-create-btn',
    zhuangtai: 'active',
  },
  {
    id: '4',
    quanxian_ming: '客户管理菜单',
    quanxian_bianma: 'customer:menu',
    miaoshu: '访问客户管理菜单的权限',
    ziyuan_leixing: 'menu',
    ziyuan_lujing: '/customers',
    zhuangtai: 'active',
  },
])

// 工具函数
const getResourceTypeTag = (type: string) => {
  const typeMap = {
    menu: 'primary',
    button: 'success',
    api: 'warning',
  }
  return typeMap[type] || 'info'
}

const getResourceTypeText = (type: string) => {
  const typeMap = {
    menu: '菜单',
    button: '按钮',
    api: '接口',
  }
  return typeMap[type] || type
}

// 事件处理
const handleSearch = () => {
  ElMessage.info('搜索功能开发中...')
}

const handleCreate = () => {
  ElMessage.info('创建权限功能开发中...')
}

const handleView = (permission: Permission) => {
  ElMessage.info(`查看权限: ${permission.quanxian_ming}`)
}

const handleEdit = (permission: Permission) => {
  ElMessage.info(`编辑权限: ${permission.quanxian_ming}`)
}

const handleDelete = async (permission: Permission) => {
  try {
    await ElMessageBox.confirm(`确定要删除权限"${permission.quanxian_ming}"吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    ElMessage.success('权限删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('权限删除失败')
    }
  }
}

// 初始化
onMounted(() => {})
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

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.permission-name {
  display: flex;
  align-items: center;
}
</style>
