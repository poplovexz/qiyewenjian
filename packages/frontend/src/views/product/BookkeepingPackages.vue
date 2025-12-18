<template>
  <div class="bookkeeping-packages">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>代理记账套餐管理</h2>
          <p class="subtitle">管理代理记账套餐和套餐包含的产品项目</p>
        </div>
      </template>

      <div class="packages-container">
        <!-- 左侧套餐列表 -->
        <div class="packages-sidebar">
          <div class="sidebar-header">
            <h3>代理记账套餐</h3>
            <el-button 
              type="primary" 
              size="small" 
              @click="handleAddPackage"
              v-if="hasPermission('product:create')"
            >
              <el-icon><Plus /></el-icon>
              新增套餐
            </el-button>
          </div>
          
          <div class="packages-list">
            <div 
              v-for="pkg in packageList" 
              :key="pkg.id"
              class="package-item"
              :class="{ active: selectedPackage?.id === pkg.id }"
              @click="selectPackage(pkg)"
            >
              <div class="package-info">
                <h4>{{ pkg.taocan_mingcheng }}</h4>
                <p class="package-desc">{{ pkg.taocan_miaoshu }}</p>
                <div class="package-meta">
                  <span class="price">¥{{ pkg.jichu_jiage }}/月</span>
                  <span class="services-count">{{ pkg.chanpin_xiangmu_count }}个产品项目</span>
                </div>
              </div>
              <div class="package-actions">
                <el-button 
                  type="text" 
                  size="small" 
                  @click.stop="handleEditPackage(pkg)"
                  v-if="hasPermission('product:update')"
                >
                  编辑
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧产品项目表格 -->
        <div class="services-content">
          <div class="content-header">
            <div class="header-left">
              <h3>产品项目管理</h3>
              <span v-if="selectedPackage" class="selected-package">
                当前套餐：{{ selectedPackage.taocan_mingcheng }} - 通过勾选管理套餐包含的产品项目
              </span>
              <span v-else class="selected-package">
                请选择左侧套餐查看和管理产品项目
              </span>
            </div>
            <div class="header-right">
              <el-button
                type="primary"
                @click="handleAddProductItem"
                v-if="hasPermission('product:create')"
              >
                <el-icon><Plus /></el-icon>
                新增产品项目
              </el-button>
            </div>
          </div>

          <!-- 产品项目表格 -->
          <el-table
            :data="allProductItemList"
            v-loading="productItemsLoading"
            class="services-table"
            border
          >
            <el-table-column v-if="selectedPackage" label="包含" width="80" align="center" fixed="left">
              <template #default="{ row }">
                <el-checkbox
                  :model-value="isProductInPackage(row.id, selectedPackage.id)"
                  @change="(value) => handleProductToggle(row.id, selectedPackage.id, value)"
                  :disabled="!hasPermission('product:update')"
                />
              </template>
            </el-table-column>

            <el-table-column prop="chanpin_mingcheng" label="产品项目名称" width="200">
              <template #default="{ row }">
                <div class="service-name">
                  <strong>{{ row.chanpin_mingcheng }}</strong>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="chanpin_miaoshu" label="产品项目说明" min-width="300">
              <template #default="{ row }">
                <div class="service-desc">{{ row.chanpin_miaoshu }}</div>
              </template>
            </el-table-column>

            <el-table-column prop="chanpin_jiage" label="产品价格" width="150" align="center">
              <template #default="{ row }">
                <span class="price">¥{{ row.chanpin_jiage }}/{{ row.jiage_danwei }}</span>
              </template>
            </el-table-column>

            <el-table-column label="产品属性" width="200" align="center">
              <template #default="{ row }">
                <div class="service-attributes">
                  <el-tag v-if="row.shi_jiben_chanpin" type="primary" size="small">基础产品</el-tag>
                  <el-tag v-if="row.shi_keyi_goumai" type="success" size="small" style="margin-left: 4px;">可购买</el-tag>
                  <el-tag v-if="row.shi_baohan_taocan" type="info" size="small" style="margin-left: 4px;">套餐包含</el-tag>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150" align="center" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleEditProductItem(row)"
                  v-if="hasPermission('product:update')"
                >
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDeleteProductItem(row)"
                  v-if="hasPermission('product:delete')"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 空状态提示 -->
          <div v-if="allProductItemList.length === 0" class="empty-state">
            <el-empty description="暂无产品项目">
              <el-button
                type="primary"
                @click="handleAddProductItem"
                v-if="hasPermission('product:create')"
              >
                创建第一个产品项目
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 套餐表单弹窗 -->
    <el-dialog
      :model-value="packageFormVisible"
      @update:model-value="packageFormVisible = $event"
      :title="packageFormMode === 'create' ? '新增套餐' : '编辑套餐'"
      width="600px"
    >
      <el-form
        ref="packageFormRef"
        :model="packageFormData"
        :rules="packageFormRules"
        label-width="120px"
      >
        <el-form-item label="套餐名称" prop="taocan_mingcheng">
          <el-input v-model="packageFormData.taocan_mingcheng" placeholder="请输入套餐名称" />
        </el-form-item>
        <el-form-item label="套餐描述" prop="taocan_miaoshu">
          <el-input 
            v-model="packageFormData.taocan_miaoshu" 
            type="textarea" 
            :rows="3"
            placeholder="请输入套餐描述"
          />
        </el-form-item>
        <el-form-item label="基础价格" prop="jichu_jiage">
          <el-input-number 
            v-model="packageFormData.jichu_jiage" 
            :min="0" 
            :precision="2"
            placeholder="请输入基础价格"
          />
          <span style="margin-left: 10px;">元/月</span>
        </el-form-item>
        <el-form-item label="排序" prop="paixu">
          <el-input-number v-model="packageFormData.paixu" :min="0" />
        </el-form-item>
        <el-form-item label="状态" prop="zhuangtai">
          <el-radio-group v-model="packageFormData.zhuangtai">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="packageFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePackageSubmit" :loading="packageSubmitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 产品项目表单弹窗 -->
    <el-dialog
      :model-value="productItemFormVisible"
      @update:model-value="productItemFormVisible = $event"
      :title="productItemFormMode === 'create' ? '新增产品项目' : '编辑产品项目'"
      width="700px"
    >
      <el-form
        ref="productItemFormRef"
        :model="productItemFormData"
        :rules="productItemFormRules"
        label-width="120px"
      >
        <el-form-item label="产品项目名称" prop="chanpin_mingcheng">
          <el-input v-model="productItemFormData.chanpin_mingcheng" placeholder="请输入产品项目名称" />
        </el-form-item>
        <el-form-item label="产品项目说明" prop="chanpin_miaoshu">
          <el-input
            v-model="productItemFormData.chanpin_miaoshu"
            type="textarea"
            :rows="4"
            placeholder="请输入产品项目说明"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="产品价格" prop="chanpin_jiage">
          <el-input-number
            v-model="productItemFormData.chanpin_jiage"
            :min="0"
            :precision="2"
            placeholder="请输入产品价格"
          />
          <el-select
            v-model="productItemFormData.jiage_danwei"
            style="width: 100px; margin-left: 10px;"
          >
            <el-option label="元/月" value="元/月" />
            <el-option label="元/年" value="元/年" />
            <el-option label="元/次" value="元/次" />
            <el-option label="元" value="元" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品属性">
          <el-checkbox v-model="productItemFormData.shi_jiben_chanpin">是否为基础产品</el-checkbox>
          <el-checkbox v-model="productItemFormData.shi_keyi_goumai" style="margin-left: 20px;">是否可以购买</el-checkbox>
          <el-checkbox v-model="productItemFormData.shi_baohan_taocan" style="margin-left: 20px;">是否包含在套餐中</el-checkbox>
        </el-form-item>
        <el-form-item label="排序" prop="paixu">
          <el-input-number v-model="productItemFormData.paixu" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productItemFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleProductItemSubmit" :loading="productItemSubmitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { hasPermission } from '@/utils/permissions'
import { productApi } from '@/api/modules/product'

// 接口类型定义
interface BookkeepingPackage {
  id: string
  taocan_mingcheng: string  // 套餐名称，如"财税服务套餐"
  taocan_miaoshu: string    // 套餐描述
  jichu_jiage: number       // 套餐基础价格
  paixu: number
  zhuangtai: string
  chanpin_xiangmu_count: number  // 包含的产品项目数量
}

interface BookkeepingProductItem {
  id: string
  chanpin_mingcheng: string // 产品项目名称，如"内账凭证/账簿"
  chanpin_miaoshu: string   // 产品项目描述
  chanpin_jiage: number     // 产品项目价格
  jiage_danwei: string      // 价格单位
  shi_jiben_chanpin: boolean // 是否为基础产品
  shi_keyi_goumai: boolean   // 是否可以购买
  shi_baohan_taocan: boolean // 是否包含在套餐中
  paixu: number
}

interface PackageProductRelation {
  taocan_id: string         // 套餐ID
  chanpin_xiangmu_id: string // 产品项目ID
}

// 响应式数据
const packageList = ref<BookkeepingPackage[]>([])
const allProductItemList = ref<BookkeepingProductItem[]>([])  // 所有产品项目列表
const packageProductRelations = ref<PackageProductRelation[]>([])  // 套餐产品关联关系
const selectedPackage = ref<BookkeepingPackage | null>(null)
const productItemsLoading = ref(false)

// 计算属性：判断产品项目是否属于当前套餐
const isProductInPackage = (productId: string, packageId: string): boolean => {
  return packageProductRelations.value.some(
    rel => rel.taocan_id === packageId && rel.chanpin_xiangmu_id === productId
  )
}

// 套餐表单
const packageFormVisible = ref(false)
const packageFormMode = ref<'create' | 'edit'>('create')
const packageFormRef = ref()
const packageSubmitting = ref(false)
const currentPackage = ref<BookkeepingPackage | null>(null)

const packageFormData = reactive({
  taocan_mingcheng: '',
  taocan_miaoshu: '',
  jichu_jiage: 0,
  paixu: 0,
  zhuangtai: 'active'
})

const packageFormRules = {
  taocan_mingcheng: [
    { required: true, message: '请输入套餐名称', trigger: 'blur' }
  ],
  jichu_jiage: [
    { required: true, message: '请输入基础价格', trigger: 'blur' }
  ]
}

// 产品项目表单
const productItemFormVisible = ref(false)
const productItemFormMode = ref<'create' | 'edit'>('create')
const productItemFormRef = ref()
const productItemSubmitting = ref(false)
const currentProductItem = ref<BookkeepingProductItem | null>(null)

const productItemFormData = reactive({
  chanpin_mingcheng: '',      // 产品项目名称
  chanpin_miaoshu: '',        // 产品项目描述
  chanpin_jiage: 0,           // 产品项目价格
  jiage_danwei: '元/月',      // 价格单位
  shi_jiben_chanpin: false,   // 是否为基础产品
  shi_keyi_goumai: true,      // 是否可以购买
  shi_baohan_taocan: true,    // 是否包含在套餐中
  paixu: 0
})

const productItemFormRules = {
  chanpin_mingcheng: [
    { required: true, message: '请输入产品项目名称', trigger: 'blur' }
  ],
  chanpin_jiage: [
    { required: true, message: '请输入产品项目价格', trigger: 'blur' }
  ]
}

// 方法
const loadPackageList = async () => {
  try {
    // TODO: 调用API获取代账套餐列表
    // 模拟数据
    packageList.value = [
      {
        id: '1',
        taocan_mingcheng: '财税服务套餐',
        taocan_miaoshu: '为小微企业提供全方位财税服务的完整套餐',
        jichu_jiage: 2000,
        paixu: 1,
        zhuangtai: '启用',
        chanpin_xiangmu_count: 4
      },
      {
        id: '2',
        taocan_mingcheng: '小微企业记账套餐',
        taocan_miaoshu: '专为小微企业设计的基础记账服务套餐',
        jichu_jiage: 800,
        paixu: 2,
        zhuangtai: '启用',
        chanpin_xiangmu_count: 3
      },
      {
        id: '3',
        taocan_mingcheng: '一般纳税人记账套餐',
        taocan_miaoshu: '一般纳税人企业专业记账服务套餐',
        jichu_jiage: 1500,
        paixu: 3,
        zhuangtai: '启用',
        chanpin_xiangmu_count: 3
      },
      {
        id: '4',
        taocan_mingcheng: '高端财务管理套餐',
        taocan_miaoshu: '大中型企业全套财务管理服务套餐',
        jichu_jiage: 3000,
        paixu: 4,
        zhuangtai: '启用',
        chanpin_xiangmu_count: 3
      }
    ]

    // 默认选择第一个套餐
    if (packageList.value.length > 0) {
      selectedPackage.value = packageList.value[0]
    }
  } catch (error) {
    ElMessage.error('加载代账套餐列表失败')
  }
}

const loadProductItemList = async () => {
  productItemsLoading.value = true
  try {
    // 调用API获取代理记账产品项目列表
    const response = await productApi.getList({
      chanpin_leixing: 'daili_jizhang',
      page: 1,
      size: 100
    })

    // 将API返回的数据转换为页面需要的格式
    allProductItemList.value = response.items.map((item: any) => ({
      id: item.id,
      chanpin_mingcheng: item.xiangmu_mingcheng,
      chanpin_miaoshu: item.xiangmu_beizhu || '',
      chanpin_jiage: Number(item.yewu_baojia),
      jiage_danwei: `元/${item.baojia_danwei}`,
      shi_jiben_chanpin: true,
      shi_keyi_goumai: item.zhuangtai === 'active',
      shi_baohan_taocan: true,
      paixu: item.paixu || 0
    }))

    
  } catch (error) {
    console.error('加载产品列表失败:', error)
    ElMessage.error('加载产品列表失败')
    allProductItemList.value = []
  } finally {
    productItemsLoading.value = false
  }
}

const loadPackageProductRelations = async () => {
  try {
    // TODO: 调用API获取套餐产品关联关系
    // 模拟数据 - 套餐与产品项目的多对多关系
    packageProductRelations.value = [
      // 财税服务套餐包含的产品项目
      { taocan_id: '1', chanpin_xiangmu_id: '1' }, // 内账凭证/账簿
      { taocan_id: '1', chanpin_xiangmu_id: '2' }, // 财务报表编制
      { taocan_id: '1', chanpin_xiangmu_id: '3' }, // 年度申报工商公示
      { taocan_id: '1', chanpin_xiangmu_id: '4' }, // 网上申报纳税

      // 小微企业记账套餐包含的产品项目
      { taocan_id: '2', chanpin_xiangmu_id: '5' }, // 基础记账服务
      { taocan_id: '2', chanpin_xiangmu_id: '6' }, // 月度财务报表
      { taocan_id: '2', chanpin_xiangmu_id: '7' }, // 税务申报服务

      // 一般纳税人记账套餐包含的产品项目
      { taocan_id: '3', chanpin_xiangmu_id: '8' }, // 一般纳税人记账
      { taocan_id: '3', chanpin_xiangmu_id: '9' }, // 增值税专用发票管理
      { taocan_id: '3', chanpin_xiangmu_id: '10' }, // 进项税额认证

      // 高端财务管理套餐包含的产品项目
      { taocan_id: '4', chanpin_xiangmu_id: '11' }, // 全套财务管理
      { taocan_id: '4', chanpin_xiangmu_id: '12' }, // 税务筹划咨询
      { taocan_id: '4', chanpin_xiangmu_id: '13' }, // 财务分析报告

      // 一些产品项目可能被多个套餐包含
      { taocan_id: '2', chanpin_xiangmu_id: '1' }, // 小微企业套餐也包含内账凭证
      { taocan_id: '3', chanpin_xiangmu_id: '2' }, // 一般纳税人套餐也包含财务报表编制
      { taocan_id: '4', chanpin_xiangmu_id: '2' }, // 高端套餐也包含财务报表编制
    ]
  } catch (error) {
    ElMessage.error('加载套餐产品关联关系失败')
  }
}

// 更新套餐的产品项目数量
const updatePackageProductItemCount = () => {
  packageList.value.forEach(pkg => {
    pkg.chanpin_xiangmu_count = packageProductRelations.value.filter(rel => rel.taocan_id === pkg.id).length
  })
}

const selectPackage = (pkg: BookkeepingPackage) => {
  selectedPackage.value = pkg
}

// 套餐操作
const handleAddPackage = () => {
  currentPackage.value = null
  packageFormMode.value = 'create'
  Object.assign(packageFormData, {
    taocan_mingcheng: '',
    taocan_miaoshu: '',
    jichu_jiage: 0,
    paixu: 0,
    zhuangtai: 'active'
  })
  packageFormVisible.value = true
}

const handleEditPackage = (pkg: BookkeepingPackage) => {
  currentPackage.value = pkg
  packageFormMode.value = 'edit'
  Object.assign(packageFormData, pkg)
  packageFormVisible.value = true
}

const handlePackageSubmit = async () => {
  try {
    await packageFormRef.value?.validate()
    packageSubmitting.value = true
    
    // TODO: 调用API保存套餐
    if (packageFormMode.value === 'create') {
      ElMessage.success('套餐创建成功')
    } else {
      ElMessage.success('套餐更新成功')
    }
    
    packageFormVisible.value = false
    loadPackageList()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    packageSubmitting.value = false
  }
}

// 产品项目操作
const handleAddProductItem = () => {
  currentProductItem.value = null
  productItemFormMode.value = 'create'
  Object.assign(productItemFormData, {
    chanpin_mingcheng: '',
    chanpin_miaoshu: '',
    chanpin_jiage: 0,
    jiage_danwei: '元/月',
    shi_jiben_chanpin: false,
    shi_keyi_goumai: true,
    shi_baohan_taocan: true,
    paixu: 0
  })
  productItemFormVisible.value = true
}

const handleEditProductItem = (item: BookkeepingProductItem) => {
  currentProductItem.value = item
  productItemFormMode.value = 'edit'
  Object.assign(productItemFormData, item)
  productItemFormVisible.value = true
}

const handleDeleteProductItem = async (item: BookkeepingProductItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品项目"${item.chanpin_mingcheng}"吗？删除后将从所有套餐中移除。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: 调用API删除产品项目
    const index = allProductItemList.value.findIndex(p => p.id === item.id)
    if (index > -1) {
      allProductItemList.value.splice(index, 1)
      // 同时删除所有相关的套餐产品关联关系
      packageProductRelations.value = packageProductRelations.value.filter(
        rel => rel.chanpin_xiangmu_id !== item.id
      )
      // 更新套餐产品项目数量
      updatePackageProductItemCount()
      ElMessage.success('产品项目删除成功')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleProductItemSubmit = async () => {
  try {
    await productItemFormRef.value?.validate()
    productItemSubmitting.value = true

    // TODO: 调用API保存产品项目
    if (productItemFormMode.value === 'create') {
      // 创建新产品项目
      const newProductItem: BookkeepingProductItem = {
        id: Date.now().toString(), // 临时ID
        ...productItemFormData
      }
      allProductItemList.value.push(newProductItem)
      ElMessage.success('产品项目创建成功')
    } else {
      // 更新现有产品项目
      const index = allProductItemList.value.findIndex(p => p.id === currentProductItem.value?.id)
      if (index > -1) {
        allProductItemList.value[index] = { ...allProductItemList.value[index], ...productItemFormData }
      }
      ElMessage.success('产品项目更新成功')
    }

    productItemFormVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    productItemSubmitting.value = false
  }
}

// 处理套餐产品关联
const handleProductToggle = async (productId: string, packageId: string, included: boolean) => {
  try {
    if (included) {
      // 添加关联
      packageProductRelations.value.push({
        taocan_id: packageId,
        chanpin_xiangmu_id: productId
      })
      // TODO: 调用API添加关联
    } else {
      // 移除关联
      const index = packageProductRelations.value.findIndex(
        rel => rel.taocan_id === packageId && rel.chanpin_xiangmu_id === productId
      )
      if (index > -1) {
        packageProductRelations.value.splice(index, 1)
        // TODO: 调用API移除关联
      }
    }

    // 更新套餐产品项目数量
    updatePackageProductItemCount()

    const productName = allProductItemList.value.find(p => p.id === productId)?.chanpin_mingcheng
    const packageName = selectedPackage.value?.taocan_mingcheng

    if (included) {
      ElMessage.success(`已将"${productName}"添加到"${packageName}"套餐中`)
    } else {
      ElMessage.success(`已将"${productName}"从"${packageName}"套餐中移除`)
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 生命周期
onMounted(() => {
  loadPackageList()
  loadProductItemList()
  loadPackageProductRelations()
})
</script>

<style scoped>
.bookkeeping-packages {
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

.packages-container {
  display: flex;
  gap: 16px; /* 减少间距 */
  margin-top: 0; /* 移除顶部间距 */
  height: calc(100vh - 200px); /* 设置固定高度 */
  overflow: auto; /* 允许滚动 */
}

/* 左侧套餐列表 */
.packages-sidebar {
  width: 280px; /* 稍微减少宽度 */
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

.packages-list {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.package-item {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.package-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.package-item.active {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.package-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.package-desc {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.package-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  color: #e6a23c;
  font-weight: 600;
  font-size: 14px;
}

.services-count {
  color: #909399;
  font-size: 12px;
}

.package-actions {
  margin-top: 8px;
  text-align: right;
}

/* 右侧服务内容 */
.services-content {
  flex: 1;
  min-width: 0; /* 允许 flex 子元素缩小 */
  overflow-y: auto; /* 允许垂直滚动 */
  display: flex;
  flex-direction: column;
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

.selected-package {
  margin-left: 16px;
  color: #409eff;
  font-size: 14px;
}

.services-table {
  border-radius: 8px;
  overflow: auto; /* 允许表格横向滚动 */
  width: 100%;
}

.service-name strong {
  color: #303133;
}

.service-desc {
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
}

.package-service-status {
  display: flex;
  justify-content: center;
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

.service-attributes {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px;
}

.service-attributes .el-tag {
  font-size: 11px;
}
</style>
