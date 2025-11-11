<template>
  <div class="profile-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        style="max-width: 600px"
      >
        <el-form-item label="用户名">
          <el-input v-model="profile.yonghu_ming" disabled />
        </el-form-item>

        <el-form-item label="姓名" prop="xingming">
          <el-input v-model="formData.xingming" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="手机号" prop="shouji">
          <el-input v-model="formData.shouji" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>

        <el-form-item label="邮箱" prop="youxiang">
          <el-input v-model="formData.youxiang" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="账号状态">
          <el-tag :type="profile.zhuangtai === 'active' ? 'success' : 'info'">
            {{ profile.zhuangtai === 'active' ? '正常' : '禁用' }}
          </el-tag>
        </el-form-item>

        <el-form-item label="创建时间">
          <span>{{ formatDate(profile.created_at) }}</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            保存修改
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getUserProfile, updateUserProfile, type UserProfile, type UserProfileUpdate } from '@/api/modules/settings'
import { formatDateTime } from '@/utils/format'

const formRef = ref<FormInstance>()
const loading = ref(false)

// 用户信息
const profile = ref<UserProfile>({
  id: '',
  yonghu_ming: '',
  xingming: '',
  shouji: '',
  youxiang: '',
  zhuangtai: '',
  created_at: ''
})

// 表单数据
const formData = reactive<UserProfileUpdate>({
  xingming: '',
  shouji: '',
  youxiang: ''
})

// 表单验证规则
const rules: FormRules = {
  xingming: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 50, message: '姓名长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  shouji: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  youxiang: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 格式化日期
const formatDate = (date: string) => {
  return date ? formatDateTime(date) : '-'
}

// 加载用户信息
const loadProfile = async () => {
  try {
    const data = await getUserProfile()
    profile.value = data
    // 初始化表单数据
    formData.xingming = data.xingming
    formData.shouji = data.shouji || ''
    formData.youxiang = data.youxiang || ''
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await updateUserProfile(formData)
        ElMessage.success('保存成功')
        await loadProfile()
      } catch (error: any) {
        ElMessage.error(error.message || '保存失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 重置表单
const handleReset = () => {
  formData.xingming = profile.value.xingming
  formData.shouji = profile.value.shouji || ''
  formData.youxiang = profile.value.youxiang || ''
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped lang="scss">
.profile-settings {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}
</style>

