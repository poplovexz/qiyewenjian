/**
 * 产品管理相关类型定义
 */

// 基础分页参数
export interface BaseListParams {
  page: number
  size: number
}

// 基础分页响应
export interface BaseListResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 产品分类
export interface ProductCategory {
  id: string
  fenlei_mingcheng: string
  fenlei_bianma: string
  chanpin_leixing: 'zengzhi' | 'daili_jizhang'
  miaoshu?: string
  paixu: number
  zhuangtai: 'active' | 'inactive'
  created_at: string
  updated_at: string
  xiangmu_count?: number
}

// 产品分类创建参数
export interface ProductCategoryCreate {
  fenlei_mingcheng: string
  fenlei_bianma: string
  chanpin_leixing: 'zengzhi' | 'daili_jizhang'
  miaoshu?: string
  paixu?: number
  zhuangtai?: 'active' | 'inactive'
}

// 产品分类更新参数
export interface ProductCategoryUpdate {
  fenlei_mingcheng?: string
  fenlei_bianma?: string
  chanpin_leixing?: 'zengzhi' | 'daili_jizhang'
  miaoshu?: string
  paixu?: number
  zhuangtai?: 'active' | 'inactive'
}

// 产品分类列表查询参数
export interface ProductCategoryListParams extends BaseListParams {
  search?: string
  chanpin_leixing?: 'zengzhi' | 'daili_jizhang' | ''
  zhuangtai?: 'active' | 'inactive' | ''
}

// 产品分类列表响应
export interface ProductCategoryListResponse extends BaseListResponse<ProductCategory> {}

// 产品分类选项（用于下拉选择）
export interface ProductCategoryOption {
  id: string
  fenlei_mingcheng: string
  fenlei_bianma: string
  chanpin_leixing: string
}

// 产品项目
export interface Product {
  id: string
  xiangmu_mingcheng: string
  xiangmu_bianma: string
  fenlei_id: string
  fenlei_mingcheng?: string
  chanpin_leixing?: 'zengzhi' | 'daili_jizhang'
  yewu_baojia: number
  baojia_danwei: string
  banshi_tianshu: number
  xiangmu_beizhu?: string
  paixu: number
  zhuangtai: 'active' | 'inactive'
  created_at: string
  updated_at: string
  buzou_count?: number
}

// 产品项目创建参数
export interface ProductCreate {
  xiangmu_mingcheng: string
  xiangmu_bianma: string
  fenlei_id: string
  chanpin_leixing?: 'zengzhi' | 'daili_jizhang'
  yewu_baojia: number
  baojia_danwei?: string
  banshi_tianshu?: number
  xiangmu_beizhu?: string
  paixu?: number
  zhuangtai?: 'active' | 'inactive'
}

// 产品项目更新参数
export interface ProductUpdate {
  xiangmu_mingcheng?: string
  xiangmu_bianma?: string
  fenlei_id?: string
  chanpin_leixing?: 'zengzhi' | 'daili_jizhang'
  yewu_baojia?: number
  baojia_danwei?: string
  banshi_tianshu?: number
  xiangmu_beizhu?: string
  paixu?: number
  zhuangtai?: 'active' | 'inactive'
}

// 产品项目列表查询参数
export interface ProductListParams extends BaseListParams {
  search?: string
  fenlei_id?: string
  chanpin_leixing?: 'zengzhi' | 'daili_jizhang' | ''
  zhuangtai?: 'active' | 'inactive' | ''
}

// 产品项目列表响应
export interface ProductListResponse extends BaseListResponse<Product> {}

// 产品步骤
export interface ProductStep {
  id: string
  buzou_mingcheng: string
  xiangmu_id: string
  yugu_shichang: number
  shichang_danwei: string
  buzou_feiyong: number
  buzou_miaoshu?: string
  paixu: number
  shi_bixu: 'Y' | 'N'
  zhuangtai: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

// 产品步骤创建参数
export interface ProductStepCreate {
  buzou_mingcheng: string
  xiangmu_id: string
  yugu_shichang: number
  shichang_danwei?: string
  buzou_feiyong?: number
  buzou_miaoshu?: string
  paixu?: number
  shi_bixu?: 'Y' | 'N'
  zhuangtai?: 'active' | 'inactive'
}

// 产品步骤更新参数
export interface ProductStepUpdate {
  buzou_mingcheng?: string
  xiangmu_id?: string
  yugu_shichang?: number
  shichang_danwei?: string
  buzou_feiyong?: number
  buzou_miaoshu?: string
  paixu?: number
  shi_bixu?: 'Y' | 'N'
  zhuangtai?: 'active' | 'inactive'
}

// 产品项目详情（包含步骤列表）
export interface ProductDetail extends Product {
  buzou_list: ProductStep[]
}

// 产品类型选项
export interface ProductTypeOption {
  value: 'zengzhi' | 'daili_jizhang'
  label: string
  description?: string
}

// 产品状态选项
export interface ProductStatusOption {
  value: 'active' | 'inactive'
  label: string
  type: 'success' | 'danger'
}

// 报价单位选项
export interface PriceUnitOption {
  value: string
  label: string
}

// 时长单位选项
export interface TimeUnitOption {
  value: string
  label: string
}
