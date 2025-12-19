<template>
  <div class="product-management">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>{{ pageTitle }}</h2>
          <p class="subtitle">{{ pageSubtitle }}</p>
        </div>
      </template>

      <div class="products-container">
        <!-- 左侧产品分类列表 -->
        <div class="categories-sidebar">
          <div class="sidebar-header">
            <h3>产品分类</h3>
            <el-button
              type="primary"
              size="small"
              @click="handleCreateCategory"
              v-if="hasPermission('product_category:create')"
            >
              <el-icon><Plus /></el-icon>
              新增分类
            </el-button>
          </div>

          <div class="categories-list">
            <div
              v-for="category in categoryList"
              :key="category.id"
              class="category-item"
              :class="{ active: selectedCategory?.id === category.id }"
              @click="selectCategory(category)"
            >
              <div class="category-info">
                <h4>{{ category.fenlei_mingcheng }}</h4>
                <p class="category-desc">{{ category.miaoshu }}</p>
                <div class="category-meta">
                  <span class="category-code">{{ category.fenlei_bianma }}</span>
                  <span class="products-count">{{ category.xiangmu_count }}个产品</span>
                </div>
              </div>
              <div class="category-actions">
                <el-button
                  type="text"
                  size="small"
                  @click.stop="handleEditCategory(category)"
                  v-if="hasPermission('product_category:update')"
                >
                  编辑
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧产品项目表格 -->
        <div class="products-content">
          <div class="content-header">
            <div class="header-left">
              <h3>产品项目管理</h3>
              <span v-if="selectedCategory" class="selected-category">
                当前分类：{{ selectedCategory.fenlei_mingcheng }}
              </span>
              <span v-else class="selected-category">
                请选择左侧分类查看产品项目
              </span>
            </div>
            <div class="header-right">
              <el-button
                type="primary"
                @click="handleCreateProduct"
                v-if="hasPermission('product:create')"
              >
                <el-icon><Plus /></el-icon>
                新增产品
              </el-button>
            </div>
          </div>

          <!-- 产品项目表格 -->
          <el-table
            :data="filteredProductList"
            v-loading="productLoading"
            class="products-table"
            border
          >
            <el-table-column prop="xiangmu_mingcheng" label="项目名称" min-width="180">
              <template #default="{ row }">
                <div class="product-name">
                  <strong>{{ row.xiangmu_mingcheng }}</strong>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="xiangmu_bianma" label="项目编码" width="150" />

            <el-table-column prop="yewu_baojia" label="业务报价" width="120" align="center">
              <template #default="{ row }">
                <span class="price">¥{{ row.yewu_baojia }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="banshi_tianshu" label="办事天数" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="warning">{{ row.banshi_tianshu }}天</el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="buzou_count" label="步骤数" width="80" align="center">
              <template #default="{ row }">
                <el-tag type="info">{{ row.buzou_count }}</el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="zhuangtai" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.zhuangtai === 'active' ? 'success' : 'danger'">
                  {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="250" align="center" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleEditProduct(row)"
                  v-if="hasPermission('product:update')"
                >
                  编辑
                </el-button>
                <el-button
                  type="info"
                  size="small"
                  @click="handleManageSteps(row)"
                  v-if="hasPermission('product:read')"
                >
                  步骤
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDeleteProduct(row)"
                  v-if="hasPermission('product:delete')"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 空状态提示 -->
          <div v-if="filteredProductList.length === 0" class="empty-state">
            <el-empty :description="selectedCategory ? '该分类下暂无产品项目' : '请选择左侧分类查看产品'">
              <el-button
                v-if="selectedCategory && hasPermission('product:create')"
                type="primary"
                @click="handleCreateProduct"
              >
                创建第一个产品项目
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 分类表单弹窗 -->
    <CategoryForm
      v-model:visible="categoryFormVisible"
      :mode="categoryFormMode"
      :category="currentCategory"
      @success="handleCategoryFormSuccess"
    />

    <!-- 产品表单弹窗 -->
    <ProductForm
      v-model:visible="productFormVisible"
      :mode="productFormMode"
      :product="currentProduct"
      @success="handleProductFormSuccess"
    />

    <!-- 产品步骤管理弹窗 -->
    <ProductStepsDialog
      v-model:visible="stepsDialogVisible"
      :product="currentProduct"
      @success="handleStepsSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { useProductStore } from '@/stores/modules/product'
import { hasPermission } from '@/utils/permissions'
import CategoryForm from '@/components/product/CategoryForm.vue'
import ProductForm from '@/components/product/ProductForm.vue'
import ProductStepsDialog from '@/components/product/ProductStepsDialog.vue'
import type { ProductCategory, Product } from '@/types/product'

// 权限检查函数已直接导入

// 路由和产品管理store
const route = useRoute()
const productStore = useProductStore()

// 分类相关数据
const categoryList = ref<ProductCategory[]>([])
const categoryLoading = ref(false)
const selectedCategory = ref<ProductCategory | null>(null)

// 产品相关数据
const productList = ref<Product[]>([])
const productLoading = ref(false)

// 表单相关
const categoryFormVisible = ref(false)
const categoryFormMode = ref<'create' | 'edit' | 'view'>('create')
const currentCategory = ref<ProductCategory | null>(null)

const productFormVisible = ref(false)
const productFormMode = ref<'create' | 'edit' | 'view'>('create')
const currentProduct = ref<Product | null>(null)

const stepsDialogVisible = ref(false)

// 计算属性
const categoryOptions = computed(() => productStore.categoryOptions)

// 根据选中的分类过滤产品列表
const filteredProductList = computed(() => {
  if (!selectedCategory.value) {
    return []
  }
  return productList.value.filter(product => product.fenlei_id === selectedCategory.value?.id)
})

// 根据URL参数确定产品类型
const productType = computed(() => route.query.type as string)

// 页面标题
const pageTitle = computed(() => {
  switch (productType.value) {
    case 'zengzhi':
      return '增值服务管理'
    case 'daili_jizhang':
      return '代理记账服务管理'
    default:
      return '产品管理'
  }
})

// 页面副标题
const pageSubtitle = computed(() => {
  switch (productType.value) {
    case 'zengzhi':
      return '管理增值产品分类和项目'
    case 'daili_jizhang':
      return '管理代理记账产品分类和项目'
    default:
      return '管理产品分类和产品项目'
  }
})

// 方法
const loadCategoryList = async () => {
  categoryLoading.value = true
  try {
    const params = {
      page: 1,
      size: 100, // 后端限制最大100
      chanpin_leixing: productType.value || undefined
    }

    await productStore.fetchCategories(params)
    categoryList.value = productStore.categories

    // 默认选择第一个分类
    if (categoryList.value.length > 0 && !selectedCategory.value) {
      selectedCategory.value = categoryList.value[0]
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error)
    ElMessage.error(`获取分类列表失败: ${errorMsg}`)
  } finally {
    categoryLoading.value = false
  }
}

const loadProductList = async () => {
  productLoading.value = true
  try {
    const params = {
      page: 1,
      size: 100, // 后端限制最大100
      chanpin_leixing: productType.value || undefined
    }

    await productStore.fetchProducts(params)
    productList.value = productStore.products
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error)
    ElMessage.error(`获取产品列表失败: ${errorMsg}`)
  } finally {
    productLoading.value = false
  }
}

// 选择分类
const selectCategory = (category: ProductCategory) => {
  selectedCategory.value = category
}

const loadCategoryOptions = async () => {
  try {
    await productStore.fetchCategoryOptions()
  } catch (error) {
    ElMessage.error('获取分类选项失败')
  }
}

// 分类操作
const handleCreateCategory = () => {
  currentCategory.value = null
  categoryFormMode.value = 'create'
  categoryFormVisible.value = true
}

const handleEditCategory = (category: ProductCategory) => {
  currentCategory.value = category
  categoryFormMode.value = 'edit'
  categoryFormVisible.value = true
}

const handleDeleteCategory = async (category: ProductCategory) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${category.fenlei_mingcheng}"吗？删除后该分类下的所有产品将不再关联此分类。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await productStore.deleteCategory(category.id)
    ElMessage.success('删除成功')

    // 如果删除的是当前选中的分类，清空选中状态
    if (selectedCategory.value?.id === category.id) {
      selectedCategory.value = null
    }

    loadCategoryList()
    loadCategoryOptions()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const axiosError = error as { message?: string }
      ElMessage.error(axiosError.message || '删除失败')
    }
  }
}

const handleCategoryFormSuccess = () => {
  categoryFormVisible.value = false
  loadCategoryList()
  loadCategoryOptions()
}

// 产品操作
const handleCreateProduct = () => {
  if (!selectedCategory.value) {
    ElMessage.warning('请先选择一个分类')
    return
  }

  currentProduct.value = null
  productFormMode.value = 'create'
  productFormVisible.value = true
}

const handleEditProduct = (product: Product) => {
  currentProduct.value = product
  productFormMode.value = 'edit'
  productFormVisible.value = true
}

const handleDeleteProduct = async (product: Product) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品"${product.xiangmu_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await productStore.deleteProduct(product.id)
    ElMessage.success('删除成功')
    loadProductList()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const axiosError = error as { message?: string }
      ElMessage.error(axiosError.message || '删除失败')
    }
  }
}

const handleManageSteps = (product: Product) => {
  currentProduct.value = product
  stepsDialogVisible.value = true
}

const handleProductFormSuccess = () => {
  productFormVisible.value = false
  loadProductList()
}

const handleStepsSuccess = () => {
  stepsDialogVisible.value = false
  loadProductList()
}

// 监听路由变化
watch(() => route.query.type, (newType) => {
  // 根据URL参数重新加载数据
  if (newType === 'zengzhi' || newType === 'daili_jizhang') {
    selectedCategory.value = null
    loadCategoryList()
    loadProductList()
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  loadCategoryList()
  loadProductList()
  loadCategoryOptions()
})
</script>

<style scoped>
.product-management {
  /* 移除额外的 padding，让内容占满空间 */
  padding: 0;
  height: 100%;
}

.page-card {
  min-height: calc(100vh - 120px);
  height: 100%;
}

/* 覆盖 el-card 的默认 padding */
.page-card :deep(.el-card__body) {
  padding: 16px;
  height: 100%;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.products-container {
  display: flex;
  gap: 16px; /* 减少间距 */
  margin-top: 0; /* 移除顶部间距 */
  height: calc(100vh - 200px); /* 设置固定高度 */
  overflow: hidden;
}

/* 左侧分类列表 */
.categories-sidebar {
  width: 280px; /* 从 300px 减少到 280px */
  flex-shrink: 0;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.sidebar-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.categories-list {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.category-item {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.category-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.category-item.active {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.category-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.category-desc {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.category-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-code {
  color: #909399;
  font-size: 12px;
}

.products-count {
  color: #909399;
  font-size: 12px;
}

.category-actions {
  margin-top: 8px;
  text-align: right;
}

/* 右侧产品内容 */
.products-content {
  flex: 1;
  min-width: 0; /* 允许 flex 子元素缩小 */
  overflow: hidden; /* 防止内容溢出 */
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.header-left h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.selected-category {
  margin-left: 16px;
  color: #409eff;
  font-size: 14px;
}

.products-table {
  border-radius: 8px;
  overflow: auto; /* 允许表格横向滚动 */
  width: 100%;
}

.product-name strong {
  color: #303133;
}

.price {
  color: #e6a23c;
  font-weight: 600;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table td) {
  padding: 12px 0;
}

.empty-state {
  margin-top: 40px;
  text-align: center;
}
</style>
