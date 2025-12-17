<template>
  <div class="handover-form">
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
            <el-form-item label="接收人" prop="jieshou_ren_id">
              <el-select
                v-model="form.jieshou_ren_id"
                placeholder="请选择接收人"
                filterable
                remote
                :remote-method="searchUsers"
                :loading="userLoading"
                style="width: 100%"
              >
                <el-option
                  v-for="user in userList"
                  :key="user.id"
                  :label="user.xing_ming"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交接时间" prop="jiaojie_shijian">
              <el-date-picker
                v-model="form.jiaojie_shijian"
                type="datetime"
                placeholder="选择交接时间"
                style="width: 100%"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="交接原因" prop="jiaojie_yuanyin">
          <el-select v-model="form.jiaojie_yuanyin" placeholder="请选择交接原因" style="width: 100%">
            <el-option label="离职" value="lizhi" />
            <el-option label="调岗" value="diaogang" />
            <el-option label="休假" value="xiujia" />
            <el-option label="其他" value="qita" />
          </el-select>
        </el-form-item>

        <!-- 交接内容 -->
        <el-divider content-position="left">交接内容</el-divider>

        <el-form-item label="工作内容" prop="jiaojie_neirong">
          <el-input
            v-model="form.jiaojie_neirong"
            type="textarea"
            :rows="4"
            placeholder="请详细描述需要交接的工作内容、项目进展、注意事项等"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="文件清单" prop="wenjian_qingdan">
          <el-input
            v-model="form.wenjian_qingdan"
            type="textarea"
            :rows="3"
            placeholder="请列出需要交接的文件、文档清单（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="设备清单" prop="shebei_qingdan">
          <el-input
            v-model="form.shebei_qingdan"
            type="textarea"
            :rows="3"
            placeholder="请列出需要交接的设备、工具清单（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="账号清单" prop="zhanghu_qingdan">
          <el-input
            v-model="form.zhanghu_qingdan"
            type="textarea"
            :rows="3"
            placeholder="请列出需要交接的系统账号、权限清单（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="待办事项" prop="daiban_shixiang">
          <el-input
            v-model="form.daiban_shixiang"
            type="textarea"
            :rows="3"
            placeholder="请列出未完成的待办事项、需要跟进的工作（选填）"
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
            :limit="10"
            accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls,.doc,.docx,.zip,.rar"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、图片、Office文档、压缩包等格式，单个文件不超过 10MB，最多上传10个文件
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
  getHandoverDetail, 
  createHandover, 
  updateHandover,
  getUserList,
  type HandoverApplication 
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
const userLoading = ref(false)
const fileList = ref<UploadUserFile[]>([])
const userList = ref<any[]>([])

const handoverId = computed(() => route.params.id as string)
const isEdit = computed(() => !!handoverId.value)
const pageTitle = computed(() => isEdit.value ? '编辑工作交接单' : '新建工作交接单')

const form = reactive<Partial<HandoverApplication>>({
  jieshou_ren_id: '',
  jiaojie_yuanyin: '',
  jiaojie_shijian: '',
  jiaojie_neirong: '',
  wenjian_qingdan: '',
  shebei_qingdan: '',
  zhanghu_qingdan: '',
  daiban_shixiang: '',
  fujian_lujing: '',
  beizhu: ''
})

const rules: FormRules = {
  jieshou_ren_id: [
    { required: true, message: '请选择接收人', trigger: 'change' }
  ],
  jiaojie_yuanyin: [
    { required: true, message: '请选择交接原因', trigger: 'change' }
  ],
  jiaojie_shijian: [
    { required: true, message: '请选择交接时间', trigger: 'change' }
  ],
  jiaojie_neirong: [
    { required: true, message: '请输入工作内容', trigger: 'blur' },
    { min: 20, message: '工作内容至少20个字符', trigger: 'blur' }
  ]
}

// 上传配置
const uploadAction = computed(() => `${import.meta.env.VITE_API_BASE_URL}/upload/file`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.accessToken}`
}))

// 搜索用户
const searchUsers = async (query: string) => {
  if (!query) {
    userList.value = []
    return
  }
  
  userLoading.value = true
  try {
    const response = await getUserList({ search: query, page_size: 20 })
    userList.value = response.items || []
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    userLoading.value = false
  }
}

// 获取详情（编辑模式）
const fetchDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getHandoverDetail(handoverId.value)
    Object.assign(form, data)
    
    // 处理附件列表
    if (data.fujian_lujing) {
      const files = data.fujian_lujing.split(',').filter(Boolean)
      fileList.value = files.map((url, index) => ({
        name: `附件${index + 1}`,
        url: url
      }))
    }
    
    // 加载接收人信息
    if (data.jieshou_ren_id) {
      userList.value = [{
        id: data.jieshou_ren_id,
        xing_ming: data.jieshou_ren_xingming
      }]
    }
  } catch (error) {
    ElMessage.error('获取交接单详情失败')
    router.push('/office/handover')
  } finally {
    loading.value = false
  }
}

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10

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
      await updateHandover(handoverId.value, data)
      ElMessage.success('草稿保存成功')
    } else {
      const result = await createHandover(data)
      ElMessage.success('草稿保存成功')
      router.replace(`/office/handover/edit/${result.id}`)
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
      `确定要${isEdit.value ? '更新' : '创建'}这条工作交接单吗？`,
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
      await updateHandover(handoverId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createHandover(data)
      ElMessage.success('创建成功')
    }

    router.push('/office/handover')
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
.handover-form {
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

