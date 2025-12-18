<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑合规模板' : '新建合规模板'"
    width="800px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      v-loading="loading"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="事项名称" prop="shixiang_mingcheng">
            <el-input
              v-model="formData.shixiang_mingcheng"
              placeholder="请输入事项名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="事项编码" prop="shixiang_bianma">
            <el-input
              v-model="formData.shixiang_bianma"
              placeholder="请输入事项编码"
              maxlength="50"
              :disabled="isEdit"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="事项类型" prop="shixiang_leixing">
            <el-select
              v-model="formData.shixiang_leixing"
              placeholder="请选择事项类型"
              style="width: 100%"
            >
              <el-option
                v-for="(label, value) in complianceStore.templateTypeMap"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="申报周期" prop="shenbao_zhouqi">
            <el-select
              v-model="formData.shenbao_zhouqi"
              placeholder="请选择申报周期"
              style="width: 100%"
            >
              <el-option
                v-for="(label, value) in complianceStore.reportCycleMap"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="风险等级" prop="fengxian_dengji">
            <el-select
              v-model="formData.fengxian_dengji"
              placeholder="请选择风险等级"
              style="width: 100%"
            >
              <el-option
                v-for="(label, value) in complianceStore.riskLevelMap"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="模板状态" prop="moban_zhuangtai">
            <el-select
              v-model="formData.moban_zhuangtai"
              placeholder="请选择模板状态"
              style="width: 100%"
            >
              <el-option
                v-for="(label, value) in complianceStore.templateStatusMap"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="提醒天数" prop="tiqian_tixing_tianshu">
        <el-input
          v-model="formData.tiqian_tixing_tianshu"
          placeholder="请输入提醒天数，多个用逗号分隔，如：7,3,1"
          maxlength="50"
        />
        <div class="form-tip">多个提醒天数用逗号分隔，如：7,3,1 表示提前7天、3天、1天提醒</div>
      </el-form-item>

      <el-form-item label="截止时间规则" prop="jiezhi_shijian_guize">
        <el-input
          v-model="formData.jiezhi_shijian_guize"
          type="textarea"
          :rows="3"
          placeholder="请输入JSON格式的截止时间规则"
        />
        <div class="form-tip">
          JSON格式，如：{"type": "monthly", "day": 15, "description": "每月15日前申报"}
        </div>
      </el-form-item>

      <el-form-item label="适用企业类型">
        <el-input
          v-model="formData.shiyong_qiye_leixing"
          type="textarea"
          :rows="2"
          placeholder="请输入JSON格式的适用企业类型"
        />
        <div class="form-tip">JSON数组格式，如：["一般纳税人", "小规模纳税人"]</div>
      </el-form-item>

      <el-form-item label="事项描述">
        <el-input
          v-model="formData.shixiang_miaoshu"
          type="textarea"
          :rows="3"
          placeholder="请输入事项描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="所需材料">
        <el-input
          v-model="formData.suoxu_cailiao"
          type="textarea"
          :rows="3"
          placeholder="请输入JSON格式的所需材料清单"
        />
        <div class="form-tip">JSON数组格式，如：["营业执照", "财务报表", "银行回单"]</div>
      </el-form-item>

      <el-form-item label="法规依据">
        <el-input
          v-model="formData.fagui_yiju"
          placeholder="请输入法规依据"
          maxlength="200"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useComplianceStore } from '@/stores/modules/complianceManagement'

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
  success: []
}>()

// Store
const complianceStore = useComplianceStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = reactive({
  shixiang_mingcheng: '',
  shixiang_bianma: '',
  shixiang_leixing: '',
  shenbao_zhouqi: '',
  fengxian_dengji: 'medium',
  moban_zhuangtai: 'active',
  tiqian_tixing_tianshu: '7,3,1',
  jiezhi_shijian_guize: '',
  shiyong_qiye_leixing: '',
  shixiang_miaoshu: '',
  suoxu_cailiao: '',
  fagui_yiju: ''
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const isEdit = computed(() => Boolean(props.templateId))

// 表单验证规则
const formRules: FormRules = {
  shixiang_mingcheng: [
    { required: true, message: '请输入事项名称', trigger: 'blur' }
  ],
  shixiang_bianma: [
    { required: true, message: '请输入事项编码', trigger: 'blur' },
    { pattern: /^[A-Z_]+$/, message: '事项编码只能包含大写字母和下划线', trigger: 'blur' }
  ],
  shixiang_leixing: [
    { required: true, message: '请选择事项类型', trigger: 'change' }
  ],
  shenbao_zhouqi: [
    { required: true, message: '请选择申报周期', trigger: 'change' }
  ],
  fengxian_dengji: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ],
  jiezhi_shijian_guize: [
    { required: true, message: '请输入截止时间规则', trigger: 'blur' },
    { validator: validateJSON, trigger: 'blur' }
  ]
}

// 验证JSON格式
function validateJSON(rule: any, value: string, callback: any) {
  if (!value) {
    callback()
    return
  }
  
  try {
    JSON.parse(value)
    callback()
  } catch (error) {
    callback(new Error('请输入有效的JSON格式'))
  }
}

// 方法
const loadTemplateData = async () => {
  if (!props.templateId) return
  
  try {
    loading.value = true
    const template = await complianceStore.fetchTemplateDetail(props.templateId)
    
    Object.assign(formData, {
      shixiang_mingcheng: template.shixiang_mingcheng,
      shixiang_bianma: template.shixiang_bianma,
      shixiang_leixing: template.shixiang_leixing,
      shenbao_zhouqi: template.shenbao_zhouqi,
      fengxian_dengji: template.fengxian_dengji,
      moban_zhuangtai: template.moban_zhuangtai,
      tiqian_tixing_tianshu: template.tiqian_tixing_tianshu,
      jiezhi_shijian_guize: template.jiezhi_shijian_guize,
      shiyong_qiye_leixing: template.shiyong_qiye_leixing || '',
      shixiang_miaoshu: template.shixiang_miaoshu || '',
      suoxu_cailiao: template.suoxu_cailiao || '',
      fagui_yiju: template.fagui_yiju || ''
    })
  } catch (error) {
    console.error('加载模板数据失败:', error)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    shixiang_mingcheng: '',
    shixiang_bianma: '',
    shixiang_leixing: '',
    shenbao_zhouqi: '',
    fengxian_dengji: 'medium',
    moban_zhuangtai: 'active',
    tiqian_tixing_tianshu: '7,3,1',
    jiezhi_shijian_guize: '',
    shiyong_qiye_leixing: '',
    shixiang_miaoshu: '',
    suoxu_cailiao: '',
    fagui_yiju: ''
  })
  formRef.value?.clearValidate()
}

const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const submitData = { ...formData }
    
    if (isEdit.value) {
      await complianceStore.updateTemplate(props.templateId, submitData)
    } else {
      await complianceStore.createTemplate(submitData)
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听器
watch(() => props.visible, (visible) => {
  if (visible) {
    if (isEdit.value) {
      loadTemplateData()
    } else {
      resetForm()
    }
  }
})
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.dialog-footer {
  text-align: right;
}
</style>
