<template>
  <div class="category-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">产品分类管理</h1>
        <p class="page-description">管理增值产品和代理记账产品的分类</p>
      </div>
      <div class="header-right">
        <el-button
          type="primary"
          :icon="Plus"
          @click="handleCreate"
          v-if="hasPermission('product_category:create')"
        >
          新增分类
        </el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="分类名称、编码、描述"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="产品类型">
          <el-select
            v-model="searchForm.chanpin_leixing"
            placeholder="请选择产品类型"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="option in productTypeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.zhuangtai"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="option in productStatusOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch"> 搜索 </el-button>
          <el-button :icon="Refresh" @click="handleReset"> 重置 </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分类列表 -->
    <el-card class="table-card" shadow="never">
      <el-table v-loading="categoryLoading" :data="categories" stripe border style="width: 100%">
        <el-table-column prop="fenlei_mingcheng" label="分类名称" width="200">
          <template #default="{ row }">
            <div class="category-name">
              <span class="name">{{ row.fenlei_mingcheng }}</span>
              <el-tag
                :type="row.chanpin_leixing === 'zengzhi' ? 'primary' : 'success'"
                size="small"
                class="type-tag"
              >
                {{ getProductTypeLabel(row.chanpin_leixing) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="fenlei_bianma" label="分类编码" width="150" />
        <el-table-column prop="miaoshu" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="xiangmu_count" label="项目数量" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.xiangmu_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paixu" label="排序" width="80" align="center" />
        <el-table-column prop="zhuangtai" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.zhuangtai === 'active' ? 'success' : 'danger'" size="small">
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="handleView(row)"
              v-if="hasPermission('product_category:read')"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
              v-if="hasPermission('product_category:update')"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
              v-if="hasPermission('product_category:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="categoryCurrentPage"
          v-model:page-size="categoryPageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="categoryTotal"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 分类表单对话框 -->
    <CategoryForm
      v-model:visible="formVisible"
      :mode="formMode"
      :category="currentCategory"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import { useProductStore } from '@/stores/modules/product'
import { useAuthStore } from '@/stores/modules/auth'
import { formatDateTime } from '@/utils/date'
import { productTypeOptions, productStatusOptions } from '@/api/modules/product'
import CategoryForm from '@/components/product/CategoryForm.vue'
import type { ProductCategory, ProductCategoryListParams } from '@/types/product'

// 权限检查
const authStore = useAuthStore()
const hasPermission = (permission: string) => {
  return authStore.hasPermission(permission)
}

// 产品管理store
const productStore = useProductStore()

// 响应式数据
const formVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const currentCategory = ref<ProductCategory | null>(null)

// 搜索表单
const searchForm = reactive<ProductCategoryListParams>({
  page: 1,
  size: 20,
  search: '',
  chanpin_leixing: '',
  zhuangtai: '',
})

// 计算属性
const { categories, categoryLoading, categoryTotal, categoryCurrentPage, categoryPageSize } =
  productStore

// 方法
const getProductTypeLabel = (type: string) => {
  const option = productTypeOptions.find((opt) => opt.value === type)
  return option?.label || type
}

const handleSearch = async () => {
  await productStore.fetchCategories(searchForm)
}

const handleReset = async () => {
  Object.assign(searchForm, {
    page: 1,
    size: 20,
    search: '',
    chanpin_leixing: '',
    zhuangtai: '',
  })
  await productStore.fetchCategories()
}

const handleCreate = () => {
  currentCategory.value = null
  formMode.value = 'create'
  formVisible.value = true
}

const handleView = (category: ProductCategory) => {
  currentCategory.value = category
  formMode.value = 'view'
  formVisible.value = true
}

const handleEdit = (category: ProductCategory) => {
  currentCategory.value = category
  formMode.value = 'edit'
  formVisible.value = true
}

const handleDelete = async (category: ProductCategory) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${category.fenlei_mingcheng}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await productStore.deleteCategory(category.id)
  } catch (error) {
    // 用户取消操作时不显示错误
    if (error !== 'cancel') {
      // 错误已通过 ElMessage 显示
    }
  }
}

const handleSizeChange = (size: number) => {
  productStore.updateCategoryPageSize(size)
  handleSearch()
}

const handleCurrentChange = (page: number) => {
  productStore.updateCategoryPage(page)
  handleSearch()
}

const handleFormSuccess = () => {
  formVisible.value = false
  handleSearch()
}

// 初始化
onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.category-list-container {
  padding: 0; /* 移除额外 padding */
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

.category-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: 500;
}

.type-tag {
  font-size: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
