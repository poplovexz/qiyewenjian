<template>
  <el-dialog
    v-model="dialogVisible"
    title="线索详情"
    width="1000px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="loading" class="xiansuo-detail">
      <template v-if="xiansuoDetail">
        <!-- 基本信息 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="getStatusTagType(xiansuoDetail.xiansuo_zhuangtai)">
                {{ getStatusText(xiansuoDetail.xiansuo_zhuangtai) }}
              </el-tag>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>线索编码：</label>
                <span>{{ xiansuoDetail.xiansuo_bianma }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>公司名称：</label>
                <span>{{ xiansuoDetail.gongsi_mingcheng }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>联系人：</label>
                <span>{{ xiansuoDetail.lianxi_ren }}</span>
              </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>联系电话：</label>
                <span>{{ xiansuoDetail.lianxi_dianhua || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>联系邮箱：</label>
                <span>{{ xiansuoDetail.lianxi_youxiang || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>行业类型：</label>
                <span>{{ xiansuoDetail.hangye_leixing || '-' }}</span>
              </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>公司规模：</label>
                <span>{{ xiansuoDetail.gongsi_guimo || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>服务类型：</label>
                <span>{{ xiansuoDetail.fuwu_leixing || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>预算范围：</label>
                <span>{{ xiansuoDetail.yusuan_fanwei || '-' }}</span>
              </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>质量评估：</label>
                <el-tag :type="getQualityTagType(xiansuoDetail.zhiliang_pinggu)" size="small">
                  {{ getQualityText(xiansuoDetail.zhiliang_pinggu) }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>质量分数：</label>
                <span>{{ xiansuoDetail.zhiliang_fenshu }}分</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>跟进次数：</label>
                <span>{{ xiansuoDetail.genjin_cishu }}次</span>
              </div>
            </el-col>
          </el-row>
          
          <div class="info-item full-width">
            <label>注册地址：</label>
            <span>{{ xiansuoDetail.zhuce_dizhi || '-' }}</span>
          </div>
          
          <div class="info-item full-width">
            <label>详细需求：</label>
            <span>{{ xiansuoDetail.xiangxi_xuqiu || '-' }}</span>
          </div>
        </el-card>

        <!-- 来源信息 -->
        <el-card class="info-card" v-if="xiansuoDetail.laiyuan">
          <template #header>
            <span>来源信息</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>来源名称：</label>
                <span>{{ xiansuoDetail.laiyuan.laiyuan_mingcheng }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>来源类型：</label>
                <span>{{ xiansuoDetail.laiyuan.laiyuan_leixing }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>获取成本：</label>
                <span>{{ xiansuoDetail.laiyuan.huoqu_chengben }}元</span>
              </div>
            </el-col>
          </el-row>
          
          <div class="info-item full-width" v-if="xiansuoDetail.laiyuan_xiangxi">
            <label>来源详细：</label>
            <span>{{ xiansuoDetail.laiyuan_xiangxi }}</span>
          </div>
        </el-card>

        <!-- 跟进记录 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>跟进记录</span>
              <el-button type="primary" size="small" @click="handleAddFollowup">
                <el-icon><Plus /></el-icon>
                添加跟进
              </el-button>
            </div>
          </template>
          
          <div v-if="xiansuoDetail.genjin_jilu_list.length === 0" class="empty-state">
            <el-empty description="暂无跟进记录" />
          </div>
          
          <el-timeline v-else>
            <el-timeline-item
              v-for="record in xiansuoDetail.genjin_jilu_list"
              :key="record.id"
              :timestamp="formatDateTime(record.genjin_shijian)"
              placement="top"
            >
              <el-card class="followup-card">
                <div class="followup-header">
                  <div class="followup-method">
                    <el-tag :type="getFollowupMethodType(record.genjin_fangshi)" size="small">
                      {{ getFollowupMethodText(record.genjin_fangshi) }}
                    </el-tag>
                  </div>
                  <div class="followup-person">
                    {{ record.genjin_ren_xingming || '未知' }}
                  </div>
                </div>
                
                <div class="followup-content">
                  <div class="content-item">
                    <strong>跟进内容：</strong>
                    <p>{{ record.genjin_neirong }}</p>
                  </div>
                  
                  <div class="content-item" v-if="record.kehu_fankui">
                    <strong>客户反馈：</strong>
                    <p>{{ record.kehu_fankui }}</p>
                  </div>
                  
                  <div class="content-item" v-if="record.kehu_taidu">
                    <strong>客户态度：</strong>
                    <el-tag :type="getAttitudeTagType(record.kehu_taidu)" size="small">
                      {{ getAttitudeText(record.kehu_taidu) }}
                    </el-tag>
                  </div>
                  
                  <div class="content-item" v-if="record.xiaci_genjin_shijian">
                    <strong>下次跟进：</strong>
                    <span>{{ formatDateTime(record.xiaci_genjin_shijian) }}</span>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <!-- 报价记录 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>报价记录</span>
              <el-button
                type="primary"
                size="small"
                @click="handleCreateBaojia"
                :disabled="!canCreateBaojia"
              >
                <el-icon><DocumentAdd /></el-icon>
                创建报价
              </el-button>
            </div>
          </template>

          <XiansuoBaojiaList
            v-if="xiansuoDetail"
            :xiansuo="xiansuoDetail"
            @edit="handleEditBaojia"
          />
        </el-card>
      </template>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleEdit">编辑线索</el-button>
      </div>
    </template>

    <!-- 跟进记录表单 -->
    <XiansuoFollowupForm
      v-model:visible="followupFormVisible"
      :xiansuo-id="xiansuoId"
      @success="handleFollowupSuccess"
    />

    <!-- 报价表单 -->
    <XiansuoBaojiaForm
      v-model:visible="baojiaFormVisible"
      :mode="baojiaFormMode"
      :xiansuo="xiansuoDetail"
      :baojia="currentBaojia"
      @success="handleBaojiaSuccess"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Plus, DocumentAdd } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import XiansuoFollowupForm from './XiansuoFollowupForm.vue'
import XiansuoBaojiaList from './XiansuoBaojiaList.vue'
import XiansuoBaojiaForm from './XiansuoBaojiaForm.vue'
import type { XiansuoDetail, XiansuoBaojia } from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  xiansuoId: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  edit: [xiansuoId: string]
}>()

// 使用store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const loading = ref(false)
const xiansuoDetail = ref<XiansuoDetail | null>(null)
const followupFormVisible = ref(false)
const baojiaFormVisible = ref(false)
const baojiaFormMode = ref<'create' | 'edit'>('create')
const currentBaojia = ref<XiansuoBaojia | null>(null)

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const canCreateBaojia = computed(() => {
  if (!xiansuoDetail.value) return false
  return !xiansuoStore.hasValidBaojia(xiansuoDetail.value.id)
})

// 监听props变化
watch(
  () => props.xiansuoId,
  async (newId) => {
    if (newId && props.visible) {
      await fetchXiansuoDetail()
    }
  },
  { immediate: true }
)

watch(
  () => props.visible,
  async (visible) => {
    if (visible && props.xiansuoId) {
      await fetchXiansuoDetail()
    }
  }
)

// 方法
const fetchXiansuoDetail = async () => {
  if (!props.xiansuoId) return
  
  loading.value = true
  try {
    xiansuoDetail.value = await xiansuoStore.getXiansuoDetail(props.xiansuoId)
    await xiansuoStore.fetchBaojiaByXiansuo(props.xiansuoId)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleEdit = () => {
  emit('edit', props.xiansuoId)
  handleClose()
}

const handleAddFollowup = () => {
  followupFormVisible.value = true
}

const handleFollowupSuccess = async () => {
  followupFormVisible.value = false
  await fetchXiansuoDetail()
}

const handleCreateBaojia = () => {
  baojiaFormMode.value = 'create'
  currentBaojia.value = null
  baojiaFormVisible.value = true
}

const handleEditBaojia = (baojia: XiansuoBaojia) => {
  baojiaFormMode.value = 'edit'
  currentBaojia.value = baojia
  baojiaFormVisible.value = true
}

const handleBaojiaSuccess = async () => {
  baojiaFormVisible.value = false
  // 刷新报价列表
  if (xiansuoDetail.value) {
    await xiansuoStore.fetchBaojiaByXiansuo(xiansuoDetail.value.id)
  }
}

// 工具方法
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

const getFollowupMethodType = (method: string) => {
  const types: Record<string, string> = {
    phone: 'primary',
    email: 'success',
    wechat: 'warning',
    visit: 'danger',
    other: 'info'
  }
  return types[method] || ''
}

const getFollowupMethodText = (method: string) => {
  const texts: Record<string, string> = {
    phone: '电话',
    email: '邮件',
    wechat: '微信',
    visit: '拜访',
    other: '其他'
  }
  return texts[method] || method
}

const getAttitudeTagType = (attitude: string) => {
  const types: Record<string, string> = {
    positive: 'success',
    neutral: 'warning',
    negative: 'danger'
  }
  return types[attitude] || ''
}

const getAttitudeText = (attitude: string) => {
  const texts: Record<string, string> = {
    positive: '积极',
    neutral: '中性',
    negative: '消极'
  }
  return texts[attitude] || attitude
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.xiansuo-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-weight: 500;
  color: #606266;
  min-width: 100px;
  margin-right: 10px;
}

.info-item span {
  color: #303133;
  word-break: break-all;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.followup-card {
  margin-bottom: 10px;
}

.followup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.followup-person {
  color: #909399;
  font-size: 14px;
}

.followup-content {
  line-height: 1.6;
}

.content-item {
  margin-bottom: 10px;
}

.content-item:last-child {
  margin-bottom: 0;
}

.content-item strong {
  color: #606266;
  margin-right: 8px;
}

.content-item p {
  margin: 5px 0 0 0;
  color: #303133;
}

.dialog-footer {
  text-align: right;
}
</style>
