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
      v-loading="loading"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="公司名称" prop="gongsi_mingcheng">
            <el-input
              v-model="formData.gongsi_mingcheng"
              placeholder="请输入公司名称"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="联系人" prop="lianxi_ren">
            <el-input
              v-model="formData.lianxi_ren"
              placeholder="请输入联系人姓名"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="联系电话" prop="lianxi_dianhua">
            <el-input
              v-model="formData.lianxi_dianhua"
              placeholder="请输入联系电话"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="联系邮箱" prop="lianxi_youxiang">
            <el-input
              v-model="formData.lianxi_youxiang"
              placeholder="请输入联系邮箱"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="行业类型" prop="hangye_leixing">
            <el-select
              v-model="formData.hangye_leixing"
              placeholder="请选择行业类型"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option label="制造业" value="manufacturing" />
              <el-option label="服务业" value="service" />
              <el-option label="贸易" value="trade" />
              <el-option label="科技" value="technology" />
              <el-option label="金融" value="finance" />
              <el-option label="房地产" value="realestate" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="公司规模" prop="gongsi_guimo">
            <el-select
              v-model="formData.gongsi_guimo"
              placeholder="请选择公司规模"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option label="1-10人" value="1-10" />
              <el-option label="11-50人" value="11-50" />
              <el-option label="51-200人" value="51-200" />
              <el-option label="201-500人" value="201-500" />
              <el-option label="500人以上" value="500+" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="注册地址" prop="zhuce_dizhi">
        <el-input
          v-model="formData.zhuce_dizhi"
          placeholder="请输入公司注册地址"
          :disabled="mode === 'view'"
        />
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="服务类型" prop="fuwu_leixing">
            <el-select
              v-model="formData.fuwu_leixing"
              placeholder="请选择服务类型"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option label="代理记账" value="bookkeeping" />
              <el-option label="税务申报" value="tax" />
              <el-option label="工商注册" value="registration" />
              <el-option label="审计服务" value="audit" />
              <el-option label="财务咨询" value="consulting" />
              <el-option label="综合服务" value="comprehensive" />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="预算范围" prop="yusuan_fanwei">
            <el-select
              v-model="formData.yusuan_fanwei"
              placeholder="请选择预算范围"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option label="1000元以下" value="<1000" />
              <el-option label="1000-3000元" value="1000-3000" />
              <el-option label="3000-5000元" value="3000-5000" />
              <el-option label="5000-10000元" value="5000-10000" />
              <el-option label="10000元以上" value=">10000" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="时间要求" prop="shijian_yaoqiu">
            <el-select
              v-model="formData.shijian_yaoqiu"
              placeholder="请选择时间要求"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option label="立即开始" value="immediate" />
              <el-option label="1周内" value="1week" />
              <el-option label="1个月内" value="1month" />
              <el-option label="3个月内" value="3months" />
              <el-option label="暂无时间要求" value="flexible" />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="线索来源" prop="laiyuan_id">
            <el-select
              v-model="formData.laiyuan_id"
              placeholder="请选择线索来源"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option
                v-for="source in active_laiyuan_list"
                :key="source.id"
                :label="source.laiyuan_mingcheng"
                :value="source.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="质量评估" prop="zhiliang_pinggu">
            <el-select
              v-model="formData.zhiliang_pinggu"
              placeholder="请选择质量评估"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option label="高质量" value="high" />
              <el-option label="中等质量" value="medium" />
              <el-option label="低质量" value="low" />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="质量分数" prop="zhiliang_fenshu">
            <el-input-number
              v-model="formData.zhiliang_fenshu"
              :min="0"
              :max="100"
              :disabled="mode === 'view'"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="来源详细" prop="laiyuan_xiangxi">
        <el-input
          v-model="formData.laiyuan_xiangxi"
          type="textarea"
          :rows="2"
          placeholder="请输入来源详细信息"
          :disabled="mode === 'view'"
        />
      </el-form-item>
      
      <el-form-item label="详细需求" prop="xiangxi_xuqiu">
        <el-input
          v-model="formData.xiangxi_xuqiu"
          type="textarea"
          :rows="3"
          placeholder="请输入客户的详细需求"
          :disabled="mode === 'view'"
        />
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
          {{ mode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import type { Xiansuo, XiansuoCreate, XiansuoUpdate } from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
  xiansuo?: Xiansuo | null
}

const props = withDefaults(defineProps<Props>(), {
  xiansuo: null
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 使用store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = ref<XiansuoCreate & { zhiliang_fenshu?: number }>({
  gongsi_mingcheng: '',
  lianxi_ren: '',
  lianxi_dianhua: '',
  lianxi_youxiang: '',
  hangye_leixing: '',
  gongsi_guimo: '',
  zhuce_dizhi: '',
  fuwu_leixing: '',
  yusuan_fanwei: '',
  shijian_yaoqiu: '',
  xiangxi_xuqiu: '',
  zhiliang_pinggu: 'medium',
  zhiliang_fenshu: 60,
  laiyuan_id: '',
  laiyuan_xiangxi: ''
})

// 表单验证规则
const formRules: FormRules = {
  gongsi_mingcheng: [
    { required: true, message: '请输入公司名称', trigger: 'blur' }
  ],
  lianxi_ren: [
    { required: true, message: '请输入联系人姓名', trigger: 'blur' }
  ],
  lianxi_dianhua: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  lianxi_youxiang: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  laiyuan_id: [
    { required: true, message: '请选择线索来源', trigger: 'change' }
  ]
}

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  const titles = {
    create: '新增线索',
    edit: '编辑线索',
    view: '查看线索'
  }
  return titles[props.mode]
})

// 使用 storeToRefs 保持响应式
const { active_laiyuan_list } = storeToRefs(xiansuoStore)

// 监听props变化
watch(
  () => props.xiansuo,
  (newXiansuo) => {
    if (newXiansuo && (props.mode === 'edit' || props.mode === 'view')) {
      formData.value = {
        gongsi_mingcheng: newXiansuo.gongsi_mingcheng,
        lianxi_ren: newXiansuo.lianxi_ren,
        lianxi_dianhua: newXiansuo.lianxi_dianhua || '',
        lianxi_youxiang: newXiansuo.lianxi_youxiang || '',
        hangye_leixing: newXiansuo.hangye_leixing || '',
        gongsi_guimo: newXiansuo.gongsi_guimo || '',
        zhuce_dizhi: newXiansuo.zhuce_dizhi || '',
        fuwu_leixing: newXiansuo.fuwu_leixing || '',
        yusuan_fanwei: newXiansuo.yusuan_fanwei || '',
        shijian_yaoqiu: newXiansuo.shijian_yaoqiu || '',
        xiangxi_xuqiu: newXiansuo.xiangxi_xuqiu || '',
        zhiliang_pinggu: newXiansuo.zhiliang_pinggu,
        zhiliang_fenshu: newXiansuo.zhiliang_fenshu,
        laiyuan_id: newXiansuo.laiyuan_id,
        laiyuan_xiangxi: newXiansuo.laiyuan_xiangxi || ''
      }
    }
  },
  { immediate: true }
)

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      // 确保线索来源列表已加载
      if (active_laiyuan_list.value.length === 0) {
        await xiansuoStore.fetchActiveLaiyuanList()
      }

      if (props.mode === 'create') {
        resetForm()
      }
    }
  }
)

// 方法
const resetForm = () => {
  formData.value = {
    gongsi_mingcheng: '',
    lianxi_ren: '',
    lianxi_dianhua: '',
    lianxi_youxiang: '',
    hangye_leixing: '',
    gongsi_guimo: '',
    zhuce_dizhi: '',
    fuwu_leixing: '',
    yusuan_fanwei: '',
    shijian_yaoqiu: '',
    xiangxi_xuqiu: '',
    zhiliang_pinggu: 'medium',
    zhiliang_fenshu: 60,
    laiyuan_id: '',
    laiyuan_xiangxi: ''
  }
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const handleClose = () => {
  // 重置表单验证状态
  formRef.value?.clearValidate()
  // 关闭弹窗
  dialogVisible.value = false
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    let success = false
    if (props.mode === 'create') {
      success = await xiansuoStore.createXiansuo(formData.value)
    } else if (props.mode === 'edit' && props.xiansuo) {
      const updateData: XiansuoUpdate = { ...formData.value }
      delete updateData.zhiliang_fenshu // 移除不需要的字段
      success = await xiansuoStore.updateXiansuo(props.xiansuo.id, updateData)
    }

    if (success) {
      // 成功后关闭弹窗并触发成功事件
      dialogVisible.value = false
      emit('success')
    }
  } catch (error) {
    console.error('表单提交失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
