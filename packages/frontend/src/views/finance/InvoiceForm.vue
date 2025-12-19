<template>
  <div class="invoice-form-container">
    <el-card class="page-header">
      <div class="header-content">
        <h2>{{ isEdit ? '编辑开票申请' : '新建开票申请' }}</h2>
        <p>{{ isEdit ? '修改开票申请信息' : '创建新的开票申请' }}</p>
      </div>
    </el-card>

    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" v-loading="loading">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开票类型" prop="kaipiao_leixing">
              <el-select
                v-model="form.kaipiao_leixing"
                placeholder="请选择开票类型"
                style="width: 100%"
              >
                <el-option label="增值税专用发票" value="zengzhishui" />
                <el-option label="普通发票" value="putong" />
                <el-option label="电子发票" value="dianzifapiao" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开票名称" prop="kaipiao_mingcheng">
              <el-input v-model="form.kaipiao_mingcheng" placeholder="请输入开票名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="开票内容" prop="kaipiao_neirong">
          <el-input
            v-model="form.kaipiao_neirong"
            type="textarea"
            :rows="3"
            placeholder="请输入开票内容"
          />
        </el-form-item>

        <!-- 金额信息 -->
        <el-divider content-position="left">金额信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="开票金额" prop="kaipiao_jine">
              <el-input-number
                v-model="form.kaipiao_jine"
                :precision="2"
                :min="0"
                style="width: 100%"
                placeholder="请输入开票金额"
                @change="calculateTotal"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="税额" prop="shuie">
              <el-input-number
                v-model="form.shuie"
                :precision="2"
                :min="0"
                style="width: 100%"
                placeholder="请输入税额"
                @change="calculateTotal"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="价税合计" prop="jia_shui_jine">
              <el-input-number
                v-model="form.jia_shui_jine"
                :precision="2"
                :min="0"
                style="width: 100%"
                placeholder="自动计算"
                readonly
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 购物方信息 -->
        <el-divider content-position="left">购物方信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购物方名称" prop="gouwu_fang_mingcheng">
              <el-input v-model="form.gouwu_fang_mingcheng" placeholder="请输入购物方名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="购物方税号" prop="gouwu_fang_shuihao">
              <el-input v-model="form.gouwu_fang_shuihao" placeholder="请输入购物方税号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购物方地址" prop="gouwu_fang_dizhi">
              <el-input v-model="form.gouwu_fang_dizhi" placeholder="请输入购物方地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="购物方电话" prop="gouwu_fang_dianhua">
              <el-input v-model="form.gouwu_fang_dianhua" placeholder="请输入购物方电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户银行" prop="gouwu_fang_yinhang">
              <el-input v-model="form.gouwu_fang_yinhang" placeholder="请输入开户银行" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账户" prop="gouwu_fang_zhanghu">
              <el-input v-model="form.gouwu_fang_zhanghu" placeholder="请输入银行账户" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 销售方信息 -->
        <el-divider content-position="left">销售方信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="销售方名称" prop="xiaoshou_fang_mingcheng">
              <el-input v-model="form.xiaoshou_fang_mingcheng" placeholder="请输入销售方名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="销售方税号" prop="xiaoshou_fang_shuihao">
              <el-input v-model="form.xiaoshou_fang_shuihao" placeholder="请输入销售方税号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="销售方地址" prop="xiaoshou_fang_dizhi">
              <el-input v-model="form.xiaoshou_fang_dizhi" placeholder="请输入销售方地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="销售方电话" prop="xiaoshou_fang_dianhua">
              <el-input v-model="form.xiaoshou_fang_dianhua" placeholder="请输入销售方电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户银行" prop="xiaoshou_fang_yinhang">
              <el-input v-model="form.xiaoshou_fang_yinhang" placeholder="请输入开户银行" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账户" prop="xiaoshou_fang_zhanghu">
              <el-input v-model="form.xiaoshou_fang_zhanghu" placeholder="请输入银行账户" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 其他信息 -->
        <el-divider content-position="left">其他信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="要求开票时间" prop="yaoqiu_kaipiao_shijian">
              <el-date-picker
                v-model="form.yaoqiu_kaipiao_shijian"
                type="datetime"
                placeholder="选择要求开票时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户" prop="kehu_id">
              <el-select
                v-model="form.kehu_id"
                placeholder="请选择客户"
                style="width: 100%"
                filterable
              >
                <el-option
                  v-for="customer in customers"
                  :key="customer.id"
                  :label="customer.kehu_mingcheng"
                  :value="customer.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="beizhu">
          <el-input v-model="form.beizhu" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
          <el-button @click="handleSaveAsDraft" :loading="draftLoading"> 保存为草稿 </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 路由
const route = useRoute()
const router = useRouter()

// 响应式数据
const formRef = ref()
const loading = ref(false)
const submitLoading = ref(false)
const draftLoading = ref(false)
const customers = ref([])

const isEdit = computed(() => route.name === 'InvoiceEdit')
const invoiceId = computed(() => route.params.id as string)

const form = reactive({
  kehu_id: '',
  hetong_id: '',
  zhifu_dingdan_id: '',
  kaipiao_leixing: '',
  kaipiao_mingcheng: '',
  kaipiao_neirong: '',
  kaipiao_jine: 0,
  shuie: 0,
  jia_shui_jine: 0,
  gouwu_fang_mingcheng: '',
  gouwu_fang_shuihao: '',
  gouwu_fang_dizhi: '',
  gouwu_fang_dianhua: '',
  gouwu_fang_yinhang: '',
  gouwu_fang_zhanghu: '',
  xiaoshou_fang_mingcheng: '',
  xiaoshou_fang_shuihao: '',
  xiaoshou_fang_dizhi: '',
  xiaoshou_fang_dianhua: '',
  xiaoshou_fang_yinhang: '',
  xiaoshou_fang_zhanghu: '',
  yaoqiu_kaipiao_shijian: null,
  beizhu: '',
})

const rules = {
  kaipiao_leixing: [{ required: true, message: '请选择开票类型', trigger: 'change' }],
  kaipiao_mingcheng: [{ required: true, message: '请输入开票名称', trigger: 'blur' }],
  kaipiao_jine: [
    { required: true, message: '请输入开票金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '开票金额必须大于0', trigger: 'blur' },
  ],
  jia_shui_jine: [
    { required: true, message: '价税合计不能为空', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '价税合计必须大于0', trigger: 'blur' },
  ],
  gouwu_fang_mingcheng: [{ required: true, message: '请输入购物方名称', trigger: 'blur' }],
  xiaoshou_fang_mingcheng: [{ required: true, message: '请输入销售方名称', trigger: 'blur' }],
  xiaoshou_fang_shuihao: [{ required: true, message: '请输入销售方税号', trigger: 'blur' }],
  kehu_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
}

// 方法
const calculateTotal = () => {
  form.jia_shui_jine = (form.kaipiao_jine || 0) + (form.shuie || 0)
}

const fetchCustomers = async () => {
  try {
    const response = await fetch('/customers')
    const data = await response.json()

    if (response.ok) {
      customers.value = data.items || []
    }
  } catch (error) {}
}

const fetchInvoiceDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const response = await fetch(`/invoices/${invoiceId.value}`)
    const data = await response.json()

    if (response.ok) {
      Object.assign(form, data)
    } else {
      ElMessage.error(data.detail || '获取开票申请详情失败')
      router.push('/finance/invoices')
    }
  } catch (error) {
    ElMessage.error('网络错误')
    router.push('/finance/invoices')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    submitLoading.value = true

    const url = isEdit.value ? `/invoices/${invoiceId.value}` : '/invoices'

    const method = isEdit.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form),
    })

    const data = await response.json()

    if (response.ok) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      router.push('/finance/invoices')
    } else {
      ElMessage.error(data.detail || '操作失败')
    }
  } catch (error) {
    if (error !== 'validation failed') {
      ElMessage.error('网络错误')
    }
  } finally {
    submitLoading.value = false
  }
}

const handleSaveAsDraft = async () => {
  try {
    // 草稿模式下，只验证必要字段
    if (!form.kaipiao_mingcheng || !form.gouwu_fang_mingcheng) {
      ElMessage.warning('请至少填写开票名称和购物方名称')
      return
    }

    draftLoading.value = true

    const url = isEdit.value ? `/invoices/${invoiceId.value}` : '/invoices'

    const method = isEdit.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...form,
        shenqing_zhuangtai: 'draft',
      }),
    })

    const data = await response.json()

    if (response.ok) {
      ElMessage.success('保存草稿成功')
      router.push('/finance/invoices')
    } else {
      ElMessage.error(data.detail || '保存失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    draftLoading.value = false
  }
}

const handleCancel = () => {
  router.push('/finance/invoices')
}

// 生命周期
onMounted(() => {
  fetchCustomers()
  if (isEdit.value) {
    fetchInvoiceDetail()
  }
})
</script>

<style scoped>
.invoice-form-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.header-content p {
  margin: 0;
  color: #606266;
}

.el-divider {
  margin: 30px 0 20px 0;
}

.el-divider__text {
  font-weight: bold;
  color: #303133;
}
</style>
