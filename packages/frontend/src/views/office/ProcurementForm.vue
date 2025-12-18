<template>
  <div class="procurement-form">
    <el-page-header @back="handleBack" :content="pageTitle" />

    <el-card class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        v-loading="loading"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采购类型" prop="caigou_leixing">
              <el-select
                v-model="form.caigou_leixing"
                placeholder="请选择采购类型"
                style="width: 100%"
                :loading="zhichuLeibieLoading"
              >
                <el-option
                  v-for="item in zhichuLeibieOptions"
                  :key="item.id"
                  :label="item.mingcheng"
                  :value="item.mingcheng"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物品名称" prop="caigou_mingcheng">
              <el-input v-model="form.caigou_mingcheng" placeholder="请输入采购物品名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="采购数量" prop="caigou_shuliang">
              <el-input-number
                v-model="form.caigou_shuliang"
                :min="1"
                :controls="false"
                placeholder="请输入数量"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单位" prop="danwei">
              <el-input v-model="form.danwei" placeholder="如：个、台、套" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预估金额" prop="yugu_jine">
              <el-input-number
                v-model="form.yugu_jine"
                :min="0.01"
                :precision="2"
                :controls="false"
                placeholder="请输入预估金额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="要求到货时间" prop="yaoqiu_shijian">
              <el-date-picker
                v-model="form.yaoqiu_shijian"
                type="date"
                placeholder="选择要求到货时间"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商信息" prop="gongyingshang_xinxi">
              <el-input v-model="form.gongyingshang_xinxi" placeholder="请输入供应商信息（选填）" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="采购原因" prop="caigou_yuanyin">
          <el-input
            v-model="form.caigou_yuanyin"
            type="textarea"
            :rows="4"
            placeholder="请详细说明采购原因和用途"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 附件上传 -->
        <el-divider content-position="left">附件上传</el-divider>

        <el-form-item label="相关文件">
          <el-upload
            ref="uploadRef"
            :action="uploadAction"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :file-list="fileList"
            :limit="5"
            accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls,.doc,.docx"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、图片、Excel、Word 格式，单个文件不超过 10MB，最多上传5个文件（如报价单、需求说明等）
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- 备注 -->
        <el-divider content-position="left">其他信息</el-divider>

        <el-form-item label="备注">
          <el-input
            v-model="form.beizhu"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button @click="handleBack">取消</el-button>
          <el-button @click="handleSaveDraft" :loading="saving">保存草稿</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadProps, UploadUserFile } from 'element-plus'
import {
  getProcurementDetail,
  createProcurement,
  updateProcurement,
  type ProcurementApplication
} from '@/api/office'
import { getZhichuLeibieList, type ZhichuLeibie } from '@/api/modules/finance-settings'
import { useAuthStore } from '@/stores/modules/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const uploadRef = ref()
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const fileList = ref<UploadUserFile[]>([])

// 支出类别选项
const zhichuLeibieOptions = ref<ZhichuLeibie[]>([])
const zhichuLeibieLoading = ref(false)

const procurementId = computed(() => route.params.id as string)
const isEdit = computed(() => Boolean(procurementId.value))
const pageTitle = computed(() => isEdit.value ? '编辑采购申请' : '新建采购申请')

const form = reactive<Partial<ProcurementApplication>>({
  caigou_leixing: '',
  caigou_mingcheng: '',
  caigou_shuliang: 1,
  danwei: '',
  yugu_jine: 0,
  caigou_yuanyin: '',
  yaoqiu_shijian: '',
  gongyingshang_xinxi: '',
  fujian_lujing: '',
  beizhu: ''
})

const rules: FormRules = {
  caigou_leixing: [
    { required: true, message: '请选择采购类型', trigger: 'change' }
  ],
  caigou_mingcheng: [
    { required: true, message: '请输入物品名称', trigger: 'blur' }
  ],
  caigou_shuliang: [
    { required: true, message: '请输入采购数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '采购数量至少为1', trigger: 'blur' }
  ],
  danwei: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ],
  yugu_jine: [
    { required: true, message: '请输入预估金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '预估金额必须大于0', trigger: 'blur' }
  ],
  caigou_yuanyin: [
    { required: true, message: '请输入采购原因', trigger: 'blur' },
    { min: 10, message: '采购原因至少10个字符', trigger: 'blur' }
  ]
}

// 上传配置
const uploadAction = computed(() => `${import.meta.env.VITE_API_BASE_URL}/upload/file`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.accessToken}`
}))

// 加载支出类别列表
const loadZhichuLeibieOptions = async () => {
  zhichuLeibieLoading.value = true
  try {
    const res = await getZhichuLeibieList({ page: 1, size: 200 })
    const allItems = (res as any).items || []
    // 只显示启用状态的类别
    zhichuLeibieOptions.value = allItems.filter((item: ZhichuLeibie) => item.zhuangtai === 'active')
  } catch (error: any) {
    ElMessage.error(error.message || '加载采购类型失败')
    zhichuLeibieOptions.value = []
  } finally {
    zhichuLeibieLoading.value = false
  }
}

// 获取详情（编辑模式）
const fetchDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getProcurementDetail(procurementId.value)
    Object.assign(form, data)
    
    // 处理附件列表
    if (data.fujian_lujing) {
      const files = data.fujian_lujing.split(',').filter(Boolean)
      fileList.value = files.map((url, index) => ({
        name: `附件${index + 1}`,
        url: url
      }))
    }
  } catch (error) {
    ElMessage.error('获取采购申请详情失败')
    router.push('/office/procurement')
  } finally {
    loading.value = false
  }
}

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const allowedTypes = [
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
  const isAllowedType = allowedTypes.includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isAllowedType) {
    ElMessage.error('只能上传 PDF、图片、Excel、Word 格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

// 上传成功
const handleUploadSuccess: UploadProps['onSuccess'] = (response, file, fileList) => {
  if (response.url) {
    const urls = fileList.map(f => f.response?.url || f.url).filter(Boolean)
    form.fujian_lujing = urls.join(',')
    ElMessage.success('文件上传成功')
  }
}

// 上传失败
const handleUploadError: UploadProps['onError'] = () => {
  ElMessage.error('文件上传失败')
}

// 保存草稿
const handleSaveDraft = async () => {
  saving.value = true
  try {
    const data = { ...form }
    
    if (isEdit.value) {
      await updateProcurement(procurementId.value, data)
      ElMessage.success('草稿保存成功')
    } else {
      const result = await createProcurement(data)
      ElMessage.success('草稿保存成功')
      router.replace(`/office/procurement/edit/${result.id}`)
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    await ElMessageBox.confirm(
      `确定要${isEdit.value ? '更新' : '创建'}这条采购申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    submitting.value = true
    const data = { ...form }

    if (isEdit.value) {
      await updateProcurement(procurementId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createProcurement(data)
      ElMessage.success('创建成功')
    }

    router.push('/office/procurement')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

// 返回
const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadZhichuLeibieOptions()
  fetchDetail()
})
</script>

<style scoped lang="scss">
.procurement-form {
  padding: 20px;

  .form-card {
    margin-top: 20px;
  }

  .el-upload__tip {
    color: #999;
    font-size: 12px;
    margin-top: 8px;
  }
}
</style>

