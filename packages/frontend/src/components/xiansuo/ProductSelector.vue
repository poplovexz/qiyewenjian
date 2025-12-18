<template>
  <el-dialog v-model="dialogVisible" title="选择服务项目" width="800px" :before-close="handleClose">
    <div v-loading="loading" class="product-selector">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索服务项目..."
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 服务分类标签 -->
      <div class="category-tabs">
        <el-radio-group v-model="activeCategory" @change="handleCategoryChange">
          <el-radio-button label="all">全部服务</el-radio-button>
          <el-radio-button label="daizang">代理记账</el-radio-button>
          <el-radio-button label="zengzhi">增值服务</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 产品列表 -->
      <div class="product-list">
        <div v-if="filteredProducts.length === 0" class="empty-state">
          <el-empty description="暂无服务项目" />
        </div>

        <div v-else class="product-grid">
          <div
            v-for="product in filteredProducts"
            :key="product.id"
            class="product-card"
            :class="{
              selected: selectedProducts.has(product.id),
              'already-in-quote': isProductInQuote(product.id),
              'daili-jizhang': isDailiJizhangProduct(product.id),
            }"
            @click="toggleProduct(product)"
          >
            <div class="product-header">
              <div class="product-name">
                {{ product.xiangmu_mingcheng }}
                <el-tag
                  v-if="isDailiJizhangPackage(product.id)"
                  type="warning"
                  size="small"
                  style="margin-left: 8px"
                >
                  代理记账套餐
                </el-tag>
                <el-tag
                  v-else-if="isDailiJizhangProduct(product.id)"
                  type="warning"
                  size="small"
                  style="margin-left: 8px"
                >
                  代理记账
                </el-tag>
                <el-tag
                  v-if="isProductInQuote(product.id)"
                  type="info"
                  size="small"
                  style="margin-left: 8px"
                >
                  已在报价单中
                </el-tag>
              </div>
              <el-checkbox
                :model-value="selectedProducts.has(product.id)"
                :disabled="isProductInQuote(product.id)"
                @change="toggleProduct(product)"
                @click.stop
              />
            </div>

            <div v-if="product.xiangmu_beizhu" class="product-desc">
              {{ product.xiangmu_beizhu }}
            </div>

            <div v-else-if="product.xiangmu_bianma" class="product-desc">
              编码：{{ product.xiangmu_bianma }}
            </div>

            <div class="product-price">
              <span class="price-label">推荐价格：</span>
              <span class="price-value">¥{{ product.yewu_baojia }}</span>
              <span class="price-unit">/ {{ product.baojia_danwei }}</span>
            </div>

            <div v-if="product.banshi_tianshu" class="service-days">
              办事天数：{{ product.banshi_tianshu }}天
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="selected-count">已选择 {{ selectedProducts.size }} 个服务项目</div>
        <div class="footer-buttons">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="handleConfirm" :disabled="selectedProducts.size === 0">
            确定选择
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import type { ChanpinXiangmuOption } from '@/types/xiansuo'

console.log('🎨 ProductSelector 组件脚本已加载')

// Props
interface Props {
  visible: boolean
  selectedServices?: ChanpinXiangmuOption[] // 已选择的服务列表
}

const props = withDefaults(defineProps<Props>(), {
  selectedServices: () => [],
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  select: [products: ChanpinXiangmuOption[]]
}>()

// Store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const loading = ref(false)
const searchKeyword = ref('')
const activeCategory = ref('all')
const selectedProducts = ref(new Set<string>())

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

const productData = computed(() => xiansuoStore.product_data)

const allProducts = computed<ChanpinXiangmuOption[]>(() => {
  if (!productData.value) return []
  return [
    ...(productData.value.daili_jizhang_xiangmu || []),
    ...(productData.value.zengzhi_xiangmu || []),
  ]
})

// 代理记账套餐数据（临时方案，后续需要从后端API获取）
const dailiJizhangPackages = ref<ChanpinXiangmuOption[]>([
  {
    id: 'package_1',
    xiangmu_mingcheng: '财税服务套餐',
    xiangmu_bianma: 'taocan_1',
    fenlei_id: '',
    yewu_baojia: 2000,
    baojia_danwei: '月',
    banshi_tianshu: 0,
    xiangmu_beizhu: '为小微企业提供全方位财税服务的完整套餐',
    paixu: 1,
    zhuangtai: 'active',
  },
  {
    id: 'package_2',
    xiangmu_mingcheng: '小微企业记账套餐',
    xiangmu_bianma: 'taocan_2',
    fenlei_id: '',
    yewu_baojia: 800,
    baojia_danwei: '月',
    banshi_tianshu: 0,
    xiangmu_beizhu: '专为小微企业设计的基础记账服务套餐',
    paixu: 2,
    zhuangtai: 'active',
  },
  {
    id: 'package_3',
    xiangmu_mingcheng: '一般纳税人记账套餐',
    xiangmu_bianma: 'taocan_3',
    fenlei_id: '',
    yewu_baojia: 1500,
    baojia_danwei: '月',
    banshi_tianshu: 0,
    xiangmu_beizhu: '一般纳税人企业专业记账服务套餐',
    paixu: 3,
    zhuangtai: 'active',
  },
  {
    id: 'package_4',
    xiangmu_mingcheng: '高端财务管理套餐',
    xiangmu_bianma: 'taocan_4',
    fenlei_id: '',
    yewu_baojia: 3000,
    baojia_danwei: '月',
    banshi_tianshu: 0,
    xiangmu_beizhu: '大中型企业全套财务管理服务套餐',
    paixu: 4,
    zhuangtai: 'active',
  },
])

const filteredProducts = computed(() => {
  console.log('🔍 filteredProducts 计算中...')
  console.log('  activeCategory:', activeCategory.value)
  console.log('  productData 是否存在:', Boolean(productData.value))

  let products: ChanpinXiangmuOption[]
  if (!productData.value) {
    console.log('  ❌ productData 为 null/undefined')
    products = []
  } else if (activeCategory.value === 'daizang') {
    // 代理记账分类：只显示套餐，不显示单独的产品项目
    products = dailiJizhangPackages.value
    console.log('  📦 代理记账分类，显示套餐数量:', products.length)
    console.log('  📦 代理记账套餐列表:', products)
  } else if (activeCategory.value === 'zengzhi') {
    products = productData.value.zengzhi_xiangmu || []
    console.log('  📦 增值服务分类，产品数量:', products.length)
  } else {
    // 全部服务：显示套餐 + 增值服务
    products = [...dailiJizhangPackages.value, ...(productData.value.zengzhi_xiangmu || [])]
    console.log('  📦 全部服务分类，产品数量:', products.length)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    products = products.filter(
      (product) =>
        product.xiangmu_mingcheng.toLowerCase().includes(keyword) ||
        product.xiangmu_bianma.toLowerCase().includes(keyword)
    )
    console.log('  🔍 搜索后产品数量:', products.length)
  }

  console.log('  ✅ 最终返回产品数量:', products.length)
  return products
})

// 方法
const loadProductData = async () => {
  // 强制重新加载，不使用缓存
  try {
    loading.value = true
    await xiansuoStore.fetchProductData()

    // 验证数据是否加载成功
    if (!productData.value) {
      console.error('产品数据加载后仍为空')
      ElMessage.error('产品数据加载失败，请刷新页面重试')
    } else {
      console.log('产品数据加载成功:', {
        代理记账项目: productData.value.daili_jizhang_xiangmu?.length || 0,
        增值服务项目: productData.value.zengzhi_xiangmu?.length || 0,
      })
    }
  } catch (error) {
    console.error('加载产品数据失败:', error)
    ElMessage.error('加载服务项目失败')
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = () => {
  // 分类切换由计算属性自动处理
}

const handleSearch = () => {
  // 搜索逻辑在计算属性中处理
}

const isDailiJizhangPackage = (productId: string): boolean => {
  // 检查是否是代理记账套餐
  return dailiJizhangPackages.value.some((p) => p.id === productId)
}

const isDailiJizhangProduct = (productId: string): boolean => {
  // 检查是否是代理记账套餐
  const isPackage = dailiJizhangPackages.value.some((p) => p.id === productId)
  if (isPackage) return true

  // 检查是否是代理记账产品项目
  return productData.value?.daili_jizhang_xiangmu?.some((p) => p.id === productId) || false
}

const isProductInQuote = (productId: string): boolean => {
  return props.selectedServices?.some((service) => service.id === productId) || false
}

const toggleProduct = (product: ChanpinXiangmuOption) => {
  if (selectedProducts.value.has(product.id)) {
    selectedProducts.value.delete(product.id)
  } else {
    // 检查是否是代理记账服务（包括套餐和单项）
    const isDailiJizhangPackage = dailiJizhangPackages.value.some((p) => p.id === product.id)
    const isDailiJizhangItem = productData.value?.daili_jizhang_xiangmu?.some(
      (p) => p.id === product.id
    )
    const isDailiJizhang = isDailiJizhangPackage || isDailiJizhangItem

    if (isDailiJizhang) {
      // 检查已选择的服务中是否已经有代理记账服务（套餐或单项）
      const hasExistingDailiJizhang = Array.from(selectedProducts.value).some((selectedId) => {
        const isPackage = dailiJizhangPackages.value.some((p) => p.id === selectedId)
        const isItem = productData.value?.daili_jizhang_xiangmu?.some((p) => p.id === selectedId)
        return isPackage || isItem
      })

      // 检查已经在报价单中的服务是否包含代理记账
      const hasExistingDailiJizhangInQuote = props.selectedServices?.some((service) => {
        const isPackage = dailiJizhangPackages.value.some((p) => p.id === service.id)
        const isItem = productData.value?.daili_jizhang_xiangmu?.some((p) => p.id === service.id)
        return isPackage || isItem
      })

      if (hasExistingDailiJizhang || hasExistingDailiJizhangInQuote) {
        ElMessage.warning({
          message: '代理记账套餐只能选择一个，请先取消已选择的代理记账套餐',
          duration: 3000,
        })
        return
      }
    }

    selectedProducts.value.add(product.id)
  }
}

const handleConfirm = () => {
  const selected = allProducts.value.filter((product) => selectedProducts.value.has(product.id))
  emit('select', selected)
  handleClose()
}

const handleClose = () => {
  emit('update:visible', false)
  // 清空选择状态
  selectedProducts.value.clear()
  searchKeyword.value = ''
  activeCategory.value = 'all'
}

// 监听器
watch(
  () => props.visible,
  (visible, oldVisible) => {
    console.log('👁️ ProductSelector visible 变化:', { 新值: visible, 旧值: oldVisible })
    if (visible) {
      console.log('📂 对话框打开，开始加载产品数据')
      void loadProductData()
    }
  },
  { immediate: true }
)

// 生命周期
onMounted(() => {
  console.log('🎬 ProductSelector 组件已挂载, visible:', props.visible)
  if (props.visible) {
    console.log('📂 组件挂载时对话框已打开，加载产品数据')
    void loadProductData()
  }
})
</script>

<style scoped>
.product-selector {
  min-height: 400px;
}

.search-bar {
  margin-bottom: 20px;
}

.category-tabs {
  margin-bottom: 20px;
}

.product-list {
  max-height: 500px;
  overflow-y: auto;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.product-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.product-card.selected {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.product-card.already-in-quote {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f5f7fa;
}

.product-card.already-in-quote:hover {
  border-color: #dcdfe6;
  box-shadow: none;
}

.product-card.daili-jizhang {
  border-left: 3px solid #e6a23c;
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.product-name {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.product-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.product-price {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.price-label {
  color: #909399;
  font-size: 14px;
}

.price-value {
  color: #e6a23c;
  font-weight: 600;
  font-size: 16px;
  margin: 0 4px;
}

.price-unit {
  color: #909399;
  font-size: 14px;
}

.price-range {
  color: #909399;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-count {
  color: #606266;
  font-size: 14px;
}

.footer-buttons {
  display: flex;
  gap: 12px;
}
</style>
