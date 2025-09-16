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
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
      </div>
    </div>

    <!-- 角色列表 -->
    <el-card class="table-card">
      <el-table 
        :data="roles" 
        :loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="jiaose_ming" label="角色名称" min-width="120" />
        <el-table-column prop="jiaose_bianma" label="角色编码" min-width="120" />
        <el-table-column prop="miaoshu" label="角色描述" min-width="200" show-overflow-tooltip />
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="success" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
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

// 响应式数据
const searchForm = ref({
  search: ''
})

const loading = ref(false)

// 模拟角色数据
const roles = ref([
  {
    id: '1',
    jiaose_ming: '系统管理员',
    jiaose_bianma: 'admin',
    miaoshu: '系统最高权限管理员',
    zhuangtai: 'active'
  },
  {
    id: '2',
    jiaose_ming: '会计',
    jiaose_bianma: 'accountant',
    miaoshu: '负责财务处理和账务管理',
    zhuangtai: 'active'
  },
  {
    id: '3',
    jiaose_ming: '客服',
    jiaose_bianma: 'customer_service',
    miaoshu: '负责客户服务和沟通',
    zhuangtai: 'active'
  }
])

// 事件处理
const handleSearch = () => {
  console.log('搜索角色:', searchForm.value.search)
  ElMessage.info('搜索功能开发中...')
}

const handleCreate = () => {
  console.log('创建角色')
  ElMessage.info('创建角色功能开发中...')
}

const handleView = (role: any) => {
  console.log('查看角色:', role)
  ElMessage.info(`查看角色: ${role.jiaose_ming}`)
}

const handleEdit = (role: any) => {
  console.log('编辑角色:', role)
  ElMessage.info(`编辑角色: ${role.jiaose_ming}`)
}

const handleDelete = async (role: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色"${role.jiaose_ming}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('删除角色:', role)
    ElMessage.success('角色删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('角色删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  console.log('角色管理页面已加载')
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
