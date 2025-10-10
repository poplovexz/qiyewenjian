<template>
  <div class="approval-matrix">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审批权责矩阵</span>
          <el-button type="primary" @click="refreshMatrix">刷新矩阵</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- 角色权限矩阵 -->
        <el-tab-pane label="角色权限矩阵" name="roles">
          <div class="matrix-content">
            <el-table :data="matrixData.roles" border style="width: 100%">
              <el-table-column prop="name" label="角色名称" width="150" />
              <el-table-column prop="code" label="角色代码" width="150" />
              <el-table-column prop="description" label="描述" />
              <el-table-column label="用户数量" width="100">
                <template #default="{ row }">
                  <el-tag type="info">{{ row.users.length }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="审批权限" width="200">
                <template #default="{ row }">
                  <div>
                    <div>最大金额: {{ formatAmount(row.approval_authority.max_amount) }}</div>
                    <div class="authority-desc">{{ row.approval_authority.description }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" @click="viewRoleUsers(row)">查看用户</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 审批级别配置 -->
        <el-tab-pane label="审批级别配置" name="levels">
          <div class="levels-content">
            <el-select v-model="selectedRuleType" placeholder="选择规则类型" style="margin-bottom: 20px">
              <el-option
                v-for="type in ruleTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>

            <el-card v-if="selectedRuleType && approvalLevels" class="levels-card">
              <template #header>
                <span>{{ approvalLevels.name }}</span>
              </template>
              
              <el-table :data="approvalLevels.levels" border>
                <el-table-column prop="level" label="级别" width="80" />
                <el-table-column prop="role_name" label="角色名称" width="150" />
                <el-table-column prop="role_code" label="角色代码" width="150" />
                <el-table-column label="金额范围" width="200">
                  <template #default="{ row }">
                    {{ formatAmount(row.min_amount) }} - 
                    {{ row.max_amount === Infinity ? '无限制' : formatAmount(row.max_amount) }}
                  </template>
                </el-table-column>
                <el-table-column label="是否必需" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.required ? 'success' : 'info'">
                      {{ row.required ? '必需' : '可选' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button size="small" @click="testAssignment(row)">测试分配</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 审批链测试 -->
        <el-tab-pane label="审批链测试" name="test">
          <div class="test-content">
            <el-form :model="testForm" label-width="120px" style="max-width: 600px">
              <el-form-item label="规则类型">
                <el-select v-model="testForm.rule_type" placeholder="选择规则类型">
                  <el-option
                    v-for="type in ruleTypes"
                    :key="type.value"
                    :label="type.label"
                    :value="type.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="金额">
                <el-input-number v-model="testForm.amount" :min="0" :precision="2" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="testApprovalChain" :loading="testing">
                  测试审批链
                </el-button>
              </el-form-item>
            </el-form>

            <el-card v-if="approvalChain" header="审批链结果" style="margin-top: 20px">
              <el-timeline>
                <el-timeline-item
                  v-for="(step, index) in approvalChain.approval_chain"
                  :key="index"
                  :type="step.approver_id ? 'success' : 'warning'"
                >
                  <div class="chain-step">
                    <h4>级别 {{ step.level }}: {{ step.role_name }}</h4>
                    <p>角色代码: {{ step.role_code }}</p>
                    <p>金额范围: {{ formatAmount(step.min_amount) }} - 
                       {{ step.max_amount ? formatAmount(step.max_amount) : '无限制' }}</p>
                    <p v-if="step.approver_id">
                      <el-tag type="success">已分配审批人: {{ step.approver_id }}</el-tag>
                    </p>
                    <p v-else>
                      <el-tag type="warning">未找到可用审批人</el-tag>
                    </p>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 角色用户详情对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="`${selectedRole?.name} - 用户列表`"
      width="600px"
    >
      <el-table :data="selectedRole?.users" border>
        <el-table-column prop="name" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="position" label="职位" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const activeTab = ref('roles')
const matrixData = ref<any>({
  roles: [],
  approval_levels: {},
  role_mappings: {}
})
const selectedRuleType = ref('')
const approvalLevels = ref<any>(null)
const userDialogVisible = ref(false)
const selectedRole = ref<any>(null)
const testing = ref(false)
const approvalChain = ref<any>(null)

// 测试表单
const testForm = reactive({
  rule_type: '',
  amount: 0
})

// 规则类型选项
const ruleTypes = ref([
  { value: 'hetong_jine_xiuzheng', label: '合同金额修正审批' },
  { value: 'baojia_shenhe', label: '报价审核' },
  { value: 'zhifu_shenhe', label: '支付审核' }
])

// 方法
const refreshMatrix = async () => {
  try {
    const response = await fetch('/api/v1/approval-matrix/matrix', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('获取审批矩阵失败')
    }
    
    const data = await response.json()
    matrixData.value = data
    
    ElMessage.success('审批矩阵刷新成功')
  } catch (error) {
    console.error('获取审批矩阵失败:', error)
    ElMessage.error('获取审批矩阵失败')
  }
}

const formatAmount = (amount: number) => {
  if (amount === Infinity || amount === 0) {
    return amount === Infinity ? '无限制' : '0'
  }
  return `¥${amount.toLocaleString()}`
}

const viewRoleUsers = (role: any) => {
  selectedRole.value = role
  userDialogVisible.value = true
}

const testAssignment = async (level: any) => {
  try {
    const response = await fetch('/api/v1/approval-matrix/assign-approver', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        role_code: level.role_code,
        amount: level.min_amount + 1000
      })
    })
    
    if (!response.ok) {
      throw new Error('测试分配失败')
    }
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(`分配成功: ${result.approver.name}`)
    } else {
      ElMessage.warning(result.message)
    }
  } catch (error) {
    console.error('测试分配失败:', error)
    ElMessage.error('测试分配失败')
  }
}

const testApprovalChain = async () => {
  if (!testForm.rule_type) {
    ElMessage.warning('请选择规则类型')
    return
  }
  
  try {
    testing.value = true
    
    const response = await fetch('/api/v1/approval-matrix/approval-chain', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        rule_type: testForm.rule_type,
        amount: testForm.amount
      })
    })
    
    if (!response.ok) {
      throw new Error('测试审批链失败')
    }
    
    const result = await response.json()
    approvalChain.value = result
    
    ElMessage.success('审批链测试完成')
  } catch (error) {
    console.error('测试审批链失败:', error)
    ElMessage.error('测试审批链失败')
  } finally {
    testing.value = false
  }
}

// 监听规则类型变化
watch(selectedRuleType, async (newType) => {
  if (newType) {
    try {
      const response = await fetch(`/api/v1/approval-matrix/approval-levels/${newType}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) {
        throw new Error('获取审批级别失败')
      }
      
      const data = await response.json()
      approvalLevels.value = data.config
    } catch (error) {
      console.error('获取审批级别失败:', error)
      ElMessage.error('获取审批级别失败')
    }
  }
})

// 生命周期
onMounted(() => {
  refreshMatrix()
})
</script>

<style scoped>
.approval-matrix {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.matrix-content,
.levels-content,
.test-content {
  padding: 20px;
}

.authority-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.levels-card {
  margin-top: 20px;
}

.chain-step h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.chain-step p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}
</style>
