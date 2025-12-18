<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑服务工单' : '创建服务工单'"
    width="800px"
    @update:model-value="emit('update:visible', $event)"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="合同" prop="hetong_id">
            <el-select
              v-model="formData.hetong_id"
              placeholder="请选择合同"
              filterable
              style="width: 100%"
              @change="handleContractChange"
            >
              <el-option
                v-for="contract in contracts"
                :key="contract.id"
                :label="`${contract.hetong_bianhao} - ${contract.hetong_mingcheng}`"
                :value="contract.id"
              />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="客户" prop="kehu_id">
            <el-select
              v-model="formData.kehu_id"
              placeholder="请选择客户"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="customer in customers"
                :key="customer.id"
                :label="customer.gongsi_mingcheng"
                :value="customer.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="工单标题" prop="gongdan_biaoti">
            <el-input v-model="formData.gongdan_biaoti" placeholder="请输入工单标题" />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="服务类型" prop="fuwu_leixing">
            <el-select
              v-model="formData.fuwu_leixing"
              placeholder="请选择服务类型"
              style="width: 100%"
            >
              <el-option
                v-for="(label, value) in serviceOrderStore.serviceTypeMap"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="优先级" prop="youxian_ji">
            <el-select v-model="formData.youxian_ji" placeholder="请选择优先级" style="width: 100%">
              <el-option
                v-for="(label, value) in serviceOrderStore.priorityMap"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="执行人" prop="zhixing_ren_id">
            <el-select
              v-model="formData.zhixing_ren_id"
              placeholder="请选择执行人"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.xingming"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="计划开始时间" prop="jihua_kaishi_shijian">
            <el-date-picker
              v-model="formData.jihua_kaishi_shijian"
              type="datetime"
              placeholder="请选择计划开始时间"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="计划结束时间" prop="jihua_jieshu_shijian">
            <el-date-picker
              v-model="formData.jihua_jieshu_shijian"
              type="datetime"
              placeholder="请选择计划结束时间"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="工单描述" prop="gongdan_miaoshu">
        <el-input
          v-model="formData.gongdan_miaoshu"
          type="textarea"
          :rows="3"
          placeholder="请输入工单描述"
        />
      </el-form-item>

      <el-form-item label="分配备注" prop="fenpei_beizhu">
        <el-input
          v-model="formData.fenpei_beizhu"
          type="textarea"
          :rows="2"
          placeholder="请输入分配备注"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  useServiceOrderStore,
  type ServiceOrderCreateData,
} from '@/stores/modules/serviceOrderManagement'

// Props
interface Props {
  visible: boolean
  orderId?: string
}

const props = withDefaults(defineProps<Props>(), {
  orderId: '',
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// Store
const serviceOrderStore = useServiceOrderStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const contracts = ref([])
const customers = ref([])
const users = ref([])

const formData = reactive<ServiceOrderCreateData>({
  hetong_id: '',
  kehu_id: '',
  zhixing_ren_id: '',
  gongdan_biaoti: '',
  gongdan_miaoshu: '',
  fuwu_leixing: 'daili_jizhang',
  youxian_ji: 'medium',
  jihua_kaishi_shijian: '',
  jihua_jieshu_shijian: '',
  fenpei_beizhu: '',
})

// 计算属性
const isEdit = computed(() => Boolean(props.orderId))

// 表单验证规则
const formRules: FormRules = {
  hetong_id: [{ required: true, message: '请选择合同', trigger: 'change' }],
  kehu_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
  gongdan_biaoti: [
    { required: true, message: '请输入工单标题', trigger: 'blur' },
    { min: 2, max: 200, message: '工单标题长度在 2 到 200 个字符', trigger: 'blur' },
  ],
  fuwu_leixing: [{ required: true, message: '请选择服务类型', trigger: 'change' }],
  youxian_ji: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  jihua_jieshu_shijian: [{ required: true, message: '请选择计划结束时间', trigger: 'change' }],
}

// 方法
const loadData = async () => {
  try {
    // 加载合同列表
    // contracts.value = await contractStore.fetchContracts({ status: 'signed' })

    // 加载客户列表
    // customers.value = await customerStore.fetchCustomers()

    // 加载用户列表
    // users.value = await userStore.fetchUsers()

    // 模拟数据
    contracts.value = []
    customers.value = []
    users.value = []
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const handleContractChange = (contractId: string) => {
  const contract = contracts.value.find((c) => c.id === contractId)
  if (contract) {
    formData.kehu_id = contract.kehu_id
    formData.gongdan_biaoti = `${contract.hetong_mingcheng} - 服务工单`
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    loading.value = true

    if (isEdit.value) {
      await serviceOrderStore.updateServiceOrder(props.orderId, formData)
    } else {
      await serviceOrderStore.createServiceOrder(formData)
    }

    emit('success')
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }

  Object.assign(formData, {
    hetong_id: '',
    kehu_id: '',
    zhixing_ren_id: '',
    gongdan_biaoti: '',
    gongdan_miaoshu: '',
    fuwu_leixing: 'daili_jizhang',
    youxian_ji: 'medium',
    jihua_kaishi_shijian: '',
    jihua_jieshu_shijian: '',
    fenpei_beizhu: '',
  })
}

// 监听
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      loadData()

      if (isEdit.value) {
        // 加载编辑数据
        serviceOrderStore.fetchServiceOrderDetail(props.orderId).then((order) => {
          Object.assign(formData, order)
        })
      }
    }
  }
)

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
