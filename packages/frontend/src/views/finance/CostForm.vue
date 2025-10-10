<template>
  <div class="cost-form-container">
    <el-card class="page-header">
      <div class="header-content">
        <h2>{{ isEdit ? '编辑成本记录' : '新建成本记录' }}</h2>
        <p>{{ isEdit ? '修改成本记录信息' : '创建新的成本记录' }}</p>
      </div>
    </el-card>

    <el-card>
      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        v-loading="loading"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="成本名称" prop="chengben_mingcheng">
              <el-input v-model="form.chengben_mingcheng" placeholder="请输入成本名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本类型" prop="chengben_leixing">
              <el-select v-model="form.chengben_leixing" placeholder="请选择成本类型" style="width: 100%">
                <el-option label="人工成本" value="rengong" />
                <el-option label="材料成本" value="cailiao" />
                <el-option label="设备成本" value="shebei" />
                <el-option label="外包成本" value="waibao" />
                <el-option label="其他成本" value="qita" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="成本分类" prop="chengben_fenlei">
              <el-select v-model="form.chengben_fenlei" placeholder="请选择成本分类" style="width: 100%">
                <el-option label="直接成本" value="zhijie" />
                <el-option label="间接成本" value="jianjie" />
                <el-option label="固定成本" value="guding" />
                <el-option label="变动成本" value="biandong" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发生时间" prop="fasheng_shijian">
              <el-date-picker
                v-model="form.fasheng_shijian"
                type="datetime"
                placeholder="选择发生时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="成本描述" prop="chengben_miaoshu">
          <el-input 
            v-model="form.chengben_miaoshu" 
            type="textarea" 
            :rows="3"
            placeholder="请输入成本描述"
          />
        </el-form-item>

        <!-- 金额信息 -->
        <el-divider content-position="left">金额信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="成本金额" prop="chengben_jine">
              <el-input-number 
                v-model="form.chengben_jine" 
                :precision="2"
                :min="0"
                style="width: 100%"
                placeholder="请输入成本金额"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预算金额" prop="yusuan_jine">
              <el-input-number 
                v-model="form.yusuan_jine" 
                :precision="2"
                :min="0"
                style="width: 100%"
                placeholder="请输入预算金额"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="币种" prop="bizhong">
              <el-select v-model="form.bizhong" placeholder="请选择币种" style="width: 100%">
                <el-option label="人民币" value="CNY" />
                <el-option label="美元" value="USD" />
                <el-option label="欧元" value="EUR" />
                <el-option label="日元" value="JPY" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 供应商信息 -->
        <el-divider content-position="left">供应商信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商名称" prop="gongyingshang_mingcheng">
              <el-input v-model="form.gongyingshang_mingcheng" placeholder="请输入供应商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商联系人" prop="gongyingshang_lianxiren">
              <el-input v-model="form.gongyingshang_lianxiren" placeholder="请输入供应商联系人" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="gongyingshang_dianhua">
              <el-input v-model="form.gongyingshang_dianhua" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商地址" prop="gongyingshang_dizhi">
              <el-input v-model="form.gongyingshang_dizhi" placeholder="请输入供应商地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 关联信息 -->
        <el-divider content-position="left">关联信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="关联合同" prop="hetong_id">
              <el-select v-model="form.hetong_id" placeholder="请选择关联合同" style="width: 100%" filterable clearable>
                <el-option 
                  v-for="contract in contracts"
                  :key="contract.id"
                  :label="contract.hetong_mingcheng"
                  :value="contract.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="关联项目" prop="xiangmu_id">
              <el-select v-model="form.xiangmu_id" placeholder="请选择关联项目" style="width: 100%" filterable clearable>
                <el-option 
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.xiangmu_mingcheng"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="所属部门" prop="bumen_id">
              <el-select v-model="form.bumen_id" placeholder="请选择所属部门" style="width: 100%" filterable clearable>
                <el-option 
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.bumen_mingcheng"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 发票信息 -->
        <el-divider content-position="left">发票信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="发票号" prop="fapiao_hao">
              <el-input v-model="form.fapiao_hao" placeholder="请输入发票号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="发票代码" prop="fapiao_daima">
              <el-input v-model="form.fapiao_daima" placeholder="请输入发票代码" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="发票状态" prop="fapiao_zhuangtai">
              <el-select v-model="form.fapiao_zhuangtai" placeholder="请选择发票状态" style="width: 100%">
                <el-option label="未开票" value="not_issued" />
                <el-option label="已开票" value="issued" />
                <el-option label="已收票" value="received" />
                <el-option label="已认证" value="verified" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发票日期" prop="fapiao_riqi">
              <el-date-picker
                v-model="form.fapiao_riqi"
                type="date"
                placeholder="选择发票日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发票金额" prop="fapiao_jine">
              <el-input-number 
                v-model="form.fapiao_jine" 
                :precision="2"
                :min="0"
                style="width: 100%"
                placeholder="请输入发票金额"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 会计信息 -->
        <el-divider content-position="left">会计信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="会计科目" prop="kuaiji_kemu">
              <el-input v-model="form.kuaiji_kemu" placeholder="请输入会计科目" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="成本中心" prop="chengben_zhongxin">
              <el-input v-model="form.chengben_zhongxin" placeholder="请输入成本中心" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分摊方式" prop="fentan_fangshi">
              <el-select v-model="form.fentan_fangshi" placeholder="请选择分摊方式" style="width: 100%">
                <el-option label="直接分摊" value="direct" />
                <el-option label="按比例分摊" value="proportional" />
                <el-option label="平均分摊" value="average" />
                <el-option label="不分摊" value="none" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="beizhu">
          <el-input 
            v-model="form.beizhu" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
          <el-button @click="handleSaveAsDraft" :loading="draftLoading">
            保存为草稿
          </el-button>
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
const contracts = ref([])
const projects = ref([])
const departments = ref([])

const isEdit = computed(() => route.name === 'CostEdit')
const costId = computed(() => route.params.id as string)

const form = reactive({
  hetong_id: '',
  xiangmu_id: '',
  bumen_id: '',
  chengben_mingcheng: '',
  chengben_leixing: '',
  chengben_fenlei: '',
  chengben_miaoshu: '',
  chengben_jine: 0,
  yusuan_jine: 0,
  bizhong: 'CNY',
  fasheng_shijian: null,
  gongyingshang_mingcheng: '',
  gongyingshang_lianxiren: '',
  gongyingshang_dianhua: '',
  gongyingshang_dizhi: '',
  fapiao_hao: '',
  fapiao_daima: '',
  fapiao_zhuangtai: 'not_issued',
  fapiao_riqi: null,
  fapiao_jine: 0,
  kuaiji_kemu: '',
  chengben_zhongxin: '',
  fentan_fangshi: 'direct',
  beizhu: ''
})

const rules = {
  chengben_mingcheng: [
    { required: true, message: '请输入成本名称', trigger: 'blur' }
  ],
  chengben_leixing: [
    { required: true, message: '请选择成本类型', trigger: 'change' }
  ],
  chengben_fenlei: [
    { required: true, message: '请选择成本分类', trigger: 'change' }
  ],
  chengben_jine: [
    { required: true, message: '请输入成本金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '成本金额必须大于0', trigger: 'blur' }
  ],
  fasheng_shijian: [
    { required: true, message: '请选择发生时间', trigger: 'change' }
  ],
  bizhong: [
    { required: true, message: '请选择币种', trigger: 'change' }
  ]
}

// 方法
const fetchOptions = async () => {
  try {
    // 获取合同列表
    const contractResponse = await fetch('/api/v1/contracts')
    if (contractResponse.ok) {
      const contractData = await contractResponse.json()
      contracts.value = contractData.items || []
    }

    // 获取项目列表
    const projectResponse = await fetch('/api/v1/projects')
    if (projectResponse.ok) {
      const projectData = await projectResponse.json()
      projects.value = projectData.items || []
    }

    // 获取部门列表
    const deptResponse = await fetch('/api/v1/departments')
    if (deptResponse.ok) {
      const deptData = await deptResponse.json()
      departments.value = deptData.items || []
    }
  } catch (error) {
    console.error('获取选项数据失败:', error)
  }
}

const fetchCostDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const response = await fetch(`/api/v1/costs/${costId.value}`)
    const data = await response.json()
    
    if (response.ok) {
      Object.assign(form, data)
    } else {
      ElMessage.error(data.detail || '获取成本记录详情失败')
      router.push('/finance/costs')
    }
  } catch (error) {
    ElMessage.error('网络错误')
    router.push('/finance/costs')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    submitLoading.value = true
    
    const url = isEdit.value 
      ? `/api/v1/costs/${costId.value}`
      : '/api/v1/costs'
    
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form)
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      router.push('/finance/costs')
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
    if (!form.chengben_mingcheng || !form.chengben_leixing) {
      ElMessage.warning('请至少填写成本名称和成本类型')
      return
    }
    
    draftLoading.value = true
    
    const url = isEdit.value 
      ? `/api/v1/costs/${costId.value}`
      : '/api/v1/costs'
    
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...form,
        shenhe_zhuangtai: 'draft'
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success('保存草稿成功')
      router.push('/finance/costs')
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
  router.push('/finance/costs')
}

// 生命周期
onMounted(() => {
  fetchOptions()
  if (isEdit.value) {
    fetchCostDetail()
  }
})
</script>

<style scoped>
.cost-form-container {
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
