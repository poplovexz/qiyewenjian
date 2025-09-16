<template>
  <el-dialog
    v-model="dialogVisible"
    title="权限管理"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="role" class="permission-dialog">
      <div class="role-info">
        <h4>角色信息</h4>
        <p><strong>角色名称：</strong>{{ role.jiaose_ming }}</p>
        <p><strong>角色编码：</strong>{{ role.jiaose_bianma }}</p>
        <p><strong>角色描述：</strong>{{ role.miaoshu || '暂无描述' }}</p>
      </div>
      
      <el-divider />
      
      <div class="permission-section">
        <div class="section-header">
          <h4>权限分配</h4>
          <div class="actions">
            <el-button size="small" @click="selectAll">全选</el-button>
            <el-button size="small" @click="selectNone">全不选</el-button>
            <el-button size="small" @click="expandAll">展开全部</el-button>
            <el-button size="small" @click="collapseAll">收起全部</el-button>
          </div>
        </div>
        
        <el-tree
          ref="treeRef"
          :data="permissionTree"
          :props="treeProps"
          show-checkbox
          node-key="id"
          :default-checked-keys="checkedPermissions"
          :default-expand-all="false"
          class="permission-tree"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-icon v-if="data.icon" class="node-icon">
                <component :is="data.icon" />
              </el-icon>
              <span class="node-label">{{ node.label }}</span>
              <el-tag 
                v-if="data.type" 
                :type="getPermissionTypeTag(data.type)"
                size="small"
                class="node-tag"
              >
                {{ getPermissionTypeText(data.type) }}
              </el-tag>
            </div>
          </template>
        </el-tree>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          :loading="loading"
          @click="handleSubmit"
        >
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElTree } from 'element-plus'
import { Menu, Mouse, Connection, Folder, Document } from '@element-plus/icons-vue'
import type { Role } from '@/api/modules/role'

interface Props {
  visible: boolean
  role?: Role | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  role: null
})

const emit = defineEmits<Emits>()

// 响应式数据
const treeRef = ref<InstanceType<typeof ElTree>>()
const loading = ref(false)
const checkedPermissions = ref<string[]>([])

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 树形结构配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 模拟权限树数据
const permissionTree = ref([
  {
    id: 'user-management',
    label: '用户管理',
    icon: 'User',
    children: [
      {
        id: 'user:menu',
        label: '用户管理菜单',
        type: 'menu'
      },
      {
        id: 'user:read',
        label: '查看用户',
        type: 'api'
      },
      {
        id: 'user:create',
        label: '创建用户',
        type: 'api'
      },
      {
        id: 'user:update',
        label: '编辑用户',
        type: 'api'
      },
      {
        id: 'user:delete',
        label: '删除用户',
        type: 'api'
      },
      {
        id: 'user:create_button',
        label: '新增用户按钮',
        type: 'button'
      }
    ]
  },
  {
    id: 'role-management',
    label: '角色管理',
    icon: 'UserFilled',
    children: [
      {
        id: 'role:menu',
        label: '角色管理菜单',
        type: 'menu'
      },
      {
        id: 'role:read',
        label: '查看角色',
        type: 'api'
      },
      {
        id: 'role:create',
        label: '创建角色',
        type: 'api'
      },
      {
        id: 'role:update',
        label: '编辑角色',
        type: 'api'
      },
      {
        id: 'role:delete',
        label: '删除角色',
        type: 'api'
      }
    ]
  },
  {
    id: 'customer-management',
    label: '客户管理',
    icon: 'UserFilled',
    children: [
      {
        id: 'customer:menu',
        label: '客户管理菜单',
        type: 'menu'
      },
      {
        id: 'customer:read',
        label: '查看客户',
        type: 'api'
      },
      {
        id: 'customer:create',
        label: '创建客户',
        type: 'api'
      },
      {
        id: 'customer:update',
        label: '编辑客户',
        type: 'api'
      },
      {
        id: 'customer:delete',
        label: '删除客户',
        type: 'api'
      }
    ]
  }
])

// 工具函数
const getPermissionTypeTag = (type: string) => {
  const typeMap = {
    menu: 'primary',
    button: 'success',
    api: 'warning'
  }
  return typeMap[type] || 'info'
}

const getPermissionTypeText = (type: string) => {
  const typeMap = {
    menu: '菜单',
    button: '按钮',
    api: '接口'
  }
  return typeMap[type] || type
}

// 树操作方法
const selectAll = () => {
  const allKeys = getAllNodeKeys(permissionTree.value)
  treeRef.value?.setCheckedKeys(allKeys)
}

const selectNone = () => {
  treeRef.value?.setCheckedKeys([])
}

const expandAll = () => {
  const allKeys = getAllNodeKeys(permissionTree.value)
  allKeys.forEach(key => {
    treeRef.value?.getNode(key)?.expand()
  })
}

const collapseAll = () => {
  const allKeys = getAllNodeKeys(permissionTree.value)
  allKeys.forEach(key => {
    treeRef.value?.getNode(key)?.collapse()
  })
}

const getAllNodeKeys = (nodes: any[]): string[] => {
  const keys: string[] = []
  const traverse = (nodeList: any[]) => {
    nodeList.forEach(node => {
      keys.push(node.id)
      if (node.children) {
        traverse(node.children)
      }
    })
  }
  traverse(nodes)
  return keys
}

// 监听角色变化
watch(() => props.role, (newRole) => {
  if (newRole) {
    // TODO: 加载角色的权限数据
    checkedPermissions.value = []
  }
}, { immediate: true })

// 处理关闭
const handleClose = () => {
  dialogVisible.value = false
}

// 处理提交
const handleSubmit = async () => {
  if (!props.role) return
  
  try {
    loading.value = true
    
    const checkedKeys = treeRef.value?.getCheckedKeys() || []
    const halfCheckedKeys = treeRef.value?.getHalfCheckedKeys() || []
    const allCheckedKeys = [...checkedKeys, ...halfCheckedKeys]
    
    // TODO: 调用API保存角色权限
    console.log('保存权限:', allCheckedKeys)
    
    ElMessage.success('权限保存成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('权限保存失败:', error)
    ElMessage.error('权限保存失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.permission-dialog {
  max-height: 600px;
  overflow-y: auto;
}

.role-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.role-info h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.role-info p {
  margin: 8px 0;
  color: #606266;
}

.permission-section {
  margin-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
}

.actions {
  display: flex;
  gap: 8px;
}

.permission-tree {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.node-icon {
  color: #409eff;
}

.node-label {
  flex: 1;
}

.node-tag {
  margin-left: auto;
}

.dialog-footer {
  text-align: right;
}
</style>
