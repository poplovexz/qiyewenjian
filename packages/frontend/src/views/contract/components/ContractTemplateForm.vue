<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    :title="dialogTitle"
    width="1000px"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      v-loading="submitting"
    >
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="模板名称" prop="moban_mingcheng">
                <el-input
                  v-model="formData.moban_mingcheng"
                  placeholder="请输入模板名称"
                  :disabled="mode === 'view'"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="模板编码" prop="moban_bianma">
                <el-input
                  v-model="formData.moban_bianma"
                  placeholder="请输入模板编码"
                  :disabled="mode === 'view'"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="合同类型" prop="hetong_leixing">
                <el-select
                  v-model="formData.hetong_leixing"
                  placeholder="请选择合同类型"
                  :disabled="mode === 'view'"
                  style="width: 100%"
                >
                  <el-option
                    v-for="option in contractTypeOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="版本号" prop="banben_hao">
                <el-input
                  v-model="formData.banben_hao"
                  placeholder="请输入版本号"
                  :disabled="mode === 'view'"
                  maxlength="20"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="模板分类">
                <el-select
                  v-model="formData.moban_fenlei"
                  placeholder="请选择模板分类"
                  :disabled="mode === 'view'"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="option in templateCategoryOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="模板状态">
                <el-select
                  v-model="formData.moban_zhuangtai"
                  placeholder="请选择模板状态"
                  :disabled="mode === 'view'"
                  style="width: 100%"
                >
                  <el-option
                    v-for="option in templateStatusOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="当前版本">
                <el-radio-group v-model="formData.shi_dangqian_banben" :disabled="mode === 'view'">
                  <el-radio label="Y">是</el-radio>
                  <el-radio label="N">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="排序号">
                <el-input-number
                  v-model="formData.paixu"
                  :min="0"
                  :max="9999"
                  :disabled="mode === 'view'"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="备注">
            <el-input
              v-model="formData.beizhu"
              type="textarea"
              :rows="3"
              placeholder="请输入备注信息"
              :disabled="mode === 'view'"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-tab-pane>

        <!-- 模板内容 -->
        <el-tab-pane label="模板内容" name="content">
          <el-form-item label="模板内容" prop="moban_neirong">
            <div class="editor-container">
              <div class="editor-toolbar">
                <el-button size="small" @click="insertVariable" :disabled="mode === 'view'">
                  插入变量
                </el-button>
                <el-button size="small" @click="showVariableHelp"> 变量说明 </el-button>
              </div>

              <!-- 富文本编辑器 -->
              <el-input
                v-model="formData.moban_neirong"
                type="textarea"
                :rows="15"
                placeholder="请输入合同模板内容，可使用 {{变量名}} 格式插入变量"
                :disabled="mode === 'view'"
                class="content-editor"
              />
            </div>
          </el-form-item>
        </el-tab-pane>

        <!-- 变量配置 -->
        <el-tab-pane label="变量配置" name="variables">
          <el-form-item label="变量配置">
            <div class="variables-container">
              <div class="variables-help">
                <el-alert title="变量配置说明" type="info" :closable="false" show-icon>
                  <template #default>
                    <p>在此配置模板中可用的变量，格式为JSON。例如：</p>
                    <pre>{{ variableExample }}</pre>
                  </template>
                </el-alert>
              </div>

              <el-input
                v-model="formData.bianliang_peizhi"
                type="textarea"
                :rows="10"
                placeholder="请输入变量配置（JSON格式）"
                :disabled="mode === 'view'"
                class="variables-editor"
              />
            </div>
          </el-form-item>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="mode !== 'view'"
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
        >
          {{ mode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>

    <!-- 变量插入对话框 -->
    <el-dialog v-model="variableDialogVisible" title="插入变量" width="500px">
      <el-form label-width="100px">
        <el-form-item label="变量名称">
          <el-input v-model="newVariableName" placeholder="请输入变量名称" />
        </el-form-item>
        <el-form-item label="变量描述">
          <el-input v-model="newVariableDesc" placeholder="请输入变量描述" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="variableDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmInsertVariable">插入</el-button>
      </template>
    </el-dialog>

    <!-- 变量说明对话框 -->
    <el-dialog v-model="helpDialogVisible" title="变量使用说明" width="600px">
      <div class="help-content">
        <h4>常用变量</h4>
        <el-table :data="commonVariables" size="small">
          <el-table-column prop="name" label="变量名" width="150" />
          <el-table-column prop="desc" label="说明" />
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="insertCommonVariable(row.name)">
                插入
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <h4 style="margin-top: 20px">使用说明</h4>
        <ul>
          <li>
            在模板内容中使用 <code>{{ 变量名 }}</code> 格式插入变量
          </li>
          <li>变量名区分大小写，建议使用下划线命名</li>
          <li>可在变量配置中定义变量的默认值和类型</li>
          <li>预览时会自动替换变量为实际值</li>
        </ul>
      </div>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useContractStore } from '@/stores/modules/contract'
import {
  contractTypeOptions,
  templateStatusOptions,
  templateCategoryOptions,
  type ContractTemplate,
  type ContractTemplateCreate,
  type ContractTemplateUpdate,
} from '@/api/modules/contract'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
  template?: ContractTemplate | null
}

const props = withDefaults(defineProps<Props>(), {
  template: null,
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// Store
const contractStore = useContractStore()

// 响应式数据
const formRef = ref()
const submitting = ref(false)
const activeTab = ref('basic')
const variableDialogVisible = ref(false)
const helpDialogVisible = ref(false)
const newVariableName = ref('')
const newVariableDesc = ref('')

const formData = reactive({
  moban_mingcheng: '',
  moban_bianma: '',
  hetong_leixing: '',
  moban_neirong: '',
  bianliang_peizhi: '',
  banben_hao: '1.0',
  shi_dangqian_banben: 'Y',
  moban_fenlei: '',
  moban_zhuangtai: 'draft',
  beizhu: '',
  paixu: 0,
})

// 表单验证规则
const formRules = {
  moban_mingcheng: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 1, max: 200, message: '模板名称长度在 1 到 200 个字符', trigger: 'blur' },
  ],
  moban_bianma: [
    { required: true, message: '请输入模板编码', trigger: 'blur' },
    { min: 1, max: 100, message: '模板编码长度在 1 到 100 个字符', trigger: 'blur' },
  ],
  hetong_leixing: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
  moban_neirong: [{ required: true, message: '请输入模板内容', trigger: 'blur' }],
}

// 变量配置示例
const variableExample = `{
  "kehu_mingcheng": {
    "label": "客户名称",
    "type": "string",
    "default": ""
  },
  "fuwu_neirong": {
    "label": "服务内容", 
    "type": "string",
    "default": "代理记账服务"
  },
  "fuwu_jiage": {
    "label": "服务价格",
    "type": "number",
    "default": 0
  }
}`

// 常用变量
const commonVariables = [
  { name: 'kehu_mingcheng', desc: '客户名称' },
  { name: 'kehu_dizhi', desc: '客户地址' },
  { name: 'kehu_lianxi', desc: '客户联系方式' },
  { name: 'fuwu_neirong', desc: '服务内容' },
  { name: 'fuwu_jiage', desc: '服务价格' },
  { name: 'hetong_qixian', desc: '合同期限' },
  { name: 'qianyue_riqi', desc: '签约日期' },
  { name: 'shengxiao_riqi', desc: '生效日期' },
]

// 计算属性
const dialogTitle = computed(() => {
  const titleMap = {
    create: '新建合同模板',
    edit: '编辑合同模板',
    view: '查看合同模板',
  }
  return titleMap[props.mode]
})

// 监听器
watch(
  () => props.visible,
  (visible) => {
    if (visible && props.template) {
      // 编辑或查看模式，填充表单数据
      Object.assign(formData, {
        moban_mingcheng: props.template.moban_mingcheng,
        moban_bianma: props.template.moban_bianma,
        hetong_leixing: props.template.hetong_leixing,
        moban_neirong: props.template.moban_neirong,
        bianliang_peizhi: props.template.bianliang_peizhi || '',
        banben_hao: props.template.banben_hao,
        shi_dangqian_banben: props.template.shi_dangqian_banben,
        moban_fenlei: props.template.moban_fenlei || '',
        moban_zhuangtai: props.template.moban_zhuangtai,
        beizhu: props.template.beizhu || '',
        paixu: props.template.paixu,
      })
    } else if (visible) {
      // 新建模式，重置表单
      resetForm()
    }
  }
)

// 方法
const resetForm = () => {
  Object.assign(formData, {
    moban_mingcheng: '',
    moban_bianma: '',
    hetong_leixing: '',
    moban_neirong: '',
    bianliang_peizhi: '',
    banben_hao: '1.0',
    shi_dangqian_banben: 'Y',
    moban_fenlei: '',
    moban_zhuangtai: 'draft',
    beizhu: '',
    paixu: 0,
  })

  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const handleClose = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (props.mode === 'create') {
      // 创建合同模板
      const createData: ContractTemplateCreate = { ...formData }
      await contractStore.createTemplate(createData)
      ElMessage.success('合同模板创建成功')
    } else {
      // 更新合同模板
      const updateData: ContractTemplateUpdate = { ...formData }
      await contractStore.updateTemplate(props.template!.id, updateData)
      ElMessage.success('合同模板更新成功')
    }

    emit('success')
  } catch (error) {
  } finally {
    submitting.value = false
  }
}

const insertVariable = () => {
  newVariableName.value = ''
  newVariableDesc.value = ''
  variableDialogVisible.value = true
}

const confirmInsertVariable = () => {
  if (!newVariableName.value.trim()) {
    ElMessage.warning('请输入变量名称')
    return
  }

  const variable = `{{ ${newVariableName.value.trim()} }}`
  formData.moban_neirong += variable
  variableDialogVisible.value = false
}

const insertCommonVariable = (variableName: string) => {
  const variable = `{{ ${variableName} }}`
  formData.moban_neirong += variable
  helpDialogVisible.value = false
}

const showVariableHelp = () => {
  helpDialogVisible.value = true
}
</script>

<style scoped>
.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.editor-toolbar {
  padding: 8px 12px;
  border-bottom: 1px solid #dcdfe6;
  background-color: #f5f7fa;
  display: flex;
  gap: 8px;
}

.content-editor {
  border: none;
}

.content-editor :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  font-family: 'Courier New', monospace;
}

.variables-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.variables-help {
  padding: 12px;
  border-bottom: 1px solid #dcdfe6;
  background-color: #f5f7fa;
}

.variables-help pre {
  margin: 8px 0 0 0;
  padding: 8px;
  background-color: #f0f2f5;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

.variables-editor {
  border: none;
}

.variables-editor :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  font-family: 'Courier New', monospace;
}

.help-content h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.help-content ul {
  margin: 0;
  padding-left: 20px;
}

.help-content li {
  margin-bottom: 8px;
  color: #606266;
}

.help-content code {
  padding: 2px 4px;
  background-color: #f5f7fa;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}
</style>
