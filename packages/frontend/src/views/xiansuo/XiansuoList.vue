<template>
  <div class="xiansuo-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>线索管理</h2>
      <p>管理销售线索，跟踪客户转化过程</p>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="线索编码、公司名称、联系人"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="线索状态">
          <el-select
            v-model="searchForm.xiansuo_zhuangtai"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="status in active_zhuangtai_list"
              :key="status.zhuangtai_bianma"
              :label="status.zhuangtai_mingcheng"
              :value="status.zhuangtai_bianma"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="线索来源">
          <el-select
            v-model="searchForm.laiyuan_id"
            placeholder="请选择来源"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="source in active_laiyuan_list"
              :key="source.id"
              :label="source.laiyuan_mingcheng"
              :value="source.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="质量评估">
          <el-select
            v-model="searchForm.zhiliang_pinggu"
            placeholder="请选择质量"
            clearable
            style="width: 120px"
          >
            <el-option label="高质量" value="high" />
            <el-option label="中等质量" value="medium" />
            <el-option label="低质量" value="low" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="action-card">
      <div class="action-bar">
        <div class="action-left">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增线索
          </el-button>
          <el-button type="success" @click="handleBatchAssign" :disabled="selectedXiansuo.length === 0">
            <el-icon><User /></el-icon>
            批量分配
          </el-button>
        </div>
        
        <div class="action-right">
          <el-tooltip content="强制刷新所有数据，清除缓存" placement="top">
            <el-button @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-tooltip>

          <!-- 缓存状态指示器 -->
          <el-tag
            v-if="cacheStatus.hasCache"
            type="success"
            size="small"
            style="margin-left: 8px"
          >
            <el-icon><Clock /></el-icon>
            已缓存
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ newXiansuo }}</div>
          <div class="stat-label">新线索</div>
        </div>
        <div class="stat-icon new">
          <el-icon><Plus /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ followingXiansuo }}</div>
          <div class="stat-label">跟进中</div>
        </div>
        <div class="stat-icon following">
          <el-icon><Phone /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ interestedXiansuo }}</div>
          <div class="stat-label">有意向</div>
        </div>
        <div class="stat-icon interested">
          <el-icon><Star /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ wonXiansuo }}</div>
          <div class="stat-label">已成交</div>
        </div>
        <div class="stat-icon won">
          <el-icon><Check /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ total }}</div>
          <div class="stat-label">总线索数</div>
        </div>
        <div class="stat-icon total">
          <el-icon><DataAnalysis /></el-icon>
        </div>
      </el-card>
    </div>

    <!-- 线索表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="xiansuo_list"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="xiansuo_bianma" label="线索编码" width="120" />
        
        <el-table-column prop="gongsi_mingcheng" label="公司信息" min-width="200">
          <template #default="{ row }">
            <div class="company-info">
              <div class="company-name">{{ row.gongsi_mingcheng }}</div>
              <div class="contact-info">{{ row.lianxi_ren }} {{ row.lianxi_dianhua }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="hangye_leixing" label="行业类型" width="120" />
        
        <el-table-column prop="zhiliang_pinggu" label="质量评估" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getQualityTagType(row.zhiliang_pinggu)"
              size="small"
            >
              {{ getQualityText(row.zhiliang_pinggu) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="xiansuo_zhuangtai" label="线索状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusTagType(row.xiansuo_zhuangtai)"
              size="small"
            >
              {{ getStatusText(row.xiansuo_zhuangtai) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="报价状态" width="100">
          <template #default="{ row }">
            <el-tag
              v-if="getBaojiaStatus(row.id)"
              :type="getBaojiaStatusTagType(getBaojiaStatus(row.id)!)"
              size="small"
            >
              {{ getBaojiaStatusText(getBaojiaStatus(row.id)!) }}
            </el-tag>
            <span v-else class="text-gray-400">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="genjin_cishu" label="跟进次数" width="80" />
        
        <el-table-column prop="zuijin_genjin_shijian" label="最近跟进" width="120">
          <template #default="{ row }">
            {{ row.zuijin_genjin_shijian ? formatDate(row.zuijin_genjin_shijian) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="success" size="small" @click="handleEdit(row)">
              编辑
            </el-button>

            <!-- 动态报价按钮 -->
            <el-button
              v-if="!hasValidBaojia(row)"
              type="warning"
              size="small"
              @click="handleCreateBaojia(row)"
            >
              报价
            </el-button>
            <el-button
              v-else
              type="info"
              size="small"
              @click="handleViewBaojia(row)"
            >
              查看报价
            </el-button>
            <el-button
              v-if="hasValidBaojia(row)"
              type="success"
              size="small"
              plain
              @click="handleCopyQuoteLink(row)"
            >
              分享报价
            </el-button>

            <!-- 生成合同按钮 -->
            <el-button
              v-if="canGenerateContract(row)"
              type="primary"
              size="small"
              @click="handleGenerateContract(row)"
              :loading="contractGenerating"
            >
              生成合同
            </el-button>

            <el-dropdown @command="(command) => handleAction(command, row)">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="assign">分配</el-dropdown-item>
                  <el-dropdown-item command="status">状态</el-dropdown-item>
                  <el-dropdown-item command="followup">跟进</el-dropdown-item>
                  <el-dropdown-item
                    v-if="hasValidBaojia(row)"
                    command="edit_baojia"
                  >
                    编辑报价
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 线索表单弹窗 -->
    <XiansuoForm
      v-model:visible="formVisible"
      :mode="formMode"
      :xiansuo="currentXiansuo"
      @success="handleFormSuccess"
    />

    <!-- 线索详情弹窗 -->
    <XiansuoDetail
      v-model:visible="detailVisible"
      :xiansuo-id="currentXiansuoId"
    />

    <!-- 报价表单弹窗 -->
    <XiansuoBaojiaForm
      v-model:visible="baojiaFormVisible"
      :mode="baojiaFormMode"
      :xiansuo="currentBaojiaXiansuo"
      :baojia="currentBaojia"
      @success="handleBaojiaSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  User,
  Clock,
  Phone,
  Star,
  Check,
  DataAnalysis,
  ArrowDown
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/modules/auth'
import XiansuoForm from '@/components/xiansuo/XiansuoForm.vue'
import XiansuoDetail from '@/components/xiansuo/XiansuoDetail.vue'
import XiansuoBaojiaForm from '@/components/xiansuo/XiansuoBaojiaForm.vue'
import type { Xiansuo, XiansuoBaojia } from '@/types/xiansuo'

// 使用store
const xiansuoStore = useXiansuoStore()
const contractStore = useContractManagementStore()
const authStore = useAuthStore()
const router = useRouter()

// 响应式数据
const searchForm = ref({
  search: '',
  xiansuo_zhuangtai: '',
  laiyuan_id: '',
  zhiliang_pinggu: ''
})

const formVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const currentXiansuo = ref<Xiansuo | null>(null)
const detailVisible = ref(false)
const currentXiansuoId = ref('')
const selectedXiansuo = ref<Xiansuo[]>([])

// 报价相关
const baojiaFormVisible = ref(false)
const baojiaFormMode = ref<'create' | 'edit'>('create')
const currentBaojia = ref<XiansuoBaojia | null>(null)
const currentBaojiaXiansuo = ref<Xiansuo | null>(null)

// 合同生成相关
const contractGenerating = ref(false)

// 计算属性
const {
  xiansuo_list,
  loading,
  total,
  currentPage,
  pageSize,
  active_laiyuan_list,
  active_zhuangtai_list,
  newXiansuo,
  followingXiansuo,
  interestedXiansuo,
  wonXiansuo,
  cache
} = storeToRefs(xiansuoStore)

// 缓存状态
const cacheStatus = computed(() => {
  const cacheState = cache.value
  const now = Date.now()
  const CACHE_EXPIRE_TIME = 5 * 60 * 1000 // 5分钟

  const hasLaiyuanCache = cacheState.laiyuan_loaded &&
    (now - cacheState.laiyuan_timestamp) < CACHE_EXPIRE_TIME
  const hasZhuangtaiCache = cacheState.zhuangtai_loaded &&
    (now - cacheState.zhuangtai_timestamp) < CACHE_EXPIRE_TIME
  const hasXiansuoCache = cacheState.xiansuo_cache && cacheState.xiansuo_cache.size > 0

  return {
    hasCache: hasLaiyuanCache || hasZhuangtaiCache || hasXiansuoCache,
    laiyuanCached: hasLaiyuanCache,
    zhuangtaiCached: hasZhuangtaiCache,
    xiansuoCached: hasXiansuoCache
  }
})

// 方法
const handleSearch = async () => {
  await xiansuoStore.fetchXiansuoList(searchForm.value)
}

const handleReset = async () => {
  searchForm.value = {
    search: '',
    xiansuo_zhuangtai: '',
    laiyuan_id: '',
    zhiliang_pinggu: ''
  }
  await xiansuoStore.fetchXiansuoList()
}

const handleRefresh = async () => {
  console.log('手动刷新数据，清除缓存')
  ElMessage.info('正在刷新数据...')

  // 强制刷新所有数据，清除缓存
  await xiansuoStore.refreshAllData()

  ElMessage.success('数据刷新完成')
}

const handleCreate = () => {
  formMode.value = 'create'
  currentXiansuo.value = null
  formVisible.value = true
}

const handleView = (xiansuo: Xiansuo) => {
  currentXiansuoId.value = xiansuo.id
  detailVisible.value = true
}

const handleEdit = (xiansuo: Xiansuo) => {
  formMode.value = 'edit'
  currentXiansuo.value = xiansuo
  formVisible.value = true
}

const handleAction = async (command: string, xiansuo: Xiansuo) => {
  switch (command) {
    case 'assign':
      // TODO: 实现分配功能
      ElMessage.info('分配功能开发中')
      break
    case 'status':
      // TODO: 实现状态更新功能
      ElMessage.info('状态更新功能开发中')
      break
    case 'followup':
      // TODO: 实现跟进功能
      ElMessage.info('跟进功能开发中')
      break
    case 'edit_baojia':
      await handleEditBaojia(xiansuo)
      break
    case 'delete':
      await handleDelete(xiansuo)
      break
  }
}

const handleDelete = async (xiansuo: Xiansuo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除线索"${xiansuo.gongsi_mingcheng}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await xiansuoStore.deleteXiansuo(xiansuo.id)
    await handleSearch()
  } catch (error) {
    // 用户取消删除
  }
}

const handleBatchAssign = () => {
  ElMessage.info('批量分配功能开发中')
}

const handleSelectionChange = (selection: Xiansuo[]) => {
  selectedXiansuo.value = selection
}

const handleSizeChange = async (size: number) => {
  pageSize.value = size
  await handleSearch()
}

const handleCurrentChange = async (page: number) => {
  currentPage.value = page
  await handleSearch()
}

const handleFormSuccess = async () => {
  formVisible.value = false
  await handleSearch()
}

// 报价相关方法
const hasValidBaojia = (xiansuo: Xiansuo) => {
  if (xiansuoStore.hasValidBaojia(xiansuo.id)) {
    return true
  }
  return ['quoted', 'won'].includes(xiansuo.xiansuo_zhuangtai)
}

const handleCreateBaojia = async (xiansuo: Xiansuo) => {
  try {
    // 先加载该线索的报价列表
    await xiansuoStore.fetchBaojiaByXiansuo(xiansuo.id)

    // 检查是否已有有效报价
    if (hasValidBaojia(xiansuo)) {
      ElMessage.warning('该线索已有有效报价，请先处理现有报价')
      return
    }

    baojiaFormMode.value = 'create'
    currentBaojia.value = null
    currentBaojiaXiansuo.value = xiansuo
    baojiaFormVisible.value = true
  } catch (error) {
    console.error('准备创建报价失败:', error)
  }
}

const handleViewBaojia = async (xiansuo: Xiansuo) => {
  try {
    // 加载报价列表并显示详情
    const list = await xiansuoStore.fetchBaojiaByXiansuo(xiansuo.id)
    if (!list.length) {
      ElMessage.warning('该线索尚未创建报价')
      return
    }
    const target = list.find(item => !item.is_expired && item.baojia_zhuangtai !== 'rejected') || list[0]
    router.push({ name: 'QuotePreview', params: { id: target.id } })
  } catch (error) {
    console.error('查看报价失败:', error)
  }
}

const handleCopyQuoteLink = async (xiansuo: Xiansuo) => {
  try {
    const list = await xiansuoStore.fetchBaojiaByXiansuo(xiansuo.id)
    const target = list.find(item => !item.is_expired && item.baojia_zhuangtai !== 'rejected') || list[0]

    if (!target) {
      ElMessage.warning('该线索尚未创建报价')
      return
    }

    const detail = await xiansuoStore.getBaojiaDetailWithXiansuo(target.id)
    const payload = encodeURIComponent(btoa(unescape(encodeURIComponent(JSON.stringify(detail)))))
    const link = `${window.location.origin}/quote-preview/${target.id}?payload=${payload}`
    await navigator.clipboard.writeText(link)
    ElMessage.success('报价链接已复制，可发送给客户')
  } catch (error) {
    console.error('复制报价链接失败:', error)
    ElMessage.error('复制报价链接失败')
  }
}

const handleEditBaojia = async (xiansuo: Xiansuo) => {
  try {
    // 加载报价列表
    await xiansuoStore.fetchBaojiaByXiansuo(xiansuo.id)

    const validBaojia = xiansuoStore.getBaojiaListByXiansuo(xiansuo.id).find(
      b => !b.is_expired && b.baojia_zhuangtai !== 'rejected'
    )

    if (!validBaojia) {
      ElMessage.warning('未找到有效的报价')
      return
    }

    baojiaFormMode.value = 'edit'
    currentBaojia.value = validBaojia
    currentBaojiaXiansuo.value = xiansuo
    baojiaFormVisible.value = true
  } catch (error) {
    console.error('准备编辑报价失败:', error)
  }
}

const handleBaojiaSuccess = async () => {
  baojiaFormVisible.value = false
  // 刷新线索列表以更新状态
  await handleSearch()
}

// 判断是否可以生成合同
const canGenerateContract = (xiansuo: Xiansuo) => {
  const baojiaStatus = getBaojiaStatus(xiansuo.id)
  return baojiaStatus === 'accepted' && hasValidBaojia(xiansuo)
}

// 生成合同
const handleGenerateContract = async (xiansuo: Xiansuo) => {
  try {
    contractGenerating.value = true

    // 获取已确认的报价
    const baojiaList = await xiansuoStore.fetchBaojiaByXiansuo(xiansuo.id)
    const acceptedBaojia = baojiaList.find(b => b.baojia_zhuangtai === 'accepted' && !b.is_expired)

    if (!acceptedBaojia) {
      ElMessage.warning('未找到已确认的报价')
      return
    }

    // 显示生成方式选择对话框
    const action = await ElMessageBox.confirm(
      `基于报价"${acceptedBaojia.baojia_mingcheng}"生成合同，请选择生成方式：`,
      '生成合同',
      {
        confirmButtonText: '直接生成',
        cancelButtonText: '自定义生成',
        distinguishCancelAndClose: true,
        type: 'info'
      }
    ).then(() => 'direct').catch((action) => {
      if (action === 'cancel') {
        return 'custom'
      }
      throw action
    })

    if (action === 'direct') {
      // 直接生成合同
      await contractStore.createContractFromQuote(acceptedBaojia.id)
      ElMessage.success('合同生成成功！')

      // 刷新线索列表
      await xiansuoStore.fetchXiansuoList()
    } else if (action === 'custom') {
      // 跳转到合同创建页面，预填报价信息
      router.push({
        path: '/contracts/create',
        query: { baojia_id: acceptedBaojia.id }
      })
    }

  } catch (error: any) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('生成合同失败:', error)
      ElMessage.error('生成合同失败')
    }
  } finally {
    contractGenerating.value = false
  }
}

// 工具方法
const getQualityTagType = (quality: string) => {
  const types: Record<string, string> = {
    high: 'success',
    medium: 'warning',
    low: 'danger'
  }
  return types[quality] || ''
}

const getQualityText = (quality: string) => {
  const texts: Record<string, string> = {
    high: '高质量',
    medium: '中等质量',
    low: '低质量'
  }
  return texts[quality] || quality
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    new: 'info',
    following: 'primary',
    interested: 'warning',
    quoted: 'danger',
    won: 'success',
    lost: 'info'
  }
  return types[status] || ''
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    new: '新线索',
    following: '跟进中',
    interested: '有意向',
    quoted: '已报价',
    won: '成交',
    lost: '无效'
  }
  return texts[status] || status
}

// 获取线索的最新报价状态
const getBaojiaStatus = (xiansuoId: string) => {
  const baojiaList = xiansuoStore.getBaojiaListByXiansuo(xiansuoId)
  if (!baojiaList || baojiaList.length === 0) {
    return null
  }

  // 获取最新的非过期、非拒绝的报价
  const validBaojia = baojiaList
    .filter(baojia => !baojia.is_expired && baojia.baojia_zhuangtai !== 'rejected')
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  return validBaojia.length > 0 ? validBaojia[0].baojia_zhuangtai : null
}

// 获取报价状态的标签类型
const getBaojiaStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    sent: 'warning',
    accepted: 'success',
    rejected: 'danger',
    expired: 'danger'
  }
  return types[status] || 'info'
}

// 获取报价状态的文本
const getBaojiaStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    sent: '已发送',
    accepted: '已确认',
    rejected: '已拒绝',
    expired: '已过期'
  }
  return texts[status] || status
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

// 生命周期
onMounted(async () => {
  console.log('线索列表页面初始化，使用缓存优化加载')

  // 检查认证状态
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated) {
    console.warn('用户未认证，尝试恢复认证状态')
    await authStore.restoreFromStorage()

    if (!authStore.isAuthenticated) {
      ElMessage.error('认证已过期，请重新登录')
      return
    }
  }

  try {
    // 先初始化基础数据（来源和状态），这些数据变化较少，优先使用缓存
    await xiansuoStore.initializeData()

    // 再加载线索列表，确保使用正确的分页参数
    await xiansuoStore.fetchXiansuoList({
      page: 1,
      size: 20
    })

    console.log('线索列表页面初始化完成')
  } catch (error) {
    console.error('线索列表页面初始化失败:', error)

    // 如果是401错误，提示重新登录
    if (error?.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      authStore.logout()
    } else {
      ElMessage.error('数据加载失败，请刷新页面重试')
    }
  }
})
</script>

<style scoped>
.xiansuo-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-card,
.action-card,
.table-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left,
.action-right {
  display: flex;
  gap: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card .el-card__body {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.new {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.stat-icon.following {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stat-icon.interested {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.stat-icon.won {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stat-icon.total {
  background: linear-gradient(135deg, #909399, #a6a9ad);
}

.company-info {
  line-height: 1.4;
}

.company-name {
  font-weight: 500;
  color: #303133;
}

.contact-info {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
