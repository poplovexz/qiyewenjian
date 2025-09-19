<template>
  <div class="permission-manager">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>权限管理工具</h2>
      <p>快速创建和管理系统权限</p>
    </div>

    <!-- 快速创建审核权限 -->
    <el-card class="quick-create-card">
      <h3>快速创建审核权限</h3>
      <el-button type="primary" @click="createAuditPermissions" :loading="creating">
        <el-icon><Plus /></el-icon>
        创建审核权限
      </el-button>
      <el-button @click="updatePermissionNames" :loading="updating">
        <el-icon><Edit /></el-icon>
        更新权限中文名称
      </el-button>
    </el-card>

    <!-- 权限列表 -->
    <el-card class="permission-list-card">
      <div class="card-header">
        <h3>当前权限列表</h3>
        <el-button @click="fetchPermissions">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="permissions"
        stripe
        style="width: 100%"
        max-height="600"
      >
        <el-table-column prop="quanxian_ming" label="权限名称" width="200" />
        <el-table-column prop="quanxian_bianma" label="权限编码" width="200" />
        <el-table-column prop="ziyuan_leixing" label="资源类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getResourceTypeTag(row.ziyuan_leixing)">
              {{ getResourceTypeText(row.ziyuan_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ziyuan_lujing" label="资源路径" show-overflow-tooltip />
        <el-table-column prop="miaoshu" label="描述" show-overflow-tooltip />
        <el-table-column prop="zhuangtai" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.zhuangtai === 'active' ? 'success' : 'info'">
              {{ row.zhuangtai === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建权限对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="创建权限"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="权限名称" prop="quanxian_ming">
          <el-input v-model="formData.quanxian_ming" placeholder="请输入权限名称" />
        </el-form-item>
        
        <el-form-item label="权限编码" prop="quanxian_bianma">
          <el-input v-model="formData.quanxian_bianma" placeholder="请输入权限编码" />
        </el-form-item>
        
        <el-form-item label="资源类型" prop="ziyuan_leixing">
          <el-select v-model="formData.ziyuan_leixing" placeholder="请选择资源类型">
            <el-option label="菜单" value="menu" />
            <el-option label="按钮" value="button" />
            <el-option label="接口" value="api" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="资源路径" prop="ziyuan_lujing">
          <el-input v-model="formData.ziyuan_lujing" placeholder="请输入资源路径" />
        </el-form-item>
        
        <el-form-item label="权限描述" prop="miaoshu">
          <el-input
            v-model="formData.miaoshu"
            type="textarea"
            :rows="3"
            placeholder="请输入权限描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Edit, Refresh } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const updating = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const permissions = ref([])
const formRef = ref<FormInstance>()

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const formData = reactive({
  quanxian_ming: '',
  quanxian_bianma: '',
  ziyuan_leixing: '',
  ziyuan_lujing: '',
  miaoshu: '',
  zhuangtai: 'active'
})

// 表单验证规则
const formRules: FormRules = {
  quanxian_ming: [
    { required: true, message: '请输入权限名称', trigger: 'blur' }
  ],
  quanxian_bianma: [
    { required: true, message: '请输入权限编码', trigger: 'blur' }
  ],
  ziyuan_leixing: [
    { required: true, message: '请选择资源类型', trigger: 'change' }
  ]
}

// 审核权限定义
const auditPermissions = [
  {
    quanxian_ming: "审核管理菜单",
    quanxian_bianma: "audit_menu",
    miaoshu: "访问审核管理菜单的权限",
    ziyuan_leixing: "menu",
    ziyuan_lujing: "/audit",
    zhuangtai: "active"
  },
  {
    quanxian_ming: "审核任务管理",
    quanxian_bianma: "audit_manage",
    miaoshu: "管理审核任务的权限",
    ziyuan_leixing: "menu",
    ziyuan_lujing: "/audit/tasks",
    zhuangtai: "active"
  },
  {
    quanxian_ming: "审核流程配置",
    quanxian_bianma: "audit_config",
    miaoshu: "配置审核流程的权限",
    ziyuan_leixing: "menu",
    ziyuan_lujing: "/audit/workflow-config",
    zhuangtai: "active"
  },
  {
    quanxian_ming: "审核规则配置",
    quanxian_bianma: "audit_rule_config",
    miaoshu: "配置审核规则的权限",
    ziyuan_leixing: "menu",
    ziyuan_lujing: "/audit/rule-config",
    zhuangtai: "active"
  }
]

// 权限名称映射
const permissionNameMappings = {
  "user:read": "查看用户",
  "user:create": "创建用户",
  "user:update": "编辑用户",
  "user:delete": "删除用户",
  "customer:read": "查看客户",
  "customer:create": "创建客户",
  "customer:update": "编辑客户",
  "customer:delete": "删除客户",
  "contract_manage": "合同管理",
  "contract:read": "查看合同",
  "contract:create": "创建合同",
  "contract:update": "编辑合同",
  "xiansuo:read": "查看线索",
  "xiansuo:create": "创建线索",
  "xiansuo:update": "编辑线索",
  "product:read": "查看产品",
  "finance_manage": "财务管理"
}

// 方法
const fetchPermissions = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取权限列表
    // const response = await permissionApi.getList(pagination)
    // permissions.value = response.data.items
    // pagination.total = response.data.total
    
    // 模拟数据
    permissions.value = []
    pagination.total = 0
    
    ElMessage.success('权限列表获取成功')
  } catch (error) {
    console.error('获取权限列表失败:', error)
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.value = false
  }
}

const createAuditPermissions = async () => {
  creating.value = true
  try {
    let successCount = 0
    
    for (const permData of auditPermissions) {
      try {
        // TODO: 调用API创建权限
        // await permissionApi.create(permData)
        successCount++
        console.log(`创建权限: ${permData.quanxian_ming}`)
      } catch (error) {
        console.error(`创建权限失败: ${permData.quanxian_ming}`, error)
      }
    }
    
    ElMessage.success(`成功创建 ${successCount} 个审核权限`)
    fetchPermissions()
  } catch (error) {
    console.error('批量创建权限失败:', error)
    ElMessage.error('批量创建权限失败')
  } finally {
    creating.value = false
  }
}

const updatePermissionNames = async () => {
  updating.value = true
  try {
    let updateCount = 0
    
    for (const [code, name] of Object.entries(permissionNameMappings)) {
      try {
        // TODO: 调用API更新权限名称
        // await permissionApi.updateName(code, name)
        updateCount++
        console.log(`更新权限: ${code} -> ${name}`)
      } catch (error) {
        console.error(`更新权限失败: ${code}`, error)
      }
    }
    
    ElMessage.success(`成功更新 ${updateCount} 个权限名称`)
    fetchPermissions()
  } catch (error) {
    console.error('批量更新权限失败:', error)
    ElMessage.error('批量更新权限失败')
  } finally {
    updating.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // TODO: 调用API创建权限
    // await permissionApi.create(formData)
    
    ElMessage.success('权限创建成功')
    dialogVisible.value = false
    resetForm()
    fetchPermissions()
  } catch (error) {
    console.error('创建权限失败:', error)
    ElMessage.error('创建权限失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    quanxian_ming: '',
    quanxian_bianma: '',
    ziyuan_leixing: '',
    ziyuan_lujing: '',
    miaoshu: '',
    zhuangtai: 'active'
  })
  formRef.value?.clearValidate()
}

const getResourceTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    menu: 'primary',
    button: 'success',
    api: 'warning'
  }
  return typeMap[type] || 'info'
}

const getResourceTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    menu: '菜单',
    button: '按钮',
    api: '接口'
  }
  return typeMap[type] || type
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  fetchPermissions()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchPermissions()
}

// 生命周期
onMounted(() => {
  fetchPermissions()
})
</script>

<style scoped>
.permission-manager {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.quick-create-card,
.permission-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
