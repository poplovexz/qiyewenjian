<template>
  <div class="product-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">产品项目管理</h1>
        <p class="page-description">管理增值产品和代理记账产品的具体项目</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="handleCreate"
          v-if="hasPermission('product:create')"
        >
          新增产品
        </el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="项目名称、编码、备注"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="产品分类">
          <el-select
            v-model="searchForm.fenlei_id"
            placeholder="请选择产品分类"
            clearable
            style="width: 180px"
          >
            <el-option
              v-for="option in categoryOptions"
              :key="option.id"
              :label="option.fenlei_mingcheng"
              :value="option.id"
            >
              <div class="option-content">
                <span class="option-label">{{ option.fenlei_mingcheng }}</span>
                <el-tag
                  :type="option.chanpin_leixing === 'zengzhi' ? 'primary' : 'success'"
                  size="small"
                  class="option-tag"
                >
                  {{ getProductTypeLabel(option.chanpin_leixing) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
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
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 产品列表 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="productLoading"
        :data="products"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="xiangmu_mingcheng" label="项目名称" width="200">
          <template #default="{ row }">
            <div class="product-name">
              <span class="name">{{ row.xiangmu_mingcheng }}</span>
              <el-tag
                :type="getProductTypeTagType(row.fenlei_mingcheng)"
                size="small"
                class="type-tag"
              >
                {{ row.fenlei_mingcheng }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="xiangmu_bianma" label="项目编码" width="150" />
        <el-table-column prop="yewu_baojia" label="业务报价" width="120" align="right">
          <template #default="{ row }">
            <span class="price">{{ formatPrice(row.yewu_baojia, row.baojia_danwei) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="banshi_tianshu" label="办事天数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.banshi_tianshu }} 天</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="buzou_count" label="步骤数量" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="warning" size="small">{{ row.buzou_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="xiangmu_beizhu" label="项目备注" min-width="200" show-overflow-tooltip />
        <el-table-column prop="paixu" label="排序" width="80" align="center" />
        <el-table-column prop="zhuangtai" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.zhuangtai === 'active' ? 'success' : 'danger'"
              size="small"
            >
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
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
              v-if="hasPermission('product:read')"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
              v-if="hasPermission('product:update')"
            >
              编辑
            </el-button>
            <el-button
              type="info"
              size="small"
              :icon="Setting"
              @click="handleSteps(row)"
              v-if="hasPermission('product:update')"
            >
              步骤
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
              v-if="hasPermission('product:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="productCurrentPage"
          v-model:page-size="productPageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="productTotal"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 产品表单对话框 -->
    <ProductForm
      v-model:visible="formVisible"
      :mode="formMode"
      :product="currentProduct"
      @success="handleFormSuccess"
    />

    <!-- 产品步骤管理对话框 -->
    <ProductStepsDialog
      v-model:visible="stepsVisible"
      :product="currentProduct"
      @success="handleStepsSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete, Setting } from '@element-plus/icons-vue'
import { useProductStore } from '@/stores/modules/product'
import { useAuthStore } from '@/stores/modules/auth'
import { formatDateTime } from '@/utils/date'
import { productTypeOptions, productStatusOptions } from '@/api/modules/product'
import ProductForm from '@/components/product/ProductForm.vue'
import ProductStepsDialog from '@/components/product/ProductStepsDialog.vue'
import type { Product, ProductListParams } from '@/types/product'

// 权限检查
const authStore = useAuthStore()
const hasPermission = (permission: string) => {
  return authStore.hasPermission(permission)
}

// 产品管理store
const productStore = useProductStore()

// 响应式数据
const formVisible = ref(false)
const stepsVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const currentProduct = ref<Product | null>(null)

// 搜索表单
const searchForm = reactive<ProductListParams>({
  page: 1,
  size: 20,
  search: '',
  fenlei_id: '',
  chanpin_leixing: '',
  zhuangtai: ''
})

// 计算属性
const { 
  products, 
  productLoading, 
  productTotal, 
  productCurrentPage, 
  productPageSize,
  categoryOptions
} = productStore

// 方法
const getProductTypeLabel = (type: string) => {
  const option = productTypeOptions.find(opt => opt.value === type)
  return option?.label || type
}

const getProductTypeTagType = (categoryName: string) => {
  // 根据分类名称判断标签类型
  return 'primary'
}

const formatPrice = (price: number, unit: string) => {
  const unitMap: Record<string, string> = {
    yuan: '元',
    ge: '个',
    ci: '次',
    nian: '年',
    yue: '月'
  }
  return `${price} ${unitMap[unit] || unit}`
}

const handleSearch = async () => {
  await productStore.fetchProducts(searchForm)
}

const handleReset = async () => {
  Object.assign(searchForm, {
    page: 1,
    size: 20,
    search: '',
    fenlei_id: '',
    chanpin_leixing: '',
    zhuangtai: ''
  })
  await productStore.fetchProducts()
}

const handleCreate = () => {
  currentProduct.value = null
  formMode.value = 'create'
  formVisible.value = true
}

const handleView = (product: Product) => {
  currentProduct.value = product
  formMode.value = 'view'
  formVisible.value = true
}

const handleEdit = (product: Product) => {
  currentProduct.value = product
  formMode.value = 'edit'
  formVisible.value = true
}

const handleSteps = (product: Product) => {
  currentProduct.value = product
  stepsVisible.value = true
}

const handleDelete = async (product: Product) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品"${product.xiangmu_mingcheng}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await productStore.deleteProduct(product.id)
  } catch (error) {
    // 用户取消操作时不显示错误
    if (error !== 'cancel') {
      // 错误已通过 ElMessage 显示
    }
  }
}

const handleSizeChange = (size: number) => {
  productStore.updateProductPageSize(size)
  handleSearch()
}

const handleCurrentChange = (page: number) => {
  productStore.updateProductPage(page)
  handleSearch()
}

const handleFormSuccess = () => {
  formVisible.value = false
  handleSearch()
}

const handleStepsSuccess = () => {
  stepsVisible.value = false
  handleSearch()
}

// 初始化
onMounted(async () => {
  await productStore.fetchCategoryOptions()
  await handleSearch()
})
</script>

<style scoped>
.product-list-container {
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

.product-name {
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

.price {
  font-weight: 500;
  color: #f56c6c;
}

.option-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.option-label {
  flex: 1;
}

.option-tag {
  font-size: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
