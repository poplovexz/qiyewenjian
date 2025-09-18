<template>
  <div class="contract-party-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑乙方主体' : '新建乙方主体' }}</span>
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
            <el-form-item label="主体名称" prop="zhuti_mingcheng">
              <el-input
                v-model="formData.zhuti_mingcheng"
                placeholder="请输入主体名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主体类型" prop="zhuti_leixing">
              <el-select
                v-model="formData.zhuti_leixing"
                placeholder="请选择主体类型"
                style="width: 100%"
              >
                <el-option
                  v-for="option in partyTypeOptions"
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
            <el-form-item label="统一社会信用代码" prop="tongyi_shehui_xinyong_daima">
              <el-input
                v-model="formData.tongyi_shehui_xinyong_daima"
                placeholder="请输入统一社会信用代码"
                maxlength="18"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="营业执照号码" prop="yingyezhizhao_haoma">
              <el-input
                v-model="formData.yingyezhizhao_haoma"
                placeholder="请输入营业执照号码"
                maxlength="20"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="法人代表" prop="faren_daibiao">
              <el-input
                v-model="formData.faren_daibiao"
                placeholder="请输入法人代表"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="lianxi_dianhua">
              <el-input
                v-model="formData.lianxi_dianhua"
                placeholder="请输入联系电话"
                maxlength="20"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="联系邮箱" prop="lianxi_youxiang">
              <el-input
                v-model="formData.lianxi_youxiang"
                placeholder="请输入联系邮箱"
                maxlength="100"
                type="email"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="注册地址" prop="zhuce_dizhi">
              <el-input
                v-model="formData.zhuce_dizhi"
                placeholder="请输入注册地址"
                maxlength="200"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">银行信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="银行名称" prop="yinhang_mingcheng">
              <el-input
                v-model="formData.yinhang_mingcheng"
                placeholder="请输入银行名称"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账户" prop="yinhang_zhanghu">
              <el-input
                v-model="formData.yinhang_zhanghu"
                placeholder="请输入银行账户"
                maxlength="30"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="开户行" prop="yinhang_kaihuhang">
              <el-input
                v-model="formData.yinhang_kaihuhang"
                placeholder="请输入开户行"
                maxlength="200"
              />
            </el-form-item>
          </el-col>
        </el-row>

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
            <el-button 
              type="primary" 
              @click="handleSave"
              :loading="saving"
            >
              保存
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { partyTypeOptions, type ContractPartyCreate, type ContractPartyUpdate } from '@/api/modules/contract'

const route = useRoute()
const router = useRouter()
const contractStore = useContractManagementStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)

// 表单数据
const formData = reactive<ContractPartyCreate>({
  zhuti_mingcheng: '',
  zhuti_leixing: '',
  tongyi_shehui_xinyong_daima: '',
  yingyezhizhao_haoma: '',
  faren_daibiao: '',
  lianxi_dianhua: '',
  lianxi_youxiang: '',
  zhuce_dizhi: '',
  yinhang_mingcheng: '',
  yinhang_zhanghu: '',
  yinhang_kaihuhang: '',
  beizhu: ''
})

// 表单验证规则
const formRules: FormRules = {
  zhuti_mingcheng: [
    { required: true, message: '请输入主体名称', trigger: 'blur' }
  ],
  zhuti_leixing: [
    { required: true, message: '请选择主体类型', trigger: 'change' }
  ],
  lianxi_dianhua: [
    { pattern: /^1[3-9]\d{9}$|^0\d{2,3}-?\d{7,8}$/, message: '请输入正确的电话号码', trigger: 'blur' }
  ],
  lianxi_youxiang: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  tongyi_shehui_xinyong_daima: [
    { pattern: /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/, message: '请输入正确的统一社会信用代码', trigger: 'blur' }
  ]
}

// 计算属性
const isEdit = computed(() => !!route.params.id)

// 方法
const fetchPartyDetail = async () => {
  if (isEdit.value) {
    const partyId = route.params.id as string
    try {
      loading.value = true
      await contractStore.fetchPartyDetail(partyId)
      
      const party = contractStore.currentParty
      if (party) {
        Object.assign(formData, {
          zhuti_mingcheng: party.zhuti_mingcheng,
          zhuti_leixing: party.zhuti_leixing,
          tongyi_shehui_xinyong_daima: party.tongyi_shehui_xinyong_daima || '',
          yingyezhizhao_haoma: party.yingyezhizhao_haoma || '',
          faren_daibiao: party.faren_daibiao || '',
          lianxi_dianhua: party.lianxi_dianhua || '',
          lianxi_youxiang: party.lianxi_youxiang || '',
          zhuce_dizhi: party.zhuce_dizhi || '',
          yinhang_mingcheng: party.yinhang_mingcheng || '',
          yinhang_zhanghu: party.yinhang_zhanghu || '',
          yinhang_kaihuhang: party.yinhang_kaihuhang || '',
          beizhu: party.beizhu || ''
        })
      }
    } catch (error) {
      console.error('获取主体详情失败:', error)
      ElMessage.error('获取主体详情失败')
    } finally {
      loading.value = false
    }
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    if (isEdit.value) {
      const partyId = route.params.id as string
      await contractStore.updateParty(partyId, formData as ContractPartyUpdate)
      ElMessage.success('乙方主体更新成功')
    } else {
      await contractStore.createParty(formData)
      ElMessage.success('乙方主体创建成功')
    }
    
    handleBack()
  } catch (error) {
    console.error('保存乙方主体失败:', error)
    if (error !== false) { // 不是表单验证错误
      ElMessage.error('保存乙方主体失败')
    }
  } finally {
    saving.value = false
  }
}

const handleBack = () => {
  router.push('/contract-parties')
}

// 生命周期
onMounted(() => {
  fetchPartyDetail()
})
</script>

<style scoped>
.contract-party-form {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-actions {
  display: flex;
  gap: 10px;
}
</style>
