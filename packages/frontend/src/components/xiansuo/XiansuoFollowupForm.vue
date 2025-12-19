<template>
  <el-dialog
    v-model="dialogVisible"
    title="添加跟进记录"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      v-loading="loading"
    >
      <el-form-item label="跟进方式" prop="genjin_fangshi">
        <el-select
          v-model="formData.genjin_fangshi"
          placeholder="请选择跟进方式"
          style="width: 100%"
        >
          <el-option label="电话" value="phone" />
          <el-option label="邮件" value="email" />
          <el-option label="微信" value="wechat" />
          <el-option label="拜访" value="visit" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>

      <el-form-item label="跟进时间" prop="genjin_shijian">
        <el-date-picker
          v-model="formData.genjin_shijian"
          type="datetime"
          placeholder="选择跟进时间"
          style="width: 100%"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>

      <el-form-item label="跟进内容" prop="genjin_neirong">
        <el-input
          v-model="formData.genjin_neirong"
          type="textarea"
          :rows="4"
          placeholder="请输入跟进内容"
        />
      </el-form-item>

      <el-form-item label="客户反馈" prop="kehu_fankui">
        <el-input
          v-model="formData.kehu_fankui"
          type="textarea"
          :rows="3"
          placeholder="请输入客户反馈"
        />
      </el-form-item>

      <el-form-item label="客户态度" prop="kehu_taidu">
        <el-select v-model="formData.kehu_taidu" placeholder="请选择客户态度" style="width: 100%">
          <el-option label="积极" value="positive" />
          <el-option label="中性" value="neutral" />
          <el-option label="消极" value="negative" />
        </el-select>
      </el-form-item>

      <el-form-item label="跟进结果" prop="genjin_jieguo">
        <el-select
          v-model="formData.genjin_jieguo"
          placeholder="请选择跟进结果"
          style="width: 100%"
        >
          <el-option label="继续跟进" value="continue" />
          <el-option label="客户有意向" value="interested" />
          <el-option label="需要报价" value="need_quote" />
          <el-option label="暂无需求" value="no_need" />
          <el-option label="已成交" value="deal" />
          <el-option label="无效线索" value="invalid" />
        </el-select>
      </el-form-item>

      <el-form-item label="下次跟进时间" prop="xiaci_genjin_shijian">
        <el-date-picker
          v-model="formData.xiaci_genjin_shijian"
          type="datetime"
          placeholder="选择下次跟进时间"
          style="width: 100%"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>

      <el-form-item label="下次跟进内容" prop="xiaci_genjin_neirong">
        <el-input
          v-model="formData.xiaci_genjin_neirong"
          type="textarea"
          :rows="2"
          placeholder="请输入下次跟进计划"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit"> 保存 </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import type { XiansuoGenjinCreate } from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  xiansuoId: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 使用store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = ref<XiansuoGenjinCreate>({
  xiansuo_id: '',
  genjin_fangshi: '',
  genjin_shijian: '',
  genjin_neirong: '',
  kehu_fankui: '',
  kehu_taidu: '',
  xiaci_genjin_shijian: '',
  xiaci_genjin_neirong: '',
  genjin_jieguo: '',
})

// 表单验证规则
const formRules: FormRules = {
  genjin_fangshi: [{ required: true, message: '请选择跟进方式', trigger: 'change' }],
  genjin_neirong: [{ required: true, message: '请输入跟进内容', trigger: 'blur' }],
}

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

// 监听props变化
watch(
  () => props.xiansuoId,
  (newId) => {
    if (newId) {
      formData.value.xiansuo_id = newId
    }
  },
  { immediate: true }
)

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      resetForm()
      // 设置默认跟进时间为当前时间
      formData.value.genjin_shijian = new Date().toISOString().slice(0, 19).replace('T', ' ')
    }
  }
)

// 方法
const resetForm = () => {
  formData.value = {
    xiansuo_id: props.xiansuoId,
    genjin_fangshi: '',
    genjin_shijian: '',
    genjin_neirong: '',
    kehu_fankui: '',
    kehu_taidu: '',
    xiaci_genjin_shijian: '',
    xiaci_genjin_neirong: '',
    genjin_jieguo: '',
  }
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    const success = await xiansuoStore.createGenjin(formData.value)
    if (success) {
      emit('success')
    }
  } catch (error) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
