/**
 * 产品管理 API 接口
 */
import { request } from '@/utils/request'
import type {
  ProductCategory,
  ProductCategoryCreate,
  ProductCategoryUpdate,
  ProductCategoryListParams,
  ProductCategoryListResponse,
  ProductCategoryOption,
  Product,
  ProductCreate,
  ProductUpdate,
  ProductListParams,
  ProductListResponse,
  ProductDetail,
  ProductStep,
  ProductStepCreate,
  ProductStepUpdate
} from '@/types/product'

/**
 * 产品分类管理 API
 */
export const productCategoryApi = {
  /**
   * 获取产品分类列表
   */
  getList(params: ProductCategoryListParams): Promise<ProductCategoryListResponse> {
    return request.get('/api/v1/product-management/categories/', { params })
  },

  /**
   * 获取产品分类选项
   */
  getOptions(chanpin_leixing?: string): Promise<ProductCategoryOption[]> {
    const params = chanpin_leixing ? { chanpin_leixing } : {}
    return request.get('/api/v1/product-management/categories/options', { params })
  },

  /**
   * 根据ID获取产品分类详情
   */
  getById(id: string): Promise<ProductCategory> {
    return request.get(`/api/v1/product-management/categories/${id}`)
  },

  /**
   * 创建产品分类
   */
  create(data: ProductCategoryCreate): Promise<ProductCategory> {
    return request.post('/api/v1/product-management/categories/', data)
  },

  /**
   * 更新产品分类
   */
  update(id: string, data: ProductCategoryUpdate): Promise<ProductCategory> {
    return request.put(`/api/v1/product-management/categories/${id}`, data)
  },

  /**
   * 删除产品分类
   */
  delete(id: string): Promise<void> {
    return request.delete(`/api/v1/product-management/categories/${id}`)
  }
}

/**
 * 产品项目管理 API
 */
export const productApi = {
  /**
   * 获取产品项目列表
   */
  getList(params: ProductListParams): Promise<ProductListResponse> {
    return request.get('/api/v1/product-management/products/', { params })
  },

  /**
   * 根据ID获取产品项目详情
   */
  getById(id: string): Promise<Product> {
    return request.get(`/api/v1/product-management/products/${id}`)
  },

  /**
   * 获取产品项目完整详情（包含步骤列表）
   */
  getDetail(id: string): Promise<ProductDetail> {
    return request.get(`/api/v1/product-management/products/${id}/detail`)
  },

  /**
   * 创建产品项目
   */
  create(data: ProductCreate): Promise<Product> {
    return request.post('/api/v1/product-management/products/', data)
  },

  /**
   * 更新产品项目
   */
  update(id: string, data: ProductUpdate): Promise<Product> {
    return request.put(`/api/v1/product-management/products/${id}`, data)
  },

  /**
   * 删除产品项目
   */
  delete(id: string): Promise<void> {
    return request.delete(`/api/v1/product-management/products/${id}`)
  }
}

/**
 * 产品步骤管理 API
 */
export const productStepApi = {
  /**
   * 获取产品步骤列表
   */
  getList(xiangmu_id: string): Promise<ProductStep[]> {
    return request.get(`/api/v1/product-management/products/${xiangmu_id}/steps`)
  },

  /**
   * 根据ID获取产品步骤详情
   */
  getById(id: string): Promise<ProductStep> {
    return request.get(`/api/v1/product-management/steps/${id}`)
  },

  /**
   * 创建产品步骤
   */
  create(data: ProductStepCreate): Promise<ProductStep> {
    return request.post('/api/v1/product-management/steps/', data)
  },

  /**
   * 更新产品步骤
   */
  update(id: string, data: ProductStepUpdate): Promise<ProductStep> {
    return request.put(`/api/v1/product-management/steps/${id}`, data)
  },

  /**
   * 删除产品步骤
   */
  delete(id: string): Promise<void> {
    return request.delete(`/api/v1/product-management/steps/${id}`)
  },

  /**
   * 批量更新产品步骤
   */
  batchUpdate(xiangmu_id: string, steps: any[]): Promise<ProductStep[]> {
    return request.put(`/api/v1/product-management/products/${xiangmu_id}/steps`, {
      xiangmu_id,
      buzou_list: steps
    })
  }
}

// 产品类型选项
export const productTypeOptions = [
  { value: 'zengzhi', label: '增值产品', description: '为客户提供增值服务的产品' },
  { value: 'daili_jizhang', label: '代理记账产品', description: '代理记账相关的产品服务' }
]

// 产品状态选项
export const productStatusOptions = [
  { value: 'active', label: '启用', type: 'success' },
  { value: 'inactive', label: '禁用', type: 'danger' }
]

// 报价单位选项
export const priceUnitOptions = [
  { value: 'yuan', label: '元' },
  { value: 'ge', label: '个' },
  { value: 'ci', label: '次' },
  { value: 'nian', label: '年' },
  { value: 'yue', label: '月' }
]

// 时长单位选项
export const timeUnitOptions = [
  { value: 'tian', label: '天' },
  { value: 'xiaoshi', label: '小时' },
  { value: 'fenzhong', label: '分钟' }
]
