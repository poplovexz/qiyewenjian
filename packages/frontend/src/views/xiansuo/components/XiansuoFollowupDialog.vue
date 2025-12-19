<template>
  <el-dialog
    :model-value="visible"
    title="跟进记录"
    width="800px"
    @close="handleClose"
    @update:model-value="(val) => emit('update:visible', val)"
  >
    <div v-if="xiansuo" class="xiansuo-info">
      <h4>线索信息</h4>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="线索编号">
          {{ xiansuo.xiansuo_bianma }}
        </el-descriptions-item>
        <el-descriptions-item label="公司名称">
          {{ xiansuo.gongsi_mingcheng }}
        </el-descriptions-item>
        <el-descriptions-item label="联系人">
          {{ xiansuo.lianxi_ren }}
        </el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="getStatusType(xiansuo.xiansuo_zhuangtai)" size="small">
            {{ getStatusText(xiansuo.xiansuo_zhuangtai) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <div class="followup-section">
      <div class="section-header">
        <h4>跟进记录</h4>
        <el-button type="primary" size="small" @click="showAddForm">
          <el-icon><Plus /></el-icon>
          添加跟进
        </el-button>
      </div>

      <!-- 跟进记录列表 -->
      <div v-if="genjinList.length > 0" class="followup-list">
        <div v-for="record in genjinList" :key="record.id" class="followup-item">
          <div class="followup-header">
            <div class="followup-meta">
              <span class="followup-time">{{ formatDateTime(record.genjin_shijian) }}</span>
              <span class="followup-user">{{ record.genjin_ren_xingming }}</span>
            </div>
            <el-tag :type="getFollowupType(record.genjin_fangshi)" size="small">
              {{ getFollowupMethodText(record.genjin_fangshi) }}
            </el-tag>
          </div>
          <div class="followup-content">
            {{ record.genjin_neirong }}
          </div>
          <div v-if="record.xiaci_genjin_shijian" class="next-followup">
            下次跟进时间：{{ formatDateTime(record.xiaci_genjin_shijian) }}
          </div>
        </div>
      </div>

      <!-- 暂无跟进记录 -->
      <div v-else class="no-followup">
        <el-empty description="暂无跟进记录" />
      </div>

      <!-- 添加跟进表单 -->
      <div v-if="showForm" class="add-form">
        <el-divider content-position="left">添加跟进记录</el-divider>
        <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
          <el-form-item label="跟进方式" prop="genjin_fangshi">
            <el-select v-model="formData.genjin_fangshi" placeholder="请选择跟进方式">
              <el-option label="电话" value="phone" />
              <el-option label="邮件" value="email" />
              <el-option label="微信" value="wechat" />
              <el-option label="面谈" value="meeting" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>

          <el-form-item label="跟进内容" prop="genjin_neirong">
            <el-input
              v-model="formData.genjin_neirong"
              type="textarea"
              :rows="4"
              placeholder="请输入跟进内容"
            />
          </el-form-item>

          <el-form-item label="下次跟进">
            <el-date-picker
              v-model="formData.xiaci_genjin_shijian"
              type="datetime"
              placeholder="选择下次跟进时间（可选）"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              保存跟进记录
            </el-button>
            <el-button @click="cancelAdd">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import type { Xiansuo, XiansuoGenjin, XiansuoGenjinCreate } from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  xiansuo: Xiansuo | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

// Store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const formRef = ref<FormInstance>()
const showForm = ref(false)
const submitting = ref(false)

const formData = reactive<XiansuoGenjinCreate>({
  xiansuo_id: '',
  genjin_fangshi: '',
  genjin_neirong: '',
  xiaci_genjin_shijian: undefined,
})

const formRules: FormRules = {
  genjin_fangshi: [{ required: true, message: '请选择跟进方式', trigger: 'change' }],
  genjin_neirong: [
    { required: true, message: '请输入跟进内容', trigger: 'blur' },
    { min: 5, message: '跟进内容至少5个字符', trigger: 'blur' },
  ],
}

// 计算属性
const genjinList = computed(() => xiansuoStore.genjin_list)

// 方法
const handleClose = () => {
  emit('update:visible', false)
  showForm.value = false
  resetForm()
}

const showAddForm = () => {
  showForm.value = true
  if (props.xiansuo) {
    formData.xiansuo_id = props.xiansuo.id
  }
}

const cancelAdd = () => {
  showForm.value = false
  resetForm()
}

const resetForm = () => {
  Object.assign(formData, {
    xiansuo_id: '',
    genjin_fangshi: '',
    genjin_neirong: '',
    xiaci_genjin_shijian: undefined,
  })
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    submitting.value = true
    const success = await xiansuoStore.createGenjin(formData)

    if (success) {
      ElMessage.success('跟进记录添加成功')
      showForm.value = false
      resetForm()
      // 重新加载跟进记录
      if (props.xiansuo) {
        await xiansuoStore.fetchGenjinByXiansuo(props.xiansuo.id)
      }
    }
  } catch (error) {
  } finally {
    submitting.value = false
  }
}

// 格式化方法
const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    new: '',
    following: 'warning',
    interested: 'success',
    won: 'success',
    lost: 'danger',
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    new: '新线索',
    following: '跟进中',
    interested: '有意向',
    won: '已成交',
    lost: '已失效',
  }
  return map[status] || status
}

const getFollowupType = (method: string) => {
  const map: Record<string, string> = {
    phone: 'primary',
    email: 'success',
    wechat: 'warning',
    meeting: 'danger',
    other: '',
  }
  return map[method] || ''
}

const getFollowupMethodText = (method: string) => {
  const map: Record<string, string> = {
    phone: '电话',
    email: '邮件',
    wechat: '微信',
    meeting: '面谈',
    other: '其他',
  }
  return map[method] || method
}

// 监听对话框显示状态
watch(
  () => props.visible,
  async (newVal) => {
    if (newVal && props.xiansuo) {
      // 加载跟进记录
      await xiansuoStore.fetchGenjinByXiansuo(props.xiansuo.id)
    }
  }
)
</script>

<style scoped>
.xiansuo-info {
  margin-bottom: 20px;
}

.xiansuo-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.followup-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
}

.followup-list {
  max-height: 400px;
  overflow-y: auto;
}

.followup-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 10px;
  background: #fafafa;
}

.followup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.followup-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.followup-time {
  font-size: 14px;
  color: #606266;
}

.followup-user {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

.followup-content {
  color: #303133;
  line-height: 1.6;
  margin-bottom: 8px;
}

.next-followup {
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

.no-followup {
  text-align: center;
  padding: 40px 0;
}

.add-form {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}
</style>
