<template>
  <el-dialog
    :model-value="modelValue"
    :title="mode === 'create' ? '新增报销类别' : '编辑报销类别'"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="类别名称" prop="mingcheng">
        <el-input v-model="form.mingcheng" placeholder="请输入类别名称" />
      </el-form-item>

      <el-form-item label="描述" prop="miaoshu">
        <el-input v-model="form.miaoshu" type="textarea" :rows="3" placeholder="请输入描述" />
      </el-form-item>

      <el-form-item label="排序" prop="paixu">
        <el-input-number v-model="form.paixu" :min="0" :max="9999" />
      </el-form-item>

      <el-form-item label="状态" prop="zhuangtai">
        <el-radio-group v-model="form.zhuangtai">
          <el-radio label="active">启用</el-radio>
          <el-radio label="inactive">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  createBaoxiaoLeibie,
  updateBaoxiaoLeibie,
  type BaoxiaoLeibie,
} from '@/api/modules/finance-settings'

const props = defineProps<{
  modelValue: boolean
  leibie: BaoxiaoLeibie | null
  mode: 'create' | 'edit'
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = ref<BaoxiaoLeibie>({
  mingcheng: '',
  bianma: '',
  miaoshu: '',
  paixu: 0,
  zhuangtai: 'active',
})

const rules: FormRules = {
  mingcheng: [{ required: true, message: '请输入类别名称', trigger: 'blur' }],
}

watch(
  () => props.leibie,
  (val) => {
    if (val) {
      form.value = { ...val }
    } else {
      form.value = {
        mingcheng: '',
        bianma: '',
        miaoshu: '',
        paixu: 0,
        zhuangtai: 'active',
      }
    }
  },
  { immediate: true }
)

const handleClose = () => {
  emit('update:modelValue', false)
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      if (props.mode === 'create') {
        await createBaoxiaoLeibie(form.value)
        ElMessage.success('创建成功')
      } else {
        await updateBaoxiaoLeibie(form.value.id!, form.value)
        ElMessage.success('更新成功')
      }
      emit('success')
      handleClose()
    } catch (error: unknown) {
      const err = error as { message?: string }
      ElMessage.error(err.message || '操作失败')
    } finally {
      loading.value = false
    }
  })
}
</script>
