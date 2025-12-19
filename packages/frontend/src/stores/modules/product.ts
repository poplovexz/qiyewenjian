/**
 * 产品管理状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  productCategoryApi, 
  productApi, 
  productStepApi 
} from '@/api/modules/product'
import type {
  ProductCategory,
  ProductCategoryCreate,
  ProductCategoryUpdate,
  ProductCategoryListParams,
  ProductCategoryOption,
  Product,
  ProductCreate,
  ProductUpdate,
  ProductListParams,
  ProductDetail,
  ProductStep,
  ProductStepCreate,
  ProductStepUpdate
} from '@/types/product'

export const useProductStore = defineStore('product', () => {
  // 产品分类状态
  const categories = ref<ProductCategory[]>([])
  const categoryOptions = ref<ProductCategoryOption[]>([])
  const categoryLoading = ref(false)
  const categoryTotal = ref(0)
  const categoryCurrentPage = ref(1)
  const categoryPageSize = ref(20)

  // 产品项目状态
  const products = ref<Product[]>([])
  const productLoading = ref(false)
  const productTotal = ref(0)
  const productCurrentPage = ref(1)
  const productPageSize = ref(20)

  // 当前选中的产品详情
  const currentProduct = ref<ProductDetail | null>(null)
  const productDetailLoading = ref(false)

  // 计算属性
  const categoryPages = computed(() => 
    Math.ceil(categoryTotal.value / categoryPageSize.value)
  )

  const productPages = computed(() => 
    Math.ceil(productTotal.value / productPageSize.value)
  )

  // 增值产品分类
  const zengzhiCategories = computed(() => 
    categoryOptions.value.filter(cat => cat.chanpin_leixing === 'zengzhi')
  )

  // 代理记账产品分类
  const dailiJizhangCategories = computed(() => 
    categoryOptions.value.filter(cat => cat.chanpin_leixing === 'daili_jizhang')
  )

  // 产品分类管理方法
  const fetchCategories = async (params: ProductCategoryListParams = {}) => {
    try {
      categoryLoading.value = true
      const response = await productCategoryApi.getList({
        page: categoryCurrentPage.value,
        size: categoryPageSize.value,
        ...params
      })
      
      categories.value = response.items
      categoryTotal.value = response.total
      categoryCurrentPage.value = response.page
      categoryPageSize.value = response.size
    } catch (error) {
      ElMessage.error('获取产品分类列表失败')
    } finally {
      categoryLoading.value = false
    }
  }

  const fetchCategoryOptions = async (chanpin_leixing?: string) => {
    try {
      const options = await productCategoryApi.getOptions(chanpin_leixing)
      categoryOptions.value = options
    } catch (error) {
      ElMessage.error('获取产品分类选项失败')
    }
  }

  const createCategory = async (data: ProductCategoryCreate) => {
    try {
      const category = await productCategoryApi.create(data)
      ElMessage.success('产品分类创建成功')
      await fetchCategories()
      await fetchCategoryOptions()
      return category
    } catch (error) {
      throw error
    }
  }

  const updateCategory = async (id: string, data: ProductCategoryUpdate) => {
    try {
      const category = await productCategoryApi.update(id, data)
      ElMessage.success('产品分类更新成功')
      await fetchCategories()
      await fetchCategoryOptions()
      return category
    } catch (error) {
      throw error
    }
  }

  const deleteCategory = async (id: string) => {
    try {
      await productCategoryApi.delete(id)
      ElMessage.success('产品分类删除成功')
      await fetchCategories()
      await fetchCategoryOptions()
    } catch (error) {
      throw error
    }
  }

  // 产品项目管理方法
  const fetchProducts = async (params: ProductListParams = {}) => {
    try {
      productLoading.value = true
      const response = await productApi.getList({
        page: productCurrentPage.value,
        size: productPageSize.value,
        ...params
      })
      
      products.value = response.items
      productTotal.value = response.total
      productCurrentPage.value = response.page
      productPageSize.value = response.size
    } catch (error) {
      ElMessage.error('获取产品项目列表失败')
    } finally {
      productLoading.value = false
    }
  }

  const fetchProductDetail = async (id: string) => {
    try {
      productDetailLoading.value = true
      const detail = await productApi.getDetail(id)
      currentProduct.value = detail
      return detail
    } catch (error) {
      ElMessage.error('获取产品详情失败')
      throw error
    } finally {
      productDetailLoading.value = false
    }
  }

  const createProduct = async (data: ProductCreate) => {
    try {
      const product = await productApi.create(data)
      ElMessage.success('产品项目创建成功')
      await fetchProducts()
      return product
    } catch (error) {
      throw error
    }
  }

  const updateProduct = async (id: string, data: ProductUpdate) => {
    try {
      const product = await productApi.update(id, data)
      ElMessage.success('产品项目更新成功')
      await fetchProducts()
      return product
    } catch (error) {
      throw error
    }
  }

  const deleteProduct = async (id: string) => {
    try {
      await productApi.delete(id)
      ElMessage.success('产品项目删除成功')
      await fetchProducts()
    } catch (error) {
      throw error
    }
  }

  // 分页控制方法
  const updateCategoryPage = (page: number) => {
    categoryCurrentPage.value = page
  }

  const updateCategoryPageSize = (size: number) => {
    categoryPageSize.value = size
    categoryCurrentPage.value = 1
  }

  const updateProductPage = (page: number) => {
    productCurrentPage.value = page
  }

  const updateProductPageSize = (size: number) => {
    productPageSize.value = size
    productCurrentPage.value = 1
  }

  return {
    // 产品分类状态
    categories,
    categoryOptions,
    categoryLoading,
    categoryTotal,
    categoryCurrentPage,
    categoryPageSize,
    categoryPages,
    zengzhiCategories,
    dailiJizhangCategories,

    // 产品项目状态
    products,
    productLoading,
    productTotal,
    productCurrentPage,
    productPageSize,
    productPages,
    currentProduct,
    productDetailLoading,

    // 产品分类方法
    fetchCategories,
    fetchCategoryOptions,
    createCategory,
    updateCategory,
    deleteCategory,

    // 产品项目方法
    fetchProducts,
    fetchProductDetail,
    createProduct,
    updateProduct,
    deleteProduct,

    // 分页控制方法
    updateCategoryPage,
    updateCategoryPageSize,
    updateProductPage,
    updateProductPageSize
  }
})
