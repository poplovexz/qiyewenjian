<template>
  <div class="payment-config-manage">
    <div class="tab-header">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建配置
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="配置类型">
          <el-select
            v-model="filterForm.peizhi_leixing"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option label="微信支付" value="weixin" />
            <el-option label="支付宝" value="zhifubao" />
            <el-option label="银行汇款" value="yinhang" />
            <el-option label="现金支付" value="xianjin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.zhuangtai"
            placeholder="全部"
            clearable
            style="width: 120px"
          >
            <el-option label="启用" value="qiyong" />
            <el-option label="停用" value="tingyong" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="配置名称或备注"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 配置列表 -->
    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="configList" stripe style="width: 100%">
        <el-table-column prop="peizhi_mingcheng" label="配置名称" min-width="150" />
        <el-table-column prop="peizhi_leixing" label="配置类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getPaymentTypeTagType(row.peizhi_leixing)">
              {{ getPaymentTypeLabel(row.peizhi_leixing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="huanjing" label="环境" width="100">
          <template #default="{ row }">
            <el-tag :type="getEnvironmentTagType(row.huanjing)" size="small">
              {{ getEnvironmentLabel(row.huanjing) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="zhuangtai" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.zhuangtai === 'qiyong' ? 'success' : 'info'" size="small">
              {{ row.zhuangtai === 'qiyong' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="配置信息" min-width="200">
          <template #default="{ row }">
            <div v-if="row.peizhi_leixing === 'weixin'" class="config-info">
              <div>APPID: {{ row.weixin_appid || '-' }}</div>
              <div>商户号: {{ row.weixin_shanghu_hao || '-' }}</div>
            </div>
            <div v-else-if="row.peizhi_leixing === 'zhifubao'" class="config-info">
              <div>APPID: {{ row.zhifubao_appid || '-' }}</div>
            </div>
            <div v-else-if="row.peizhi_leixing === 'yinhang'" class="config-info">
              <div>银行: {{ row.yinhang_mingcheng || '-' }}</div>
              <div>账号: {{ row.yinhang_zhanghu_haoma || '-' }}</div>
            </div>
            <div v-else-if="row.peizhi_leixing === 'xianjin'" class="config-info">
              <div>现金支付</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="beizhu" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)"> 查看 </el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)"> 编辑 </el-button>
            <el-button
              link
              :type="row.zhuangtai === 'qiyong' ? 'warning' : 'success'"
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.zhuangtai === 'qiyong' ? '停用' : '启用' }}
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)"> 删除 </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="140px">
        <el-form-item label="配置名称" prop="peizhi_mingcheng">
          <el-input v-model="formData.peizhi_mingcheng" placeholder="请输入配置名称" />
        </el-form-item>

        <el-form-item label="配置类型" prop="peizhi_leixing">
          <el-radio-group v-model="formData.peizhi_leixing" :disabled="isEdit">
            <el-radio label="weixin">微信支付</el-radio>
            <el-radio label="zhifubao">支付宝</el-radio>
            <el-radio label="yinhang">银行汇款</el-radio>
            <el-radio label="xianjin">现金支付</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          label="环境"
          prop="huanjing"
          v-if="formData.peizhi_leixing === 'weixin' || formData.peizhi_leixing === 'zhifubao'"
        >
          <el-radio-group v-model="formData.huanjing">
            <el-radio label="shachang">沙箱环境</el-radio>
            <el-radio label="shengchan">生产环境</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="状态" prop="zhuangtai">
          <el-radio-group v-model="formData.zhuangtai">
            <el-radio label="qiyong">启用</el-radio>
            <el-radio label="tingyong">停用</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 微信支付配置 -->
        <template v-if="formData.peizhi_leixing === 'weixin'">
          <el-divider content-position="left">微信支付配置</el-divider>

          <el-form-item label="微信APPID" prop="weixin_appid">
            <el-input v-model="formData.weixin_appid" placeholder="请输入微信APPID" />
          </el-form-item>

          <el-form-item label="微信商户号" prop="weixin_shanghu_hao">
            <el-input v-model="formData.weixin_shanghu_hao" placeholder="请输入微信商户号" />
          </el-form-item>

          <el-form-item label="商户私钥" prop="weixin_shanghu_siyao">
            <el-input
              v-model="formData.weixin_shanghu_siyao"
              type="textarea"
              :rows="4"
              placeholder="请输入商户私钥（PEM格式）"
            />
          </el-form-item>

          <el-form-item label="证书序列号" prop="weixin_zhengshu_xuliehao">
            <el-input v-model="formData.weixin_zhengshu_xuliehao" placeholder="请输入证书序列号" />
          </el-form-item>

          <el-form-item label="API v3密钥" prop="weixin_api_v3_miyao">
            <el-input
              v-model="formData.weixin_api_v3_miyao"
              type="password"
              show-password
              placeholder="请输入API v3密钥"
            />
          </el-form-item>
        </template>

        <!-- 支付宝配置 -->
        <template v-if="formData.peizhi_leixing === 'zhifubao'">
          <el-divider content-position="left">支付宝配置</el-divider>

          <el-form-item label="支付宝APPID" prop="zhifubao_appid">
            <el-input v-model="formData.zhifubao_appid" placeholder="请输入支付宝APPID" />
          </el-form-item>

          <el-form-item label="支付宝网关" prop="zhifubao_wangguan">
            <el-input v-model="formData.zhifubao_wangguan" placeholder="请输入支付宝网关地址" />
            <div class="form-tip">
              沙箱环境: https://openapi-sandbox.dl.alipaydev.com/gateway.do<br />
              生产环境: https://openapi.alipay.com/gateway.do
            </div>
          </el-form-item>

          <el-form-item label="商户私钥" prop="zhifubao_shanghu_siyao">
            <el-input
              v-model="formData.zhifubao_shanghu_siyao"
              type="textarea"
              :rows="4"
              placeholder="请输入商户私钥（RSA2格式）"
            />
          </el-form-item>

          <el-form-item label="支付宝公钥" prop="zhifubao_zhifubao_gongyao">
            <el-input
              v-model="formData.zhifubao_zhifubao_gongyao"
              type="textarea"
              :rows="4"
              placeholder="请输入支付宝公钥"
            />
          </el-form-item>
        </template>

        <!-- 银行汇款配置 -->
        <template v-if="formData.peizhi_leixing === 'yinhang'">
          <el-divider content-position="left">银行账户信息</el-divider>

          <el-form-item label="银行名称" prop="yinhang_mingcheng">
            <el-input
              v-model="formData.yinhang_mingcheng"
              placeholder="请输入银行名称，如：中国银行"
            />
          </el-form-item>

          <el-form-item label="账户名称" prop="yinhang_zhanghu_mingcheng">
            <el-input v-model="formData.yinhang_zhanghu_mingcheng" placeholder="请输入账户名称" />
          </el-form-item>

          <el-form-item label="银行账号" prop="yinhang_zhanghu_haoma">
            <el-input v-model="formData.yinhang_zhanghu_haoma" placeholder="请输入银行账号" />
          </el-form-item>

          <el-form-item label="开户行名称" prop="kaihuhang_mingcheng">
            <el-input v-model="formData.kaihuhang_mingcheng" placeholder="请输入开户行名称" />
          </el-form-item>

          <el-form-item label="开户行联行号" prop="kaihuhang_lianhanghao">
            <el-input
              v-model="formData.kaihuhang_lianhanghao"
              placeholder="请输入开户行联行号（可选）"
            />
          </el-form-item>
        </template>

        <!-- 通用配置 -->
        <el-divider content-position="left">通用配置</el-divider>

        <el-form-item
          label="回调通知URL"
          prop="tongzhi_url"
          v-if="formData.peizhi_leixing === 'weixin' || formData.peizhi_leixing === 'zhifubao'"
        >
          <el-input v-model="formData.tongzhi_url" placeholder="请输入回调通知URL" />
          <div class="form-tip">支付成功后，第三方平台会向此URL发送通知</div>
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="formData.beizhu"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit"> 确定 </el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog v-model="viewDialogVisible" title="配置详情" width="700px">
      <el-descriptions :column="2" border v-if="viewData">
        <el-descriptions-item label="配置名称">{{
          viewData.peizhi_mingcheng
        }}</el-descriptions-item>
        <el-descriptions-item label="配置类型">
          <el-tag :type="getPaymentTypeTagType(viewData.peizhi_leixing)">
            {{ getPaymentTypeLabel(viewData.peizhi_leixing) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="环境">
          <el-tag :type="getEnvironmentTagType(viewData.huanjing)">
            {{ getEnvironmentLabel(viewData.huanjing) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewData.zhuangtai === 'qiyong' ? 'success' : 'info'">
            {{ viewData.zhuangtai === 'qiyong' ? '启用' : '停用' }}
          </el-tag>
        </el-descriptions-item>

        <template v-if="viewData.peizhi_leixing === 'weixin'">
          <el-descriptions-item label="微信APPID" :span="2">{{
            viewData.weixin_appid || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="微信商户号" :span="2">{{
            viewData.weixin_shanghu_hao || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="商户私钥" :span="2">{{
            viewData.weixin_shanghu_siyao_masked || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="证书序列号" :span="2">{{
            viewData.weixin_zhengshu_xuliehao || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="API v3密钥" :span="2">{{
            viewData.weixin_api_v3_miyao_masked || '-'
          }}</el-descriptions-item>
        </template>

        <template v-if="viewData.peizhi_leixing === 'zhifubao'">
          <el-descriptions-item label="支付宝APPID" :span="2">{{
            viewData.zhifubao_appid || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="支付宝网关" :span="2">{{
            viewData.zhifubao_wangguan || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="商户私钥" :span="2">{{
            viewData.zhifubao_shanghu_siyao_masked || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="支付宝公钥" :span="2">{{
            viewData.zhifubao_zhifubao_gongyao_masked || '-'
          }}</el-descriptions-item>
        </template>

        <template v-if="viewData.peizhi_leixing === 'yinhang'">
          <el-descriptions-item label="银行名称" :span="2">{{
            viewData.yinhang_mingcheng || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="账户名称" :span="2">{{
            viewData.yinhang_zhanghu_mingcheng || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="银行账号" :span="2">{{
            viewData.yinhang_zhanghu_haoma || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="开户行名称" :span="2">{{
            viewData.kaihuhang_mingcheng || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="开户行联行号" :span="2">{{
            viewData.kaihuhang_lianhanghao || '-'
          }}</el-descriptions-item>
        </template>

        <el-descriptions-item
          label="回调通知URL"
          :span="2"
          v-if="viewData.peizhi_leixing === 'weixin' || viewData.peizhi_leixing === 'zhifubao'"
          >{{ viewData.tongzhi_url || '-' }}</el-descriptions-item
        >
        <el-descriptions-item label="备注" :span="2">{{
          viewData.beizhu || '-'
        }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{
          formatDateTime(viewData.created_at)
        }}</el-descriptions-item>
        <el-descriptions-item label="更新时间" :span="2">{{
          formatDateTime(viewData.updated_at)
        }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getZhifuPeizhiList,
  getZhifuPeizhiForEdit,
  createZhifuPeizhi,
  updateZhifuPeizhi,
  deleteZhifuPeizhi,
  toggleZhifuPeizhiStatus,
  type ZhifuPeizhiResponse,
  type ZhifuPeizhiCreate,
  type ZhifuPeizhiUpdate,
} from '@/api/modules/payment-config'
import { formatDateTime } from '@/utils/date'

// 列表数据
const loading = ref(false)
const configList = ref<ZhifuPeizhiResponse[]>([])

// 筛选表单
const filterForm = reactive({
  peizhi_leixing: '',
  zhuangtai: '',
  search: '',
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

// 表单数据
const formData = reactive<ZhifuPeizhiCreate>({
  peizhi_mingcheng: '',
  peizhi_leixing: 'weixin',
  zhuangtai: 'qiyong',
  huanjing: 'shachang',
  weixin_appid: '',
  weixin_shanghu_hao: '',
  weixin_shanghu_siyao: '',
  weixin_zhengshu_xuliehao: '',
  weixin_api_v3_miyao: '',
  zhifubao_appid: '',
  zhifubao_wangguan: '',
  zhifubao_shanghu_siyao: '',
  zhifubao_zhifubao_gongyao: '',
  tongzhi_url: '',
  beizhu: '',
})

// 表单验证规则
const formRules: FormRules = {
  peizhi_mingcheng: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  peizhi_leixing: [{ required: true, message: '请选择配置类型', trigger: 'change' }],
}

// 查看对话框
const viewDialogVisible = ref(false)
const viewData = ref<ZhifuPeizhiResponse | null>(null)

// 加载列表
const loadList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      peizhi_leixing: filterForm.peizhi_leixing || undefined,
      zhuangtai: filterForm.zhuangtai || undefined,
      search: filterForm.search || undefined,
    }
    const res = await getZhifuPeizhiList(params)
    configList.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadList()
}

// 重置
const handleReset = () => {
  filterForm.peizhi_leixing = ''
  filterForm.zhuangtai = ''
  filterForm.search = ''
  handleSearch()
}

// 分页变化
const handleSizeChange = () => {
  loadList()
}

const handlePageChange = () => {
  loadList()
}

// 新建
const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新建支付配置'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = async (row: ZhifuPeizhiResponse) => {
  try {
    isEdit.value = true
    dialogTitle.value = '编辑支付配置'

    // 调用编辑专用API获取完整数据（包括解密后的敏感信息）
    const data = await getZhifuPeizhiForEdit(row.id)

    // 先重置表单，避免旧数据残留
    resetForm()

    // 将获取的数据赋值给表单
    Object.assign(formData, data)

    dialogVisible.value = true
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '获取配置详情失败')
  }
}

// 查看
const handleView = (row: ZhifuPeizhiResponse) => {
  viewData.value = row
  viewDialogVisible.value = true
}

// 切换状态
const handleToggleStatus = async (row: ZhifuPeizhiResponse) => {
  try {
    await toggleZhifuPeizhiStatus(row.id)
    ElMessage.success('状态切换成功')
    loadList()
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

// 删除
const handleDelete = async (row: ZhifuPeizhiResponse) => {
  try {
    await ElMessageBox.confirm('确定要删除此配置吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteZhifuPeizhi(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateZhifuPeizhi((formData as any).id, formData as ZhifuPeizhiUpdate)
        ElMessage.success('更新成功')
      } else {
        await createZhifuPeizhi(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitLoading.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    peizhi_mingcheng: '',
    peizhi_leixing: 'weixin',
    zhuangtai: 'qiyong',
    huanjing: 'wuxu',
    weixin_appid: '',
    weixin_shanghu_hao: '',
    weixin_shanghu_siyao: '',
    weixin_zhengshu_xuliehao: '',
    weixin_api_v3_miyao: '',
    zhifubao_appid: '',
    zhifubao_shanghu_siyao: '',
    zhifubao_zhifubao_gongyao: '',
    yinhang_mingcheng: '',
    yinhang_zhanghu_mingcheng: '',
    yinhang_zhanghu_haoma: '',
    kaihuhang_mingcheng: '',
    kaihuhang_lianhanghao: '',
    tongzhi_url: '',
    beizhu: '',
  })
  formRef.value?.clearValidate()
}

// 辅助函数：获取支付类型标签
const getPaymentTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    weixin: '微信支付',
    zhifubao: '支付宝',
    yinhang: '银行汇款',
    xianjin: '现金支付',
  }
  return map[type] || type
}

// 辅助函数：获取支付类型标签颜色
const getPaymentTypeTagType = (type: string) => {
  const map: Record<string, string> = {
    weixin: 'success',
    zhifubao: 'primary',
    yinhang: 'warning',
    xianjin: 'info',
  }
  return map[type] || ''
}

// 辅助函数：获取环境标签
const getEnvironmentLabel = (env: string) => {
  const map: Record<string, string> = {
    shachang: '沙箱',
    shengchan: '生产',
    wuxu: '无需',
  }
  return map[env] || env
}

// 辅助函数：获取环境标签颜色
const getEnvironmentTagType = (env: string) => {
  const map: Record<string, string> = {
    shachang: 'warning',
    shengchan: 'danger',
    wuxu: 'info',
  }
  return map[env] || ''
}

onMounted(() => {
  loadList()
})
</script>

<style scoped lang="scss">
.payment-config-manage {
  .tab-header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;
  }

  .filter-card {
    margin-bottom: 20px;
  }

  .table-card {
    .config-info {
      font-size: 12px;
      color: #606266;
      line-height: 1.6;
    }

    .pagination-container {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}
</style>
