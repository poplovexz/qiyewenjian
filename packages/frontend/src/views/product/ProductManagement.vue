<template>
  <div class="product-management">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>{{ pageTitle }}</h2>
          <p class="subtitle">{{ pageSubtitle }}</p>
        </div>
      </template>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" type="card" class="product-tabs">
        <!-- 产品分类标签页 -->
        <el-tab-pane label="产品分类" name="categories">
          <div class="tab-content">
            <!-- 分类管理工具栏 -->
            <div class="toolbar">
              <div class="toolbar-left">
                <el-input
                  v-model="categorySearch"
                  placeholder="搜索分类名称或编码"
                  style="width: 300px"
                  clearable
                  @input="handleCategorySearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select
                  v-model="categoryTypeFilter"
                  placeholder="产品类型"
                  style="width: 150px; margin-left: 10px"
                  clearable
                  @change="handleCategorySearch"
                  v-if="!productType"
                >
                  <el-option label="增值产品" value="zengzhi" />
                  <el-option label="代理记账" value="daili_jizhang" />
                </el-select>
                <el-tag
                  v-else
                  :type="productType === 'zengzhi' ? 'primary' : 'success'"
                  style="margin-left: 10px"
                >
                  {{ productType === 'zengzhi' ? '增值产品' : '代理记账产品' }}
                </el-tag>
              </div>
              <div class="toolbar-right">
                <el-button
                  type="primary"
                  @click="handleCreateCategory"
                  v-if="hasPermission('product_category:create')"
                >
                  <el-icon><Plus /></el-icon>
                  新增分类
                </el-button>
              </div>
            </div>

            <!-- 分类列表 -->
            <el-table
              :data="categoryList"
              v-loading="categoryLoading"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="fenlei_mingcheng" label="分类名称" min-width="150" />
              <el-table-column prop="fenlei_bianma" label="分类编码" width="150" />
              <el-table-column prop="chanpin_leixing" label="产品类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.chanpin_leixing === 'zengzhi' ? 'primary' : 'success'">
                    {{ row.chanpin_leixing === 'zengzhi' ? '增值产品' : '代理记账' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="miaoshu" label="描述" min-width="200" show-overflow-tooltip />
              <el-table-column prop="xiangmu_count" label="项目数量" width="100" align="center">
                <template #default="{ row }">
                  <el-tag type="info">{{ row.xiangmu_count }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="paixu" label="排序" width="80" align="center" />
              <el-table-column prop="zhuangtai" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.zhuangtai === 'active' ? 'success' : 'danger'">
                    {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    size="small"
                    @click="handleEditCategory(row)"
                    v-if="hasPermission('product_category:update')"
                  >
                    编辑
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    @click="handleDeleteCategory(row)"
                    v-if="hasPermission('product_category:delete')"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分类分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="categoryPagination.page"
                v-model:page-size="categoryPagination.size"
                :total="categoryPagination.total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="loadCategoryList"
                @current-change="loadCategoryList"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 产品项目标签页 -->
        <el-tab-pane label="产品项目" name="products">
          <div class="tab-content">
            <!-- 项目管理工具栏 -->
            <div class="toolbar">
              <div class="toolbar-left">
                <el-input
                  v-model="productSearch"
                  placeholder="搜索项目名称或编码"
                  style="width: 300px"
                  clearable
                  @input="handleProductSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select
                  v-model="productCategoryFilter"
                  placeholder="选择分类"
                  style="width: 200px; margin-left: 10px"
                  clearable
                  @change="handleProductSearch"
                >
                  <el-option
                    v-for="category in categoryOptions"
                    :key="category.id"
                    :label="category.fenlei_mingcheng"
                    :value="category.id"
                  />
                </el-select>
              </div>
              <div class="toolbar-right">
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

            <!-- 项目列表 -->
            <el-table
              :data="productList"
              v-loading="productLoading"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="xiangmu_mingcheng" label="项目名称" min-width="150" />
              <el-table-column prop="xiangmu_bianma" label="项目编码" width="150" />
              <el-table-column prop="fenlei_mingcheng" label="所属分类" width="150" />
              <el-table-column prop="yewu_baojia" label="业务报价" width="120" align="right">
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

            <!-- 项目分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="productPagination.page"
                v-model:page-size="productPagination.size"
                :total="productPagination.total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="loadProductList"
                @current-change="loadProductList"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
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

// 当前激活的标签页
const activeTab = ref('categories')

// 分类相关数据
const categoryList = ref<ProductCategory[]>([])
const categoryLoading = ref(false)
const categorySearch = ref('')
const categoryTypeFilter = ref('')
const categoryPagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 产品相关数据
const productList = ref<Product[]>([])
const productLoading = ref(false)
const productSearch = ref('')
const productCategoryFilter = ref('')
const productPagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

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
      page: categoryPagination.page,
      size: categoryPagination.size,
      search: categorySearch.value || undefined,
      chanpin_leixing: categoryTypeFilter.value || productType.value || undefined
    }

    await productStore.fetchCategories(params)
    categoryList.value = productStore.categories
    categoryPagination.total = productStore.categoryTotal
  } catch (error) {
    console.error('获取分类列表失败:', error)
    ElMessage.error(`获取分类列表失败: ${error.message || error}`)
  } finally {
    categoryLoading.value = false
  }
}

const loadProductList = async () => {
  productLoading.value = true
  try {
    const params = {
      page: productPagination.page,
      size: productPagination.size,
      search: productSearch.value || undefined,
      fenlei_id: productCategoryFilter.value || undefined
    }
    
    await productStore.fetchProducts(params)
    productList.value = productStore.products
    productPagination.total = productStore.productTotal
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error(`获取产品列表失败: ${error.message || error}`)
  } finally {
    productLoading.value = false
  }
}

const loadCategoryOptions = async () => {
  try {
    await productStore.fetchCategoryOptions()
  } catch (error) {
    ElMessage.error('获取分类选项失败')
  }
}

// 搜索处理
const handleCategorySearch = () => {
  categoryPagination.page = 1
  loadCategoryList()
}

const handleProductSearch = () => {
  productPagination.page = 1
  loadProductList()
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
      `确定要删除分类"${category.fenlei_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await productStore.deleteCategory(category.id)
    ElMessage.success('删除成功')
    loadCategoryList()
    loadCategoryOptions()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
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
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
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
  // 根据URL参数设置分类类型筛选
  if (newType === 'zengzhi' || newType === 'daili_jizhang') {
    categoryTypeFilter.value = newType
    // 重置分页并重新加载数据
    categoryPagination.page = 1
    productPagination.page = 1
    loadCategoryList()
    loadProductList()
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  // 根据URL参数设置初始筛选
  if (productType.value === 'zengzhi' || productType.value === 'daili_jizhang') {
    categoryTypeFilter.value = productType.value
  }

  loadCategoryList()
  loadProductList()
  loadCategoryOptions()
})
</script>

<style scoped>
.product-management {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 120px);
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

.product-tabs {
  margin-top: 20px;
}

.tab-content {
  padding: 20px 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.price {
  color: #e6a23c;
  font-weight: 600;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}
</style>
