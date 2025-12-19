<template>
  <div class="finance-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>财务设置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- 收付款渠道 -->
        <el-tab-pane label="收付款渠道" name="qudao">
          <div class="tab-header">
            <el-button type="primary" @click="handleAddQudao">
              <el-icon><Plus /></el-icon>
              新增渠道
            </el-button>
          </div>

          <el-table :data="qudaoList" v-loading="qudaoLoading" border stripe>
            <el-table-column prop="mingcheng" label="渠道名称" width="150" />
            <el-table-column prop="leixing" label="类型" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.leixing === 'shoukuan'" type="success">收款</el-tag>
                <el-tag v-else-if="row.leixing === 'fukuan'" type="warning">付款</el-tag>
                <el-tag v-else type="info">收付款</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="zhanghu_mingcheng" label="账户名称" min-width="200" />
            <el-table-column prop="zhanghu_haoma" label="账户号码" min-width="180" />
            <el-table-column prop="kaihuhang" label="开户行" min-width="200" show-overflow-tooltip />
            <el-table-column prop="zhuangtai" label="状态" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.zhuangtai === 'active'" type="success" size="small">启用</el-tag>
                <el-tag v-else type="info" size="small">禁用</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditQudao(row)">修改</el-button>
                <el-button link type="danger" size="small" @click="handleDeleteQudao(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 收入类别 -->
        <el-tab-pane label="收入类别" name="shouru">
          <div class="tab-header">
            <el-button type="primary" @click="handleAddShouruLeibie">
              <el-icon><Plus /></el-icon>
              新增类别
            </el-button>
          </div>

          <el-table :data="shouruLeibieList" v-loading="shouruLoading" border stripe>
            <el-table-column prop="mingcheng" label="类别名称" min-width="200" />
            <el-table-column prop="miaoshu" label="描述" min-width="400" show-overflow-tooltip />
            <el-table-column prop="zhuangtai" label="状态" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.zhuangtai === 'active'" type="success" size="small">启用</el-tag>
                <el-tag v-else type="info" size="small">禁用</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditShouruLeibie(row)">修改</el-button>
                <el-button link type="danger" size="small" @click="handleDeleteShouruLeibie(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 报销类别 -->
        <el-tab-pane label="报销类别" name="baoxiao">
          <div class="tab-header">
            <el-button type="primary" @click="handleAddBaoxiaoLeibie">
              <el-icon><Plus /></el-icon>
              新增类别
            </el-button>
          </div>

          <el-table :data="baoxiaoLeibieList" v-loading="baoxiaoLoading" border stripe>
            <el-table-column prop="mingcheng" label="类别名称" min-width="200" />
            <el-table-column prop="miaoshu" label="描述" min-width="400" show-overflow-tooltip />
            <el-table-column prop="zhuangtai" label="状态" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.zhuangtai === 'active'" type="success" size="small">启用</el-tag>
                <el-tag v-else type="info" size="small">禁用</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditBaoxiaoLeibie(row)">修改</el-button>
                <el-button link type="danger" size="small" @click="handleDeleteBaoxiaoLeibie(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 支出类别 -->
        <el-tab-pane label="支出类别" name="zhichu">
          <div class="tab-header">
            <el-button type="primary" @click="handleAddZhichuLeibie">
              <el-icon><Plus /></el-icon>
              新增类别
            </el-button>
          </div>

          <el-table
            :data="zhichuTreeData"
            v-loading="zhichuLoading"
            border
            stripe
            row-key="id"
            :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
            default-expand-all
          >
            <el-table-column prop="mingcheng" label="分类/类别名称" min-width="300">
              <template #default="{ row }">
                <span v-if="row.isCategory" style="font-weight: bold; color: #409EFF;">
                  <el-icon style="margin-right: 5px;"><Folder /></el-icon>
                  {{ row.mingcheng }}
                </span>
                <span v-else>{{ row.mingcheng }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="miaoshu" label="描述" min-width="300" show-overflow-tooltip />
            <el-table-column prop="zhuangtai" label="状态" width="80">
              <template #default="{ row }">
                <template v-if="!row.isCategory">
                  <el-tag v-if="row.zhuangtai === 'active'" type="success" size="small">启用</el-tag>
                  <el-tag v-else type="info" size="small">禁用</el-tag>
                </template>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <template v-if="!row.isCategory">
                  <el-button link type="primary" size="small" @click="handleEditZhichuLeibie(row)">修改</el-button>
                  <el-button link type="danger" size="small" @click="handleDeleteZhichuLeibie(row)">删除</el-button>
                </template>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 收付款渠道对话框 -->
    <QudaoDialog
      v-model="qudaoDialogVisible"
      :qudao="currentQudao"
      :mode="dialogMode"
      @success="loadQudaoList"
    />

    <!-- 收入类别对话框 -->
    <ShouruLeibieDialog
      v-model="shouruDialogVisible"
      :leibie="currentShouruLeibie"
      :mode="dialogMode"
      @success="loadShouruLeibieList"
    />

    <!-- 报销类别对话框 -->
    <BaoxiaoLeibieDialog
      v-model="baoxiaoDialogVisible"
      :leibie="currentBaoxiaoLeibie"
      :mode="dialogMode"
      @success="loadBaoxiaoLeibieList"
    />

    <!-- 支出类别对话框 -->
    <ZhichuLeibieDialog
      v-model="zhichuDialogVisible"
      :leibie="currentZhichuLeibie"
      :mode="dialogMode"
      @success="loadZhichuLeibieList"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder } from '@element-plus/icons-vue'
import {
  getQudaoList,
  deleteQudao,
  getShouruLeibieList,
  deleteShouruLeibie,
  getBaoxiaoLeibieList,
  deleteBaoxiaoLeibie,
  getZhichuLeibieList,
  deleteZhichuLeibie,
  type ShoufukuanQudao,
  type ShouruLeibie,
  type BaoxiaoLeibie,
  type ZhichuLeibie
} from '@/api/modules/finance-settings'
import QudaoDialog from './components/QudaoDialog.vue'
import ShouruLeibieDialog from './components/ShouruLeibieDialog.vue'
import BaoxiaoLeibieDialog from './components/BaoxiaoLeibieDialog.vue'
import ZhichuLeibieDialog from './components/ZhichuLeibieDialog.vue'

const activeTab = ref('qudao')
const dialogMode = ref<'create' | 'edit'>('create')

// 收付款渠道
const qudaoList = ref<ShoufukuanQudao[]>([])
const qudaoLoading = ref(false)
const qudaoDialogVisible = ref(false)
const currentQudao = ref<ShoufukuanQudao | null>(null)

// 收入类别
const shouruLeibieList = ref<ShouruLeibie[]>([])
const shouruLoading = ref(false)
const shouruDialogVisible = ref(false)
const currentShouruLeibie = ref<ShouruLeibie | null>(null)

// 报销类别
const baoxiaoLeibieList = ref<BaoxiaoLeibie[]>([])
const baoxiaoLoading = ref(false)
const baoxiaoDialogVisible = ref(false)
const currentBaoxiaoLeibie = ref<BaoxiaoLeibie | null>(null)

// 支出类别
const zhichuLeibieList = ref<ZhichuLeibie[]>([])
const zhichuLoading = ref(false)
const zhichuDialogVisible = ref(false)
const currentZhichuLeibie = ref<ZhichuLeibie | null>(null)

// 加载收付款渠道列表
const loadQudaoList = async () => {
  qudaoLoading.value = true
  try {
    const res = await getQudaoList({ page: 1, size: 100 })
    const response = res as { items?: ShoufukuanQudao[] }
    qudaoList.value = response.items || []
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载收付款渠道失败')
  } finally {
    qudaoLoading.value = false
  }
}

// 加载收入类别列表
const loadShouruLeibieList = async () => {
  shouruLoading.value = true
  try {
    const res = await getShouruLeibieList({ page: 1, size: 100 })
    const response = res as { items?: ShouruLeibie[] }
    shouruLeibieList.value = response.items || []
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载收入类别失败')
  } finally {
    shouruLoading.value = false
  }
}

// 加载报销类别列表
const loadBaoxiaoLeibieList = async () => {
  baoxiaoLoading.value = true
  try {
    const res = await getBaoxiaoLeibieList({ page: 1, size: 100 })
    const response = res as { items?: BaoxiaoLeibie[] }
    baoxiaoLeibieList.value = response.items || []
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载报销类别失败')
  } finally {
    baoxiaoLoading.value = false
  }
}

// 加载支出类别列表
const loadZhichuLeibieList = async () => {
  zhichuLoading.value = true
  try {
    const res = await getZhichuLeibieList({ page: 1, size: 200 })
    const response = res as { items?: ZhichuLeibie[] }
    zhichuLeibieList.value = response.items || []
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '加载支出类别失败')
  } finally {
    zhichuLoading.value = false
  }
}

// 将支出类别转换为树状结构
const zhichuTreeData = computed(() => {
  // 按分类分组
  const groupedData: Record<string, ZhichuLeibie[]> = {}

  zhichuLeibieList.value.forEach(item => {
    const fenlei = item.fenlei || '其他'
    if (!groupedData[fenlei]) {
      groupedData[fenlei] = []
    }
    groupedData[fenlei].push(item)
  })

  // 转换为树状结构
  interface TreeNode {
    id: string
    mingcheng: string
    isCategory: boolean
    children?: (ZhichuLeibie & { isCategory: boolean })[]
  }
  const treeData: TreeNode[] = []
  Object.keys(groupedData).sort().forEach(fenlei => {
    const categoryNode: TreeNode = {
      id: `category-${fenlei}`,
      mingcheng: fenlei,
      isCategory: true,
      children: groupedData[fenlei].map(item => ({
        ...item,
        isCategory: false
      }))
    }
    treeData.push(categoryNode)
  })

  return treeData
})

// 收付款渠道操作
const handleAddQudao = () => {
  dialogMode.value = 'create'
  currentQudao.value = null
  qudaoDialogVisible.value = true
}

const handleEditQudao = (row: ShoufukuanQudao) => {
  dialogMode.value = 'edit'
  currentQudao.value = { ...row }
  qudaoDialogVisible.value = true
}

const handleDeleteQudao = async (row: ShoufukuanQudao) => {
  try {
    await ElMessageBox.confirm('确定要删除该收付款渠道吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteQudao(row.id!)
    ElMessage.success('删除成功')
    loadQudaoList()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { message?: string }
      ElMessage.error(err.message || '删除失败')
    }
  }
}

// 其他类别操作类似...
const handleAddShouruLeibie = () => {
  dialogMode.value = 'create'
  currentShouruLeibie.value = null
  shouruDialogVisible.value = true
}

const handleEditShouruLeibie = (row: ShouruLeibie) => {
  dialogMode.value = 'edit'
  currentShouruLeibie.value = { ...row }
  shouruDialogVisible.value = true
}

const handleDeleteShouruLeibie = async (row: ShouruLeibie) => {
  try {
    await ElMessageBox.confirm('确定要删除该收入类别吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteShouruLeibie(row.id!)
    ElMessage.success('删除成功')
    loadShouruLeibieList()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { message?: string }
      ElMessage.error(err.message || '删除失败')
    }
  }
}

const handleAddBaoxiaoLeibie = () => {
  dialogMode.value = 'create'
  currentBaoxiaoLeibie.value = null
  baoxiaoDialogVisible.value = true
}

const handleEditBaoxiaoLeibie = (row: BaoxiaoLeibie) => {
  dialogMode.value = 'edit'
  currentBaoxiaoLeibie.value = { ...row }
  baoxiaoDialogVisible.value = true
}

const handleDeleteBaoxiaoLeibie = async (row: BaoxiaoLeibie) => {
  try {
    await ElMessageBox.confirm('确定要删除该报销类别吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteBaoxiaoLeibie(row.id!)
    ElMessage.success('删除成功')
    loadBaoxiaoLeibieList()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { message?: string }
      ElMessage.error(err.message || '删除失败')
    }
  }
}

const handleAddZhichuLeibie = () => {
  dialogMode.value = 'create'
  currentZhichuLeibie.value = null
  zhichuDialogVisible.value = true
}

const handleEditZhichuLeibie = (row: ZhichuLeibie) => {
  dialogMode.value = 'edit'
  currentZhichuLeibie.value = { ...row }
  zhichuDialogVisible.value = true
}

const handleDeleteZhichuLeibie = async (row: ZhichuLeibie) => {
  try {
    await ElMessageBox.confirm('确定要删除该支出类别吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteZhichuLeibie(row.id!)
    ElMessage.success('删除成功')
    loadZhichuLeibieList()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const err = error as { message?: string }
      ElMessage.error(err.message || '删除失败')
    }
  }
}

onMounted(() => {
  loadQudaoList()
  loadShouruLeibieList()
  loadBaoxiaoLeibieList()
  loadZhichuLeibieList()
})
</script>

<style scoped lang="scss">
.finance-settings {
  .card-header {
    font-weight: 600;
    font-size: 16px;
  }

  .tab-header {
    margin-bottom: 16px;
  }
}
</style>
