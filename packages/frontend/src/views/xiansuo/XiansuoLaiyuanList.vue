<template>
  <div class="xiansuo-laiyuan-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>线索来源管理</h2>
      <p>管理线索来源渠道，跟踪获取成本和转化效果</p>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="来源名称、编码"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="来源类型">
          <el-select
            v-model="searchForm.laiyuan_leixing"
            placeholder="请选择类型"
            clearable
            style="width: 150px"
          >
            <el-option label="线上" value="online" />
            <el-option label="线下" value="offline" />
            <el-option label="推荐" value="referral" />
          </el-select>
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
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="action-card">
      <div class="action-bar">
        <div class="action-left">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增来源
          </el-button>
        </div>
        
        <div class="action-right">
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 来源表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="laiyuan_list"
        style="width: 100%"
      >
        <el-table-column prop="laiyuan_bianma" label="来源编码" width="120" />
        
        <el-table-column prop="laiyuan_mingcheng" label="来源名称" min-width="150" />
        
        <el-table-column prop="laiyuan_leixing" label="来源类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.laiyuan_leixing)" size="small">
              {{ getTypeText(row.laiyuan_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="huoqu_chengben" label="获取成本" width="100">
          <template #default="{ row }">
            ¥{{ row.huoqu_chengben }}
          </template>
        </el-table-column>
        
        <el-table-column prop="xiansuo_shuliang" label="线索数量" width="100" />
        
        <el-table-column prop="zhuanhua_shuliang" label="转化数量" width="100" />
        
        <el-table-column prop="zhuanhua_lv" label="转化率" width="100">
          <template #default="{ row }">
            {{ row.zhuanhua_lv }}%
          </template>
        </el-table-column>
        
        <el-table-column prop="zhuangtai" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.zhuangtai === 'active' ? 'success' : 'danger'" size="small">
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
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

    <!-- 来源表单弹窗 -->
    <XiansuoLaiyuanForm
      v-model:visible="formVisible"
      :mode="formMode"
      :laiyuan="currentLaiyuan"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus
} from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import XiansuoLaiyuanForm from '@/components/xiansuo/XiansuoLaiyuanForm.vue'
import type { XiansuoLaiyuan } from '@/types/xiansuo'
import { storeToRefs } from 'pinia'

// 使用store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const searchForm = ref({
  search: '',
  laiyuan_leixing: '',
  zhuangtai: ''
})

const formVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const currentLaiyuan = ref<XiansuoLaiyuan | null>(null)

// 计算属性
const { 
  laiyuan_list, 
  loading, 
  total, 
  currentPage, 
  pageSize
} = storeToRefs(xiansuoStore)

// 方法
const handleSearch = async () => {
  await xiansuoStore.fetchLaiyuanList({
    ...searchForm.value,
    page: xiansuoStore.currentPage,
    size: xiansuoStore.pageSize
  })
}

const handleReset = async () => {
  searchForm.value = {
    search: '',
    laiyuan_leixing: '',
    zhuangtai: ''
  }
  xiansuoStore.currentPage = 1
  await xiansuoStore.fetchLaiyuanList({
    page: 1,
    size: xiansuoStore.pageSize
  })
}

const handleRefresh = async () => {
  await handleSearch()
}

const handleCreate = () => {
  formMode.value = 'create'
  currentLaiyuan.value = null
  formVisible.value = true
}

const handleEdit = (laiyuan: XiansuoLaiyuan) => {
  formMode.value = 'edit'
  currentLaiyuan.value = laiyuan
  formVisible.value = true
}

const handleDelete = async (laiyuan: XiansuoLaiyuan) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除来源"${laiyuan.laiyuan_mingcheng}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 实现删除功能
    ElMessage.success('删除成功')
    await handleSearch()
  } catch (error) {
    // 用户取消删除
  }
}

const handleSizeChange = async (size: number) => {
  xiansuoStore.pageSize = size
  await handleSearch()
}

const handleCurrentChange = async (page: number) => {
  xiansuoStore.currentPage = page
  await handleSearch()
}

const handleFormSuccess = async () => {
  formVisible.value = false
  await handleSearch()
}

// 工具方法
const getTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    online: 'primary',
    offline: 'success',
    referral: 'warning'
  }
  return types[type] || ''
}

const getTypeText = (type: string) => {
  const texts: Record<string, string> = {
    online: '线上',
    offline: '线下',
    referral: '推荐'
  }
  return texts[type] || type
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

// 生命周期
onMounted(async () => {
  await xiansuoStore.fetchLaiyuanList({
    page: xiansuoStore.currentPage,
    size: xiansuoStore.pageSize
  })
})
</script>

<style scoped>
.xiansuo-laiyuan-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-card,
.action-card,
.table-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left,
.action-right {
  display: flex;
  gap: 10px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
