<template>
  <el-dialog
    :model-value="modelValue"
    :title="mode === 'create' ? '新增收付款渠道' : '编辑收付款渠道'"
    width="600px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="渠道名称" prop="mingcheng">
        <el-input v-model="form.mingcheng" placeholder="请输入渠道名称" />
      </el-form-item>

      <el-form-item label="渠道类型" prop="leixing">
        <el-select v-model="form.leixing" placeholder="请选择渠道类型" style="width: 100%">
          <el-option label="收款" value="shoukuan" />
          <el-option label="付款" value="fukuan" />
          <el-option label="收付款" value="shoufukuan" />
        </el-select>
      </el-form-item>

      <el-form-item label="账户名称" prop="zhanghu_mingcheng">
        <el-input v-model="form.zhanghu_mingcheng" placeholder="请输入账户名称" />
      </el-form-item>

      <el-form-item label="账户号码" prop="zhanghu_haoma">
        <el-input v-model="form.zhanghu_haoma" placeholder="请输入账户号码" />
      </el-form-item>

      <el-form-item label="开户行" prop="kaihuhang">
        <el-input v-model="form.kaihuhang" placeholder="请输入开户行" />
      </el-form-item>

      <el-form-item label="联行号" prop="lianhanghao">
        <el-input v-model="form.lianhanghao" placeholder="请输入联行号" />
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
import { createQudao, updateQudao, type ShoufukuanQudao } from '@/api/modules/finance-settings'

const props = defineProps<{
  modelValue: boolean
  qudao: ShoufukuanQudao | null
  mode: 'create' | 'edit'
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = ref<ShoufukuanQudao>({
  mingcheng: '',
  leixing: 'shoufukuan',
  zhanghu_mingcheng: '',
  zhanghu_haoma: '',
  kaihuhang: '',
  lianhanghao: '',
  miaoshu: '',
  paixu: 0,
  zhuangtai: 'active',
})

const rules: FormRules = {
  mingcheng: [{ required: true, message: '请输入渠道名称', trigger: 'blur' }],
  leixing: [{ required: true, message: '请选择渠道类型', trigger: 'change' }],
}

watch(
  () => props.qudao,
  (val) => {
    if (val) {
      form.value = { ...val }
    } else {
      form.value = {
        mingcheng: '',
        leixing: 'shoufukuan',
        zhanghu_mingcheng: '',
        zhanghu_haoma: '',
        kaihuhang: '',
        lianhanghao: '',
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
        await createQudao(form.value)
        ElMessage.success('创建成功')
      } else {
        await updateQudao(form.value.id!, form.value)
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
