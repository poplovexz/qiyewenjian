<template>
  <div class="contract-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑合同' : '新建合同' }}</span>
          <el-button @click="handleBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        v-loading="loading"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同名称" prop="hetong_mingcheng">
              <el-input
                v-model="formData.hetong_mingcheng"
                placeholder="请输入合同名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同类型" prop="hetong_leixing">
              <el-select
                v-model="formData.hetong_leixing"
                placeholder="请选择合同类型"
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
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同模板" prop="moban_id">
              <el-select
                v-model="formData.moban_id"
                placeholder="请选择合同模板"
                style="width: 100%"
                @change="handleTemplateChange"
                clearable
              >
                <el-option
                  v-for="template in templates"
                  :key="template.id"
                  :label="template.moban_mingcheng"
                  :value="template.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联报价" prop="baojia_id">
              <el-select
                v-model="formData.baojia_id"
                placeholder="请选择关联报价"
                style="width: 100%"
                clearable
                filterable
              >
                <el-option
                  v-for="quote in quotes"
                  :key="quote.id"
                  :label="`${quote.baojia_bianhao} - ${quote.baojia_mingcheng}`"
                  :value="quote.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="乙方主体" prop="yifang_zhuti_id">
              <el-select
                v-model="formData.yifang_zhuti_id"
                placeholder="请选择乙方主体"
                style="width: 100%"
                clearable
              >
                <el-option
                  v-for="party in parties"
                  :key="party.id"
                  :label="party.zhuti_mingcheng"
                  :value="party.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同金额" prop="hetong_jine">
              <el-input-number
                v-model="formData.hetong_jine"
                placeholder="请输入合同金额"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="签订日期" prop="qianding_riqi">
              <el-date-picker
                v-model="formData.qianding_riqi"
                type="date"
                placeholder="请选择签订日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="生效日期" prop="shengxiao_riqi">
              <el-date-picker
                v-model="formData.shengxiao_riqi"
                type="date"
                placeholder="请选择生效日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="结束日期" prop="jieshu_riqi">
              <el-date-picker
                v-model="formData.jieshu_riqi"
                type="date"
                placeholder="请选择结束日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="合同内容" prop="hetong_neirong">
          <div class="content-editor">
            <div class="editor-toolbar">
              <el-button
                v-if="formData.moban_id"
                type="primary"
                size="small"
                @click="previewTemplate"
                :loading="previewing"
              >
                <el-icon><View /></el-icon>
                预览模板
              </el-button>
            </div>
            <el-input
              v-model="formData.hetong_neirong"
              type="textarea"
              placeholder="请输入合同内容"
              :rows="15"
              maxlength="10000"
              show-word-limit
            />
          </div>
        </el-form-item>

        <el-form-item label="备注" prop="beizhu">
          <el-input
            v-model="formData.beizhu"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <el-button @click="handleBack">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving"> 保存 </el-button>
            <el-button v-if="!isEdit" type="success" @click="handleSaveAndSign" :loading="saving">
              保存并签署
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 模板预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="模板预览"
      width="80%"
      :close-on-click-modal="false"
    >
      <div class="template-preview" v-html="sanitizeContractHtml(previewContent)"></div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="previewDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="useTemplateContent"> 使用此内容 </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, View } from '@element-plus/icons-vue'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { useContractStore } from '@/stores/modules/contract'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import {
  contractTypeOptions,
  type ContractCreate,
  type ContractUpdate,
} from '@/api/modules/contract'
import { sanitizeContractHtml } from '@/utils/sanitize'

const route = useRoute()
const router = useRouter()
const contractStore = useContractManagementStore()
const templateStore = useContractStore()
const xiansuoStore = useXiansuoStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const previewing = ref(false)
const previewDialogVisible = ref(false)
const previewContent = ref('')

// 表单数据
const formData = reactive<ContractCreate>({
  hetong_mingcheng: '',
  hetong_leixing: '',
  moban_id: '',
  baojia_id: '',
  yifang_zhuti_id: '',
  hetong_neirong: '',
  hetong_jine: 0,
  qianding_riqi: '',
  shengxiao_riqi: '',
  jieshu_riqi: '',
  beizhu: '',
})

// 表单验证规则
const formRules: FormRules = {
  hetong_mingcheng: [{ required: true, message: '请输入合同名称', trigger: 'blur' }],
  hetong_leixing: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
  hetong_neirong: [{ required: true, message: '请输入合同内容', trigger: 'blur' }],
}

// 计算属性
const isEdit = computed(() => Boolean(route.params.id))
const templates = computed(() => templateStore.templates)
const parties = computed(() => contractStore.parties)
const quotes = computed(() => xiansuoStore.quotes)

// 方法
const fetchInitialData = async () => {
  try {
    loading.value = true

    // 获取合同模板列表
    await templateStore.fetchTemplates({ moban_zhuangtai: 'active' })

    // 获取乙方主体列表
    await contractStore.fetchParties()

    // 获取报价列表
    await xiansuoStore.fetchQuotes({ zhuangtai: 'accepted' })

    // 如果是编辑模式，获取合同详情
    if (isEdit.value) {
      const contractId = route.params.id as string
      await contractStore.fetchContractDetail(contractId)

      const contract = contractStore.currentContract
      if (contract) {
        Object.assign(formData, {
          hetong_mingcheng: contract.hetong_mingcheng,
          hetong_leixing: contract.hetong_leixing,
          moban_id: contract.moban_id || '',
          baojia_id: contract.baojia_id || '',
          yifang_zhuti_id: contract.yifang_zhuti_id || '',
          hetong_neirong: contract.hetong_neirong,
          hetong_jine: contract.hetong_jine || 0,
          qianding_riqi: contract.qianding_riqi || '',
          shengxiao_riqi: contract.shengxiao_riqi || '',
          jieshu_riqi: contract.jieshu_riqi || '',
          beizhu: contract.beizhu || '',
        })
      }
    } else {
      // 如果是创建模式且有报价ID，自动填充报价信息
      const baojiaId = route.query.baojia_id as string
      if (baojiaId) {
        formData.baojia_id = baojiaId

        // 获取报价详情并自动填充
        const quote = quotes.value.find((q) => q.id === baojiaId)
        if (quote) {
          formData.hetong_mingcheng = `${quote.baojia_mingcheng} - 服务合同`
          formData.hetong_leixing = 'daili_jizhang' // 默认代理记账
          formData.hetong_jine = quote.zongjia

          // 设置默认日期
          const today = new Date()
          formData.qianding_riqi = today.toISOString().split('T')[0]
          formData.shengxiao_riqi = today.toISOString().split('T')[0]

          // 设置结束日期为一年后
          const nextYear = new Date(today)
          nextYear.setFullYear(nextYear.getFullYear() + 1)
          formData.jieshu_riqi = nextYear.toISOString().split('T')[0]
        }
      }
    }
  } catch (error) {
    ElMessage.error('获取初始数据失败')
  } finally {
    loading.value = false
  }
}

const handleTemplateChange = async (templateId: string) => {
  if (!templateId) return

  try {
    // 获取模板变量配置
    const variables = await templateStore.getTemplateVariables(templateId)
  } catch (error) {}
}

const previewTemplate = async () => {
  if (!formData.moban_id) {
    ElMessage.warning('请先选择合同模板')
    return
  }

  try {
    previewing.value = true

    // 构建变量数据
    const variables: Record<string, any> = {}

    // 如果有关联报价，从报价中获取变量
    if (formData.baojia_id) {
      const quote = quotes.value.find((q) => q.id === formData.baojia_id)
      if (quote) {
        variables.baojia_bianhao = quote.baojia_bianhao
        variables.baojia_mingcheng = quote.baojia_mingcheng
        variables.baojia_jine = quote.zongjia
      }
    }

    // 如果有乙方主体，从主体中获取变量
    if (formData.yifang_zhuti_id) {
      const party = parties.value.find((p) => p.id === formData.yifang_zhuti_id)
      if (party) {
        variables.yifang_mingcheng = party.zhuti_mingcheng
        variables.yifang_lianxi_dianhua = party.lianxi_dianhua
        variables.yifang_zhuce_dizhi = party.zhuce_dizhi
      }
    }

    // 添加合同基本信息
    variables.hetong_mingcheng = formData.hetong_mingcheng
    variables.hetong_jine = formData.hetong_jine
    variables.qianding_riqi = formData.qianding_riqi
    variables.shengxiao_riqi = formData.shengxiao_riqi
    variables.jieshu_riqi = formData.jieshu_riqi

    const content = await templateStore.previewTemplate(formData.moban_id, variables)
    previewContent.value = content
    previewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('预览模板失败')
  } finally {
    previewing.value = false
  }
}

const useTemplateContent = () => {
  formData.hetong_neirong = previewContent.value
  previewDialogVisible.value = false
  ElMessage.success('已应用模板内容')
}

const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    if (isEdit.value) {
      const contractId = route.params.id as string
      await contractStore.updateContract(contractId, formData as ContractUpdate)
      ElMessage.success('合同更新成功')
    } else {
      const contract = await contractStore.createContract(formData)
      ElMessage.success('合同创建成功')
      router.push(`/contracts/${contract.id}`)
      return
    }

    handleBack()
  } catch (error) {
    if (error !== false) {
      // 不是表单验证错误
      ElMessage.error('保存合同失败')
    }
  } finally {
    saving.value = false
  }
}

const handleSaveAndSign = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    const contract = await contractStore.createContract({
      ...formData,
      hetong_zhuangtai: 'pending_signature',
    })

    ElMessage.success('合同创建成功')
    router.push(`/contracts/${contract.id}`)
  } catch (error) {
    if (error !== false) {
      // 不是表单验证错误
      ElMessage.error('保存合同失败')
    }
  } finally {
    saving.value = false
  }
}

const handleBack = () => {
  router.back()
}

// 生命周期
onMounted(() => {
  fetchInitialData()
})
</script>

<style scoped>
.contract-form {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-editor {
  width: 100%;
}

.editor-toolbar {
  margin-bottom: 10px;
  display: flex;
  gap: 10px;
}

.form-actions {
  display: flex;
  gap: 10px;
}

.template-preview {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 20px;
  background-color: #fafafa;
  min-height: 400px;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
