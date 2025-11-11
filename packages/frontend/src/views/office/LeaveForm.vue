<template>
  <div class="leave-form">
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
            <el-form-item label="请假类型" prop="qingjia_leixing">
              <el-select v-model="form.qingjia_leixing" placeholder="请选择请假类型" style="width: 100%">
                <el-option label="事假" value="shijia" />
                <el-option label="病假" value="bingjia" />
                <el-option label="年假" value="nianjia" />
                <el-option label="调休" value="tiaoxiu" />
                <el-option label="婚假" value="hunjia" />
                <el-option label="产假" value="chanjia" />
                <el-option label="陪产假" value="peichanjia" />
                <el-option label="丧假" value="sangjia" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="请假天数" prop="qingjia_tianshu">
              <el-input-number
                v-model="form.qingjia_tianshu"
                :min="0.5"
                :step="0.5"
                :precision="1"
                :controls="false"
                placeholder="请输入请假天数"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="kaishi_shijian">
              <el-date-picker
                v-model="form.kaishi_shijian"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                @change="calculateDays"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="jieshu_shijian">
              <el-date-picker
                v-model="form.jieshu_shijian"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                @change="calculateDays"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="请假原因" prop="qingjia_yuanyin">
          <el-input
            v-model="form.qingjia_yuanyin"
            type="textarea"
            :rows="4"
            placeholder="请详细说明请假原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 附件上传 -->
        <el-divider content-position="left">附件上传</el-divider>

        <el-form-item label="相关证明">
          <el-upload
            ref="uploadRef"
            :action="uploadAction"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :file-list="fileList"
            :limit="5"
            accept=".pdf,.jpg,.jpeg,.png"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、JPG、PNG 格式，单个文件不超过 10MB，最多上传5个文件（如病假条等）
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
  getLeaveDetail, 
  createLeave, 
  updateLeave,
  type LeaveApplication 
} from '@/api/office'
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

const leaveId = computed(() => route.params.id as string)
const isEdit = computed(() => !!leaveId.value)
const pageTitle = computed(() => isEdit.value ? '编辑请假申请' : '新建请假申请')

const form = reactive<Partial<LeaveApplication>>({
  qingjia_leixing: '',
  kaishi_shijian: '',
  jieshu_shijian: '',
  qingjia_tianshu: 1,
  qingjia_yuanyin: '',
  fujian_lujing: '',
  beizhu: ''
})

const rules: FormRules = {
  qingjia_leixing: [
    { required: true, message: '请选择请假类型', trigger: 'change' }
  ],
  kaishi_shijian: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  jieshu_shijian: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  qingjia_tianshu: [
    { required: true, message: '请输入请假天数', trigger: 'blur' },
    { type: 'number', min: 0.5, message: '请假天数至少0.5天', trigger: 'blur' }
  ],
  qingjia_yuanyin: [
    { required: true, message: '请输入请假原因', trigger: 'blur' },
    { min: 10, message: '请假原因至少10个字符', trigger: 'blur' }
  ]
}

// 上传配置
const uploadAction = computed(() => `${import.meta.env.VITE_API_BASE_URL}/upload/file`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.accessToken}`
}))

// 计算请假天数
const calculateDays = () => {
  if (form.kaishi_shijian && form.jieshu_shijian) {
    const start = new Date(form.kaishi_shijian)
    const end = new Date(form.jieshu_shijian)
    
    if (end > start) {
      const diffTime = Math.abs(end.getTime() - start.getTime())
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      form.qingjia_tianshu = diffDays
    } else {
      ElMessage.warning('结束时间必须大于开始时间')
    }
  }
}

// 获取详情（编辑模式）
const fetchDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getLeaveDetail(leaveId.value)
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
    ElMessage.error('获取请假申请详情失败')
    router.push('/office/leave')
  } finally {
    loading.value = false
  }
}

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
  const isAllowedType = allowedTypes.includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isAllowedType) {
    ElMessage.error('只能上传 PDF、JPG、PNG 格式的文件!')
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
      await updateLeave(leaveId.value, data)
      ElMessage.success('草稿保存成功')
    } else {
      const result = await createLeave(data)
      ElMessage.success('草稿保存成功')
      router.replace(`/office/leave/edit/${result.id}`)
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
      `确定要${isEdit.value ? '更新' : '创建'}这条请假申请吗？`,
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
      await updateLeave(leaveId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createLeave(data)
      ElMessage.success('创建成功')
    }

    router.push('/office/leave')
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
  fetchDetail()
})
</script>

<style scoped lang="scss">
.leave-form {
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

