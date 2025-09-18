<template>
  <el-dialog
    v-model="dialogVisible"
    :title="mode === 'create' ? '新增线索状态' : '编辑线索状态'"
    width="600px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <el-form-item label="状态编码" prop="zhuangtai_bianma">
        <el-input
          v-model="formData.zhuangtai_bianma"
          placeholder="请输入状态编码"
          :disabled="mode === 'edit'"
        />
      </el-form-item>

      <el-form-item label="状态名称" prop="zhuangtai_mingcheng">
        <el-input
          v-model="formData.zhuangtai_mingcheng"
          placeholder="请输入状态名称"
        />
      </el-form-item>

      <el-form-item label="状态类型" prop="zhuangtai_leixing">
        <el-select
          v-model="formData.zhuangtai_leixing"
          placeholder="请选择状态类型"
          style="width: 100%"
        >
          <el-option label="初始状态" value="initial" />
          <el-option label="处理中" value="processing" />
          <el-option label="成功状态" value="success" />
          <el-option label="失败状态" value="failed" />
        </el-select>
      </el-form-item>

      <el-form-item label="颜色编码" prop="yanse_bianma">
        <el-color-picker
          v-model="formData.yanse_bianma"
          show-alpha
          :predefine="predefineColors"
        />
        <span style="margin-left: 10px; color: #909399;">选择状态显示颜色</span>
      </el-form-item>

      <el-form-item label="排序" prop="paixu">
        <el-input-number
          v-model="formData.paixu"
          :min="0"
          :max="999"
          placeholder="请输入排序值"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="成功状态" prop="shi_chenggong_zhuangtai">
        <el-radio-group v-model="formData.shi_chenggong_zhuangtai">
          <el-radio value="Y">是</el-radio>
          <el-radio value="N">否</el-radio>
        </el-radio-group>
        <div style="color: #909399; font-size: 12px; margin-top: 5px;">
          标记为成功状态的线索将计入转化统计
        </div>
      </el-form-item>

      <el-form-item label="终止状态" prop="shi_zhongzhong_zhuangtai">
        <el-radio-group v-model="formData.shi_zhongzhong_zhuangtai">
          <el-radio value="Y">是</el-radio>
          <el-radio value="N">否</el-radio>
        </el-radio-group>
        <div style="color: #909399; font-size: 12px; margin-top: 5px;">
          标记为终止状态的线索将不能再进行状态流转
        </div>
      </el-form-item>

      <el-form-item label="下一个状态" prop="xiayige_zhuangtai">
        <el-input
          v-model="formData.xiayige_zhuangtai"
          placeholder="请输入下一个状态编码，多个用逗号分隔"
        />
        <div style="color: #909399; font-size: 12px; margin-top: 5px;">
          配置可以流转到的下一个状态，如：processing,success,failed
        </div>
      </el-form-item>

      <el-form-item label="状态" prop="zhuangtai">
        <el-radio-group v-model="formData.zhuangtai">
          <el-radio value="active">启用</el-radio>
          <el-radio value="inactive">禁用</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="描述" prop="miaoshu">
        <el-input
          v-model="formData.miaoshu"
          type="textarea"
          :rows="3"
          placeholder="请输入状态描述"
        />
      </el-form-item>

      <el-form-item label="备注" prop="beizhu">
        <el-input
          v-model="formData.beizhu"
          type="textarea"
          :rows="2"
          placeholder="请输入备注信息"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ mode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import type { XiansuoZhuangtai, XiansuoZhuangtaiCreate, XiansuoZhuangtaiUpdate } from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit'
  zhuangtai?: XiansuoZhuangtai | null
}

const props = withDefaults(defineProps<Props>(), {
  zhuangtai: null
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)

const formData = ref<XiansuoZhuangtaiCreate>({
  zhuangtai_bianma: '',
  zhuangtai_mingcheng: '',
  zhuangtai_leixing: 'initial',
  yanse_bianma: '#409eff',
  paixu: 0,
  shi_chenggong_zhuangtai: 'N',
  shi_zhongzhong_zhuangtai: 'N',
  xiayige_zhuangtai: '',
  zhuangtai: 'active',
  miaoshu: '',
  beizhu: ''
})

// 预定义颜色
const predefineColors = [
  '#ff4500',
  '#ff8c00',
  '#ffd700',
  '#90ee90',
  '#00ced1',
  '#1e90ff',
  '#c71585',
  '#409eff',
  '#67c23a',
  '#e6a23c',
  '#f56c6c',
  '#909399'
]

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 表单验证规则
const formRules: FormRules = {
  zhuangtai_bianma: [
    { required: true, message: '请输入状态编码', trigger: 'blur' },
    { min: 2, max: 50, message: '编码长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  zhuangtai_mingcheng: [
    { required: true, message: '请输入状态名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  zhuangtai_leixing: [
    { required: true, message: '请选择状态类型', trigger: 'change' }
  ],
  paixu: [
    { required: true, message: '请输入排序值', trigger: 'blur' },
    { type: 'number', min: 0, max: 999, message: '排序值在 0 到 999 之间', trigger: 'blur' }
  ]
}

// 方法
const resetForm = () => {
  formData.value = {
    zhuangtai_bianma: '',
    zhuangtai_mingcheng: '',
    zhuangtai_leixing: 'initial',
    yanse_bianma: '#409eff',
    paixu: 0,
    shi_chenggong_zhuangtai: 'N',
    shi_zhongzhong_zhuangtai: 'N',
    xiayige_zhuangtai: '',
    zhuangtai: 'active',
    miaoshu: '',
    beizhu: ''
  }
}

const loadFormData = () => {
  if (props.mode === 'edit' && props.zhuangtai) {
    formData.value = {
      zhuangtai_bianma: props.zhuangtai.zhuangtai_bianma,
      zhuangtai_mingcheng: props.zhuangtai.zhuangtai_mingcheng,
      zhuangtai_leixing: props.zhuangtai.zhuangtai_leixing,
      yanse_bianma: props.zhuangtai.yanse_bianma || '#409eff',
      paixu: props.zhuangtai.paixu || 0,
      shi_chenggong_zhuangtai: props.zhuangtai.shi_chenggong_zhuangtai || 'N',
      shi_zhongzhong_zhuangtai: props.zhuangtai.shi_zhongzhong_zhuangtai || 'N',
      xiayige_zhuangtai: props.zhuangtai.xiayige_zhuangtai || '',
      zhuangtai: props.zhuangtai.zhuangtai,
      miaoshu: props.zhuangtai.miaoshu || '',
      beizhu: props.zhuangtai.beizhu || ''
    }
  } else {
    resetForm()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    if (props.mode === 'create') {
      // TODO: 调用创建API
      await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
      ElMessage.success('创建成功')
    } else {
      // TODO: 调用更新API
      await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
      ElMessage.success('更新成功')
    }

    // 成功后关闭弹窗并触发成功事件
    dialogVisible.value = false
    emit('success')
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  formRef.value?.resetFields()
  emit('update:visible', false)
}

// 监听器
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      loadFormData()
    }
  }
)
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
