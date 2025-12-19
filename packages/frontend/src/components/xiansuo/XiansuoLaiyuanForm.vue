<template>
  <el-dialog
    v-model="dialogVisible"
    :title="mode === 'create' ? '新增线索来源' : '编辑线索来源'"
    width="600px"
    :before-close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
      <el-form-item label="来源编码" prop="laiyuan_bianma">
        <el-input
          v-model="formData.laiyuan_bianma"
          placeholder="请输入来源编码"
          :disabled="mode === 'edit'"
        />
      </el-form-item>

      <el-form-item label="来源名称" prop="laiyuan_mingcheng">
        <el-input v-model="formData.laiyuan_mingcheng" placeholder="请输入来源名称" />
      </el-form-item>

      <el-form-item label="来源类型" prop="laiyuan_leixing">
        <el-select
          v-model="formData.laiyuan_leixing"
          placeholder="请选择来源类型"
          style="width: 100%"
        >
          <el-option label="线上" value="online" />
          <el-option label="线下" value="offline" />
          <el-option label="推荐" value="referral" />
        </el-select>
      </el-form-item>

      <el-form-item label="获取成本" prop="huoqu_chengben">
        <el-input-number
          v-model="formData.huoqu_chengben"
          :min="0"
          :precision="2"
          placeholder="请输入获取成本"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="联系人" prop="lianxiren">
        <el-input v-model="formData.lianxiren" placeholder="请输入联系人" />
      </el-form-item>

      <el-form-item label="联系电话" prop="lianxi_dianhua">
        <el-input v-model="formData.lianxi_dianhua" placeholder="请输入联系电话" />
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
          placeholder="请输入来源描述"
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
import type { XiansuoLaiyuan, XiansuoLaiyuanCreate, XiansuoLaiyuanUpdate } from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit'
  laiyuan?: XiansuoLaiyuan | null
}

const props = withDefaults(defineProps<Props>(), {
  laiyuan: null,
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)

const formData = ref<XiansuoLaiyuanCreate>({
  laiyuan_bianma: '',
  laiyuan_mingcheng: '',
  laiyuan_leixing: 'online',
  huoqu_chengben: 0,
  lianxiren: '',
  lianxi_dianhua: '',
  zhuangtai: 'active',
  miaoshu: '',
  beizhu: '',
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

// 表单验证规则
const formRules: FormRules = {
  laiyuan_bianma: [
    { required: true, message: '请输入来源编码', trigger: 'blur' },
    { min: 2, max: 50, message: '编码长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  laiyuan_mingcheng: [
    { required: true, message: '请输入来源名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' },
  ],
  laiyuan_leixing: [{ required: true, message: '请选择来源类型', trigger: 'change' }],
  huoqu_chengben: [
    { required: true, message: '请输入获取成本', trigger: 'blur' },
    { type: 'number', min: 0, message: '获取成本不能小于0', trigger: 'blur' },
  ],
  lianxi_dianhua: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }],
}

// 方法
const resetForm = () => {
  formData.value = {
    laiyuan_bianma: '',
    laiyuan_mingcheng: '',
    laiyuan_leixing: 'online',
    huoqu_chengben: 0,
    lianxiren: '',
    lianxi_dianhua: '',
    zhuangtai: 'active',
    miaoshu: '',
    beizhu: '',
  }
}

const loadFormData = () => {
  if (props.mode === 'edit' && props.laiyuan) {
    formData.value = {
      laiyuan_bianma: props.laiyuan.laiyuan_bianma,
      laiyuan_mingcheng: props.laiyuan.laiyuan_mingcheng,
      laiyuan_leixing: props.laiyuan.laiyuan_leixing,
      huoqu_chengben: props.laiyuan.huoqu_chengben,
      lianxiren: props.laiyuan.lianxiren || '',
      lianxi_dianhua: props.laiyuan.lianxi_dianhua || '',
      zhuangtai: props.laiyuan.zhuangtai,
      miaoshu: props.laiyuan.miaoshu || '',
      beizhu: props.laiyuan.beizhu || '',
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
      await new Promise((resolve) => setTimeout(resolve, 1000)) // 模拟API调用
      ElMessage.success('创建成功')
    } else {
      // TODO: 调用更新API
      await new Promise((resolve) => setTimeout(resolve, 1000)) // 模拟API调用
      ElMessage.success('更新成功')
    }

    // 成功后关闭弹窗并触发成功事件
    dialogVisible.value = false
    emit('success')
  } catch (error) {
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
