<template>
  <div class="lead-source-settings">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新增来源
      </el-button>
    </div>

    <el-table :data="sourceList" v-loading="loading" border>
      <el-table-column prop="laiyuan_mingcheng" label="来源名称" min-width="150" />
      <el-table-column prop="laiyuan_bianma" label="来源编码" width="120" />
      <el-table-column prop="laiyuan_leixing" label="来源类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getSourceTypeTag(row.laiyuan_leixing)">
            {{ getSourceTypeLabel(row.laiyuan_leixing) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="miaoshu" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="paixu" label="排序" width="80" align="center" />
      <el-table-column prop="zhuangtai" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.zhuangtai"
            active-value="active"
            inactive-value="inactive"
            @change="handleStatusChange(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="danger" link @click="handleDelete(row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 表单弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="formMode === 'create' ? '新增线索来源' : '编辑线索来源'"
      width="500px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="来源名称" prop="laiyuan_mingcheng">
          <el-input v-model="formData.laiyuan_mingcheng" placeholder="请输入来源名称" />
        </el-form-item>
        <el-form-item label="来源编码" prop="laiyuan_bianma">
          <el-input v-model="formData.laiyuan_bianma" placeholder="请输入来源编码" />
        </el-form-item>
        <el-form-item label="来源类型" prop="laiyuan_leixing">
          <el-select v-model="formData.laiyuan_leixing" placeholder="请选择来源类型" style="width: 100%">
            <el-option label="线上渠道" value="online" />
            <el-option label="线下渠道" value="offline" />
            <el-option label="转介绍" value="referral" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="miaoshu">
          <el-input
            v-model="formData.miaoshu"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="排序" prop="paixu">
          <el-input-number v-model="formData.paixu" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态" prop="zhuangtai">
          <el-radio-group v-model="formData.zhuangtai">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

// 模拟数据类型
interface LeadSource {
  id: string
  laiyuan_mingcheng: string
  laiyuan_bianma: string
  laiyuan_leixing: string
  miaoshu: string
  paixu: number
  zhuangtai: string
}

const loading = ref(false)
const formVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 来源列表
const sourceList = ref<LeadSource[]>([])

// 表单数据
const formData = reactive({
  id: '',
  laiyuan_mingcheng: '',
  laiyuan_bianma: '',
  laiyuan_leixing: '',
  miaoshu: '',
  paixu: 0,
  zhuangtai: 'active'
})

// 表单验证规则
const formRules: FormRules = {
  laiyuan_mingcheng: [
    { required: true, message: '请输入来源名称', trigger: 'blur' }
  ],
  laiyuan_bianma: [
    { required: true, message: '请输入来源编码', trigger: 'blur' }
  ],
  laiyuan_leixing: [
    { required: true, message: '请选择来源类型', trigger: 'change' }
  ]
}

// 获取来源类型标签
const getSourceTypeTag = (type: string) => {
  const map: Record<string, string> = {
    online: 'success',
    offline: 'warning',
    referral: 'primary',
    other: 'info'
  }
  return map[type] || 'info'
}

// 获取来源类型文本
const getSourceTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    online: '线上渠道',
    offline: '线下渠道',
    referral: '转介绍',
    other: '其他'
  }
  return map[type] || type
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取数据
    // 这里使用模拟数据
    sourceList.value = [
      {
        id: '1',
        laiyuan_mingcheng: '官网咨询',
        laiyuan_bianma: 'WEB',
        laiyuan_leixing: 'online',
        miaoshu: '通过官网在线咨询获取的线索',
        paixu: 1,
        zhuangtai: 'active'
      },
      {
        id: '2',
        laiyuan_mingcheng: '电话咨询',
        laiyuan_bianma: 'TEL',
        laiyuan_leixing: 'offline',
        miaoshu: '客户主动电话咨询',
        paixu: 2,
        zhuangtai: 'active'
      }
    ]
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 新增
const handleCreate = () => {
  formMode.value = 'create'
  Object.assign(formData, {
    id: '',
    laiyuan_mingcheng: '',
    laiyuan_bianma: '',
    laiyuan_leixing: '',
    miaoshu: '',
    paixu: 0,
    zhuangtai: 'active'
  })
  formVisible.value = true
}

// 编辑
const handleEdit = (row: LeadSource) => {
  formMode.value = 'edit'
  Object.assign(formData, row)
  formVisible.value = true
}

// 删除
const handleDelete = async (row: LeadSource) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除线索来源"${row.laiyuan_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 状态切换
const handleStatusChange = async (row: LeadSource) => {
  try {
    // TODO: 调用API更新状态
    ElMessage.success('状态已更新')
  } catch (error: any) {
    ElMessage.error(error.message || '更新状态失败')
    // 恢复原状态
    row.zhuangtai = row.zhuangtai === 'active' ? 'inactive' : 'active'
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      // TODO: 调用API保存
      ElMessage.success(formMode.value === 'create' ? '创建成功' : '更新成功')
      formVisible.value = false
      loadData()
    } catch (error: any) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.lead-source-settings {
  .toolbar {
    margin-bottom: 16px;
  }
}
</style>

