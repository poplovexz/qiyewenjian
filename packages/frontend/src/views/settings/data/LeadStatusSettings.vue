<template>
  <div class="lead-status-settings">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新增状态
      </el-button>
    </div>

    <el-table :data="statusList" v-loading="loading" border>
      <el-table-column prop="zhuangtai_mingcheng" label="状态名称" min-width="150" />
      <el-table-column prop="zhuangtai_bianma" label="状态编码" width="120" />
      <el-table-column prop="zhuangtai_leixing" label="状态类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusTypeTag(row.zhuangtai_leixing)">
            {{ getStatusTypeLabel(row.zhuangtai_leixing) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="zhuangtai_yanse" label="显示颜色" width="100" align="center">
        <template #default="{ row }">
          <el-tag :color="row.zhuangtai_yanse" style="border: none">
            {{ row.zhuangtai_yanse }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="shi_zhongtai" label="是否终态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.shi_zhongtai === 'Y' ? 'danger' : 'info'" size="small">
            {{ row.shi_zhongtai === 'Y' ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
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
      :title="formMode === 'create' ? '新增线索状态' : '编辑线索状态'"
      width="500px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="状态名称" prop="zhuangtai_mingcheng">
          <el-input v-model="formData.zhuangtai_mingcheng" placeholder="请输入状态名称" />
        </el-form-item>
        <el-form-item label="状态编码" prop="zhuangtai_bianma">
          <el-input v-model="formData.zhuangtai_bianma" placeholder="请输入状态编码" />
        </el-form-item>
        <el-form-item label="状态类型" prop="zhuangtai_leixing">
          <el-select v-model="formData.zhuangtai_leixing" placeholder="请选择状态类型" style="width: 100%">
            <el-option label="新建" value="new" />
            <el-option label="跟进中" value="following" />
            <el-option label="已转化" value="converted" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="显示颜色" prop="zhuangtai_yanse">
          <el-color-picker v-model="formData.zhuangtai_yanse" />
        </el-form-item>
        <el-form-item label="是否终态" prop="shi_zhongtai">
          <el-radio-group v-model="formData.shi_zhongtai">
            <el-radio value="Y">是</el-radio>
            <el-radio value="N">否</el-radio>
          </el-radio-group>
          <div class="form-tip">终态表示线索流程的最终状态，如"已转化"、"已关闭"</div>
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
interface LeadStatus {
  id: string
  zhuangtai_mingcheng: string
  zhuangtai_bianma: string
  zhuangtai_leixing: string
  zhuangtai_yanse: string
  shi_zhongtai: string
  paixu: number
  zhuangtai: string
}

const loading = ref(false)
const formVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 状态列表
const statusList = ref<LeadStatus[]>([])

// 表单数据
const formData = reactive({
  id: '',
  zhuangtai_mingcheng: '',
  zhuangtai_bianma: '',
  zhuangtai_leixing: '',
  zhuangtai_yanse: '#409EFF',
  shi_zhongtai: 'N',
  paixu: 0,
  zhuangtai: 'active'
})

// 表单验证规则
const formRules: FormRules = {
  zhuangtai_mingcheng: [
    { required: true, message: '请输入状态名称', trigger: 'blur' }
  ],
  zhuangtai_bianma: [
    { required: true, message: '请输入状态编码', trigger: 'blur' }
  ],
  zhuangtai_leixing: [
    { required: true, message: '请选择状态类型', trigger: 'change' }
  ]
}

// 获取状态类型标签
const getStatusTypeTag = (type: string) => {
  const map: Record<string, string> = {
    new: 'info',
    following: 'warning',
    converted: 'success',
    closed: 'danger'
  }
  return map[type] || 'info'
}

// 获取状态类型文本
const getStatusTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    new: '新建',
    following: '跟进中',
    converted: '已转化',
    closed: '已关闭'
  }
  return map[type] || type
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取数据
    // 这里使用模拟数据
    statusList.value = [
      {
        id: '1',
        zhuangtai_mingcheng: '新建',
        zhuangtai_bianma: 'NEW',
        zhuangtai_leixing: 'new',
        zhuangtai_yanse: '#909399',
        shi_zhongtai: 'N',
        paixu: 1,
        zhuangtai: 'active'
      },
      {
        id: '2',
        zhuangtai_mingcheng: '跟进中',
        zhuangtai_bianma: 'FOLLOWING',
        zhuangtai_leixing: 'following',
        zhuangtai_yanse: '#E6A23C',
        shi_zhongtai: 'N',
        paixu: 2,
        zhuangtai: 'active'
      },
      {
        id: '3',
        zhuangtai_mingcheng: '已转化',
        zhuangtai_bianma: 'CONVERTED',
        zhuangtai_leixing: 'converted',
        zhuangtai_yanse: '#67C23A',
        shi_zhongtai: 'Y',
        paixu: 3,
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
    zhuangtai_mingcheng: '',
    zhuangtai_bianma: '',
    zhuangtai_leixing: '',
    zhuangtai_yanse: '#409EFF',
    shi_zhongtai: 'N',
    paixu: 0,
    zhuangtai: 'active'
  })
  formVisible.value = true
}

// 编辑
const handleEdit = (row: LeadStatus) => {
  formMode.value = 'edit'
  Object.assign(formData, row)
  formVisible.value = true
}

// 删除
const handleDelete = async (row: LeadStatus) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除线索状态"${row.zhuangtai_mingcheng}"吗？`,
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
const handleStatusChange = async (row: LeadStatus) => {
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
.lead-status-settings {
  .toolbar {
    margin-bottom: 16px;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
}
</style>

