<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      :disabled="mode === 'view'"
    >
      <el-form-item label="权限名称" prop="quanxian_ming">
        <el-input
          v-model="formData.quanxian_ming"
          placeholder="请输入权限名称，如：查看用户列表"
          maxlength="50"
          show-word-limit
          @input="handleNameInput"
        />
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>输入权限名称后，其他字段将自动填充（可手动修改）</span>
        </div>
      </el-form-item>

      <el-form-item label="权限编码" prop="quanxian_bianma">
        <el-input
          v-model="formData.quanxian_bianma"
          placeholder="自动生成或手动输入，如：user:read"
          maxlength="100"
          show-word-limit
        >
          <template #append>
            <el-button @click="autoFillAll" :icon="Refresh">
              自动填充
            </el-button>
          </template>
        </el-input>
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>权限编码会根据权限名称自动生成（格式：模块:操作），也可以手动修改</span>
        </div>
      </el-form-item>

      <el-form-item label="权限描述" prop="miaoshu">
        <el-input
          v-model="formData.miaoshu"
          type="textarea"
          :rows="3"
          placeholder="自动生成或手动输入"
          maxlength="200"
          show-word-limit
        />
        <div class="form-tip" v-if="formData.miaoshu">
          <el-icon><InfoFilled /></el-icon>
          <span>已自动生成描述，可手动修改</span>
        </div>
      </el-form-item>
      
      <el-form-item label="资源类型" prop="ziyuan_leixing">
        <el-select
          v-model="formData.ziyuan_leixing"
          placeholder="自动推荐或手动选择"
          style="width: 100%"
          @change="handleResourceTypeChange"
        >
          <el-option label="菜单" value="menu">
            <div class="option-item">
              <el-icon><Menu /></el-icon>
              <span>菜单</span>
              <small>页面访问权限</small>
            </div>
          </el-option>
          <el-option label="按钮" value="button">
            <div class="option-item">
              <el-icon><Mouse /></el-icon>
              <span>按钮</span>
              <small>页面操作权限</small>
            </div>
          </el-option>
          <el-option label="接口" value="api">
            <div class="option-item">
              <el-icon><Connection /></el-icon>
              <span>接口</span>
              <small>API访问权限</small>
            </div>
          </el-option>
        </el-select>
        <div class="form-tip" v-if="formData.ziyuan_leixing">
          <el-icon><InfoFilled /></el-icon>
          <span>已自动推荐资源类型，可手动修改</span>
        </div>
      </el-form-item>

      <el-form-item label="资源路径" prop="ziyuan_lujing">
        <el-input
          v-model="formData.ziyuan_lujing"
          placeholder="自动生成或手动输入"
          maxlength="200"
          show-word-limit
        />
        <div class="form-tip">
          {{ getResourcePathTip() }}
        </div>
      </el-form-item>
      
      <el-form-item label="状态" prop="zhuangtai">
        <el-radio-group v-model="formData.zhuangtai">
          <el-radio label="active">启用</el-radio>
          <el-radio label="inactive">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          v-if="mode !== 'view'"
          type="primary" 
          :loading="loading"
          @click="handleSubmit"
        >
          {{ mode === 'create' ? '创建' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Menu, Mouse, Connection, Refresh, InfoFilled } from '@element-plus/icons-vue'
import { usePermissionStore } from '@/stores/modules/permission'
import type { Permission } from '@/api/modules/permission'

interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
  permission?: Permission | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  permission: null
})

const emit = defineEmits<Emits>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const permissionStore = usePermissionStore()

const formData = ref({
  quanxian_ming: '',
  quanxian_bianma: '',
  miaoshu: '',
  ziyuan_leixing: '',
  ziyuan_lujing: '',
  zhuangtai: 'active'
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  const titleMap = {
    create: '新增权限',
    edit: '编辑权限',
    view: '查看权限'
  }
  return titleMap[props.mode]
})

// 获取资源路径提示
const getResourcePathTip = () => {
  switch (formData.value.ziyuan_leixing) {
    case 'menu':
      return '菜单路径，如：/users、/customers'
    case 'button':
      return '按钮标识，如：user-create-btn、customer-edit-btn'
    case 'api':
      return 'API路径，如：/api/v1/users/*、/api/v1/customers/'
    default:
      return '请先选择资源类型'
  }
}

// 表单验证规则
const formRules: FormRules = {
  quanxian_ming: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '权限名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  quanxian_bianma: [
    { required: true, message: '请输入权限编码', trigger: 'blur' },
    { min: 2, max: 100, message: '权限编码长度在 2 到 100 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_:]*$/, message: '权限编码必须以字母开头，只能包含字母、数字、下划线和冒号', trigger: 'blur' }
  ],
  miaoshu: [
    { max: 200, message: '权限描述不能超过 200 个字符', trigger: 'blur' }
  ],
  ziyuan_leixing: [
    { required: true, message: '请选择资源类型', trigger: 'change' }
  ],
  ziyuan_lujing: [
    { required: true, message: '请输入资源路径', trigger: 'blur' },
    { max: 200, message: '资源路径不能超过 200 个字符', trigger: 'blur' }
  ],
  zhuangtai: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 中文拼音映射表（常用字）
const pinyinMap: Record<string, string> = {
  '查': 'cha', '看': 'kan', '阅': 'yue', '读': 'du', '览': 'lan',
  '创': 'chuang', '建': 'jian', '新': 'xin', '增': 'zeng', '加': 'jia',
  '编': 'bian', '辑': 'ji', '修': 'xiu', '改': 'gai', '更': 'geng',
  '删': 'shan', '除': 'chu', '移': 'yi',
  '用': 'yong', '户': 'hu', '客': 'ke', '服': 'fu',
  '角': 'jue', '色': 'se', '权': 'quan', '限': 'xian',
  '管': 'guan', '理': 'li', '员': 'yuan',
  '业': 'ye', '务': 'wu', '财': 'cai',
  '合': 'he', '同': 'tong', '报': 'bao', '价': 'jia',
  '线': 'xian', '索': 'suo', '跟': 'gen', '进': 'jin',
  '审': 'shen', '核': 'he', '批': 'pi', '准': 'zhun',
  '导': 'dao', '出': 'chu', '入': 'ru',
  '上': 'shang', '传': 'chuan', '下': 'xia', '载': 'zai',
  '启': 'qi', '禁': 'jin',
  '列': 'lie', '表': 'biao', '详': 'xiang', '情': 'qing',
  '统': 'tong', '计': 'ji', '分': 'fen', '析': 'xi'
}

// 操作动词映射
const actionMap: Record<string, string> = {
  '查看': 'read',
  '阅读': 'read',
  '查询': 'query',
  '创建': 'create',
  '新建': 'create',
  '新增': 'create',
  '添加': 'create',
  '编辑': 'update',
  '修改': 'update',
  '更新': 'update',
  '删除': 'delete',
  '移除': 'delete',
  '导出': 'export',
  '导入': 'import',
  '上传': 'upload',
  '下载': 'download',
  '审核': 'audit',
  '审批': 'approve',
  '启用': 'enable',
  '禁用': 'disable',
  '管理': 'manage',
  '分配': 'assign',
  '统计': 'statistics'
}

// 模块名称映射
const moduleMap: Record<string, string> = {
  '用户': 'user',
  '客户': 'customer',
  '角色': 'role',
  '权限': 'permission',
  '合同': 'contract',
  '报价': 'quote',
  '线索': 'lead',
  '业务': 'business',
  '财务': 'finance',
  '审核': 'audit',
  '审批': 'approval'
}

// 智能分析权限名称
const analyzePermissionName = (name: string) => {
  let module = ''
  let action = ''
  let actionChinese = ''
  let moduleChinese = ''

  // 尝试匹配操作动词
  for (const [key, value] of Object.entries(actionMap)) {
    if (name.includes(key)) {
      action = value
      actionChinese = key
      break
    }
  }

  // 尝试匹配模块名称
  for (const [key, value] of Object.entries(moduleMap)) {
    if (name.includes(key)) {
      module = value
      moduleChinese = key
      break
    }
  }

  // 如果没有匹配到，使用拼音转换
  if (!module || !action) {
    let pinyin = ''
    for (const char of name) {
      if (pinyinMap[char]) {
        pinyin += pinyinMap[char]
      } else if (/[a-zA-Z0-9]/.test(char)) {
        pinyin += char.toLowerCase()
      }
    }

    // 如果没有找到模块，使用拼音的前半部分
    if (!module && pinyin) {
      const mid = Math.floor(pinyin.length / 2)
      module = pinyin.substring(0, mid) || 'resource'
    }

    // 如果没有找到操作，使用拼音的后半部分或默认值
    if (!action && pinyin) {
      const mid = Math.floor(pinyin.length / 2)
      action = pinyin.substring(mid) || 'action'
    }
  }

  return { module, action, actionChinese, moduleChinese }
}

// 生成权限编码
const generateCode = () => {
  const name = formData.value.quanxian_ming.trim()
  if (!name) {
    ElMessage.warning('请先输入权限名称')
    return ''
  }

  const { module, action } = analyzePermissionName(name)

  // 生成最终编码
  let code = ''
  if (module && action) {
    code = `${module}:${action}`
  } else if (module) {
    code = module
  } else {
    code = 'permission_' + Date.now()
  }

  // 清理编码：只保留字母、数字、冒号和下划线
  code = code.replace(/[^a-z0-9:_]/g, '')

  return code
}

// 生成权限描述
const generateDescription = () => {
  const name = formData.value.quanxian_ming.trim()
  if (!name) return ''

  const { actionChinese, moduleChinese } = analyzePermissionName(name)

  if (actionChinese && moduleChinese) {
    return `允许用户${actionChinese}${moduleChinese}相关信息`
  } else if (name) {
    return `${name}的权限`
  }

  return ''
}

// 推荐资源类型
const recommendResourceType = () => {
  const name = formData.value.quanxian_ming.trim()
  if (!name) return 'api'

  // 菜单相关关键词
  const menuKeywords = ['页面', '菜单', '访问', '进入', '打开', '列表', '管理']
  // 按钮相关关键词
  const buttonKeywords = ['创建', '新增', '编辑', '修改', '删除', '导出', '导入', '审核', '审批', '启用', '禁用', '分配']

  // 检查是否包含菜单关键词
  for (const keyword of menuKeywords) {
    if (name.includes(keyword)) {
      return 'menu'
    }
  }

  // 检查是否包含按钮关键词
  for (const keyword of buttonKeywords) {
    if (name.includes(keyword)) {
      return 'button'
    }
  }

  // 默认为API
  return 'api'
}

// 生成资源路径
const generateResourcePath = () => {
  const name = formData.value.quanxian_ming.trim()
  const resourceType = formData.value.ziyuan_leixing
  if (!name) return ''

  const { module, action } = analyzePermissionName(name)

  if (resourceType === 'menu') {
    // 菜单路径：/模块名
    return `/${module}`
  } else if (resourceType === 'button') {
    // 按钮路径：模块名-操作
    return `${module}-${action}`
  } else if (resourceType === 'api') {
    // API路径：/api/v1/模块名
    return `/${module}`
  }

  return ''
}

// 自动填充所有字段
const autoFillAll = () => {
  const name = formData.value.quanxian_ming.trim()
  if (!name) {
    ElMessage.warning('请先输入权限名称')
    return
  }

  // 生成权限编码
  const code = generateCode()
  formData.value.quanxian_bianma = code

  // 生成权限描述
  if (!formData.value.miaoshu) {
    formData.value.miaoshu = generateDescription()
  }

  // 推荐资源类型
  if (!formData.value.ziyuan_leixing) {
    formData.value.ziyuan_leixing = recommendResourceType()
  }

  // 生成资源路径
  if (!formData.value.ziyuan_lujing) {
    formData.value.ziyuan_lujing = generateResourcePath()
  }

  ElMessage.success('已自动填充所有字段')
}

// 处理权限名称输入
const handleNameInput = () => {
  // 只在创建模式时自动填充
  if (props.mode === 'create') {
    // 自动生成编码
    if (!formData.value.quanxian_bianma) {
      formData.value.quanxian_bianma = generateCode()
    }

    // 自动生成描述
    if (!formData.value.miaoshu) {
      formData.value.miaoshu = generateDescription()
    }

    // 自动推荐资源类型
    if (!formData.value.ziyuan_leixing) {
      formData.value.ziyuan_leixing = recommendResourceType()
    }

    // 自动生成资源路径
    if (!formData.value.ziyuan_lujing) {
      formData.value.ziyuan_lujing = generateResourcePath()
    }
  }
}

// 处理资源类型变化
const handleResourceTypeChange = () => {
  // 资源类型变化时，重新生成资源路径
  if (props.mode === 'create' && formData.value.quanxian_ming) {
    formData.value.ziyuan_lujing = generateResourcePath()
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    quanxian_ming: '',
    quanxian_bianma: '',
    miaoshu: '',
    ziyuan_leixing: '',
    ziyuan_lujing: '',
    zhuangtai: 'active'
  }
  formRef.value?.clearValidate()
}

// 监听权限数据变化
watch(() => props.permission, (newPermission) => {
  if (newPermission) {
    formData.value = {
      quanxian_ming: newPermission.quanxian_ming || '',
      quanxian_bianma: newPermission.quanxian_bianma || '',
      miaoshu: newPermission.miaoshu || '',
      ziyuan_leixing: newPermission.ziyuan_leixing || '',
      ziyuan_lujing: newPermission.ziyuan_lujing || '',
      zhuangtai: newPermission.zhuangtai || 'active'
    }
  } else {
    resetForm()
  }
}, { immediate: true })

// 处理关闭
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    // 调用API创建或更新权限
    if (props.mode === 'create') {
      await permissionStore.createPermission(formData.value)
      ElMessage.success('权限创建成功')
    } else {
      await permissionStore.updatePermission(props.permission!.id, formData.value)
      ElMessage.success('权限更新成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('权限操作失败:', error)
    ElMessage.error(props.mode === 'create' ? '权限创建失败' : '权限更新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-item small {
  margin-left: auto;
  color: #909399;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  font-size: 14px;
}
</style>
