<template>
  <el-dialog
    v-model="dialogVisible"
    title="合规模板详情"
    width="800px"
    :before-close="handleClose"
  >
    <div v-loading="loading" class="template-detail">
      <template v-if="templateData">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h3 class="section-title">基本信息</h3>
          <el-row :gutter="20" class="detail-row">
            <el-col :span="12">
              <div class="detail-item">
                <label>事项名称：</label>
                <span>{{ templateData.shixiang_mingcheng }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>事项编码：</label>
                <span>{{ templateData.shixiang_bianma }}</span>
              </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" class="detail-row">
            <el-col :span="12">
              <div class="detail-item">
                <label>事项类型：</label>
                <el-tag :type="getTypeTagType(templateData.shixiang_leixing)">
                  {{ complianceStore.templateTypeMap[templateData.shixiang_leixing] }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>申报周期：</label>
                <span>{{ complianceStore.reportCycleMap[templateData.shenbao_zhouqi] }}</span>
              </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" class="detail-row">
            <el-col :span="12">
              <div class="detail-item">
                <label>风险等级：</label>
                <el-tag :type="getRiskTagType(templateData.fengxian_dengji)" size="small">
                  {{ complianceStore.riskLevelMap[templateData.fengxian_dengji] }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>模板状态：</label>
                <el-tag :type="getStatusTagType(templateData.moban_zhuangtai)" size="small">
                  {{ complianceStore.templateStatusMap[templateData.moban_zhuangtai] }}
                </el-tag>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 时间配置 -->
        <div class="detail-section">
          <h3 class="section-title">时间配置</h3>
          <el-row :gutter="20" class="detail-row">
            <el-col :span="12">
              <div class="detail-item">
                <label>提醒天数：</label>
                <div class="reminder-tags">
                  <el-tag
                    v-for="day in templateData.tiqian_tixing_tianshu.split(',')"
                    :key="day"
                    size="small"
                    class="reminder-tag"
                  >
                    {{ day }}天
                  </el-tag>
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>截止时间规则：</label>
                <div class="json-content">
                  <pre>{{ formatJSON(templateData.jiezhi_shijian_guize) }}</pre>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 适用范围 -->
        <div class="detail-section" v-if="templateData.shiyong_qiye_leixing">
          <h3 class="section-title">适用范围</h3>
          <div class="detail-item">
            <label>适用企业类型：</label>
            <div class="enterprise-types">
              <el-tag
                v-for="type in parseJSON(templateData.shiyong_qiye_leixing)"
                :key="type"
                size="small"
                type="info"
                class="enterprise-tag"
              >
                {{ type }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 详细说明 -->
        <div class="detail-section" v-if="templateData.shixiang_miaoshu">
          <h3 class="section-title">详细说明</h3>
          <div class="detail-item">
            <label>事项描述：</label>
            <div class="description-content">
              {{ templateData.shixiang_miaoshu }}
            </div>
          </div>
        </div>

        <!-- 所需材料 -->
        <div class="detail-section" v-if="templateData.suoxu_cailiao">
          <h3 class="section-title">所需材料</h3>
          <div class="detail-item">
            <div class="materials-list">
              <div
                v-for="(material, index) in parseJSON(templateData.suoxu_cailiao)"
                :key="index"
                class="material-item"
              >
                <el-icon><Document /></el-icon>
                <span>{{ material }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 法规依据 -->
        <div class="detail-section" v-if="templateData.fagui_yiju">
          <h3 class="section-title">法规依据</h3>
          <div class="detail-item">
            <div class="regulation-content">
              {{ templateData.fagui_yiju }}
            </div>
          </div>
        </div>

        <!-- 创建信息 -->
        <div class="detail-section">
          <h3 class="section-title">创建信息</h3>
          <el-row :gutter="20" class="detail-row">
            <el-col :span="12">
              <div class="detail-item">
                <label>创建时间：</label>
                <span>{{ formatDateTime(templateData.created_at) }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>创建人：</label>
                <span>{{ templateData.created_by }}</span>
              </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" class="detail-row" v-if="templateData.updated_at">
            <el-col :span="12">
              <div class="detail-item">
                <label>更新时间：</label>
                <span>{{ formatDateTime(templateData.updated_at) }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>更新人：</label>
                <span>{{ templateData.updated_by || '-' }}</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </template>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Document } from '@element-plus/icons-vue'
import { useComplianceStore } from '@/stores/modules/complianceManagement'
import { format } from 'date-fns'

// Props
interface Props {
  visible: boolean
  templateId?: string
}

const props = withDefaults(defineProps<Props>(), {
  templateId: ''
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

// Store
const complianceStore = useComplianceStore()

// 响应式数据
const loading = ref(false)
const templateData = ref(null)

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 方法
const loadTemplateData = async () => {
  if (!props.templateId) return
  
  try {
    loading.value = true
    templateData.value = await complianceStore.fetchTemplateDetail(props.templateId)
  } catch (error) {
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  templateData.value = null
}

const getTypeTagType = (type: string) => {
  const typeMap = {
    shuiwu_shenbao: 'danger',
    nianbao_shenbao: 'warning',
    zhizhao_nianjian: 'primary',
    qita_heguishixiang: 'info'
  }
  return typeMap[type] || 'info'
}

const getRiskTagType = (risk: string) => {
  const riskMap = {
    low: 'success',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return riskMap[risk] || 'info'
}

const getStatusTagType = (status: string) => {
  const statusMap = {
    active: 'success',
    inactive: 'info',
    draft: 'warning'
  }
  return statusMap[status] || 'info'
}

const formatDateTime = (dateString: string) => {
  return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss')
}

const formatJSON = (jsonString: string) => {
  try {
    return JSON.stringify(JSON.parse(jsonString), null, 2)
  } catch {
    return jsonString
  }
}

const parseJSON = (jsonString: string) => {
  try {
    return JSON.parse(jsonString)
  } catch {
    return []
  }
}

// 监听器
watch(() => props.visible, (visible) => {
  if (visible && props.templateId) {
    loadTemplateData()
  }
})
</script>

<style scoped>
.template-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 12px;
}

.detail-row {
  margin-bottom: 12px;
}

.detail-item {
  margin-bottom: 12px;
}

.detail-item label {
  display: inline-block;
  min-width: 100px;
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
}

.reminder-tags {
  display: inline-flex;
  gap: 4px;
  flex-wrap: wrap;
}

.reminder-tag {
  margin-right: 4px;
}

.json-content {
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px;
  margin-top: 4px;
}

.json-content pre {
  margin: 0;
  font-size: 12px;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-all;
}

.enterprise-types {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.enterprise-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.description-content {
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 4px;
  line-height: 1.6;
  color: #606266;
  margin-top: 4px;
}

.materials-list {
  margin-top: 8px;
}

.material-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.material-item:last-child {
  border-bottom: none;
}

.material-item .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.regulation-content {
  background-color: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 4px;
  padding: 12px;
  margin-top: 4px;
  color: #d46b08;
  line-height: 1.6;
}

.dialog-footer {
  text-align: right;
}
</style>
