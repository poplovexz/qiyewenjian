<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      :disabled="mode === 'view'"
    >
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="公司名称" prop="gongsi_mingcheng">
                <el-input v-model="formData.gongsi_mingcheng" placeholder="请输入公司名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="统一社会信用代码" prop="tongyi_shehui_xinyong_daima">
                <el-input v-model="formData.tongyi_shehui_xinyong_daima" placeholder="请输入18位信用代码" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="成立日期" prop="chengli_riqi">
                <el-date-picker
                  v-model="formData.chengli_riqi"
                  type="date"
                  placeholder="选择成立日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="客户状态" prop="kehu_zhuangtai">
                <el-select v-model="formData.kehu_zhuangtai" placeholder="选择客户状态" style="width: 100%">
                  <el-option label="活跃" value="active" />
                  <el-option label="续约中" value="renewing" />
                  <el-option label="已终止" value="terminated" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="注册地址" prop="zhuce_dizhi">
            <el-input
              v-model="formData.zhuce_dizhi"
              type="textarea"
              :rows="2"
              placeholder="请输入注册地址"
            />
          </el-form-item>
        </el-tab-pane>

        <!-- 法人信息 -->
        <el-tab-pane label="法人信息" name="legal">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="法人姓名" prop="faren_xingming">
                <el-input v-model="formData.faren_xingming" placeholder="请输入法人姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="法人身份证" prop="faren_shenfenzheng">
                <el-input v-model="formData.faren_shenfenzheng" placeholder="请输入18位身份证号" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="法人联系方式" prop="faren_lianxi">
            <el-input v-model="formData.faren_lianxi" placeholder="请输入法人联系方式" />
          </el-form-item>
        </el-tab-pane>

        <!-- 联系信息 -->
        <el-tab-pane label="联系信息" name="contact">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="联系电话" prop="lianxi_dianhua">
                <el-input v-model="formData.lianxi_dianhua" placeholder="请输入联系电话" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系邮箱" prop="lianxi_youxiang">
                <el-input v-model="formData.lianxi_youxiang" placeholder="请输入联系邮箱" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="联系地址" prop="lianxi_dizhi">
            <el-input
              v-model="formData.lianxi_dizhi"
              type="textarea"
              :rows="2"
              placeholder="请输入联系地址"
            />
          </el-form-item>
        </el-tab-pane>

        <!-- 服务信息 -->
        <el-tab-pane label="服务信息" name="service">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="服务开始日期" prop="fuwu_kaishi_riqi">
                <el-date-picker
                  v-model="formData.fuwu_kaishi_riqi"
                  type="date"
                  placeholder="选择服务开始日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="服务结束日期" prop="fuwu_jieshu_riqi">
                <el-date-picker
                  v-model="formData.fuwu_jieshu_riqi"
                  type="date"
                  placeholder="选择服务结束日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="营业执照路径" prop="yingye_zhizhao_lujing">
                <el-input v-model="formData.yingye_zhizhao_lujing" placeholder="营业执照文件路径" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="营业执照有效期" prop="yingye_zhizhao_youxiao_qi">
                <el-date-picker
                  v-model="formData.yingye_zhizhao_youxiao_qi"
                  type="date"
                  placeholder="选择有效期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button v-if="mode !== 'view'" type="primary" :loading="loading" @click="handleSubmit">
          {{ mode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useCustomerStore } from '@/stores/modules/customer'
import type { Customer, CustomerCreate, CustomerUpdate } from '@/api/modules/customer'

interface Props {
  visible: boolean
  customer?: Customer | null
  mode: 'create' | 'edit' | 'view'
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  customer: null,
  mode: 'create'
})

const emit = defineEmits<Emits>()

const customerStore = useCustomerStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const activeTab = ref('basic')

// 表单数据
const formData = ref<CustomerCreate>({
  gongsi_mingcheng: '',
  tongyi_shehui_xinyong_daima: '',
  chengli_riqi: '',
  zhuce_dizhi: '',
  faren_xingming: '',
  faren_shenfenzheng: '',
  faren_lianxi: '',
  lianxi_dianhua: '',
  lianxi_youxiang: '',
  lianxi_dizhi: '',
  yingye_zhizhao_lujing: '',
  yingye_zhizhao_youxiao_qi: '',
  kehu_zhuangtai: 'active',
  fuwu_kaishi_riqi: '',
  fuwu_jieshu_riqi: ''
})

// 表单验证规则
const formRules: FormRules = {
  gongsi_mingcheng: [
    { required: true, message: '请输入公司名称', trigger: 'blur' }
  ],
  tongyi_shehui_xinyong_daima: [
    { required: true, message: '请输入统一社会信用代码', trigger: 'blur' },
    { len: 18, message: '统一社会信用代码必须为18位', trigger: 'blur' },
    { pattern: /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/, message: '统一社会信用代码格式不正确', trigger: 'blur' }
  ],
  faren_xingming: [
    { required: true, message: '请输入法人姓名', trigger: 'blur' }
  ],
  faren_shenfenzheng: [
    { pattern: /^\d{17}[\dXx]$/, message: '身份证号码格式不正确', trigger: 'blur' }
  ],
  lianxi_youxiang: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  kehu_zhuangtai: [
    { required: true, message: '请选择客户状态', trigger: 'change' }
  ]
}

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  const titleMap = {
    create: '新增客户',
    edit: '编辑客户',
    view: '查看客户'
  }
  return titleMap[props.mode]
})

// 方法
const resetForm = () => {
  formData.value = {
    gongsi_mingcheng: '',
    tongyi_shehui_xinyong_daima: '',
    chengli_riqi: '',
    zhuce_dizhi: '',
    faren_xingming: '',
    faren_shenfenzheng: '',
    faren_lianxi: '',
    lianxi_dianhua: '',
    lianxi_youxiang: '',
    lianxi_dizhi: '',
    yingye_zhizhao_lujing: '',
    yingye_zhizhao_youxiao_qi: '',
    kehu_zhuangtai: 'active',
    fuwu_kaishi_riqi: '',
    fuwu_jieshu_riqi: ''
  }

  // 清除表单验证
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

// 监听客户数据变化
watch(
  () => props.customer,
  (customer) => {
    if (customer) {
      // 编辑或查看模式，填充表单数据
      Object.assign(formData.value, {
        gongsi_mingcheng: customer.gongsi_mingcheng,
        tongyi_shehui_xinyong_daima: customer.tongyi_shehui_xinyong_daima,
        chengli_riqi: customer.chengli_riqi || '',
        zhuce_dizhi: customer.zhuce_dizhi || '',
        faren_xingming: customer.faren_xingming,
        faren_shenfenzheng: customer.faren_shenfenzheng || '',
        faren_lianxi: customer.faren_lianxi || '',
        lianxi_dianhua: customer.lianxi_dianhua || '',
        lianxi_youxiang: customer.lianxi_youxiang || '',
        lianxi_dizhi: customer.lianxi_dizhi || '',
        yingye_zhizhao_lujing: customer.yingye_zhizhao_lujing || '',
        yingye_zhizhao_youxiao_qi: customer.yingye_zhizhao_youxiao_qi || '',
        kehu_zhuangtai: customer.kehu_zhuangtai,
        fuwu_kaishi_riqi: customer.fuwu_kaishi_riqi || '',
        fuwu_jieshu_riqi: customer.fuwu_jieshu_riqi || ''
      })
    } else {
      // 新增模式，重置表单
      resetForm()
    }
  },
  { immediate: true }
)

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    if (props.mode === 'create') {
      await customerStore.createCustomer(formData.value)
    } else if (props.mode === 'edit' && props.customer) {
      await customerStore.updateCustomer(props.customer.id, formData.value as CustomerUpdate)
    }
    
    emit('success')
  } catch (error) {
    console.error('表单提交失败:', error)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  activeTab.value = 'basic'
  if (props.mode === 'create') {
    resetForm()
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
