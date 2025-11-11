<template>
  <div class="data-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>基础数据管理</span>
        </div>
      </template>

      <el-alert
        title="基础数据说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        基础数据是系统运行的基础配置，包括产品目录、线索来源、合同模板等。这些数据相对固定，是业务操作的基础。
      </el-alert>

      <el-row :gutter="20">
        <!-- 产品设置 -->
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-card shadow="hover" class="data-card" @click="navigateTo('/product')">
            <div class="data-card-content">
              <div class="icon-wrapper product">
                <el-icon :size="32"><Box /></el-icon>
              </div>
              <h3>产品设置</h3>
              <p>管理产品分类、产品项目和产品步骤</p>
              <div class="stats">
                <el-tag type="info" size="small">{{ productStats.categories }} 个分类</el-tag>
                <el-tag type="success" size="small">{{ productStats.products }} 个产品</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 线索设置 -->
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-card shadow="hover" class="data-card" @click="handleLeadSettings">
            <div class="data-card-content">
              <div class="icon-wrapper lead">
                <el-icon :size="32"><Opportunity /></el-icon>
              </div>
              <h3>线索设置</h3>
              <p>管理线索来源和线索状态</p>
              <div class="stats">
                <el-tag type="info" size="small">{{ leadStats.sources }} 个来源</el-tag>
                <el-tag type="success" size="small">{{ leadStats.statuses }} 个状态</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 合同设置 -->
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-card shadow="hover" class="data-card" @click="handleContractSettings">
            <div class="data-card-content">
              <div class="icon-wrapper contract">
                <el-icon :size="32"><Document /></el-icon>
              </div>
              <h3>合同设置</h3>
              <p>管理合同模板、乙方主体和支付方式</p>
              <div class="stats">
                <el-tag type="info" size="small">敬请期待</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 合规设置 -->
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-card shadow="hover" class="data-card" @click="handleComplianceSettings">
            <div class="data-card-content">
              <div class="icon-wrapper compliance">
                <el-icon :size="32"><DocumentChecked /></el-icon>
              </div>
              <h3>合规设置</h3>
              <p>管理合规事项模板</p>
              <div class="stats">
                <el-tag type="info" size="small">敬请期待</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 线索设置弹窗 -->
    <el-dialog
      v-model="leadSettingsVisible"
      title="线索设置"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="leadActiveTab">
        <el-tab-pane label="线索来源" name="source">
          <LeadSourceSettings />
        </el-tab-pane>
        <el-tab-pane label="线索状态" name="status">
          <LeadStatusSettings />
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, Opportunity, Document, DocumentChecked } from '@element-plus/icons-vue'
import LeadSourceSettings from './LeadSourceSettings.vue'
import LeadStatusSettings from './LeadStatusSettings.vue'

const router = useRouter()

// 统计数据
const productStats = ref({
  categories: 0,
  products: 0
})

const leadStats = ref({
  sources: 0,
  statuses: 0
})

// 线索设置弹窗
const leadSettingsVisible = ref(false)
const leadActiveTab = ref('source')

// 导航到产品管理
const navigateTo = (path: string) => {
  router.push(path)
}

// 打开线索设置
const handleLeadSettings = () => {
  leadSettingsVisible.value = true
}

// 打开合同设置
const handleContractSettings = () => {
  ElMessage.info('合同设置功能开发中，敬请期待')
}

// 打开合规设置
const handleComplianceSettings = () => {
  ElMessage.info('合规设置功能开发中，敬请期待')
}

// 加载统计数据
const loadStats = async () => {
  try {
    // TODO: 调用API获取统计数据
    // 这里暂时使用模拟数据
    productStats.value = {
      categories: 8,
      products: 24
    }
    
    leadStats.value = {
      sources: 6,
      statuses: 5
    }
  } catch (error: any) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped lang="scss">
.data-management {
  .card-header {
    font-weight: 600;
    font-size: 16px;
  }

  .data-card {
    cursor: pointer;
    transition: all 0.3s;
    margin-bottom: 20px;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .data-card-content {
      text-align: center;
      padding: 20px 10px;

      .icon-wrapper {
        width: 64px;
        height: 64px;
        margin: 0 auto 16px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        &.product {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        &.lead {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          color: white;
        }

        &.contract {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          color: white;
        }

        &.compliance {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          color: white;
        }
      }

      h3 {
        margin: 0 0 8px;
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }

      p {
        margin: 0 0 16px;
        font-size: 14px;
        color: #909399;
        min-height: 40px;
      }

      .stats {
        display: flex;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
      }
    }
  }
}
</style>

