<template>
  <div class="xiansuo-zhuangtai-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>线索状态管理</h2>
      <p>管理线索状态流转，配置工作流程</p>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="状态名称、编码"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="状态类型">
          <el-select
            v-model="searchForm.zhuangtai_leixing"
            placeholder="请选择类型"
            clearable
            style="width: 150px"
          >
            <el-option label="初始状态" value="initial" />
            <el-option label="处理中" value="processing" />
            <el-option label="成功状态" value="success" />
            <el-option label="失败状态" value="failed" />
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
            新增状态
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

    <!-- 状态表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="zhuangtai_list"
        style="width: 100%"
      >
        <el-table-column prop="zhuangtai_bianma" label="状态编码" width="120" />
        
        <el-table-column prop="zhuangtai_mingcheng" label="状态名称" min-width="150" />
        
        <el-table-column prop="zhuangtai_leixing" label="状态类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.zhuangtai_leixing)" size="small">
              {{ getTypeText(row.zhuangtai_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="yanse_bianma" label="颜色" width="80">
          <template #default="{ row }">
            <div 
              class="color-block" 
              :style="{ backgroundColor: row.yanse_bianma || '#409eff' }"
            ></div>
          </template>
        </el-table-column>
        
        <el-table-column prop="shi_chenggong_zhuangtai" label="成功状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.shi_chenggong_zhuangtai === 'Y' ? 'success' : 'info'" size="small">
              {{ row.shi_chenggong_zhuangtai === 'Y' ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="shi_zhongzhong_zhuangtai" label="终止状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.shi_zhongzhong_zhuangtai === 'Y' ? 'danger' : 'info'" size="small">
              {{ row.shi_zhongzhong_zhuangtai === 'Y' ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="paixu" label="排序" width="80" />
        
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

    <!-- 状态表单弹窗 -->
    <XiansuoZhuangtaiForm
      v-model:visible="formVisible"
      :mode="formMode"
      :zhuangtai="currentZhuangtai"
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
import XiansuoZhuangtaiForm from '@/components/xiansuo/XiansuoZhuangtaiForm.vue'
import type { XiansuoZhuangtai } from '@/types/xiansuo'

// 使用store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const searchForm = ref({
  search: '',
  zhuangtai_leixing: '',
  zhuangtai: ''
})

const formVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const currentZhuangtai = ref<XiansuoZhuangtai | null>(null)

// 计算属性
const { 
  zhuangtai_list, 
  loading, 
  total, 
  currentPage, 
  pageSize
} = xiansuoStore

// 方法
const handleSearch = async () => {
  try {
    await xiansuoStore.fetchZhuangtaiList({
      page: currentPage.value,
      size: pageSize.value,
      search: searchForm.value.search,
      zhuangtai_leixing: searchForm.value.zhuangtai_leixing,
      zhuangtai: searchForm.value.zhuangtai
    })
  } catch (error) {
    ElMessage.error('获取状态列表失败')
  }
}

const handleReset = async () => {
  searchForm.value = {
    search: '',
    zhuangtai_leixing: '',
    zhuangtai: ''
  }
  await handleSearch()
}

const handleRefresh = async () => {
  await handleSearch()
}

const handleCreate = () => {
  formMode.value = 'create'
  currentZhuangtai.value = null
  formVisible.value = true
}

const handleEdit = (zhuangtai: XiansuoZhuangtai) => {
  formMode.value = 'edit'
  currentZhuangtai.value = zhuangtai
  formVisible.value = true
}

const handleDelete = async (zhuangtai: XiansuoZhuangtai) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除状态"${zhuangtai.zhuangtai_mingcheng}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await xiansuoStore.deleteZhuangtai(zhuangtai.id)
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
    initial: 'info',
    processing: 'primary',
    success: 'success',
    failed: 'danger'
  }
  return types[type] || ''
}

const getTypeText = (type: string) => {
  const texts: Record<string, string> = {
    initial: '初始状态',
    processing: '处理中',
    success: '成功状态',
    failed: '失败状态'
  }
  return texts[type] || type
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

// 生命周期
onMounted(async () => {
  await handleSearch()
})
</script>

<style scoped>
.xiansuo-zhuangtai-list {
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

.color-block {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
