<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择服务项目"
    width="800px"
    :before-close="handleClose"
  >
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
            :class="{ selected: selectedProducts.has(product.id) }"
            @click="toggleProduct(product)"
          >
            <div class="product-header">
              <div class="product-name">{{ product.xiangmu_mingcheng }}</div>
              <el-checkbox
                :model-value="selectedProducts.has(product.id)"
                @change="toggleProduct(product)"
                @click.stop
              />
            </div>
            
            <div v-if="product.xiangmu_bianma" class="product-desc">
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
        <div class="selected-count">
          已选择 {{ selectedProducts.size }} 个服务项目
        </div>
        <div class="footer-buttons">
          <el-button @click="handleClose">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleConfirm"
            :disabled="selectedProducts.size === 0"
          >
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

// Props
interface Props {
  visible: boolean
}

const props = defineProps<Props>()

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
  set: (value) => emit('update:visible', value)
})

const productData = computed(() => xiansuoStore.product_data)

const allProducts = computed<ChanpinXiangmuOption[]>(() => {
  if (!productData.value) return []
  return [
    ...(productData.value.daili_jizhang_xiangmu || []),
    ...(productData.value.zengzhi_xiangmu || [])
  ]
})

const filteredProducts = computed(() => {
  let products: ChanpinXiangmuOption[]
  if (!productData.value) {
    products = []
  } else if (activeCategory.value === 'daizang') {
    products = productData.value.daili_jizhang_xiangmu || []
  } else if (activeCategory.value === 'zengzhi') {
    products = productData.value.zengzhi_xiangmu || []
  } else {
    products = allProducts.value
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    products = products.filter(product =>
      product.xiangmu_mingcheng.toLowerCase().includes(keyword) ||
      product.xiangmu_bianma.toLowerCase().includes(keyword)
    )
  }

  return products
})

// 方法
const loadProductData = async () => {
  if (productData.value) return
  try {
    loading.value = true
    await xiansuoStore.fetchProductData()
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

const toggleProduct = (product: ChanpinXiangmuOption) => {
  if (selectedProducts.value.has(product.id)) {
    selectedProducts.value.delete(product.id)
  } else {
    selectedProducts.value.add(product.id)
  }
}

const handleConfirm = () => {
  const selected = allProducts.value.filter(product =>
    selectedProducts.value.has(product.id)
  )
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
watch(() => props.visible, (visible) => {
  if (visible) {
    void loadProductData()
  }
})

// 生命周期
onMounted(() => {
  if (props.visible) {
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
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.product-card.selected {
  border-color: #409EFF;
  background-color: #F0F9FF;
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
  color: #E6A23C;
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
