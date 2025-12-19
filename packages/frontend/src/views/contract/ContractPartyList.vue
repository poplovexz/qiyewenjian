<template>
  <div class="contract-party-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>乙方主体管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增主体
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :model="searchForm" inline>
          <el-form-item label="主体名称">
            <el-input
              v-model="searchForm.search"
              placeholder="请输入主体名称"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="主体类型">
            <el-select
              v-model="searchForm.zhuti_leixing"
              placeholder="请选择类型"
              clearable
              style="width: 150px"
            >
              <el-option
                v-for="option in partyTypeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
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
      </div>

      <!-- 表格区域 -->
      <div class="table-area">
        <el-table
          :data="parties"
          v-loading="loading"
          stripe
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="zhuti_mingcheng" label="主体名称" min-width="150" />
          <el-table-column prop="zhuti_leixing" label="主体类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getPartyTypeTagType(row.zhuti_leixing)">
                {{ getPartyTypeLabel(row.zhuti_leixing) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="tongyi_shehui_xinyong_daima"
            label="统一社会信用代码"
            width="180"
          />
          <el-table-column prop="faren_daibiao" label="法人代表" width="120" />
          <el-table-column prop="lianxi_dianhua" label="联系电话" width="130" />
          <el-table-column prop="lianxi_youxiang" label="联系邮箱" width="180" />
          <el-table-column prop="payment_method_count" label="支付方式数" width="120">
            <template #default="{ row }">
              <el-tag type="info">{{ row.payment_method_count || 0 }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleView(row)"> 查看 </el-button>
              <el-button type="warning" size="small" @click="handleEdit(row)"> 编辑 </el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)"> 删除 </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页区域 -->
      <div class="pagination-area">
        <el-pagination
          v-model:current-page="partyPage"
          v-model:page-size="partySize"
          :total="partyTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>

      <!-- 批量操作区域 -->
      <div class="batch-actions" v-if="selectedParties.length > 0">
        <el-alert
          :title="`已选择 ${selectedParties.length} 项`"
          type="info"
          show-icon
          :closable="false"
        >
          <template #default>
            <div class="batch-buttons">
              <el-button type="danger" size="small" @click="handleBatchDelete">
                批量删除
              </el-button>
            </div>
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 主体详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="主体详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="party-detail" v-if="currentParty">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="主体名称">
            {{ currentParty.zhuti_mingcheng }}
          </el-descriptions-item>
          <el-descriptions-item label="主体类型">
            <el-tag :type="getPartyTypeTagType(currentParty.zhuti_leixing)">
              {{ getPartyTypeLabel(currentParty.zhuti_leixing) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="统一社会信用代码">
            {{ currentParty.tongyi_shehui_xinyong_daima || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="营业执照号码">
            {{ currentParty.yingyezhizhao_haoma || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="法人代表">
            {{ currentParty.faren_daibiao || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            {{ currentParty.lianxi_dianhua || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="联系邮箱">
            {{ currentParty.lianxi_youxiang || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="注册地址" span="2">
            {{ currentParty.zhuce_dizhi || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="银行名称">
            {{ currentParty.yinhang_mingcheng || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="银行账户">
            {{ currentParty.yinhang_zhanghu || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="开户行">
            {{ currentParty.yinhang_kaihuhang || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(currentParty.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" span="2">
            {{ currentParty.beizhu || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="payment-methods" v-if="currentParty.payment_methods?.length">
          <el-divider content-position="left">关联支付方式</el-divider>
          <el-table :data="currentParty.payment_methods" size="small" stripe>
            <el-table-column prop="zhifu_mingcheng" label="支付方式" min-width="120" />
            <el-table-column prop="zhifu_leixing" label="类型" width="120">
              <template #default="{ row }">
                <el-tag
                  :type="
                    row.zhifu_leixing === 'yinhangzhuanzhang'
                      ? 'primary'
                      : row.zhifu_leixing === 'weixin'
                        ? 'success'
                        : row.zhifu_leixing === 'zhifubao'
                          ? 'warning'
                          : 'info'
                  "
                >
                  {{ getPaymentTypeText(row.zhifu_leixing) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="zhanghu_mingcheng" label="账户名称" min-width="150" />
            <el-table-column prop="zhanghu_haoma" label="账户号" min-width="150" />
            <el-table-column prop="shi_moren" label="默认" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.shi_moren ? 'success' : 'info'">{{
                  row.shi_moren ? '是' : '否'
                }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleEditFromDetail" v-if="currentParty">
            编辑
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { partyTypeOptions, type ContractParty } from '@/api/modules/contract'
import { formatDateTime } from '@/utils/format'

const router = useRouter()
const contractStore = useContractManagementStore()

// 响应式数据
const searchForm = reactive({
  search: '',
  zhuti_leixing: '',
})

const selectedParties = ref<ContractParty[]>([])
const detailDialogVisible = ref(false)

// 计算属性
const parties = computed(() => contractStore.parties)
const loading = computed(() => contractStore.partyLoading)
const partyTotal = computed(() => contractStore.partyTotal)
const partyPage = computed({
  get: () => contractStore.partyPage,
  set: (value) => contractStore.setPartyPage(value),
})
const partySize = computed({
  get: () => contractStore.partySize,
  set: (value) => contractStore.setPartySize(value),
})
const currentParty = computed(() => contractStore.currentParty)

const getPaymentTypeText = (type: string) => {
  const map: Record<string, string> = {
    yinhangzhuanzhang: '银行转账',
    weixin: '微信支付',
    zhifubao: '支付宝',
    xianjin: '现金',
    qita: '其他',
  }
  return map[type] || type
}

// 方法
const fetchParties = async () => {
  try {
    await contractStore.fetchParties({
      search: searchForm.search || undefined,
      zhuti_leixing: searchForm.zhuti_leixing || undefined,
    })
  } catch (error) {}
}

const handleSearch = () => {
  contractStore.setPartyPage(1)
  fetchParties()
}

const handleReset = () => {
  searchForm.search = ''
  searchForm.zhuti_leixing = ''
  contractStore.setPartyPage(1)
  fetchParties()
}

const handleCreate = () => {
  router.push('/contract-parties/create')
}

const handleView = async (party: ContractParty) => {
  try {
    await contractStore.fetchPartyDetail(party.id)
    detailDialogVisible.value = true
  } catch (error) {}
}

const handleEdit = (party: ContractParty) => {
  router.push(`/contract-parties/${party.id}/edit`)
}

const handleEditFromDetail = () => {
  if (currentParty.value) {
    detailDialogVisible.value = false
    router.push(`/contract-parties/${currentParty.value.id}/edit`)
  }
}

const handleDelete = async (party: ContractParty) => {
  try {
    await ElMessageBox.confirm(`确定要删除主体"${party.zhuti_mingcheng}"吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await contractStore.deleteParty(party.id)
    await fetchParties()
  } catch (error) {
    if (error !== 'cancel') {
    }
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedParties.value.length} 个主体吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const ids = selectedParties.value.map((item) => item.id)
    await contractStore.batchDeleteParties(ids)
    selectedParties.value = []
    await fetchParties()
  } catch (error) {
    if (error !== 'cancel') {
    }
  }
}

const handleSelectionChange = (selection: ContractParty[]) => {
  selectedParties.value = selection
}

const handlePageChange = (page: number) => {
  contractStore.setPartyPage(page)
  fetchParties()
}

const handleSizeChange = (size: number) => {
  contractStore.setPartySize(size)
  fetchParties()
}

// 辅助方法
const getPartyTypeLabel = (type: string) => {
  const option = partyTypeOptions.find((item) => item.value === type)
  return option?.label || type
}

const getPartyTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    enterprise: 'primary',
    individual_business: 'success',
    individual: 'warning',
  }
  return typeMap[type] || 'info'
}

// 生命周期
onMounted(() => {
  fetchParties()
})
</script>

<style scoped>
.contract-party-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-area {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.table-area {
  margin-bottom: 20px;
}

.pagination-area {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.batch-actions {
  margin-top: 20px;
}

.batch-buttons {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.party-detail {
  padding: 20px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
