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
          <el-button
            type="success"
            @click="handleBatchAssign"
            :disabled="selectedXiansuo.length === 0"
          >
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
          <el-tag v-if="cacheStatus.hasCache" type="success" size="small" style="margin-left: 8px">
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
            <el-tag :type="getQualityTagType(row.zhiliang_pinggu)" size="small">
              {{ getQualityText(row.zhiliang_pinggu) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="xiansuo_zhuangtai" label="线索状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.xiansuo_zhuangtai)" size="small">
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

        <el-table-column label="操作" width="320" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <!-- 第一行：主要操作按钮 -->
              <div class="action-row primary-actions">
                <el-button type="primary" size="small" link @click="handleView(row)">
                  查看
                </el-button>
                <el-button type="success" size="small" @click="handleEdit(row)"> 编辑 </el-button>

                <!-- 动态报价按钮 -->
                <el-button
                  v-if="!hasValidBaojia(row)"
                  type="warning"
                  size="small"
                  @click="handleCreateBaojia(row)"
                >
                  报价
                </el-button>
                <el-button v-else type="info" size="small" @click="handleViewBaojia(row)">
                  查看报价
                </el-button>

                <el-dropdown @command="(command: string) => handleAction(command, row)">
                  <el-button size="small">
                    更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="assign">分配</el-dropdown-item>
                      <el-dropdown-item command="status">状态</el-dropdown-item>
                      <el-dropdown-item command="followup">跟进</el-dropdown-item>
                      <el-dropdown-item v-if="hasValidBaojia(row)" command="edit_baojia">
                        编辑报价
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>

              <!-- 第二行：次要操作按钮（仅在有报价或合同时显示） -->
              <div
                v-if="hasValidBaojia(row) || getLeadActionType(row)"
                class="action-row secondary-actions"
              >
                <!-- 分享报价按钮 -->
                <el-button
                  v-if="hasValidBaojia(row)"
                  type="success"
                  size="small"
                  plain
                  @click="handleCopyQuoteLink(row)"
                >
                  分享报价
                </el-button>

                <!-- 动态按钮：根据状态显示不同的操作 -->
                <!-- 查看审核按钮 -->
                <el-button
                  v-if="getLeadActionType(row) === 'view_audit'"
                  type="warning"
                  size="small"
                  @click="handleViewAudit(row)"
                >
                  查看审核
                </el-button>

                <!-- 查看合同按钮 -->
                <el-button
                  v-else-if="getLeadActionType(row) === 'view_contract'"
                  type="success"
                  size="small"
                  @click="handleViewContract(row)"
                >
                  查看合同
                </el-button>

                <!-- 生成合同按钮 -->
                <el-button
                  v-else-if="getLeadActionType(row) === 'generate_contract'"
                  type="primary"
                  size="small"
                  @click="handleGenerateContract(row)"
                  :loading="contractGenerating"
                >
                  生成合同
                </el-button>
              </div>
            </div>
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
    <XiansuoDetail v-model:visible="detailVisible" :xiansuo-id="currentXiansuoId" />

    <!-- 报价表单弹窗 -->
    <XiansuoBaojiaForm
      v-model:visible="baojiaFormVisible"
      :mode="baojiaFormMode"
      :xiansuo="currentBaojiaXiansuo"
      :baojia="currentBaojia"
      @success="handleBaojiaSuccess"
    />

    <!-- 分配对话框 -->
    <XiansuoAssignDialog
      v-model:visible="assignDialogVisible"
      :xiansuo="currentAssignXiansuo"
      @success="handleAssignSuccess"
    />

    <!-- 跟进对话框 -->
    <XiansuoFollowupDialog
      v-model:visible="followupDialogVisible"
      :xiansuo="currentFollowupXiansuo"
    />

    <!-- 审核详情弹框 -->
    <el-dialog
      v-model="auditDialogVisible"
      title="合同审核进度"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="currentAuditDetails" class="audit-details">
        <div class="audit-header">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="流程编号">
              {{ currentAuditDetails.workflow_number }}
            </el-descriptions-item>
            <el-descriptions-item label="当前步骤">
              {{ currentAuditDetails.current_step }} / {{ currentAuditDetails.total_steps }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{
                currentAuditDetails.created_at
                  ? new Date(currentAuditDetails.created_at).toLocaleString()
                  : '-'
              }}
            </el-descriptions-item>
            <el-descriptions-item label="完成时间">
              {{
                currentAuditDetails.completed_at
                  ? new Date(currentAuditDetails.completed_at).toLocaleString()
                  : '审核中'
              }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="audit-steps" style="margin-top: 20px">
          <el-timeline>
            <el-timeline-item
              v-for="step in currentAuditDetails.steps"
              :key="step.step_number"
              :type="
                step.status === 'approved'
                  ? 'success'
                  : step.status === 'rejected'
                    ? 'danger'
                    : 'primary'
              "
              :hollow="step.status === 'pending'"
            >
              <div class="step-content">
                <div class="step-header">
                  <span class="step-name">{{ step.step_name }}</span>
                  <el-tag
                    :type="
                      step.status === 'approved'
                        ? 'success'
                        : step.status === 'rejected'
                          ? 'danger'
                          : 'info'
                    "
                    size="small"
                  >
                    {{
                      step.status === 'approved'
                        ? '已通过'
                        : step.status === 'rejected'
                          ? '已拒绝'
                          : '待审核'
                    }}
                  </el-tag>
                </div>
                <div class="step-info">
                  <div>审核人：{{ step.auditor_name }}</div>
                  <div v-if="step.audit_time">
                    审核时间：{{ new Date(step.audit_time).toLocaleString() }}
                  </div>
                  <div v-if="step.comment" class="step-comment">审核意见：{{ step.comment }}</div>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>

      <template #footer>
        <el-button @click="auditDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
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
  ArrowDown,
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import { useAuthStore } from '@/stores/modules/auth'
import { storeToRefs } from 'pinia'
import XiansuoForm from '@/components/xiansuo/XiansuoForm.vue'
import XiansuoDetail from '@/components/xiansuo/XiansuoDetail.vue'
import XiansuoBaojiaForm from '@/components/xiansuo/XiansuoBaojiaForm.vue'
import XiansuoAssignDialog from './components/XiansuoAssignDialog.vue'
import XiansuoFollowupDialog from './components/XiansuoFollowupDialog.vue'
import type { Xiansuo, XiansuoBaojia } from '@/types/xiansuo'
import { xiansuoApi } from '@/api/modules/xiansuo'

// 使用store
const xiansuoStore = useXiansuoStore()
const router = useRouter()

// 响应式数据
const searchForm = ref({
  search: '',
  xiansuo_zhuangtai: '',
  laiyuan_id: '',
  zhiliang_pinggu: '',
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

// 分配相关
const assignDialogVisible = ref(false)
const currentAssignXiansuo = ref<Xiansuo | null>(null)

// 跟进相关
const followupDialogVisible = ref(false)
const currentFollowupXiansuo = ref<Xiansuo | null>(null)

// 合同生成相关
const contractGenerating = ref(false)
const contractStatusMap = ref<Map<string, any>>(new Map()) // 存储线索ID -> 合同状态信息的映射

// 审核弹框相关
const auditDialogVisible = ref(false)
const currentAuditDetails = ref<any>(null)

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
  cache,
} = storeToRefs(xiansuoStore)

// 缓存状态
const cacheStatus = computed(() => {
  const cacheState = cache.value
  const now = Date.now()
  const CACHE_EXPIRE_TIME = 5 * 60 * 1000 // 5分钟

  const hasLaiyuanCache =
    cacheState.laiyuan_loaded && now - cacheState.laiyuan_timestamp < CACHE_EXPIRE_TIME
  const hasZhuangtaiCache =
    cacheState.zhuangtai_loaded && now - cacheState.zhuangtai_timestamp < CACHE_EXPIRE_TIME
  const hasXiansuoCache = cacheState.xiansuo_cache && cacheState.xiansuo_cache.size > 0

  return {
    hasCache: hasLaiyuanCache || hasZhuangtaiCache || hasXiansuoCache,
    laiyuanCached: hasLaiyuanCache,
    zhuangtaiCached: hasZhuangtaiCache,
    xiansuoCached: hasXiansuoCache,
  }
})

// 方法
const handleSearch = async () => {
  await xiansuoStore.fetchXiansuoList(searchForm.value)
  // 加载合同状态
  await loadContractStatuses()
}

// 加载所有线索的合同状态
const loadContractStatuses = async () => {
  try {
    const leads = xiansuo_list.value

    // 批量加载合同状态（只加载有已确认报价的线索）
    const promises = leads
      .filter((lead) => {
        const baojiaStatus = getBaojiaStatus(lead.id)
        return baojiaStatus === 'accepted' && hasValidBaojia(lead)
      })
      .map(async (lead) => {
        try {
          const response = await xiansuoApi.getContractStatus(lead.id)
          // response本身就是数据对象，不需要.data
          if (response?.contract_status) {
            contractStatusMap.value.set(lead.id, response)
          }
        } catch (error) {
          console.error(`加载线索 ${lead.id} 的合同状态失败:`, error)
        }
      })

    await Promise.all(promises)
  } catch (error) {
    console.error('加载合同状态失败:', error)
  }
}

const handleReset = async () => {
  searchForm.value = {
    search: '',
    xiansuo_zhuangtai: '',
    laiyuan_id: '',
    zhiliang_pinggu: '',
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
      currentAssignXiansuo.value = xiansuo
      assignDialogVisible.value = true
      break
    case 'status':
      // 状态已改为自动流转，不再支持手动修改
      ElMessage.info('线索状态会根据业务流程自动更新：分配→跟进中，报价→已报价，签约→已成交')
      break
    case 'followup':
      currentFollowupXiansuo.value = xiansuo
      followupDialogVisible.value = true
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
        type: 'warning',
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
    const target =
      list.find((item) => !item.is_expired && item.baojia_zhuangtai !== 'rejected') || list[0]
    router.push({ name: 'QuotePreview', params: { id: target.id } })
  } catch (error) {
    console.error('查看报价失败:', error)
  }
}

const handleCopyQuoteLink = async (xiansuo: Xiansuo) => {
  try {
    const list = await xiansuoStore.fetchBaojiaByXiansuo(xiansuo.id)
    const target =
      list.find((item) => !item.is_expired && item.baojia_zhuangtai !== 'rejected') || list[0]

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

    const validBaojia = xiansuoStore
      .getBaojiaListByXiansuo(xiansuo.id)
      .find((b) => !b.is_expired && b.baojia_zhuangtai !== 'rejected')

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

const handleAssignSuccess = async () => {
  assignDialogVisible.value = false
  // 刷新线索列表以更新状态
  await handleSearch()
}

// 获取合同状态信息
const getContractStatusInfo = (xiansuoId: string) => {
  return contractStatusMap.value.get(xiansuoId) || null
}

// 判断线索的操作类型
const getLeadActionType = (xiansuo: Xiansuo) => {
  const baojiaStatus = getBaojiaStatus(xiansuo.id)

  // 如果没有已确认的报价，不显示任何按钮
  if (baojiaStatus !== 'accepted' || !hasValidBaojia(xiansuo)) {
    return null
  }

  // 检查是否有合同
  const contractInfo = getContractStatusInfo(xiansuo.id)

  if (!contractInfo || !contractInfo.contract_status) {
    // 没有合同，可以生成
    return 'generate_contract'
  }

  // 如果有审核流程且审核状态为pending
  if (contractInfo.audit_status === 'pending') {
    // 合同待审核或审核中
    return 'view_audit'
  } else if (
    contractInfo.contract_status === 'active' ||
    contractInfo.contract_status === 'signed' ||
    contractInfo.contract_status === 'approved'
  ) {
    // 合同已生效或已签署
    return 'view_contract'
  } else if (contractInfo.contract_status === 'pending') {
    // 合同待审核（没有审核流程的情况）
    return 'view_audit'
  } else {
    // 其他状态，显示查看合同
    return 'view_contract'
  }
}

// 判断是否可以生成合同（保留向后兼容）
const canGenerateContract = (xiansuo: Xiansuo) => {
  return getLeadActionType(xiansuo) === 'generate_contract'
}

// 查看审核
const handleViewAudit = async (xiansuo: Xiansuo) => {
  try {
    const contractInfo = getContractStatusInfo(xiansuo.id)

    if (contractInfo?.audit_details) {
      // 显示审核详情弹框
      currentAuditDetails.value = contractInfo.audit_details
      auditDialogVisible.value = true
    } else {
      // 如果没有审核详情，跳转到审核任务页面
      router.push('/audit/tasks')
      ElMessage.info('请在审核任务列表中查看相关审核')
    }
  } catch (error: any) {
    console.error('查看审核失败:', error)
    ElMessage.error('查看审核失败')
  }
}

// 查看合同
const handleViewContract = async (xiansuo: Xiansuo) => {
  try {
    // 直接跳转到合同列表页面
    router.push('/contracts')
  } catch (error: any) {
    console.error('跳转到合同页面失败:', error)
    ElMessage.error('跳转失败')
  }
}

// 生成合同
const handleGenerateContract = async (xiansuo: Xiansuo) => {
  try {
    contractGenerating.value = true

    // 获取已确认的报价
    const baojiaList = await xiansuoStore.fetchBaojiaByXiansuo(xiansuo.id)
    const acceptedBaojia = baojiaList.find(
      (b) => b.baojia_zhuangtai === 'accepted' && !b.is_expired
    )

    if (!acceptedBaojia) {
      ElMessage.warning('未找到已确认的报价')
      return
    }

    // 直接跳转到合同生成页面，预填报价信息
    router.push({
      path: '/contracts/generate',
      query: { baojia_id: acceptedBaojia.id },
    })
  } catch (error: any) {
    console.error('跳转到合同生成页面失败:', error)
    ElMessage.error('跳转失败: ' + (error?.message || '未知错误'))
  } finally {
    contractGenerating.value = false
  }
}

// 工具方法
const getQualityTagType = (quality: string) => {
  const types: Record<string, string> = {
    high: 'success',
    medium: 'warning',
    low: 'danger',
  }
  return types[quality] || ''
}

const getQualityText = (quality: string) => {
  const texts: Record<string, string> = {
    high: '高质量',
    medium: '中等质量',
    low: '低质量',
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
    lost: 'info',
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
    lost: '无效',
  }
  return texts[status] || status
}

// 获取线索的最新报价状态
const getBaojiaStatus = (xiansuoId: string) => {
  const baojiaList = xiansuoStore.getBaojiaListByXiansuo(xiansuoId)
  console.log(`🔍 获取线索 ${xiansuoId} 的报价状态:`)
  console.log(`   - 从store获取的报价列表长度: ${baojiaList ? baojiaList.length : 0}`)

  if (!baojiaList || baojiaList.length === 0) {
    console.log(`   - 结果: 无报价数据`)
    return null
  }

  // 获取最新的非过期、非拒绝的报价
  const validBaojia = baojiaList
    .filter((baojia) => !baojia.is_expired && baojia.baojia_zhuangtai !== 'rejected')
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  console.log(`   - 有效报价数量: ${validBaojia.length}`)
  if (validBaojia.length > 0) {
    console.log(`   - 最新有效报价状态: ${validBaojia[0].baojia_zhuangtai}`)
  }

  const result = validBaojia.length > 0 ? validBaojia[0].baojia_zhuangtai : null
  console.log(`   - 结果: ${result || '无有效报价'}`)
  return result
}

// 获取报价状态的标签类型
const getBaojiaStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    sent: 'warning',
    accepted: 'success',
    rejected: 'danger',
    expired: 'danger',
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
    expired: '已过期',
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
      size: 20,
    })

    // 加载合同状态
    await loadContractStatuses()

    console.log('线索列表页面初始化完成')
  } catch (error) {
    console.error('线索列表页面初始化失败:', error)

    // 如果是401错误，提示重新登录
    if ((error as any)?.response?.status === 401) {
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

/* 审核详情样式 */
.audit-details {
  .audit-header {
    margin-bottom: 20px;
  }

  .step-content {
    .step-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .step-name {
        font-weight: 500;
        font-size: 15px;
        color: #303133;
      }
    }

    .step-info {
      font-size: 13px;
      color: #606266;
      line-height: 1.8;

      .step-comment {
        margin-top: 8px;
        padding: 8px 12px;
        background-color: #f5f7fa;
        border-radius: 4px;
        color: #606266;
      }
    }
  }
}

/* 操作按钮布局优化 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  width: 100%;
}

.action-row {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
}

.action-row.secondary-actions {
  /* 次要操作行 */
  padding-top: 2px;
}

/* 确保按钮不换行 */
.action-buttons .el-button {
  white-space: nowrap;
  margin: 0 !important;
}

/* 优化按钮间距 */
.action-buttons .el-button + .el-button {
  margin-left: 0 !important;
}

/* 优化下拉菜单按钮 */
.action-buttons .el-dropdown {
  margin-left: 0 !important;
}

.action-buttons .el-dropdown .el-button {
  margin-left: 0 !important;
}
</style>
